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

export type UpdateOperatorParams = Array<
  { add_operator: OperatorKey } | { remove_operator: OperatorKey }
>;

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

export interface MintParams {
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

// Oracle

export interface OracleMintParams {
  address: string;
  token_id: number;
}
