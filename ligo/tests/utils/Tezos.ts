import { InMemorySigner } from "@taquito/signer";
import { DefaultContractType, TezosToolkit } from "@taquito/taquito";

import { Config } from "../types";

export default class Tezos {
  private _tezos: TezosToolkit;

  constructor({ rpc }: Config) {
    this._tezos = new TezosToolkit(rpc);
  }

  setProvider(sk: string) {
    this._tezos.setProvider({ signer: new InMemorySigner(sk) });
  }

  async originate(code: string, storage: string): Promise<DefaultContractType> {
    try {
      const op = await this._tezos.contract.originate({ code, storage });
      await op.confirmation();
      return op.contract();
    } catch (err: any) {
      throw err;
    }
  }

  async getStorage(instance: DefaultContractType): Promise<any> {
    try {
      return await instance.storage();
    } catch (err: any) {
      throw err;
    }
  }
}

module.exports.Tezos = Tezos;
