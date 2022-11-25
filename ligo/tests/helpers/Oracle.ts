/**
 * This class forms a common interface template for Point, Create and SVG structure.
 */

import * as fs from "fs";
import { DefaultContractType, TransactionOperation } from "@taquito/taquito";

import Tezos from "./Tezos";
import { OracleMintParams } from "../types";

export default class Oracle {
  private _instance: DefaultContractType;

  constructor(instance: DefaultContractType) {
    this._instance = instance;
  }

  static async originate(tezos: Tezos, storage: any): Promise<Oracle> {
    try {
      const code = fs.readFileSync(`${__dirname}/../../contracts/michelson/oracle.tz`).toString();
      return new Oracle(await tezos.originate(code, storage));
    } catch (err: any) {
      throw err;
    }
  }

  static async originateHelper(tezos: Tezos, storage: any): Promise<string> {
    try {
      const code = fs
        .readFileSync(`${__dirname}/../../contracts/helpers/state_oracle.tz`)
        .toString();
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

  async mint(params: OracleMintParams): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methodsObject.mint(params).send();
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
