export interface Config {
  rpc: string;
}

// Contract EP parameter types

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

export interface MintParams {
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
