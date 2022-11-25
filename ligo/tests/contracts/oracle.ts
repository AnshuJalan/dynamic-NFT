import { MichelsonMap, UnitValue } from "@taquito/taquito";

import Oracle from "../helpers/Oracle";
import Tezos from "../helpers/Tezos";
import { config } from "../config";
import accounts from "../helpers/accounts";

import metadata from "../../contracts/metadata/oracle.json";

const tests = () =>
  describe("oracle", () => {
    let storage: any;
    const tezos = new Tezos(config);

    beforeEach(() => {
      storage = {
        admin: accounts.alice.pkh, // Alice is the admin
        ledger: MichelsonMap.fromLiteral({}),
        tokens: MichelsonMap.fromLiteral({}),
        oracle_address: "tz1eUzpKnk5gKLYw4HWs2sWsynfbT7ypGxNM",
        operators: MichelsonMap.fromLiteral({}),
        metadata: MichelsonMap.fromLiteral({}),
      };
    });

    describe("mint", () => {
      it("creates an NFT for the supplied address", async () => {
        tezos.setProvider(accounts.alice.sk);

        const oracle = await Oracle.originate(tezos, storage);

        // When Alice mints token-id 1 for Bob
        await oracle.mint({
          token_id: 1,
          address: accounts.bob.pkh,
        });

        const updatedStorage = await oracle.getStorage(tezos);

        const bobBalance = await updatedStorage.ledger.get({ 0: accounts.bob.pkh, 1: 1 });

        // An NFT is created correctly
        expect(bobBalance.toNumber()).toEqual(1);
        expect(await updatedStorage.tokens.get(1)).toEqual(UnitValue);
      });

      it("fails if sender is not the admin", async () => {
        // Set Bob (not admin) as the sender
        tezos.setProvider(accounts.bob.sk);

        const oracle = await Oracle.originate(tezos, storage);

        // When Bob mints token-id 1 for Alice, the txn fails
        await expect(
          oracle.mint({
            token_id: 1,
            address: accounts.bob.pkh,
          })
        ).rejects.toThrow("NOT_AUTHORISED");
      });

      it("fails if token id already exists", async () => {
        tezos.setProvider(accounts.alice.sk);

        storage.tokens.set(1, {});

        const oracle = await Oracle.originate(tezos, storage);

        // When Alice mints token-id 1 for Bob, the txn fails
        await expect(
          oracle.mint({
            token_id: 1,
            address: accounts.bob.pkh,
          })
        ).rejects.toThrow("TOKEN_ID_ALREADY_EXISTS");
      });
    });

    describe("token_metadata - offchain view", () => {
      it("correctly returns the token metadata", async () => {
        // Deploy a dummy state oracle
        const stateOracle = await Oracle.originateHelper(tezos, {
          prop_1: 5,
          prop_2: 6,
        });

        storage.tokens.set(1, {});
        storage.oracle_address = stateOracle;

        const oracle = await Oracle.originate(tezos, storage);

        const tokenMetadata = await oracle.tokenMetadata(tezos, metadata, 1);

        expect(tokenMetadata.token_id.toNumber()).toEqual(1);

        // Expected URI: https://metadata_url.com/5/6/1
        expect(tokenMetadata.token_info.get("")).toEqual(
          "68747470733a2f2f6d657461646174615f75726c2e636f6d2f352f362f31"
        );
      });

      it("fails if the token does not exist", async () => {
        const oracle = await Oracle.originate(tezos, storage);

        await expect(oracle.tokenMetadata(tezos, metadata, 1)).rejects.toThrow(
          "FA2_TOKEN_UNDEFINED"
        );
      });

      it("fails if the oracle view is invalid", async () => {
        storage.tokens.set(1, {});

        const oracle = await Oracle.originate(tezos, storage);

        await expect(oracle.tokenMetadata(tezos, metadata, 1)).rejects.toThrow("INVALID_VIEW");
      });
    });
  });

export default tests;
