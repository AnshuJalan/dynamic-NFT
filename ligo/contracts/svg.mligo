(*                              SVG Structure

  SVG structure is an extension of Create with the difference that the
  artifactUri and displayUri are an SVG data URI that is dynamically generated
  in the token_metadata off-chain view.
 
  This is useful when the artifact is an SVG, or can possibly be converted to an
  SVG and save the overheads of separately maintaining off-chain data.
*)

#include "../common/utils.mligo"
#include "../common/constants.mligo"
#include "../common/fa2/fa2_lib.mligo"
#include "../data/svg_structure.mligo"
#import "../common/errors.mligo" "ERRORS"
#import "../common/fa2/fa2_errors.mligo" "FA2_ERRORS"

(* SVG Structure storage types *)

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
    states : states;
    metadata: (string, bytes) big_map;
}

(* SVG Structure parameter types *)

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
    else if Big_map.mem params.token_id store.states then failwith ERRORS.token_id_already_exists
    else
        let updated_ledger = Big_map.update (params.address, params.token_id) (Some 1n) store.ledger in
        let updated_states = Big_map.update (params.token_id) (Some params.state) store.states in
        { store with ledger = updated_ledger; states = updated_states; }

(*
    `change_state` may be called differently in your implementation - for example, by an
    externally authorised contract or internally by the NFT contract itself.
*)
let change_state (store : storage) (params : change_state_params) : states =
    if Tezos.get_sender () <> store.admin then failwith ERRORS.not_authorised
    else if not Big_map.mem params.token_id store.states then failwith FA2_ERRORS.fa2_token_undefined
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

(* Constant fields in bytes *)

(* string: 'dNFT SVG' *)
let name = 0x644e465420535647

(* string: 'dNFTS' *)
let symbol = 0x644e465453

(* string: '0' *)
let decimals = 0x30

(* string: 'https://image_url.com/thumbnail.png' *)
let thumbnail_uri = 0x68747470733a2f2f696d6167655f75726c2e636f6d2f7468756d626e61696c2e706e67

let token_metadata (token_id, store : nat * storage) : token_metadata_value = 
    match Big_map.find_opt token_id store.states with
    | None -> failwith FA2_ERRORS.fa2_token_undefined
    | Some s -> begin
        let prop_sum = bytes_of_nat (s.prop_1 + s.prop_2) in
        let b_token_id = bytes_of_nat token_id in
        (* 
            Construct the SVG data URI (in bytes form) using the helper.

            This is a sample construction. You would need to write your
            helper to join the different sections of the SVG data URI.
        *)
        let image_uri = build_svg b_token_id prop_sum in
        { 
            token_id = token_id;
            (* TZIP-21 compliant format *)
            token_info = Map.literal [
                ("name", name);
                ("symbol", symbol);
                ("decimals", decimals);
                ("thumbnailUri", thumbnail_uri);
                ("artifactUri", image_uri);
                ("displayUri", image_uri);
                ("ttl", bytes_of_nat 600n);
            ]; 
        }
    end