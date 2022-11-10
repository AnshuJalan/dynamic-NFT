import { MichelsonMap } from "@taquito/taquito";

import Brute from "../helpers/Brute";
import Tezos from "../helpers/Tezos";
import { config } from "../config";
import accounts from "../helpers/accounts";
import { toBytes } from "../helpers/utils";

const tests = () =>
  describe("brute", () => {
    let storage: any;
    const tezos = new Tezos(config);

    beforeEach(() => {
      storage = {
        admin: accounts.alice.pkh, // Alice is the admin
        ledger: MichelsonMap.fromLiteral({}),
        operators: MichelsonMap.fromLiteral({}),
        metadata: MichelsonMap.fromLiteral({}),
        token_metadata: MichelsonMap.fromLiteral({}),
      };
    });

    describe("mint", () => {
      it("creates an NFT for the supplied address", async () => {
        tezos.setProvider(accounts.alice.sk);

        const brute = await Brute.originate(tezos, storage);

        // When Alice mints token-id 1 for Bob
        await brute.mint({
          address: accounts.bob.pkh,
          token_id: 1,
          metadata: { "": toBytes("https://external_link.com") },
        });

        const updatedStorage = await brute.getStorage(tezos);

        const bobBalance = await updatedStorage.ledger.get({ 0: accounts.bob.pkh, 1: 1 });
        const token1Metadata = await updatedStorage.token_metadata.get(1);

        // An NFT is created correctly
        expect(bobBalance.toNumber()).toEqual(1);
        expect(token1Metadata.token_id.toNumber()).toEqual(1);
        expect(token1Metadata.token_info.get("")).toEqual(
          toBytes("https://external_link.com").slice(2)
        );
      });

      it("fails if sender is not the admin", async () => {
        // Set Bob (not admin) as the sender
        tezos.setProvider(accounts.bob.sk);

        const brute = await Brute.originate(tezos, storage);

        // When Bob mints token-id 1 for Alice, the txn fails
        await expect(
          brute.mint({
            address: accounts.alice.pkh,
            token_id: 1,
            metadata: { "": toBytes("https://external_link.com") },
          })
        ).rejects.toThrow("NOT_AUTHORISED");
      });

      it("fails if token id already exists", async () => {
        tezos.setProvider(accounts.alice.sk);

        storage.token_metadata.set(1, {
          token_id: 1,
          token_info: { "": toBytes("https://external_link.com") },
        });

        const brute = await Brute.originate(tezos, storage);

        // When Alice mints token-id 1 for Bob, the txn fails
        await expect(
          brute.mint({
            address: accounts.bob.pkh,
            token_id: 1,
            metadata: { "": toBytes("https://external_link.com") },
          })
        ).rejects.toThrow("TOKEN_ID_ALREADY_EXISTS");
      });
    });

    describe("update_token_metadata", () => {
      it("correctly updates the metadata of a token", async () => {
        tezos.setProvider(accounts.alice.sk);

        storage.token_metadata.set(1, {
          token_id: 1,
          token_info: { "": toBytes("https://external_link.com") },
        });

        const brute = await Brute.originate(tezos, storage);

        // When Alice updates the token metadata of token-id 1
        await brute.updateTokenMetadata({
          token_id: 1,
          metadata: { "": toBytes("https://external_link_new.com") },
        });

        const updatedStorage = await brute.getStorage(tezos);

        const token1Metadata = await updatedStorage.token_metadata.get(1);

        // The metadata is updated correctly
        expect(token1Metadata.token_id.toNumber()).toEqual(1);
        expect(token1Metadata.token_info.get("")).toEqual(
          toBytes("https://external_link_new.com").slice(2)
        );
      });

      it("fails if sender is not the admin", async () => {
        // Set Bob (not admin) as the sender
        tezos.setProvider(accounts.bob.sk);

        storage.token_metadata.set(1, {
          token_id: 1,
          token_info: { "": toBytes("https://external_link.com") },
        });

        const brute = await Brute.originate(tezos, storage);

        // When Bob updates the token metadata of token-id 1, the txn fails
        await expect(
          brute.updateTokenMetadata({
            token_id: 1,
            metadata: { "": toBytes("https://external_link_new.com") },
          })
        ).rejects.toThrow("NOT_AUTHORISED");
      });

      it("fails if token id does not exist", async () => {
        tezos.setProvider(accounts.alice.sk);

        const brute = await Brute.originate(tezos, storage);

        // When Alice updated the token-metadata token-id 1 for Bob, the txn fails
        await expect(
          brute.updateTokenMetadata({
            token_id: 1,
            metadata: { "": toBytes("https://external_link.com") },
          })
        ).rejects.toThrow("FA2_TOKEN_UNDEFINED");
      });
    });
  });

export default tests;
