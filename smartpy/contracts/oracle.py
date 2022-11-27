#################################################################################
#                                 Oracle Structure
#
# Oracle structure allows for fetching a 'state' from an on-chain oracle and
# dynamically building the token metadata using the retrieved values. The
# metadata is then served through an offchain view.
#
# It's useful when the metadata depends on some off-chain data that needs to be
# put on-chain in a decentralised way through an oracle.
#
# The liveness of the oracle and integrity of the data must be ensured.
#################################################################################

import smartpy as sp

Utils = sp.io.import_script_from_url("file:../common/utils.py")
Errors = sp.io.import_script_from_url("file:../common/errors.py")
Addresses = sp.io.import_script_from_url("file:../common/addresses.py")
StateOracle = sp.io.import_script_from_url("file:helpers/state_oracle.py").StateOracle
FA2_Errors = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Errors
FA2_Lib = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Lib


class Types:
    # State is a generic representation of the attributes/properties an NFT may have.
    # Example: The construction status of different areas of a real estate (lawn, roofing etc)
    #          A nat value 0 would mean under-construction, and 1 may mean completed.
    STATE = sp.TRecord(prop_1=sp.TNat, prop_2=sp.TNat)


class Oracle(FA2_Lib):
    def __init__(
        self,
        admin=Addresses.ADMIN,
        tokens=sp.big_map(l={}, tkey=sp.TNat, tvalue=sp.TUnit),
        oracle_address=Addresses.ORACLE,
        # IPFS link hosts the metadata at ./metadata/oracle.json
        metadata=sp.utils.metadata_of_url("ipfs://QmSWfZ48phyiq2ZcvbKutfSFWadAtt2E3146i8x6HhC6bC"),
        **kwargs
    ):
        # Use the storage and entrypoints of the FA2 lib
        FA2_Lib.__init__(self, **kwargs)

        # Add admin, oracle_address and metadata to the existing storage
        self.update_initial_storage(
            admin=admin,
            tokens=tokens,
            oracle_address=oracle_address,
            metadata=metadata,
        )

        METADATA = {
            "name": "dNFT Oracle",
            "version": "1.0.0",
            "description": "dNFT (dynamic NFT) contract with Oracle Structure",
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
            ),
        )

        # Sanity checks
        sp.verify(sp.sender == self.data.admin, Errors.NOT_AUTHORISED)
        sp.verify(~self.data.tokens.contains(params.token_id), Errors.TOKEN_ID_ALREADY_EXISTS)

        # Mint the token
        self.data.ledger[(params.address, params.token_id)] = 1
        self.data.tokens[params.token_id] = sp.unit

    # offchain-view is not pure because the metadata for a particular token-id changes based on the states
    @sp.offchain_view(pure=False)
    def token_metadata(self, token_id):
        sp.set_type(token_id, sp.TNat)

        # Verify that token id exist
        sp.verify(self.data.tokens.contains(token_id), FA2_Errors.FA2_TOKEN_UNDEFINED)

        # Fetch the current state of the entity behind the token-id through the oracle
        # NOTE: The semantics of this call is utility dependent. You may fetch all TZIP-21
        #       fields from the oracle and/or some co-related state and build the metadata
        #       as shown in this structure
        state = sp.view(
            "get_state",
            self.data.oracle_address,
            token_id,
            Types.STATE,
        ).open_some(Errors.INVALID_VIEW)

        bytes_of_nat = sp.compute(Utils.bytes_of_nat)

        # Convert values to bytes
        prop_1 = bytes_of_nat(state.prop_1)
        prop_2 = bytes_of_nat(state.prop_2)
        b_token_id = bytes_of_nat(token_id)

        slash = sp.utils.bytes_of_string("/")

        # Construct the metadata uri in bytes form
        # NOTE: This is a sample construction. The form your url may take depends entirely
        #       upon how your artifacts are hosted.
        metadata_url = sp.utils.bytes_of_string("https://metadata_url.com")
        metadata_uri = metadata_url + slash + prop_1 + slash + prop_2 + slash + b_token_id

        # Return the TZIP-16 compliant metadata
        sp.result(
            sp.record(
                token_id=token_id,
                token_info={
                    "": metadata_uri,
                },
            )
        )


########
# Tests
########

if __name__ == "__main__":

    @sp.add_test(name="mint - correctly mints an NFT")
    def test():
        scenario = sp.test_scenario()

        oracle = Oracle()
        scenario += oracle

        # When the ADMIN mints an NFT with token-id 1 for Alice
        scenario += oracle.mint(
            address=Addresses.ALICE,
            token_id=1,
        ).run(sender=Addresses.ADMIN)

        # The storage is updated correctly
        scenario.verify(oracle.data.ledger[(Addresses.ALICE, 1)] == 1)
        scenario.verify(oracle.data.tokens[1] == sp.unit)

    @sp.add_test(name="mint - fails if sender is not the admin")
    def test():
        scenario = sp.test_scenario()

        oracle = Oracle()
        scenario += oracle

        # When the ALICE (not admin) mints an NFT with token-id 1, txn fails
        scenario += oracle.mint(
            address=Addresses.ALICE,
            token_id=1,
        ).run(sender=Addresses.ALICE, valid=False, exception=Errors.NOT_AUTHORISED)

    @sp.add_test(name="mint - fails if token already exists")
    def test():
        scenario = sp.test_scenario()

        oracle = Oracle(
            tokens=sp.big_map(
                {
                    1: sp.unit,
                }
            )
        )
        scenario += oracle

        # When the ADMIN mints an NFT with token-id 1 (already exists), txn fails
        scenario += oracle.mint(
            address=Addresses.ALICE,
            token_id=1,
        ).run(sender=Addresses.ADMIN, valid=False, exception=Errors.TOKEN_ID_ALREADY_EXISTS)

    @sp.add_test(name="token_metadata - returns the correct metadata")
    def test():
        scenario = sp.test_scenario()

        # Initialise dummy state oracle
        state_oracle = StateOracle(
            state=sp.record(
                prop_1=sp.nat(0),
                prop_2=sp.nat(1),
            )
        )
        scenario += state_oracle

        # Insert an arbitrary token-id and state
        oracle = Oracle(
            tokens=sp.big_map(
                l={
                    21: sp.unit,
                },
            ),
            oracle_address=state_oracle.address,
        )
        scenario += oracle

        # Bytes value represents https://metadata_url.com/0/1/21
        expected_metadata = sp.record(
            token_id=21,
            token_info={
                "": sp.bytes("0x68747470733a2f2f6d657461646174615f75726c2e636f6d2f302f312f3231"),
            },
        )

        scenario.verify_equal(oracle.token_metadata(21), expected_metadata)

    @sp.add_test(name="token_metadata - fails if token does not exist")
    def test():
        scenario = sp.test_scenario()

        oralce = Oracle()
        scenario += oralce

        scenario.verify(sp.is_failing(oralce.token_metadata(21)))

    sp.add_compilation_target("oracle", Oracle())
