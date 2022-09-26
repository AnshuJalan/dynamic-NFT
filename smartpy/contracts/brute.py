#################################################################################
#                                Brute Structure
#
# Brute structure represents the most basic form of a dynamic NFT. It allows
# an admin address to modify the token_metadata big_map directly through a
# dedicated entrypoint.
#
# This is useful when the metadata depends entirely on data stored on off-chain
# servers or its generation requires extensive computation that is not possible
# on-chain.
#
# Every metadata update will require a transaction on the blockchain, incurring
# fees. Thus, a brute structure must only be used when the metadata changes are
# infrequent.
#################################################################################

import smartpy as sp

FA2_NFT = sp.io.import_script_from_url("file:fa2_nft.py")
Errors = sp.io.import_script_from_url("file:../common/errors.py")
Addresses = sp.io.import_script_from_url("file:../common/addresses.py")


class Brute(FA2_NFT.FA2_NFT):
    def __init__(
        self,
        token_metadata=sp.big_map(
            l={},
            tkey=sp.TNat,
            tvalue=sp.TRecord(
                token_id=sp.TNat,
                token_info=sp.TMap(sp.TString, sp.TBytes),
            ),
        ),
        **kwargs
    ):
        # Use the storage and entrypoints of the base FA2 NFT contract
        FA2_NFT.FA2_NFT.__init__(self, **kwargs)

        # Add a token_metadata big_map to the existing FA2 NFT storage
        self.update_initial_storage(token_metadata=token_metadata)

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
        sp.verify(self.data.tokens.contains(params.token_id), FA2_NFT.FA2_Errors.FA2_TOKEN_UNDEFINED)

        # Update the storage
        self.data.token_metadata[params.token_id] = sp.record(
            token_id=params.token_id,
            token_info=params.token_info,
        )


########
# Tests
########

if __name__ == "__main__":

    @sp.add_test(name="update_token_metadata - correctly updates the metadata")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and associated metadata (in this case a URL)
        brute_fa2 = Brute(
            tokens=sp.big_map(
                l={
                    4: sp.unit,
                }
            ),
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
        scenario += brute_fa2

        # When the ADMIN calls update_token_metdata with a new metadata URL
        scenario += brute_fa2.update_token_metadata(
            token_id=4,
            token_info={
                "": sp.utils.bytes_of_string("https://new_external_link.com"),
            },
        ).run(sender=Addresses.ADMIN)

        # The token_metadata is updated with the new URL
        scenario.verify_equal(
            brute_fa2.data.token_metadata[4],
            sp.record(
                token_id=4,
                token_info={
                    "": sp.utils.bytes_of_string("https://new_external_link.com"),
                },
            ),
        )

    sp.add_compilation_target("brute", Brute())
