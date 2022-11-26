(*                              Create Structure

  Create structure allows for more naturally dynamic token metadata similar to
  Point, but instead of building an external link to a TZIP-21 Json, it builds
  and serves the JSON through an off-chain view.

  It is useful when most of the fields in the metadata JSON are static or the
  off-chain datastore needs to be simplified. For instance, if a token has fixed
  'symbol' and 'decimals' and a static thumbnailUri, only fields like artifactUri
  and displayUri need to be dynamically generated. These may be an external link
  or an SVG (as shown in SVG Structure).  

  The liveness of the external server on which the artifact is hosted must be
  ensured. A decentralised storage service like IPFS is recommended. Moreover,
  the URIs generated in the off-chain view must be verified.
*)

#include "../common/utils.mligo"
#include "../common/constants.mligo"
#include "../common/fa2/fa2_lib.mligo"
#import "../common/errors.mligo" "ERRORS"
#import "../common/fa2/fa2_errors.mligo" "FA2_ERRORS"

(* Create Structure storage types *)

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

(* Create Structure parameter types *)

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

(* string: dNFT Create' *)
let name = 0x644e465420437265617465

(* string: 'dNFTC' *)
let symbol = 0x644e465443

(* string: '0' *)
let decimals = 0x30

(* string: 'https://image_url.com/thumbnail.png' *)
let thumbnail_uri = 0x68747470733a2f2f696d6167655f75726c2e636f6d2f7468756d626e61696c2e706e67

let token_metadata (token_id, store : nat * storage) : token_metadata_value = 
    match Big_map.find_opt token_id store.states with
    | None -> failwith FA2_ERRORS.fa2_token_undefined
    | Some s -> begin
        let prop_1 = bytes_of_nat s.prop_1 in
        let prop_2 = bytes_of_nat s.prop_2 in
        let b_token_id = bytes_of_nat token_id in
        (* 
            Contruct a URI (in bytes form) that points to the artifact and display image of the NFT.
            This is a sample construction. The form that your URI takes depends entirely on
            how your artifacts are hosted.

            Contructed URI: https://image_url.com/<prop_1>/<prop_2>/<token_id>.png
        *)
        let image_uri = join_bytes [ image_url; slash; prop_1; slash; prop_2; slash; b_token_id; png; ] in
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