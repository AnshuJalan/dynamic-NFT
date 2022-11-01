export interface Config {
  rpc: string;
}

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
