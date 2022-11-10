import * as fs from "fs";
import { DefaultContractType, TransactionOperation } from "@taquito/taquito";

import Tezos from "./Tezos";
import { MintParams, UpdateTokenMetadataParams } from "../types";

export default class Brute {
  private _instance: DefaultContractType;

  constructor(instance: DefaultContractType) {
    this._instance = instance;
  }

  static async originate(tezos: Tezos, storage: any): Promise<Brute> {
    try {
      const code = fs.readFileSync(`${__dirname}/../../contracts/michelson/brute.tz`).toString();
      return new Brute(await tezos.originate(code, storage));
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

  async mint(params: MintParams): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methodsObject.mint(params).send();
      await op.confirmation();
      return op;
    } catch (err: any) {
      throw err;
    }
  }

  async updateTokenMetadata(params: UpdateTokenMetadataParams): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methodsObject.update_token_metadata(params).send();
      await op.confirmation();
      return op;
    } catch (err: any) {
      throw err;
    }
  }
}
