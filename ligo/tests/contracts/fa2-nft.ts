import { MichelsonMap, UnitValue } from "@taquito/taquito";

import FA2 from "../helpers/FA2";
import Tezos from "../helpers/Tezos";
import { config } from "../config";
import accounts from "../helpers/accounts";

const tests = () =>
  describe("fa2", () => {
    let storage: any;
    const tezos = new Tezos(config);

    beforeEach(() => {
      storage = {
        ledger: MichelsonMap.fromLiteral({}),
        operators: MichelsonMap.fromLiteral({}),
      };
    });

    describe("transfer", () => {
      it("sends tokens between addresses", async () => {
        tezos.setProvider(accounts.alice.sk);

        // Set the initial token-id 0 balance for alice as 5
        storage.ledger.set({ 0: accounts.alice.pkh, 1: 0 }, 5);

        const fa2 = await FA2.originate(tezos, storage);

        // When Alice transfers 3 tokens to Bob
        await fa2.transfer([
          { from_: accounts.alice.pkh, txs: [{ to_: accounts.bob.pkh, token_id: 0, amount: 3 }] },
        ]);

        const updatedStorage = await fa2.getStorage(tezos);

        const aliceBalance = await updatedStorage.ledger.get({ 0: accounts.alice.pkh, 1: 0 });
        const bobBalance = await updatedStorage.ledger.get({ 0: accounts.bob.pkh, 1: 0 });

        // Storage is updated correctly
        expect(aliceBalance.toNumber()).toEqual(2);
        expect(bobBalance.toNumber()).toEqual(3);
      });

      it("allows operator to send tokens", async () => {
        tezos.setProvider(accounts.bob.sk);

        // Set the initial token-id 0 balance for alice as 5
        storage.ledger.set({ 0: accounts.alice.pkh, 1: 0 }, 5);

        // Make Bob and operator for alice's token-id 0
        storage.operators.set(
          { owner: accounts.alice.pkh, operator: accounts.bob.pkh, token_id: 0 },
          {}
        );

        const fa2 = await FA2.originate(tezos, storage);

        // When Bob transfers 3 tokens from Alice to himself
        await fa2.transfer([
          { from_: accounts.alice.pkh, txs: [{ to_: accounts.bob.pkh, token_id: 0, amount: 3 }] },
        ]);

        const updatedStorage = await fa2.getStorage(tezos);

        const aliceBalance = await updatedStorage.ledger.get({ 0: accounts.alice.pkh, 1: 0 });
        const bobBalance = await updatedStorage.ledger.get({ 0: accounts.bob.pkh, 1: 0 });

        // Storage is updated correctly
        expect(aliceBalance.toNumber()).toEqual(2);
        expect(bobBalance.toNumber()).toEqual(3);
      });

      it("fails if the sender is not an operator or owner", async () => {
        tezos.setProvider(accounts.bob.sk);

        // Set the initial token-id 0 balance for alice as 5
        storage.ledger.set({ 0: accounts.alice.pkh, 1: 0 }, 5);

        const fa2 = await FA2.originate(tezos, storage);

        // When Bob tries to transfer 3 tokens from Alice to himself, the txn fails
        await expect(
          fa2.transfer([
            { from_: accounts.alice.pkh, txs: [{ to_: accounts.bob.pkh, token_id: 0, amount: 3 }] },
          ])
        ).rejects.toThrow("FA2_NOT_OPERATOR");
      });

      it("fails if the sender does not have enough balance", async () => {
        tezos.setProvider(accounts.bob.sk);

        const fa2 = await FA2.originate(tezos, storage);

        // When Bob tries to transfer 3 tokens to Alice, the txn fails
        await expect(
          fa2.transfer([
            { from_: accounts.bob.pkh, txs: [{ to_: accounts.alice.pkh, token_id: 0, amount: 3 }] },
          ])
        ).rejects.toThrow("FA2_INSUFFICIENT_BALANCE");
      });
    });

    describe("update_operators", () => {
      it("sets the operator for a token", async () => {
        tezos.setProvider(accounts.alice.sk);

        const fa2 = await FA2.originate(tezos, storage);

        const opKey = { owner: accounts.alice.pkh, operator: accounts.bob.pkh, token_id: 5 };

        // When Alice makes Bob the operator of token-id 5
        await fa2.updateOperators([{ add_operator: opKey }]);

        const updatedStorage = await fa2.getStorage(tezos);

        // Storage is updated correctly
        expect(await updatedStorage.operators.get(opKey)).toEqual(UnitValue);
      });

      it("removes the operator for a token", async () => {
        tezos.setProvider(accounts.alice.sk);

        const opKey = { owner: accounts.alice.pkh, operator: accounts.bob.pkh, token_id: 5 };

        // Set Bob as the Operator of alice for token-id 5
        storage.operators.set(opKey, {});

        const fa2 = await FA2.originate(tezos, storage);

        // When Alice removes Bob as the operator of token-id 5
        await fa2.updateOperators([{ remove_operator: opKey }]);

        const updatedStorage = await fa2.getStorage(tezos);

        // Storage is updated correctly
        expect(await updatedStorage.operators.get(opKey)).toEqual(undefined);
      });

      it("fails if the sender is not the owner", async () => {
        tezos.setProvider(accounts.bob.sk);

        const fa2 = await FA2.originate(tezos, storage);

        const opKey = { owner: accounts.alice.pkh, operator: accounts.bob.pkh, token_id: 5 };

        // When Bob tries to make himself the operator of Alice's token-id 5, the transactio fails
        await expect(fa2.updateOperators([{ add_operator: opKey }])).rejects.toThrow(
          "FA2_NOT_OWNER"
        );
      });
    });
  });

export default tests;
