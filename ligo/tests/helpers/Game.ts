import * as fs from "fs";
import { DefaultContractType, TransactionOperation } from "@taquito/taquito";

import Tezos from "./Tezos";
import { ChangeWeaponParams, AttackParams, BasicMintParams } from "../types";

export default class Game {
  private _instance: DefaultContractType;

  constructor(instance: DefaultContractType) {
    this._instance = instance;
  }

  static async originate(tezos: Tezos, codepath: string, storage: any): Promise<Game> {
    try {
      const code = fs.readFileSync(codepath).toString();
      return new Game(await tezos.originate(code, storage));
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

  async mint(params: BasicMintParams): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methodsObject.mint(params).send();
      await op.confirmation();
      return op;
    } catch (err: any) {
      throw err;
    }
  }

  async changeWeapon(params: ChangeWeaponParams): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methodsObject.change_weapon(params).send();
      await op.confirmation();
      return op;
    } catch (err: any) {
      throw err;
    }
  }

  async attack(params: AttackParams): Promise<TransactionOperation> {
    try {
      const op = await this._instance.methodsObject.attack(params).send();
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
