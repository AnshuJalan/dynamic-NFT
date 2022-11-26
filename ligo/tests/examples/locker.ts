import { MichelsonMap, UnitValue } from "@taquito/taquito";

import Locker from "../helpers/Locker";
import Tezos from "../helpers/Tezos";
import { config } from "../config";
import accounts from "../helpers/accounts";

import metadata from "../../examples/metadata/locker.json";
import { SAMPLE_SVG_BYTES } from "../../data/svg_example";

const tests = () =>
  describe("locker", () => {
    let storage: any;
    const tezos = new Tezos(config);

    beforeEach(() => {
      storage = {
        ledger: MichelsonMap.fromLiteral({}),
        operators: MichelsonMap.fromLiteral({}),
        locks: MichelsonMap.fromLiteral({}),
        lock_count: 0,
        harbinger_address: "tz1eUzpKnk5gKLYw4HWs2sWsynfbT7ypGxNM",
        metadata: MichelsonMap.fromLiteral({}),
      };
    });

    describe("mint", () => {
      it("creates an NFT for the supplied address", async () => {
        tezos.setProvider(accounts.alice.sk);

        const locker = await Locker.originate(tezos, storage);

        // When Alice mints a lock with 10 tez
        await locker.mint(10);

        const updatedStorage = await locker.getStorage(tezos);

        const aliceBalance = await updatedStorage.ledger.get({ 0: accounts.alice.pkh, 1: 1 });
        const lockAmount = await updatedStorage.locks.get(1);

        const balance = await locker.getBalance(tezos);

        // An NFT representing the lock is created correctly
        expect(aliceBalance.toNumber()).toEqual(1);
        expect(lockAmount.toNumber()).toEqual(10_000_000); // 10 tez or 10,000,000 mutez
        expect(updatedStorage.lock_count.toNumber()).toEqual(1);

        // Contract's balance is updated
        expect(balance.toNumber()).toEqual(10_000_000);
      });

      it("fails if send amount is 0 tez", async () => {
        tezos.setProvider(accounts.alice.sk);

        const locker = await Locker.originate(tezos, storage);

        // When Alice mints a lock with 0 tez, the txn fails
        await expect(locker.mint(0)).rejects.toThrow("ZERO_AMOUNT_BEING_LOCKED");
      });
    });

    describe("withdraw", () => {
      it("returns the locked tez to the owner", async () => {
        tezos.setProvider(accounts.alice.sk);

        const locker = await Locker.originate(tezos, storage);

        // Initialise a lock of 10 tez for Alice
        await locker.mint(10);

        const aliceOriginalBalance = await tezos.getBalanceOf(accounts.alice.pkh);

        // // When Alice withdraws lock id 1
        await locker.withdraw(1);

        const aliceNewBalance = await tezos.getBalanceOf(accounts.alice.pkh);

        const updatedStorage = await locker.getStorage(tezos);

        // Alice got her tez back (gas fees approximation)
        expect(aliceNewBalance.toNumber() - aliceOriginalBalance.toNumber()).toBeGreaterThan(9_999_000);
        // Lock is deleted
        expect(await updatedStorage.locks.get(1)).toBeUndefined();
      });

      it("fail if lock does not exist", async () => {
        tezos.setProvider(accounts.alice.sk);

        const locker = await Locker.originate(tezos, storage);

        await expect(locker.withdraw(1)).rejects.toThrow("FA2_TOKEN_UNDEFINED");
      });

      it("fails if sender does not own the lock", async () => {
        tezos.setProvider(accounts.alice.sk);

        storage.locks.set(1, 10);

        const locker = await Locker.originate(tezos, storage);

        await expect(locker.withdraw(1)).rejects.toThrow("NOT_AUTHORISED");
      });
    });

    describe("token_metadata - offchain view", () => {
      it("correctly returns the token metadata", async () => {
        // Initialise a lock with token-id 21 and locked amount as 35 tez
        storage.locks.set(21, 35_000_000);

        // Initialise dummy harbinger with price as $1.5 (granularity 10 ^ 6)
        const harbinger = await Locker.originateHarbinger(tezos, 1_500_000);

        storage.harbinger_address = harbinger;

        const locker = await Locker.originate(tezos, storage);

        const tokenMetadata = await locker.tokenMetadata(tezos, metadata, 21);

        expect(tokenMetadata.token_id.toNumber()).toEqual(21);
        /* Expected TZIP-21 based metadata: 
          {
            name: "Locker dNFT",
            symbol: "LOCK",
            decimals: "0",
            thumbnailUri: "https://image_url.com/thumbnail.png",
            artifactUri: SAMPLE_SVG_BYTES,
            displayUri: SAMPLE_SVG_BYTES
          }
        */
        expect(tokenMetadata.token_info.get("name")).toEqual("4c6f636b657220644e4654");
        expect(tokenMetadata.token_info.get("symbol")).toEqual("4c4f434b");
        expect(tokenMetadata.token_info.get("decimals")).toEqual("30");
        expect(tokenMetadata.token_info.get("thumbnailUri")).toEqual(
          "68747470733a2f2f696d6167655f75726c2e636f6d2f7468756d626e61696c2e706e67"
        );
        expect(tokenMetadata.token_info.get("artifactUri")).toEqual(SAMPLE_SVG_BYTES);
        expect(tokenMetadata.token_info.get("displayUri")).toEqual(SAMPLE_SVG_BYTES);
        expect(tokenMetadata.token_info.get("ttl")).toEqual("363030");
      });

      it("fails if the token does not exist", async () => {
        const locker = await Locker.originate(tezos, storage);

        await expect(locker.tokenMetadata(tezos, metadata, 1)).rejects.toThrow("FA2_TOKEN_UNDEFINED");
      });

      it("fails if oracle contract is invalid", async () => {
        storage.locks.set(1, 10);

        const locker = await Locker.originate(tezos, storage);

        await expect(locker.tokenMetadata(tezos, metadata, 1)).rejects.toThrow("INVALID_VIEW");
      });
    });
  });

export default tests;
