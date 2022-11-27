import smartpy as sp

Addresses = sp.io.import_script_from_url("file:../common/addresses.py")
Errors = sp.io.import_script_from_url("file:../common/errors.py")
FA2_Errors = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Errors
FA2_Lib = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Lib


class FA2_NFT(FA2_Lib):
    def __init__(self, **kwargs):
        FA2_Lib.__init__(self, **kwargs)


########
# Tests
########

if __name__ == "__main__":

    @sp.add_test(name="transfer - correctly sends tokens from one address to another")
    def test():
        scenario = sp.test_scenario()

        fa2_nft = FA2_NFT(
            ledger=sp.big_map(
                {
                    (Addresses.ALICE, 1): 1,
                },
            )
        )

        scenario += fa2_nft

        # When ALICE transfers 1 NFT to BOB
        scenario += fa2_nft.transfer(
            [
                sp.record(
                    from_=Addresses.ALICE,
                    txs=[
                        sp.record(to_=Addresses.BOB, token_id=1, amount=1),
                    ],
                )
            ]
        ).run(sender=Addresses.ALICE)

        # BOB gets the NFT
        scenario.verify(fa2_nft.data.ledger[(Addresses.BOB, 1)] == 1)

    @sp.add_test(name="transfer - allows operator to transfer tokens")
    def test():
        scenario = sp.test_scenario()

        fa2_nft = FA2_NFT(
            ledger=sp.big_map(
                {
                    (Addresses.ALICE, 1): 1,
                },
            ),
            operators=sp.big_map(
                {
                    sp.record(
                        operator=Addresses.BOB,
                        owner=Addresses.ALICE,
                        token_id=1,
                    ): sp.unit
                }
            ),
        )

        scenario += fa2_nft

        # When BOB (operator for alice) transfers the NFT with token-id 1 to himself
        scenario += fa2_nft.transfer(
            [
                sp.record(
                    from_=Addresses.ALICE,
                    txs=[
                        sp.record(to_=Addresses.BOB, token_id=1, amount=1),
                    ],
                )
            ]
        ).run(sender=Addresses.BOB)

        # He gets the NFT
        scenario.verify(fa2_nft.data.ledger[(Addresses.BOB, 1)] == 1)

    @sp.add_test(name="transfer - fails if sender is not the owner or operator")
    def test():
        scenario = sp.test_scenario()

        fa2_nft = FA2_NFT(
            ledger=sp.big_map(
                {
                    (Addresses.ALICE, 1): 1,
                },
            ),
        )

        scenario += fa2_nft

        # When BOB (not an operator for alice) transfers the NFT with token-id 1 to himself, the txn fails
        scenario += fa2_nft.transfer(
            [
                sp.record(
                    from_=Addresses.ALICE,
                    txs=[
                        sp.record(to_=Addresses.BOB, token_id=1, amount=1),
                    ],
                )
            ]
        ).run(sender=Addresses.BOB, valid=False, exception=FA2_Errors.FA2_NOT_OPERATOR)

    @sp.add_test(name="transfer - fails if the sender has insufficient balance")
    def test():
        scenario = sp.test_scenario()

        fa2_nft = FA2_NFT(
            ledger=sp.big_map(
                {
                    (Addresses.ALICE, 1): 1,
                },
            )
        )

        scenario += fa2_nft

        # When ALICE transfers 2 NFTs with token-id 1 to BOB, the txn fails
        scenario += fa2_nft.transfer(
            [
                sp.record(
                    from_=Addresses.ALICE,
                    txs=[
                        sp.record(to_=Addresses.BOB, token_id=1, amount=2),
                    ],
                )
            ]
        ).run(sender=Addresses.ALICE, valid=False, exception=FA2_Errors.FA2_INSUFFICIENT_BALANCE)

    @sp.add_test(name="update_operator - sets the operator for a token and owner")
    def test():
        scenario = sp.test_scenario()

        fa2_nft = FA2_NFT()

        scenario += fa2_nft

        # When ALICE sets BOB as the operator for her token-id 1
        scenario += fa2_nft.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(
                        operator=Addresses.BOB,
                        owner=Addresses.ALICE,
                        token_id=1,
                    ),
                )
            ]
        ).run(sender=Addresses.ALICE)

        # The storage is updated correctly
        scenario.verify(
            fa2_nft.data.operators[
                sp.record(
                    operator=Addresses.BOB,
                    owner=Addresses.ALICE,
                    token_id=1,
                )
            ]
            == sp.unit
        )

    @sp.add_test(name="update_operator - removes the operator for a token and owner")
    def test():
        scenario = sp.test_scenario()

        fa2_nft = FA2_NFT(
            operators=sp.big_map(
                {
                    sp.record(
                        operator=Addresses.BOB,
                        owner=Addresses.ALICE,
                        token_id=1,
                    ): sp.unit,
                }
            )
        )

        scenario += fa2_nft

        # When ALICE removes BOB as the operator for her token-id 1
        scenario += fa2_nft.update_operators(
            [
                sp.variant(
                    "remove_operator",
                    sp.record(
                        operator=Addresses.BOB,
                        owner=Addresses.ALICE,
                        token_id=1,
                    ),
                )
            ]
        ).run(sender=Addresses.ALICE)

        # The storage is updated correctly
        scenario.verify(
            ~fa2_nft.data.operators.contains(
                sp.record(
                    operator=Addresses.BOB,
                    owner=Addresses.ALICE,
                    token_id=1,
                )
            )
        )

    @sp.add_test(name="update_operator - fails if the sender is not the owner")
    def test():
        scenario = sp.test_scenario()

        fa2_nft = FA2_NFT()

        scenario += fa2_nft

        # When BOB sets himself as the operator for ALICE's token-id 1, txn fails
        scenario += fa2_nft.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(
                        operator=Addresses.BOB,
                        owner=Addresses.ALICE,
                        token_id=1,
                    ),
                )
            ]
        ).run(sender=Addresses.BOB, valid=False, exception=FA2_Errors.FA2_NOT_OWNER)

    sp.add_compilation_target("fa2_nft", FA2_NFT())
