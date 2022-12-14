#################################################################################
#                                  SVG Structure
#
# SVG structure is an extension of Create with the difference that the
# artifactUri and displayUri are an SVG data URI that is dynamically generated
# in the token_metadata off-chain view.
#
# This is useful when the artifact is an SVG, or can possibly be converted to an
# SVG and save the overheads of separately maintaining off-chain data.
#################################################################################

import smartpy as sp

Utils = sp.io.import_script_from_url("file:../common/utils.py")
Errors = sp.io.import_script_from_url("file:../common/errors.py")
DataSVG = sp.io.import_script_from_url("file:../data/svg_structure.py")
Addresses = sp.io.import_script_from_url("file:../common/addresses.py")
FA2_Errors = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Errors
FA2_Lib = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Lib


class Types:
    # State is a generic representation of the attributes/properties an NFT may have.
    # Example: The construction status of different areas of a real estate (lawn, roofing etc)
    #          A nat value 0 would mean under-construction, and 1 may mean completed.
    STATE = sp.TRecord(prop_1=sp.TNat, prop_2=sp.TNat)


class SVG(FA2_Lib):
    def __init__(
        self,
        admin=Addresses.ADMIN,
        # A mapping from token_id to the state of an NFT
        states=sp.big_map(
            l={},
            tkey=sp.TNat,
            tvalue=Types.STATE,
        ),
        # IPFS link hosts the metadata at ./metadata/svg.json
        metadata=sp.utils.metadata_of_url("ipfs://QmYnmWznaFuAk8w9CVJRU3DG6tonVYthQfy8k2QpvwDeJ1"),
        **kwargs
    ):
        # Use the storage and entrypoints of the FA2 lib
        FA2_Lib.__init__(self, **kwargs)

        # Add admin, states and metadata to the existing storage
        self.update_initial_storage(admin=admin, states=states, metadata=metadata)

        METADATA = {
            "name": "dNFT SVG",
            "version": "1.0.0",
            "description": "dNFT (dynamic NFT) contract with SVG Structure",
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

    # This may called by an admin, another authorised contract or internally by the same contract
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
        prop_sum = bytes_of_nat(state.prop_1 + state.prop_2)
        b_token_id = bytes_of_nat(token_id)

        # Construct the SVG data URI (in bytes form) using the helper
        # NOTE: This is a sample construction. You would need to write your own
        #       helper to join the different sections of the SVG data URI
        svg_bytes = DataSVG.build_svg(sp.record(token_id=b_token_id, prop_sum=prop_sum))

        # Create a TZIP-21 compliant token-info
        metadata_tzip_21 = {
            "name": sp.utils.bytes_of_string("dNFT SVG"),
            "symbol": sp.utils.bytes_of_string("dNFTS"),
            "decimals": sp.utils.bytes_of_string("0"),
            "thumbnailUri": sp.utils.bytes_of_string("https://image_url.com/thumbnail.png"),  # Dummy link
            # Dynamic fields
            "artifactUri": svg_bytes,
            "displayUri": svg_bytes,
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

        svg = SVG()
        scenario += svg

        # When the ADMIN mints an NFT with token-id 1 for Alice
        scenario += svg.mint(
            address=Addresses.ALICE,
            token_id=1,
            state=sp.record(prop_1=5, prop_2=6),
        ).run(sender=Addresses.ADMIN)

        # The storage is updated correctly
        scenario.verify(svg.data.ledger[(Addresses.ALICE, 1)] == 1)
        scenario.verify(svg.data.states[1] == sp.record(prop_1=5, prop_2=6))

    @sp.add_test(name="mint - fails if sender is not the admin")
    def test():
        scenario = sp.test_scenario()

        svg = SVG()
        scenario += svg

        # When the ALICE (not admin) mints an NFT with token-id 1, txn fails
        scenario += svg.mint(
            address=Addresses.ALICE,
            token_id=1,
            state=sp.record(prop_1=5, prop_2=6),
        ).run(sender=Addresses.ALICE, valid=False, exception=Errors.NOT_AUTHORISED)

    @sp.add_test(name="mint - fails if token already exists")
    def test():
        scenario = sp.test_scenario()

        svg = SVG(
            states=sp.big_map(
                {
                    1: sp.record(prop_1=5, prop_2=6),
                }
            )
        )
        scenario += svg

        # When the ADMIN mints an NFT with token-id 1 (already exists), txn fails
        scenario += svg.mint(
            address=Addresses.ALICE,
            token_id=1,
            state=sp.record(prop_1=5, prop_2=6),
        ).run(sender=Addresses.ADMIN, valid=False, exception=Errors.TOKEN_ID_ALREADY_EXISTS)

    @sp.add_test(name="change_state - updates the state of a token")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and state
        svg = SVG(
            states=sp.big_map(
                l={
                    21: sp.record(prop_1=0, prop_2=1),
                },
            ),
        )
        scenario += svg

        new_state = sp.record(prop_1=5, prop_2=10)

        # Call change_state on token 21 and assign a new state
        scenario += svg.change_state(
            token_id=21,
            state=new_state,
        ).run(sender=Addresses.ADMIN)

        # State is updated correctly
        scenario.verify(svg.data.states[21] == new_state)

    @sp.add_test(name="change_state - fails if sender is not the admin")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and state
        svg = SVG(
            states=sp.big_map(
                l={
                    21: sp.record(prop_1=0, prop_2=1),
                },
            ),
        )
        scenario += svg

        new_state = sp.record(prop_1=5, prop_2=10)

        # When ALICE (not admin) tries to update the state, txn fails
        scenario += svg.change_state(
            token_id=21,
            state=new_state,
        ).run(sender=Addresses.ALICE, valid=False, exception=Errors.NOT_AUTHORISED)

    @sp.add_test(name="change_state - fails if token does not exist")
    def test():
        scenario = sp.test_scenario()

        svg = SVG()
        scenario += svg

        new_state = sp.record(prop_1=5, prop_2=10)

        # When ADMIN tries to update the state of token-d 21 (does not exist), txn fails
        scenario += svg.change_state(
            token_id=21,
            state=new_state,
        ).run(sender=Addresses.ADMIN, valid=False, exception=FA2_Errors.FA2_TOKEN_UNDEFINED)

    @sp.add_test(name="token_metadata - returns the correct metadata")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and state
        svg = SVG(
            states=sp.big_map(
                l={
                    21: sp.record(prop_1=5, prop_2=6),
                },
            ),
        )
        scenario += svg

        expected_metadata = sp.record(
            token_id=21,
            token_info={
                "name": sp.bytes("0x644e465420535647"),
                "symbol": sp.bytes("0x644e465453"),
                "decimals": sp.bytes("0x30"),
                "thumbnailUri": sp.bytes("0x68747470733a2f2f696d6167655f75726c2e636f6d2f7468756d626e61696c2e706e67"),
                "artifactUri": DataSVG.SAMPLE_BYTES,
                "displayUri": DataSVG.SAMPLE_BYTES,
                "ttl": sp.bytes("0x363030"),
            },
        )

        scenario.verify_equal(svg.token_metadata(21), expected_metadata)

    @sp.add_test(name="token_metadata - fails if token does not exist")
    def test():
        scenario = sp.test_scenario()

        svg = SVG()
        scenario += svg

        scenario.verify(sp.is_failing(svg.token_metadata(21)))

    sp.add_compilation_target("svg", SVG())
