import { DefaultContractType } from "@taquito/taquito";

export interface Config {
  rpc: string;
}

// Tezos

export interface ExecuteViewParams {
  metadataObject: any;
  contract: DefaultContractType;
  params: any;
}

// FA2

export type TransferParams = Array<{
  from_: string;
  txs: Array<{ to_: string; amount: number; token_id: number }>;
}>;

export interface OperatorKey {
  owner: string;
  operator: string;
  token_id: number;
}

export type UpdateOperatorParams = Array<{ add_operator: OperatorKey } | { remove_operator: OperatorKey }>;

export interface BasicMintParams {
  address: string;
  token_id: number;
}

// Brute

export interface BruteMintParams {
  address: string;
  token_id: number;
  metadata: {
    [key: string]: string;
  };
}

export interface UpdateTokenMetadataParams {
  token_id: number;
  metadata: {
    [key: string]: string;
  };
}

// Point, Create, SVG

export interface CommonMintParams {
  address: string;
  token_id: number;
  state: {
    prop_1: number;
    prop_2: number;
  };
}

export interface ChangeStateParams {
  token_id: number;
  state: {
    prop_1: number;
    prop_2: number;
  };
}

// Game

export interface ChangeWeaponParams {
  token_id: number;
  weapon: {
    [key: string]: {};
  };
}

export interface AttackParams {
  attacker_id: number;
  victim_id: number;
}
