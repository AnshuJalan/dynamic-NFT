######################################################################################
#             Tokenised XTZ locker based on Oracle and SVG Structure
#
# An XTZ locking contract where the locked positions are tradable as NFTs. The
# token metadata (specifically the 'artifactUri' and 'displayUri') of these NFTs
# are dynamically generated and the graphic displays the market value (in dollars)
# of the locked amount.
#
# Entire dynamic generation of token metadata happens onchain. The price of XTZ
# is pulled through Harbinger oracle and the final graphic is an SVG data URI.
#
# Although a simple example, this pattern of having a fancy graphic for tokenised
# positions has been particularly popular in Defi of the late. A Tezos implementation
# is Plenty's veNFT (under development). On other chains there's Uniswap v3 positions
# and  Angle protocol CDPs (Ethereum).
######################################################################################

import smartpy as sp

Utils = sp.io.import_script_from_url("file:../common/utils.py")
Errors = sp.io.import_script_from_url("file:../common/errors.py")
Dummy = sp.io.import_script_from_url("file:helpers/dummy.py").Dummy
DataSVG = sp.io.import_script_from_url("file:../data/svg_example.py")
Addresses = sp.io.import_script_from_url("file:../common/addresses.py")
Harbinger = sp.io.import_script_from_url("file:helpers/harbinger.py").Harbinger
FA2_Errors = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Errors
FA2_Lib = sp.io.import_script_from_url("file:../common/fa2/fa2_lib.py").FA2_Lib


class Locker(FA2_Lib):
    def __init__(
        self,
        # A mapping from token_id to locked amount
        locks=sp.big_map(
            l={},
            tkey=sp.TNat,
            tvalue=sp.TMutez,
        ),
        lock_count=sp.nat(0),
        harbinger_address=sp.address("KT1ENe4jbDE1QVG1euryp23GsAeWuEwJutQX"),
        # IPFS link hosts the metadata at ./metadata/locker.json
        metadata=sp.utils.metadata_of_url("ipfs://QmYMA1iwLzqcx7zLzbgHrquX75EDMcMYLy8yva8SAxGRFL"),
        **kwargs,
    ):
        # Use the storage and entrypoints of the FA2 lib
        FA2_Lib.__init__(self, **kwargs)

        # Add additional items to storage
        self.update_initial_storage(
            locks=locks,
            lock_count=lock_count,
            metadata=metadata,
            harbinger_address=harbinger_address,
        )

        METADATA = {
            "name": "dNFT Locker",
            "version": "1.0.0",
            "description": "Tokenised XTZ locker based on Oracle and SVG Structure",
            "interfaces": ["TZIP-012", "TZIP-016", "TZIP-021"],
            "views": [self.token_metadata],
        }

        # Smartpy's helper to create the metadata json
        self.init_metadata("metadata", METADATA)

    @sp.entry_point
    def mint(self):
        # Verify that a non-zero XTZ amount is being locked
        sp.verify(sp.amount > sp.tez(0), Errors.ZERO_AMOUNT_BEING_LOCKED)

        # Increment lock count
        self.data.lock_count += 1

        lock_count = sp.compute(self.data.lock_count)

        # Initialise a lock
        self.data.locks[lock_count] = sp.amount

        # Mint an NFT to represent the lock using lock_count as token id
        self.data.ledger[(sp.sender, lock_count)] = sp.nat(1)

    @sp.entry_point
    def withdraw(self, token_id):
        # Fetch locked amount
        locked_amount = sp.compute(self.data.locks.get(token_id, sp.mutez(0)))

        # Verify that token id exist
        sp.verify(locked_amount > sp.mutez(0), FA2_Errors.FA2_TOKEN_UNDEFINED)

        # Verify ownership
        sp.verify(self.data.ledger.get((sp.sender, token_id), 0) == 1, Errors.NOT_AUTHORISED)

        # Return locked XTZ to the owner
        sp.send(sp.sender, locked_amount)

        # Update storage
        del self.data.locks[token_id]
        del self.data.ledger[(sp.sender, token_id)]

    # offchain-view is not pure because the metadata for a particular token-id changes based on the states
    @sp.offchain_view(pure=False)
    def token_metadata(self, token_id):
        sp.set_type(token_id, sp.TNat)

        # Fetch locked amount
        locked_amount = sp.compute(self.data.locks.get(token_id, sp.mutez(0)))

        # Verify that token id exist
        sp.verify(locked_amount > sp.tez(0), FA2_Errors.FA2_TOKEN_UNDEFINED)

        bytes_of_nat = sp.compute(Utils.bytes_of_nat)

        # Convert locked_amount to bytes (essentially a 'floating point string')
        n_locked_amount = sp.compute(sp.utils.mutez_to_nat(locked_amount))
        whole_amount = sp.compute(n_locked_amount // 10**6)
        fractional_amount = sp.as_nat(n_locked_amount - (whole_amount * 10**6))
        b_locked_amount = bytes_of_nat(whole_amount) + sp.utils.bytes_of_string(".") + bytes_of_nat(fractional_amount)

        b_token_id = bytes_of_nat(token_id)

        # Fetch Dollar value of XTZ from Harbinger Oracle
        harbinger_price = sp.view(
            "getPrice",
            self.data.harbinger_address,  # Ghostnet normaliser contract for Harbinger
            "XTZ-USD",  # Asset code
            sp.TPair(sp.TTimestamp, sp.TNat),
        ).open_some(Errors.INVALID_VIEW)

        # Calculate dollar value of locked amount (granularity of 1_000_000)
        n_value = (sp.snd(harbinger_price) * (n_locked_amount)) // 10**6
        whole_value = n_value // 10**6
        fractional_value = sp.as_nat(n_value - (whole_value * 10**6)) // 10_000  # Limit fraction to 2 digits
        b_value = bytes_of_nat(whole_value) + sp.utils.bytes_of_string(".") + bytes_of_nat(fractional_value)

        # Construct the SVG data URI (in bytes form) using the helper
        svg_bytes = DataSVG.build_svg(
            sp.record(
                token_id=b_token_id,
                amount=b_locked_amount,
                value=b_value,
            )
        )

        # Create a TZIP-21 compliant token-info
        metadata_tzip_21 = {
            "name": sp.utils.bytes_of_string("Locker dNFT"),
            "symbol": sp.utils.bytes_of_string("LOCK"),
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

    @sp.add_test(name="mint - correctly initialises a lock")
    def test():
        scenario = sp.test_scenario()

        locker = Locker()
        scenario += locker

        # When ALICE locks 35 tez
        scenario += locker.mint().run(amount=sp.tez(35), sender=Addresses.ALICE)

        # She gets an NFT
        scenario.verify(locker.data.ledger[(Addresses.ALICE, 1)] == 1)

        # A lock is initlaised
        scenario.verify(locker.data.locks[1] == sp.tez(35))

        # Contract has the correct balance
        scenario.verify(locker.balance == sp.tez(35))

    @sp.add_test(name="mint - fails if zero amount is sent")
    def test():
        scenario = sp.test_scenario()

        locker = Locker()
        scenario += locker

        # When ALICE locks 0 tez, txn fails
        scenario += locker.mint().run(
            amount=sp.tez(0),
            sender=Addresses.ALICE,
            valid=False,
            exception=Errors.ZERO_AMOUNT_BEING_LOCKED,
        )

    @sp.add_test(name="withdraw - returns the correct amount to the lock holder")
    def test():
        scenario = sp.test_scenario()

        dummy = Dummy()
        scenario += dummy

        locker = Locker(
            locks=sp.big_map(
                l={
                    21: sp.tez(35),
                }
            ),
            ledger=sp.big_map(
                l={
                    (dummy.address, 21): 1,
                }
            ),
        )
        locker.set_initial_balance(sp.tez(35))

        scenario += locker

        # When Dummy withdraws lock 21
        scenario += locker.withdraw(21).run(sender=dummy.address)

        # It gets back the locked tez
        scenario.verify(dummy.balance == sp.tez(35))

        # Storage is updated correctly
        scenario.verify(~locker.data.locks.contains(21))
        scenario.verify(~locker.data.ledger.contains((dummy.address, 21)))

    @sp.add_test(name="withdraw - fails if lock does not exist")
    def test():
        scenario = sp.test_scenario()

        locker = Locker(
            locks=sp.big_map(
                l={
                    21: sp.tez(35),
                }
            ),
        )

        scenario += locker

        # When ALICE withdraws lock 21 (she does not own)
        scenario += locker.withdraw(21).run(
            sender=Addresses.ALICE,
            valid=False,
            exception=Errors.NOT_AUTHORISED,
        )

    @sp.add_test(name="withdraw - fails if sender does not own the lock")
    def test():
        scenario = sp.test_scenario()

        dummy = Dummy()
        scenario += dummy

        locker = Locker()

        scenario += locker

        # When ALICE withdraws lock 21 (does not exist)
        scenario += locker.withdraw(21).run(
            sender=Addresses.ALICE, valid=False, exception=FA2_Errors.FA2_TOKEN_UNDEFINED
        )

    @sp.add_test(name="token_metadata - returns the correct metadata")
    def test():
        scenario = sp.test_scenario()

        # Set price to be returned as $1.5 (10^6 granularity)
        harbinger = Harbinger(price=sp.nat(1_500_000))
        scenario += harbinger

        # Insert an arbitrary token-id and associated lock
        locker = Locker(
            locks=sp.big_map(
                l={
                    21: sp.tez(35),
                }
            ),
            harbinger_address=harbinger.address,
        )
        scenario += locker

        expected_metadata = sp.record(
            token_id=21,
            token_info={
                "name": sp.bytes("0x4c6f636b657220644e4654"),
                "symbol": sp.bytes("0x4c4f434b"),
                "decimals": sp.bytes("0x30"),
                "thumbnailUri": sp.bytes("0x68747470733a2f2f696d6167655f75726c2e636f6d2f7468756d626e61696c2e706e67"),
                "artifactUri": DataSVG.SAMPLE_BYTES,
                "displayUri": DataSVG.SAMPLE_BYTES,
                "ttl": sp.bytes("0x363030"),
            },
        )

        scenario.verify_equal(locker.token_metadata(21), expected_metadata)

    sp.add_compilation_target("locker", Locker())
