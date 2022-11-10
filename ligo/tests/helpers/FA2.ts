import * as fs from "fs";
import { DefaultContractType, TransactionOperation } from "@taquito/taquito";

import Tezos from "./Tezos";
import { TransferParams, UpdateOperatorParams } from "../types";

export default class FA2 {
  private _instance: DefaultContractType;

  constructor(instance: DefaultContractType) {
    this._instance = instance;
  }

  static async originate(tezos: Tezos, storage: any): Promise<FA2> {
    try {
      const code = fs.readFileSync(`${__dirname}/../../contracts/michelson/fa2_nft.tz`).toString();
      return new FA2(await tezos.originate(code, storage));
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

  async transfer(params: TransferParams): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methods.transfer(params).send();
      await op.confirmation();
      return op;
    } catch (err: any) {
      throw err;
    }
  }

  async updateOperators(params: UpdateOperatorParams): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methods.update_operators(params).send();
      await op.confirmation();
      return op;
    } catch (err: any) {
      throw err;
    }
  }
}
