###################################################################################
#                  Game character dNFT based on Create Structure
#
# Similar to game1.py, but instead of building an external link to a TZIP-21 Json,
# it builds and serves the JSON through an off-chain view.
#
# Properties like token 'decimals', 'symbol', 'name' and 'thumbnailUri' are static,
# thus the Create structure is a perfect alternative to prevent data duplication.
#
# NOTE: 'player' and 'character' are used interchangeably in the code & comments.
###################################################################################

import smartpy as sp

FA2_NFT = sp.io.import_script_from_url("file:fa2_nft.py")
Utils = sp.io.import_script_from_url("file:../common/utils.py")
Errors = sp.io.import_script_from_url("file:../common/errors.py")
Addresses = sp.io.import_script_from_url("file:../common/addresses.py")


class Types:
    WEAPON = sp.TVariant(
        sword=sp.TUnit,
        pistol=sp.TUnit,
        rifle=sp.TUnit,
    )

    PLAYER_STATE = sp.TRecord(
        lives=sp.TNat,  # Maximum lives = 3
        weapon=WEAPON,
    )


class Game(FA2_NFT.FA2_NFT):
    def __init__(
        self,
        # A mapping from token_id (player/character) to the state
        player_states=sp.big_map(
            l={},
            tkey=sp.TNat,
            tvalue=Types.PLAYER_STATE,
        ),
        # IPFS links hosts the metadata at ./metadata/game1.json
        metadata=sp.utils.metadata_of_url("ipfs://QmU69Krzk3f872kCk6WLdaftyUYA1CPwa1Wx2sVRDfPSGe"),
        **kwargs
    ):
        # Use the storage and entrypoints of the base FA2 NFT contract
        FA2_NFT.FA2_NFT.__init__(self, **kwargs)

        # Add a states object to the existing FA2 NFT storage
        self.update_initial_storage(player_states=player_states, metadata=metadata)

        METADATA = {
            "name": "dNFT Game 2",
            "version": "1.0.0",
            "description": "Game character dNFT based on Create Structure",
            "interfaces": ["TZIP-012", "TZIP-016", "TZIP-021"],
            "views": [self.token_metadata],
        }

        # Smartpy's helper to create the metadata json
        self.init_metadata("metadata", METADATA)

    # Override existing mint function to initialise player state
    @sp.entry_point
    def mint(self, params):
        sp.set_type(params, sp.TRecord(address=sp.TAddress, token_id=sp.TNat))

        # Only admin can mint
        sp.verify(sp.sender == self.data.admin, Errors.NOT_AUTHORISED)

        # Token must not be minted already
        sp.verify(~self.data.tokens.contains(params.token_id), Errors.TOKEN_ID_ALREADY_EXISTS)

        # Mint the token at the provided address
        self.data.ledger[(params.address, params.token_id)] = sp.nat(1)

        # Record the token-id
        self.data.tokens[params.token_id] = sp.unit

        # Set initial player state
        self.data.player_states[params.token_id] = sp.record(
            lives=3,
            weapon=sp.variant("sword", sp.unit),
        )

    @sp.entry_point
    def change_weapon(self, params):
        sp.set_type(params, sp.TRecord(token_id=sp.TNat, weapon=Types.WEAPON))

        # Verify that token exists
        sp.verify(self.data.tokens.contains(params.token_id), FA2_NFT.FA2_Errors.FA2_TOKEN_UNDEFINED)

        # Verify that sender holds the token
        sp.verify(self.data.ledger.get((sp.sender, params.token_id), 0) == 1, Errors.NOT_AUTHORISED)

        # Switch weapon
        self.data.player_states[params.token_id].weapon = params.weapon

    @sp.entry_point
    def attack(self, params):
        sp.set_type(params, sp.TRecord(attacker_id=sp.TNat, victim_id=sp.TNat))

        # Verify that both token ids exists
        sp.verify(self.data.tokens.contains(params.attacker_id), FA2_NFT.FA2_Errors.FA2_TOKEN_UNDEFINED)
        sp.verify(self.data.tokens.contains(params.victim_id), FA2_NFT.FA2_Errors.FA2_TOKEN_UNDEFINED)

        # Verify that sender holds the token
        sp.verify(self.data.ledger.get((sp.sender, params.attacker_id), 0) == 1, Errors.NOT_AUTHORISED)

        damage = sp.local("damage", sp.nat(0))

        with self.data.player_states[params.attacker_id].weapon.match_cases() as arg:
            with arg.match("sword") as _:
                damage.value = 1
            with arg.match("pistol") as _:
                damage.value = 2
            with arg.match("rifle") as _:
                damage.value = 3

        victim_state = self.data.player_states[params.victim_id]

        victim_state.lives = sp.as_nat(victim_state.lives - damage.value, Errors.VICTIM_ALREADY_DEAD)

    # offchain-view is not pure because the metadata for a particular token-id changes based on the states
    @sp.offchain_view(pure=False)
    def token_metadata(self, token_id):
        sp.set_type(token_id, sp.TNat)

        # Verify that token id exist
        sp.verify(self.data.tokens.contains(token_id), FA2_NFT.FA2_Errors.FA2_TOKEN_UNDEFINED)

        # Fetch the current state of the player
        player_state = sp.compute(self.data.player_states[token_id])

        bytes_of_nat = sp.compute(Utils.bytes_of_nat)

        # Assigning a nat value to each weapon. Sword -> 0, Pistol -> 1, Rifle -> 2
        n_weapon = sp.local("n_weapon", sp.nat(0))

        with player_state.weapon.match_cases() as arg:
            with arg.match("pistol") as _:
                n_weapon.value = sp.nat(1)
            with arg.match("rifle") as _:
                n_weapon.value = sp.nat(2)

        # Convert values to bytes
        b_lives = bytes_of_nat(player_state.lives)
        b_weapon = bytes_of_nat(n_weapon.value)
        b_token_id = bytes_of_nat(token_id)

        slash = sp.utils.bytes_of_string("/")

        png = sp.utils.bytes_of_string(".png")

        # Construct the image uri (in bytes form)
        image_url = sp.utils.bytes_of_string("https://image_url.com")
        image_uri = image_url + slash + b_lives + slash + b_weapon + slash + b_token_id + png

        # NOTE: The image_uri would point to an image that may look like
        # >> https://gateway.pinata.cloud/ipfs/QmdxHSsGvT6WwYZz4k331C7HpxTiJArv7BwJQj5GahZJoZ

        # Create a TZIP-21 compliant token-info
        metadata_tzip_21 = {
            "name": sp.utils.bytes_of_string("Game dNFT"),
            "symbol": sp.utils.bytes_of_string("GAME"),
            "decimals": sp.utils.bytes_of_string("0"),
            "thumbnailUri": sp.utils.bytes_of_string("https://image_url.com/thumbnail.png"),  # Dummy link
            # Dynamic fields
            "artifactUri": image_uri,
            "displayUri": image_uri,
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

    @sp.add_test(name="token_metadata - returns the correct metadata")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and player-state
        game = Game(
            tokens=sp.big_map(
                l={
                    21: sp.unit,
                },
            ),
            player_states=sp.big_map(
                l={
                    21: sp.record(
                        lives=2,
                        weapon=sp.variant("pistol", sp.unit),
                    ),
                },
            ),
        )
        scenario += game

        expected_metadata = sp.record(
            token_id=21,
            token_info={
                "name": sp.bytes("0x47616d6520644e4654"),
                "symbol": sp.bytes("0x47414d45"),
                "decimals": sp.bytes("0x30"),
                "thumbnailUri": sp.bytes("0x68747470733a2f2f696d6167655f75726c2e636f6d2f7468756d626e61696c2e706e67"),
                # bytes represent: https://image_url.com/2/1/21.png
                "artifactUri": sp.bytes("0x68747470733a2f2f696d6167655f75726c2e636f6d2f322f312f32312e706e67"),
                "displayUri": sp.bytes("0x68747470733a2f2f696d6167655f75726c2e636f6d2f322f312f32312e706e67"),
            },
        )

        scenario.verify_equal(game.token_metadata(21), expected_metadata)

    @sp.add_test(name="mint - correctly sets the initial state for new player")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and player-state
        game = Game()
        scenario += game

        # When ADMIN mints token-id 1 for ALICE
        scenario += game.mint(token_id=1, address=Addresses.ALICE).run(sender=Addresses.ADMIN)

        # She gets the token
        scenario.verify(game.data.ledger[(Addresses.ALICE, 1)] == 1)

        # The state of the player/character behind the token is initialised correctly
        scenario.verify(game.data.player_states[1].lives == 3)
        scenario.verify(game.data.player_states[1].weapon.is_variant("sword"))

    @sp.add_test(name="change_weapon - correctly switches the weapon for a player")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and player-state
        game = Game(
            tokens=sp.big_map(
                l={
                    21: sp.unit,
                },
            ),
            ledger=sp.big_map(
                l={
                    (Addresses.ALICE, 21): 1,
                },
            ),
            player_states=sp.big_map(
                l={
                    21: sp.record(
                        lives=2,
                        weapon=sp.variant("pistol", sp.unit),
                    ),
                },
            ),
        )
        scenario += game

        # When ALICE calls change_weapon for her token-id 21
        scenario += game.change_weapon(
            token_id=21,
            weapon=sp.variant("rifle", sp.unit),
        ).run(sender=Addresses.ALICE)

        # Her weapon is switched correctly
        scenario.verify(game.data.player_states[21].weapon.is_variant("rifle"))

    @sp.add_test(name="attack - correctly reduces the lives")
    def test():
        scenario = sp.test_scenario()

        # Insert an arbitrary token-id and player-state
        game = Game(
            tokens=sp.big_map(
                l={
                    21: sp.unit,
                    22: sp.unit,
                },
            ),
            ledger=sp.big_map(
                l={
                    (Addresses.ALICE, 21): 1,
                },
            ),
            player_states=sp.big_map(
                l={
                    21: sp.record(
                        lives=2,
                        weapon=sp.variant("pistol", sp.unit),
                    ),
                    22: sp.record(
                        lives=3,
                        weapon=sp.variant("sword", sp.unit),
                    ),
                },
            ),
        )
        scenario += game

        # When ALICE attacks player with token-id 22 with a pistol
        scenario += game.attack(
            attacker_id=21,
            victim_id=22,
        ).run(sender=Addresses.ALICE)

        # Lives of player with token-id 22 is reduced correctly (i.e by 2)
        scenario.verify(game.data.player_states[22].lives == 1)

    sp.add_compilation_target("game2", Game())
