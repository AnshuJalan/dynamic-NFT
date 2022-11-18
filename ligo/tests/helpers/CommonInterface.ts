/**
 * This class forms a common interface template for Point, Create and SVG structure.
 */

import * as fs from "fs";
import { DefaultContractType, TransactionOperation } from "@taquito/taquito";

import Tezos from "./Tezos";
import { ChangeStateParams, PointMintParams } from "../types";

class CommonInterface {
  private _instance: DefaultContractType;

  constructor(instance: DefaultContractType) {
    this._instance = instance;
  }

  static async originate(tezos: Tezos, storage: any): Promise<CommonInterface> {
    try {
      const code = fs.readFileSync(`${__dirname}/../../contracts/michelson/point.tz`).toString();
      return new CommonInterface(await tezos.originate(code, storage));
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

// All these structures have the same interface
export const Point = CommonInterface;
export const Create = CommonInterface;
export const SVG = CommonInterface;
