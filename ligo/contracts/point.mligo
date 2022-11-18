(*                                Point Structure

  Point structure allows more naturally dynamic token metadata through an
  off-chain view that dynamically creates an external metadata URI (that points
  to a TZIP-21 json) using values from the contract's storage.

  It's useful when the metadata depends on some properties (of the entity
  behind the token) stored in the contract's storage.

  The liveness of the external server on which the metadata is hosted must be
  ensured. A decentralised storage service like IPFS is recommended. Moreover,
  the URIs generated in the off-chain view must be verified.
*)

#include "../common/utils.mligo"
#include "../common/constants.mligo"
#include "../common/fa2/fa2_lib.mligo"
#import "../common/errors.mligo" "ERRORS"
#import "../common/fa2/fa2_errors.mligo" "FA2_ERRORS"

(* Point Structure storage types *)

(* 
    `state` is a generic representation of the attributes/properties an NFT may have. 
    Example: 
        * The construction status of different areas of a real estate (lawn, roofing etc)
        * A nat value 0 would mean under-construction, and 1 may mean completed.
    The state of your NFT will depend on what underlying entity it represents.
*)
type state = {
    prop_1 : nat;
    prop_2 : nat;
}

type states = (nat, state) big_map

type storage = {
    admin : address;
    ledger : ledger;
    operators : operators;
    tokens : (nat, unit) big_map; // Records minted token-ids
    states : states;
    metadata: (string, bytes) big_map;
}

(* Point Structure parameter types *)

type mint_params = [@layout:comb] { 
    address : address;
    token_id : nat;
    state : state;
}

type change_state_params = [@layout:comb] {
    token_id : nat;
    state : state;
}

type parameter =
    | Mint of mint_params
    | Transfer of transfer_params
    | Balance_of of balance_of_params
    | Update_operators of update_operator_params
    | Change_state of change_state_params

type return = operation list * storage

(* Entrypoints *)

let mint (store : storage) (params : mint_params) : storage =
    if Tezos.get_sender () <> store.admin then failwith ERRORS.not_authorised
    else if Big_map.mem params.token_id store.tokens then failwith ERRORS.token_id_already_exists
    else
        let updated_tokens = Big_map.update params.token_id (Some ()) store.tokens in
        let updated_ledger = Big_map.update (params.address, params.token_id) (Some 1n) store.ledger in
        let updated_states = Big_map.update (params.token_id) (Some params.state) store.states in
        { store with tokens = updated_tokens; ledger = updated_ledger; states = updated_states; }

(*
    `change_state` may be called differently in your implementation - for example, by an
    externally authorised contract or internally by the NFT contract itself.
*)
let change_state (store : storage) (params : change_state_params) : states =
    if Tezos.get_sender () <> store.admin then failwith ERRORS.not_authorised
    else if not Big_map.mem params.token_id store.tokens then failwith FA2_ERRORS.fa2_token_undefined
    else Big_map.update (params.token_id) (Some params.state) store.states

(* Main *)

let main (action, store : parameter * storage) : return =
    match action with 
    | Mint params -> ([], mint store params)
    | Transfer params -> ([], { store with ledger = transfer store.ledger store.operators params })
    | Balance_of params -> (balance_of store.ledger params, store)
    | Update_operators params -> ([], { store with operators = update_operators store.operators params })
    | Change_state params -> ([], { store with states = change_state store params })

(* Token-metadata Offchain view *)

type token_metadata_value = {
  token_id : nat;
  token_info : (string, bytes) map;
}

let token_metadata (token_id, store : nat * storage) : token_metadata_value = 
    match Big_map.find_opt token_id store.states with
    | None -> failwith FA2_ERRORS.fa2_token_undefined
    | Some s -> begin
        let prop_1 = bytes_of_nat s.prop_1 in
        let prop_2 = bytes_of_nat s.prop_2 in
        let b_token_id = bytes_of_nat token_id in
        (* 
            Contruct a URI (in bytes form) that points to a TZIP-21 based metadata JSON.
            This is a sample construction. The form that your URI takes depends entirely on
            how your artifacts are hosted.

            Contructed URI: https://metadata_url.com/<prop_1>/<prop_2>/<token_id>
        *)
        let metadata_uri = join_bytes [ metadata_url; slash; prop_1; slash; prop_2; slash; b_token_id; ] in
        { token_id = token_id; token_info = Map.literal [ ("", metadata_uri) ]; }
    end