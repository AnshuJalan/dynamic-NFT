import { MichelsonMap, UnitValue } from "@taquito/taquito";

import { SVG } from "../helpers/CommonInterface";
import Tezos from "../helpers/Tezos";
import { config } from "../config";
import accounts from "../helpers/accounts";

import metadata from "../../contracts/metadata/svg.json";
import { SAMPLE_SVG_BYTES } from "../../data/svg_structure";

const tests = () =>
  describe("svg", () => {
    let storage: any;
    const tezos = new Tezos(config);

    beforeEach(() => {
      storage = {
        admin: accounts.alice.pkh, // Alice is the admin
        ledger: MichelsonMap.fromLiteral({}),
        tokens: MichelsonMap.fromLiteral({}),
        states: MichelsonMap.fromLiteral({}),
        operators: MichelsonMap.fromLiteral({}),
        metadata: MichelsonMap.fromLiteral({}),
      };
    });

    describe("mint", () => {
      it("creates an NFT for the supplied address", async () => {
        tezos.setProvider(accounts.alice.sk);

        const svg = await SVG.originate(tezos, storage);

        // When Alice mints token-id 1 for Bob
        await svg.mint({
          token_id: 1,
          address: accounts.bob.pkh,
          state: { prop_1: 5, prop_2: 6 },
        });

        const updatedStorage = await svg.getStorage(tezos);

        const bobBalance = await updatedStorage.ledger.get({ 0: accounts.bob.pkh, 1: 1 });
        const token1State = await updatedStorage.states.get(1);

        // An NFT is created correctly
        expect(bobBalance.toNumber()).toEqual(1);
        expect(token1State.prop_1.toNumber()).toEqual(5);
        expect(token1State.prop_2.toNumber()).toEqual(6);
        expect(await updatedStorage.tokens.get(1)).toEqual(UnitValue);
      });

      it("fails if sender is not the admin", async () => {
        // Set Bob (not admin) as the sender
        tezos.setProvider(accounts.bob.sk);

        const svg = await SVG.originate(tezos, storage);

        // When Bob mints token-id 1 for Alice, the txn fails
        await expect(
          svg.mint({
            token_id: 1,
            address: accounts.bob.pkh,
            state: { prop_1: 5, prop_2: 6 },
          })
        ).rejects.toThrow("NOT_AUTHORISED");
      });

      it("fails if token id already exists", async () => {
        tezos.setProvider(accounts.alice.sk);

        storage.tokens.set(1, {});

        const svg = await SVG.originate(tezos, storage);

        // When Alice mints token-id 1 for Bob, the txn fails
        await expect(
          svg.mint({
            token_id: 1,
            address: accounts.bob.pkh,
            state: { prop_1: 5, prop_2: 6 },
          })
        ).rejects.toThrow("TOKEN_ID_ALREADY_EXISTS");
      });
    });

    describe("change_state", () => {
      it("correctly changes the state of a token", async () => {
        tezos.setProvider(accounts.alice.sk);

        storage.tokens.set(1, {});

        storage.states.set(1, {
          prop_1: 5,
          prop_2: 6,
        });

        const svg = await SVG.originate(tezos, storage);

        // When Alice changes the state of token-id 1
        await svg.changeState({
          token_id: 1,
          state: {
            prop_1: 10,
            prop_2: 11,
          },
        });

        const updatedStorage = await svg.getStorage(tezos);

        const tokenState = await updatedStorage.states.get(1);

        // The state of token-id 1 is updated correctly
        expect(tokenState.prop_1.toNumber()).toEqual(10);
        expect(tokenState.prop_2.toNumber()).toEqual(11);
      });

      it("fails if sender is not the admin", async () => {
        // Set Bob (not admin) as the sender
        tezos.setProvider(accounts.bob.sk);

        storage.states.set(1, {
          prop_1: 5,
          prop_2: 6,
        });

        const svg = await SVG.originate(tezos, storage);

        // When Bob changes the state of token-id 1, the txn fails
        await expect(
          svg.changeState({
            token_id: 1,
            state: {
              prop_1: 10,
              prop_2: 11,
            },
          })
        ).rejects.toThrow("NOT_AUTHORISED");
      });

      it("fails if token id does not exist", async () => {
        tezos.setProvider(accounts.alice.sk);

        const svg = await SVG.originate(tezos, storage);

        // When Alice changes the state of token-id 1, the txn fails
        await expect(
          svg.changeState({
            token_id: 1,
            state: {
              prop_1: 10,
              prop_2: 11,
            },
          })
        ).rejects.toThrow("FA2_TOKEN_UNDEFINED");
      });
    });

    describe("token_metadata - offchain view", () => {
      it("correctly returns the token metadata", async () => {
        storage.tokens.set(21, {});

        // Here the token-id is 21 and prop-sum will be 11
        storage.states.set(21, {
          prop_1: 5,
          prop_2: 6,
        });

        const svg = await SVG.originate(tezos, storage);

        const tokenMetadata = await svg.tokenMetadata(tezos, metadata, 21);

        expect(tokenMetadata.token_id.toNumber()).toEqual(21);
        /* Expected TZIP-21 based metadata: 
          {
            name: "dNFT SVG",
            symbol: "dNFTC",
            decimals: "0",
            thumbnailUri: "https://image_url.com/thumbnail.png",
            artifactUri: SAMPLE_SVG_BYTES,
            displayUri: SAMPLE_SVG_BYTES
          }
        */
        expect(tokenMetadata.token_info.get("name")).toEqual("644e465420535647");
        expect(tokenMetadata.token_info.get("symbol")).toEqual("644e465453");
        expect(tokenMetadata.token_info.get("decimals")).toEqual("30");
        expect(tokenMetadata.token_info.get("thumbnailUri")).toEqual(
          "68747470733a2f2f696d6167655f75726c2e636f6d2f7468756d626e61696c2e706e67"
        );
        expect(tokenMetadata.token_info.get("artifactUri")).toEqual(SAMPLE_SVG_BYTES);
        expect(tokenMetadata.token_info.get("displayUri")).toEqual(SAMPLE_SVG_BYTES);
        expect(tokenMetadata.token_info.get("ttl")).toEqual("363030");
      });

      it("fails if the token does not exist", async () => {
        const svg = await SVG.originate(tezos, storage);

        await expect(svg.tokenMetadata(tezos, metadata, 1)).rejects.toThrow("FA2_TOKEN_UNDEFINED");
      });
    });
  });

export default tests;
