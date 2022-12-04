import { MichelsonMap, TezosToolkit } from "@taquito/taquito";

export interface Game {
  admin: string;
  ledger: MichelsonMap<any, any>;
  operators: MichelsonMap<any, any>;
  player_states: MichelsonMap<any, any>;
  metadata: MichelsonMap<any, any>;
}

export interface Locker {
  ledger: MichelsonMap<any, any>;
  operators: MichelsonMap<any, any>;
  locks: MichelsonMap<any, any>;
  lock_count: number;
  harbinger_address: string;
  metadata: MichelsonMap<any, any>;
}

export interface DeployParams {
  tezos: TezosToolkit;
  language: string;
  admin: string;
  harbingerAddress: string;
}

export interface MetadataStore {
  game1: string;
  game2: string;
  locker: string;
}
