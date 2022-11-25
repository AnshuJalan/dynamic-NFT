import { MichelsonMap, UnitValue } from "@taquito/taquito";

import Game from "../helpers/Game";
import Tezos from "../helpers/Tezos";
import { config } from "../config";
import accounts from "../helpers/accounts";

import metadata from "../../examples/metadata/game1.json";

const tests = () =>
  describe("game1", () => {
    let storage: any;
    const tezos = new Tezos(config);

    const codepath = `${__dirname}/../../examples/michelson/game1.tz`;

    beforeEach(() => {
      storage = {
        admin: accounts.alice.pkh, // Alice is the admin
        ledger: MichelsonMap.fromLiteral({}),
        player_states: MichelsonMap.fromLiteral({}),
        operators: MichelsonMap.fromLiteral({}),
        metadata: MichelsonMap.fromLiteral({}),
      };
    });

    describe("mint", () => {
      it("creates an NFT for the supplied address", async () => {
        tezos.setProvider(accounts.alice.sk);

        const game = await Game.originate(tezos, codepath, storage);

        // When Alice mints token-id 1 for Bob
        await game.mint({
          token_id: 1,
          address: accounts.bob.pkh,
        });

        const updatedStorage = await game.getStorage(tezos);

        const bobBalance = await updatedStorage.ledger.get({ 0: accounts.bob.pkh, 1: 1 });
        const token1State = await updatedStorage.player_states.get(1);

        // An NFT is created correctly
        expect(bobBalance.toNumber()).toEqual(1);
        expect(token1State.lives.toNumber()).toEqual(3);
        expect(token1State.weapon["sword"]).toEqual(UnitValue);
      });

      it("fails if sender is not the admin", async () => {
        // Set Bob (not admin) as the sender
        tezos.setProvider(accounts.bob.sk);

        const game = await Game.originate(tezos, codepath, storage);

        // When Bob mints token-id 1 for Alice, the txn fails
        await expect(
          game.mint({
            token_id: 1,
            address: accounts.bob.pkh,
          })
        ).rejects.toThrow("NOT_AUTHORISED");
      });

      it("fails if token id already exists", async () => {
        tezos.setProvider(accounts.alice.sk);

        storage.player_states.set(1, {
          lives: 2,
          weapon: {
            pistol: {},
          },
        });

        const game = await Game.originate(tezos, codepath, storage);

        // When Alice mints token-id 1 for Bob, the txn fails
        await expect(
          game.mint({
            token_id: 1,
            address: accounts.bob.pkh,
          })
        ).rejects.toThrow("TOKEN_ID_ALREADY_EXISTS");
      });
    });

    describe("change_weapon", () => {
      it("allows a player to change its weapon", async () => {
        tezos.setProvider(accounts.bob.sk);

        // Bob owns a character with token-id 1
        storage.ledger.set({ 0: accounts.bob.pkh, 1: 1 }, 1);

        // Current weapon in hand is a sword
        storage.player_states.set(1, {
          lives: 2,
          weapon: {
            sword: {},
          },
        });

        const game = await Game.originate(tezos, codepath, storage);

        // When Bob changes the weapon from sword to rifle
        await game.changeWeapon({ token_id: 1, weapon: { rifle: {} } });

        const updatedStorage = await game.getStorage(tezos);
        const updatedPlayer = await updatedStorage.player_states.get(1);

        // He now has a rifle in hand
        expect(updatedPlayer.weapon["rifle"]).toEqual(UnitValue);
      });

      it("fails if the player token does not exist", async () => {
        tezos.setProvider(accounts.bob.sk);

        const game = await Game.originate(tezos, codepath, storage);

        // When Bob changes the weapon for player with token-id 1 (does not exist), the txn fails
        await expect(game.changeWeapon({ token_id: 1, weapon: { rifle: {} } })).rejects.toThrow("FA2_TOKEN_UNDEFINED");
      });

      it("fails if the sender does not own the player token", async () => {
        tezos.setProvider(accounts.bob.sk);

        storage.player_states.set(1, {
          lives: 2,
          weapon: {
            sword: {},
          },
        });

        const game = await Game.originate(tezos, codepath, storage);

        // When Bob changes the weapon for player with token-id 1 (he does not own), the txn fails
        await expect(game.changeWeapon({ token_id: 1, weapon: { rifle: {} } })).rejects.toThrow("NOT_AUTHORISED");
      });
    });

    describe("attack", () => {
      it("allows a player to attack another", async () => {
        tezos.setProvider(accounts.bob.sk);

        // Bob owns a character with token-id 1
        storage.ledger.set({ 0: accounts.bob.pkh, 1: 1 }, 1);

        // Initial states of player 1 and 2
        storage.player_states.set(1, {
          lives: 2,
          weapon: {
            pistol: {},
          },
        });
        storage.player_states.set(2, {
          lives: 3,
          weapon: {
            sword: {},
          },
        });

        const game = await Game.originate(tezos, codepath, storage);

        // When Bob attacks player with token-id 2
        await game.attack({ attacker_id: 1, victim_id: 2 });

        const updatedStorage = await game.getStorage(tezos);
        const updatedPlayer2 = await updatedStorage.player_states.get(1);

        // Player with token-id 2 now has just 2 lives left (Damage 1 inflicted by rifle)
        expect(updatedPlayer2.lives.toNumber()).toEqual(2);
      });

      it("fails if attacker does not exist", async () => {
        tezos.setProvider(accounts.bob.sk);

        storage.player_states.set(2, {
          lives: 3,
          weapon: {
            sword: {},
          },
        });

        const game = await Game.originate(tezos, codepath, storage);

        // When Bob attacks player with token-id 2 using token-id 1 (does not exist), the txn fails
        await expect(game.attack({ attacker_id: 1, victim_id: 2 })).rejects.toThrow("FA2_TOKEN_UNDEFINED");
      });

      it("fails if victim does not exist", async () => {
        tezos.setProvider(accounts.bob.sk);

        storage.player_states.set(1, {
          lives: 3,
          weapon: {
            sword: {},
          },
        });

        const game = await Game.originate(tezos, codepath, storage);

        // When Bob attacks player with token-id 2 (does not exist) using token-id 1, the txn fails
        await expect(game.attack({ attacker_id: 1, victim_id: 2 })).rejects.toThrow("FA2_TOKEN_UNDEFINED");
      });

      it("fails if sender does not own attacking player", async () => {
        tezos.setProvider(accounts.bob.sk);

        storage.player_states.set(1, {
          lives: 3,
          weapon: {
            sword: {},
          },
        });
        storage.player_states.set(2, {
          lives: 2,
          weapon: {
            sword: {},
          },
        });

        const game = await Game.originate(tezos, codepath, storage);

        // When Bob attacks player with token-id 2 using token-id 1 (he does not own), the txn fails
        await expect(game.attack({ attacker_id: 1, victim_id: 2 })).rejects.toThrow("NOT_AUTHORISED");
      });
    });

    describe("token_metadata - offchain view", () => {
      it("correctly returns the token metadata", async () => {
        // Initialise a player with 2 lives and carrying a pistol
        storage.player_states.set(1, {
          lives: 2,
          weapon: {
            pistol: {},
          },
        });

        const game = await Game.originate(tezos, codepath, storage);

        const tokenMetadata = await game.tokenMetadata(tezos, metadata, 1);

        expect(tokenMetadata.token_id.toNumber()).toEqual(1);
        // Expected URI: https://metadata_url.com/2/1/1
        expect(tokenMetadata.token_info.get("")).toEqual(
          "68747470733a2f2f6d657461646174615f75726c2e636f6d2f322f312f31"
        );
      });

      it("fails if the token does not exist", async () => {
        const game = await Game.originate(tezos, codepath, storage);

        await expect(game.tokenMetadata(tezos, metadata, 1)).rejects.toThrow("FA2_TOKEN_UNDEFINED");
      });
    });
  });

export default tests;
