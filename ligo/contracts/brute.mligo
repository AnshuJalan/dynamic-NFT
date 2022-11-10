(*                               Brute Structure

  Brute structure represents the most basic form of a dynamic NFT. It allows
  an admin address to directly modify the token_metadata big_map through a
  dedicated entrypoint.
 
  It's useful when the metadata depends entirely on data stored on off-chain
  servers or its generation requires extensive computation that is not possible
  on-chain.
 
  Every metadata update will require a transaction on the blockchain, incurring
  fees. Thus, a brute structure must only be used when the metadata changes are
  infrequent. 
*)

#include "../common/fa2/fa2_lib.mligo"
#import "../common/errors.mligo" "ERRORS"
#import "../common/fa2/fa2_errors.mligo" "FA2_ERRORS"

(* Brute Structure storage types *)

type token_metadata_value = {
  token_id : nat;
  token_info : (string, bytes) map;
}

type token_metadata = (nat, token_metadata_value) big_map

type storage = {
    admin : address;
    ledger : ledger;
    operators : operators;
    metadata: (string, bytes) big_map;
    token_metadata : token_metadata;
}

(* Brute structure parameter types *)

type mint_params = [@layout:comb] { 
    address : address;
    token_id : nat;
    metadata : (string, bytes) map;
}

type update_token_metadata_params = [@layout:comb] {
    token_id : nat;
    metadata : (string, bytes) map;
}

type parameter =
    | Mint of mint_params
    | Transfer of transfer_params
    | Balance_of of balance_of_params
    | Update_operators of update_operator_params
    | Update_token_metadata of update_token_metadata_params

type return = operation list * storage

(* Entrypoints *)

let mint (store : storage) (params : mint_params) : storage =
    (* Only the admin can mint an NFT with a unique token-id *)
    if Tezos.get_sender () <> store.admin then failwith ERRORS.not_authorised
    else if Big_map.mem params.token_id store.token_metadata then failwith ERRORS.token_id_already_exists
    else 
        let updated_ledger = Big_map.update (params.address, params.token_id) (Some 1n) store.ledger in
        let metadata_value = { token_id = params.token_id; token_info = params.metadata; } in
        let updated_token_metadata = Big_map.update (params.token_id) (Some metadata_value) store.token_metadata in
        { store with ledger = updated_ledger; token_metadata = updated_token_metadata; }

let update_token_metadata (store : storage) (params : update_token_metadata_params) : token_metadata =
    if Tezos.get_sender () <> store.admin then failwith ERRORS.not_authorised
    else match Big_map.find_opt params.token_id store.token_metadata with
        | None -> failwith FA2_ERRORS.fa2_token_undefined 
        | Some tmv ->
            let updated_metadata = { tmv with token_info = params.metadata; } in
            Big_map.update (params.token_id) (Some updated_metadata) store.token_metadata

(* Main *)

let main (action, store : parameter * storage) : return =
    match action with 
    | Mint params -> ([], mint store params)
    | Transfer params -> ([], { store with ledger = transfer store.ledger store.operators params })
    | Balance_of params -> (balance_of store.ledger params, store)
    | Update_operators params -> ([], { store with operators = update_operators store.operators params })
    | Update_token_metadata params -> ([], { store with token_metadata = update_token_metadata store params })