import * as fs from "fs";
import { DefaultContractType, TransactionOperation } from "@taquito/taquito";

import Tezos from "./Tezos";

export default class Locker {
  private _instance: DefaultContractType;

  constructor(instance: DefaultContractType) {
    this._instance = instance;
  }

  static async originate(tezos: Tezos, storage: any): Promise<Locker> {
    try {
      const code = fs.readFileSync(`${__dirname}/../../examples/michelson/locker.tz`).toString();
      return new Locker(await tezos.originate(code, storage));
    } catch (err: any) {
      throw err;
    }
  }

  static async originateHarbinger(tezos: Tezos, storage: any): Promise<string> {
    try {
      const code = fs.readFileSync(`${__dirname}/../../examples/helpers/harbinger.tz`).toString();
      return (await tezos.originate(code, storage)).address;
    } catch (err: any) {
      throw err;
    }
  }

  async getStorage(tezos: Tezos): Promise<any> {
    try {
      return await tezos.getStorage(this._instance);
    } catch (err: any) {
      throw err;
    }
  }

  async getBalance(tezos: Tezos): Promise<any> {
    try {
      return await tezos.getBalance(this._instance);
    } catch (err: any) {
      throw err;
    }
  }

  getAddress() {
    return this._instance.address;
  }

  async mint(amount: number): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methodsObject.mint([["unit"]]).send({
        amount,
        mutez: false,
      });
      await op.confirmation();
      return op;
    } catch (err: any) {
      throw err;
    }
  }

  async withdraw(tokenId: number): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methodsObject.withdraw(tokenId).send();
      await op.confirmation();
      return op;
    } catch (err: any) {
      throw err;
    }
  }

  async tokenMetadata(tezos: Tezos, tzip16Metadata: any, tokenId: number): Promise<any> {
    try {
      return await tezos.executeView({
        metadataObject: tzip16Metadata,
        contract: this._instance,
        params: tokenId,
      });
    } catch (err: any) {
      throw err;
    }
  }
}
