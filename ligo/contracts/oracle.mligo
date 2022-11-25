(*                            Oracle Structure

  Oracle structure allows for fetching a 'state' from an on-chain oracle and
  dynamically building the token metadata using the retrieved values. The
  metadata is then served through an offchain view.

  It's useful when the metadata depends on some off-chain data that needs to be
  put on-chain in a decentralised way through an oracle.
 
  The liveness of the oracle and integrity of the data must be ensured.
*)

#include "../common/utils.mligo"
#include "../common/constants.mligo"
#include "../common/fa2/fa2_lib.mligo"
#import "../common/errors.mligo" "ERRORS"
#import "../common/fa2/fa2_errors.mligo" "FA2_ERRORS"

(* Oracle Structure storage types *)

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

type storage = {
    admin : address;
    ledger : ledger;
    operators : operators;
    tokens : (nat, unit) big_map; // Records minted token-ids
    oracle_address : address;
    metadata: (string, bytes) big_map;
}

(* Oracle Structure parameter types *)

type mint_params = [@layout:comb] { 
    address : address;
    token_id : nat;
}

type parameter =
    | Mint of mint_params
    | Transfer of transfer_params
    | Balance_of of balance_of_params
    | Update_operators of update_operator_params

type return = operation list * storage

(* Entrypoints *)

let mint (store : storage) (params : mint_params) : storage =
    if Tezos.get_sender () <> store.admin then failwith ERRORS.not_authorised
    else if Big_map.mem params.token_id store.tokens then failwith ERRORS.token_id_already_exists
    else
        let updated_tokens = Big_map.update params.token_id (Some ()) store.tokens in
        let updated_ledger = Big_map.update (params.address, params.token_id) (Some 1n) store.ledger in
        { store with tokens = updated_tokens; ledger = updated_ledger; }

(* Main *)

let main (action, store : parameter * storage) : return =
    match action with 
    | Mint params -> ([], mint store params)
    | Transfer params -> ([], { store with ledger = transfer store.ledger store.operators params })
    | Balance_of params -> (balance_of store.ledger params, store)
    | Update_operators params -> ([], { store with operators = update_operators store.operators params })

(* Token-metadata Offchain view *)

type token_metadata_value = {
  token_id : nat;
  token_info : (string, bytes) map;
}

let token_metadata (token_id, store : nat * storage) : token_metadata_value = 
    match Big_map.find_opt token_id store.tokens with
    | None -> failwith FA2_ERRORS.fa2_token_undefined
    | Some _ -> begin
        (* 
            Fetch the current state of the entity behind the token-id through the oracle.
            The semantics of this call is utility dependent. You may fetch all TZIP-21
            fields from the oracle and/or some co-related state and build the metadata
            URI as shown in this structure.
         *)
        match ((Tezos.call_view "get_state" token_id store.oracle_address) : state option) with
        | None -> failwith ERRORS.invalid_view
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
    end