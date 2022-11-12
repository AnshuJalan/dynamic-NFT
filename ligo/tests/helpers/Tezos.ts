import { InMemorySigner } from "@taquito/signer";
import { DefaultContractType, RpcReadAdapter, TezosToolkit } from "@taquito/taquito";
import { MichelsonStorageView } from "@taquito/tzip16";

import { Config, ExecuteViewParams } from "../types";

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

  async executeView(params: ExecuteViewParams) {
    try {
      const view = new MichelsonStorageView(
        "token_metadata", // Same in the context of all contracts in this project
        // @ts-ignore
        params.contract,
        this._tezos.rpc,
        new RpcReadAdapter(this._tezos.rpc),
        params.metadataObject.views[0].implementations[0].michelsonStorageView.returnType,
        params.metadataObject.views[0].implementations[0].michelsonStorageView.code,
        params.metadataObject.views[0].implementations[0].michelsonStorageView.parameter
      );
      return await view.executeView(params.params);
    } catch (err: any) {
      throw err;
    }
  }
}

module.exports.Tezos = Tezos;
