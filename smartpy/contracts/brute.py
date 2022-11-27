#################################################################################
#                                Brute Structure
#
# Brute structure represents the most basic form of a dynamic NFT. It allows
# an admin address to directly modify the token_metadata big_map through a
# dedicated entrypoint.
#
# It's useful when the metadata depends entirely on data stored on off-chain
# servers or its generation requires extensive computation that is not possible
# on-chain.
#
# Every metadata update will require a transaction on the blockchain, incurring
# fees. Thus, a brute structure must only be used when the metadata changes are
# infrequent.
#################################################################################

import smartpy as sp

Errors = sp.io.import_script_from_url("file:../common/errors.py")
Addresses = sp.io.import_script_from_url("file:../common/addresses.py")
FA2_Errors = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Errors
FA2_Lib = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Lib


class Brute(FA2_Lib):
    def __init__(
        self,
        admin=Addresses.ADMIN,
        token_metadata=sp.big_map(
            l={},
            tkey=sp.TNat,
            tvalue=sp.TRecord(
                token_id=sp.TNat,
                token_info=sp.TMap(sp.TString, sp.TBytes),
            ),
        ),
        # IPFS link hosts the metadata at ./metadata/brute.json
        metadata=sp.utils.metadata_of_url("ipfs://QmTovUx5bbdZzAGwZaQpzqN5YwRACkCrv3ntNbP3CzostA"),
        **kwargs
    ):
        # Use the storage and entrypoints of FA2 lib
        FA2_Lib.__init__(self, **kwargs)

        # Add admin, token_metadata and metadata to the existing storage
        self.update_initial_storage(admin=admin, token_metadata=token_metadata, metadata=metadata)

        METADATA = {
            "name": "dNFT Brute",
            "version": "1.0.0",
            "description": "dNFT (dynamic NFT) contract with Brute Structure",
            "interfaces": ["TZIP-012", "TZIP-016"],
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
                metadata=sp.TMap(sp.TString, sp.TBytes),
            ),
        )

        # Sanity checks
        sp.verify(sp.sender == self.data.admin, Errors.NOT_AUTHORISED)
        sp.verify(~self.data.token_metadata.contains(params.token_id), Errors.TOKEN_ID_ALREADY_EXISTS)

        # Mint the token
        self.data.ledger[(params.address, params.token_id)] = 1
        self.data.token_metadata[params.token_id] = sp.record(
            token_id=params.token_id,
            token_info=params.metadata,
        )

    @sp.entry_point
    def update_token_metadata(self, params):
        sp.set_type(
            params,
            sp.TRecord(
                token_id=sp.TNat,
                token_info=sp.TMap(sp.TString, sp.TBytes),
            ),
        )

        # Only admin can update the metadata
        sp.verify(sp.sender == self.data.admin, Errors.NOT_AUTHORISED)

        # token-id must exist
        sp.verify(self.data.token_metadata.contains(params.token_id), FA2_Errors.FA2_TOKEN_UNDEFINED)

        # Update the storage
        self.data.token_metadata[params.token_id] = sp.record(
            token_id=params.token_id,
            token_info=params.token_info,
        )


########
# Tests
########

if __name__ == "__main__":

    @sp.add_test(name="mint - correctly mints an NFT")
    def test():
        scenario = sp.test_scenario()

        brute = Brute()
        scenario += brute

        # When the ADMIN mints an NFT with token-id 1 for Alice
        scenario += brute.mint(
            address=Addresses.ALICE,
            token_id=1,
            metadata={
                "": sp.utils.bytes_of_string("https://external_link.com"),
            },
        ).run(sender=Addresses.ADMIN)

        # The storage is updated correctly
        scenario.verify(brute.data.ledger[(Addresses.ALICE, 1)] == 1)
        scenario.verify_equal(
            brute.data.token_metadata[1],
            sp.record(
                token_id=1,
                token_info={
                    "": sp.utils.bytes_of_string("https://external_link.com"),
                },
            ),
        )

    @sp.add_test(name="mint - fails if sender is not the admin")
    def test():
        scenario = sp.test_scenario()

        brute = Brute()
        scenario += brute

        # When the ALICE (not admin) mints an NFT with token-id 1, txn fails
        scenario += brute.mint(
            address=Addresses.ALICE,
            token_id=1,
            metadata={
                "": sp.utils.bytes_of_string("https://external_link.com"),
            },
        ).run(sender=Addresses.ALICE, valid=False, exception=Errors.NOT_AUTHORISED)

    @sp.add_test(name="mint - fails if token already exists")
    def test():
        scenario = sp.test_scenario()

        brute = Brute(
            token_metadata=sp.big_map(
                {
                    1: sp.record(
                        token_id=1,
                        token_info={
                            "": sp.utils.bytes_of_string("https://external_link.com"),
                        },
                    )
                }
            )
        )
        scenario += brute

        # When the ADMIN mints an NFT with token-id 1 (already exists), txn fails
        scenario += brute.mint(
            address=Addresses.ALICE,
            token_id=1,
            metadata={
                "": sp.utils.bytes_of_string("https://external_link.com"),
            },
        ).run(sender=Addresses.ADMIN, valid=False, exception=Errors.TOKEN_ID_ALREADY_EXISTS)

    @sp.add_test(name="update_token_metadata - correctly updates the metadata")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and associated metadata (in this case a URL)
        brute = Brute(
            token_metadata=sp.big_map(
                l={
                    4: sp.record(
                        token_id=4,
                        token_info={
                            "": sp.utils.bytes_of_string("https://external_link.com"),
                        },
                    )
                }
            ),
        )
        scenario += brute

        # When the ADMIN calls update_token_metdata with a new metadata URL
        scenario += brute.update_token_metadata(
            token_id=4,
            token_info={
                "": sp.utils.bytes_of_string("https://new_external_link.com"),
            },
        ).run(sender=Addresses.ADMIN)

        # The token_metadata is updated with the new URL
        scenario.verify_equal(
            brute.data.token_metadata[4],
            sp.record(
                token_id=4,
                token_info={
                    "": sp.utils.bytes_of_string("https://new_external_link.com"),
                },
            ),
        )

    @sp.add_test(name="update_token_metadata - fails if sender is not the admin")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and associated metadata (in this case a URL)
        brute = Brute(
            token_metadata=sp.big_map(
                l={
                    4: sp.record(
                        token_id=4,
                        token_info={
                            "": sp.utils.bytes_of_string("https://external_link.com"),
                        },
                    )
                }
            ),
        )
        scenario += brute

        # When the ALICE (not admin) calls update_token_metdata with a new metadata URL, txn fails
        scenario += brute.update_token_metadata(
            token_id=4,
            token_info={
                "": sp.utils.bytes_of_string("https://new_external_link.com"),
            },
        ).run(sender=Addresses.ALICE, valid=False, exception=Errors.NOT_AUTHORISED)

    sp.add_compilation_target("brute", Brute())
