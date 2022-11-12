import * as fs from "fs";
import { DefaultContractType, TransactionOperation } from "@taquito/taquito";

import Tezos from "./Tezos";
import { ChangeStateParams, PointMintParams } from "../types";

// Metadata json
import metadata from "../../contracts/metadata/point.json";

export default class Point {
  private _instance: DefaultContractType;

  constructor(instance: DefaultContractType) {
    this._instance = instance;
  }

  static async originate(tezos: Tezos, storage: any): Promise<Point> {
    try {
      const code = fs.readFileSync(`${__dirname}/../../contracts/michelson/point.tz`).toString();
      return new Point(await tezos.originate(code, storage));
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

  async mint(params: PointMintParams): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methodsObject.mint(params).send();
      await op.confirmation();
      return op;
    } catch (err: any) {
      throw err;
    }
  }

  async changeState(params: ChangeStateParams): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methodsObject.change_state(params).send();
      await op.confirmation();
      return op;
    } catch (err: any) {
      throw err;
    }
  }

  async tokenMetadata(tezos: Tezos, tokenId: number): Promise<any> {
    try {
      return await tezos.executeView({
        metadataObject: metadata,
        contract: this._instance,
        params: tokenId,
      });
    } catch (err: any) {
      throw err;
    }
  }
}
