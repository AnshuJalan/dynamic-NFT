##################################################################################
#                                Create Structure
#
# Create structure allows for more naturally dynamic token metadata similar to
# Point, but instead of building an external link to a TZIP-21 Json, it builds
# and serves the JSON through an off-chain view.
#
# It is useful when most of the fields in the metadata JSON are static or the
# off-chain datastore needs to be simplified. For instance, if a token has fixed
# 'symbol' and 'decimals' and a static thumbnailUri, only fields like artifactUri
# and displayUri need to be dynamically generated. These may be an external link
# or an SVG (as shown in SVG Structure).
#
# The liveness of the external server on which the artifact is hosted must be
# ensured. A decentralised storage service like IPFS is recommended. Moreover,
# the URIs generated in the off-chain view must be verified.
##################################################################################

import smartpy as sp

Utils = sp.io.import_script_from_url("file:../common/utils.py")
Errors = sp.io.import_script_from_url("file:../common/errors.py")
Addresses = sp.io.import_script_from_url("file:../common/addresses.py")
FA2_Errors = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Errors
FA2_Lib = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Lib


class Types:
    # State is a generic representation of the attributes/properties an NFT may have.
    # Example: The construction status of different areas of a real estate (lawn, roofing etc)
    #          A nat value 0 would mean under-construction, and 1 may mean completed.
    STATE = sp.TRecord(prop_1=sp.TNat, prop_2=sp.TNat)


class Create(FA2_Lib):
    def __init__(
        self,
        admin=Addresses.ADMIN,
        # A mapping from token_id to the state of an NFT
        states=sp.big_map(
            l={},
            tkey=sp.TNat,
            tvalue=Types.STATE,
        ),
        # IPFS link hosts the metadata at ./metadata/create.json
        metadata=sp.utils.metadata_of_url("ipfs://QmUnvi9cQADj95FVdStweU7S4b2BYD8HCcvEhyEKEr4Bo4"),
        **kwargs
    ):
        # Use the storage and entrypoints of the FA2 lib
        FA2_Lib.__init__(self, **kwargs)

        # Add admin, states and metadata to the existing storage
        self.update_initial_storage(admin=admin, states=states, metadata=metadata)

        METADATA = {
            "name": "dNFT Create",
            "version": "1.0.0",
            "description": "dNFT (dynamic NFT) contract with Create Structure",
            "interfaces": ["TZIP-012", "TZIP-016", "TZIP-021"],
            "views": [self.token_metadata],
        }

        # Smartpy's helper to create the metadata json
        self.init_metadata("metadata", METADATA)

    @sp.entry_point
    def mint(self, params):
        sp.set_type(
            params,
            sp.TRecord(
                address=sp.TAddress,
                token_id=sp.TNat,
                state=Types.STATE,
            ),
        )

        # Sanity checks
        sp.verify(sp.sender == self.data.admin, Errors.NOT_AUTHORISED)
        sp.verify(~self.data.states.contains(params.token_id), Errors.TOKEN_ID_ALREADY_EXISTS)

        # Mint the token
        self.data.ledger[(params.address, params.token_id)] = 1
        self.data.states[params.token_id] = params.state

    # This may called by an admin, another authorised contract or internally by the same contract.
    # Call structure depends on the use-case
    @sp.entry_point
    def change_state(self, params):
        sp.set_type(
            params,
            sp.TRecord(token_id=sp.TNat, state=Types.STATE),
        )

        sp.verify(sp.sender == self.data.admin, Errors.NOT_AUTHORISED)

        # Verify that token exists
        sp.verify(self.data.states.contains(params.token_id), FA2_Errors.FA2_TOKEN_UNDEFINED)

        # Update the state of the entity behind the token_id
        self.data.states[params.token_id] = params.state

    # offchain-view is not pure because the metadata for a particular token-id changes based on the states
    @sp.offchain_view(pure=False)
    def token_metadata(self, token_id):
        sp.set_type(token_id, sp.TNat)

        # Verify that token id exist
        sp.verify(self.data.states.contains(token_id), FA2_Errors.FA2_TOKEN_UNDEFINED)

        # Fetch the current state of the entity behind the token-id
        state = sp.compute(self.data.states[token_id])

        bytes_of_nat = sp.compute(Utils.bytes_of_nat)

        # Convert values to bytes
        prop_1 = bytes_of_nat(state.prop_1)
        prop_2 = bytes_of_nat(state.prop_2)
        b_token_id = bytes_of_nat(token_id)

        slash = sp.utils.bytes_of_string("/")

        png = sp.utils.bytes_of_string(".png")

        # Construct the artifact/display image uri in bytes form
        # NOTE: This is a sample construction. The form your may url take depends entirely
        #       upon how your artifacts are hosted.
        image_url = sp.utils.bytes_of_string("https://image_url.com")
        image_uri = image_url + slash + prop_1 + slash + prop_2 + slash + b_token_id + png

        # Create a TZIP-21 compliant token-info
        metadata_tzip_21 = {
            "name": sp.utils.bytes_of_string("dNFT Create"),
            "symbol": sp.utils.bytes_of_string("dNFTC"),
            "decimals": sp.utils.bytes_of_string("0"),
            "thumbnailUri": sp.utils.bytes_of_string("https://image_url.com/thumbnail.png"),  # Dummy link
            # Dynamic fields
            "artifactUri": image_uri,
            "displayUri": image_uri,
            "ttl": bytes_of_nat(sp.nat(600)),
        }

        # Return the TZIP-16 compliant metadata
        sp.result(
            sp.record(
                token_id=token_id,
                token_info=metadata_tzip_21,
            )
        )


########
# Tests
########

if __name__ == "__main__":

    @sp.add_test(name="mint - correctly mints an NFT")
    def test():
        scenario = sp.test_scenario()

        create = Create()
        scenario += create

        # When the ADMIN mints an NFT with token-id 1 for Alice
        scenario += create.mint(
            address=Addresses.ALICE,
            token_id=1,
            state=sp.record(prop_1=5, prop_2=6),
        ).run(sender=Addresses.ADMIN)

        # The storage is updated correctly
        scenario.verify(create.data.ledger[(Addresses.ALICE, 1)] == 1)
        scenario.verify(create.data.states[1] == sp.record(prop_1=5, prop_2=6))

    @sp.add_test(name="mint - fails if sender is not the admin")
    def test():
        scenario = sp.test_scenario()

        create = Create()
        scenario += create

        # When the ALICE (not admin) mints an NFT with token-id 1, txn fails
        scenario += create.mint(
            address=Addresses.ALICE,
            token_id=1,
            state=sp.record(prop_1=5, prop_2=6),
        ).run(sender=Addresses.ALICE, valid=False, exception=Errors.NOT_AUTHORISED)

    @sp.add_test(name="mint - fails if token already exists")
    def test():
        scenario = sp.test_scenario()

        create = Create(
            states=sp.big_map(
                {
                    1: sp.record(prop_1=5, prop_2=6),
                }
            )
        )
        scenario += create

        # When the ADMIN mints an NFT with token-id 1 (already exists), txn fails
        scenario += create.mint(
            address=Addresses.ALICE,
            token_id=1,
            state=sp.record(prop_1=5, prop_2=6),
        ).run(sender=Addresses.ADMIN, valid=False, exception=Errors.TOKEN_ID_ALREADY_EXISTS)

    @sp.add_test(name="change_state - updates the state of a token")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and state
        create = Create(
            states=sp.big_map(
                l={
                    21: sp.record(prop_1=0, prop_2=1),
                },
            ),
        )
        scenario += create

        new_state = sp.record(prop_1=5, prop_2=10)

        # Call change_state on token 21 and assign a new state
        scenario += create.change_state(
            token_id=21,
            state=new_state,
        ).run(sender=Addresses.ADMIN)

        # State is updated correctly
        scenario.verify(create.data.states[21] == new_state)

    @sp.add_test(name="change_state - fails if sender is not the admin")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and state
        create = Create(
            states=sp.big_map(
                l={
                    21: sp.record(prop_1=0, prop_2=1),
                },
            ),
        )
        scenario += create

        new_state = sp.record(prop_1=5, prop_2=10)

        # When ALICE (not admin) tries to update the state, txn fails
        scenario += create.change_state(
            token_id=21,
            state=new_state,
        ).run(sender=Addresses.ALICE, valid=False, exception=Errors.NOT_AUTHORISED)

    @sp.add_test(name="change_state - fails if token does not exist")
    def test():
        scenario = sp.test_scenario()

        create = Create()
        scenario += create

        new_state = sp.record(prop_1=5, prop_2=10)

        # When ADMIN tries to update the state of token-d 21 (does not exist), txn fails
        scenario += create.change_state(
            token_id=21,
            state=new_state,
        ).run(sender=Addresses.ADMIN, valid=False, exception=FA2_Errors.FA2_TOKEN_UNDEFINED)

    @sp.add_test(name="token_metadata - returns the correct metadata")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and state
        create_fa2 = Create(
            states=sp.big_map(
                l={
                    21: sp.record(prop_1=0, prop_2=1),
                },
            ),
        )
        scenario += create_fa2

        expected_metadata = sp.record(
            token_id=21,
            token_info={
                "name": sp.bytes("0x644e465420437265617465"),
                "symbol": sp.bytes("0x644e465443"),
                "decimals": sp.bytes("0x30"),
                "thumbnailUri": sp.bytes("0x68747470733a2f2f696d6167655f75726c2e636f6d2f7468756d626e61696c2e706e67"),
                "artifactUri": sp.bytes("0x68747470733a2f2f696d6167655f75726c2e636f6d2f302f312f32312e706e67"),
                "displayUri": sp.bytes("0x68747470733a2f2f696d6167655f75726c2e636f6d2f302f312f32312e706e67"),
                "ttl": sp.bytes("0x363030"),
            },
        )

        scenario.verify_equal(create_fa2.token_metadata(21), expected_metadata)

    @sp.add_test(name="token_metadata - fails if token does not exist")
    def test():
        scenario = sp.test_scenario()

        create = Create()
        scenario += create

        scenario.verify(sp.is_failing(create.token_metadata(21)))

    sp.add_compilation_target("create", Create())
