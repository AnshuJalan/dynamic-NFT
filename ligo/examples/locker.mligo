(*           Tokenised XTZ locker based on Oracle and SVG Structure

  An XTZ locking contract where the locked positions are tradable as NFTs. The
  token metadata (specifically the 'artifactUri' and 'displayUri') of these NFTs
  are dynamically generated and the graphic displays the market value (in dollars)
  of the locked amount.
 
  Entire dynamic generation of token metadata happens onchain. The price of XTZ
  is pulled through Harbinger oracle and the final graphic is an SVG data URI.
 
  Although a simple example, this pattern of having a fancy graphic for tokenised
  positions has been particularly popular in Defi of the late. A Tezos implementation
  is Plenty's veNFT (under development by our team). On other chains there's 
  Uniswap v3 positions and Angle protocol CDPs (Ethereum).
*)

#include "../common/utils.mligo"
#include "../common/constants.mligo"
#include "../common/fa2/fa2_lib.mligo"
#include "../data/svg_example.mligo"
#import "../common/errors.mligo" "ERRORS"
#import "../common/fa2/fa2_errors.mligo" "FA2_ERRORS"

(* Locker storage types *)

type locks = (nat, tez) big_map

type storage = {
    ledger : ledger;
    operators : operators;
    locks : locks;
    lock_count : nat;
    harbinger_address : address;
    metadata: (string, bytes) big_map;
}

(* Locker parameter types *)

type parameter =
    | Mint
    | Transfer of transfer_params
    | Balance_of of balance_of_params
    | Update_operators of update_operator_params
    | Withdraw of nat

type return = operation list * storage

(* Utilities *)

let return_tez (amt : tez) : operation =
    match Tezos.get_contract_opt (Tezos.get_sender ()) with
    | None -> failwith ERRORS.not_authorised
    | Some d -> Tezos.transaction () amt d

(* Entrypoints *)

let mint (store : storage) (_ : unit) : storage = 
    if Tezos.get_amount () = 0tez then failwith ERRORS.zero_amount_being_locked
    else
        let lock_count = store.lock_count + 1n in
        let updated_ledger = Big_map.update (Tezos.get_sender (), lock_count) (Some 1n) store.ledger in
        let updated_locks = Big_map.update lock_count (Some (Tezos.get_amount ())) store.locks in
        { store with ledger = updated_ledger; locks = updated_locks; lock_count = lock_count; }

let withdraw (store : storage) (token_id : nat) : operation list * storage =
    match Big_map.find_opt token_id store.locks with
    | None -> failwith FA2_ERRORS.fa2_token_undefined
    | Some amt -> begin
        let sender = Tezos.get_sender () in
        if (get_balance store.ledger (Tezos.get_sender ()) token_id) = 0n then failwith ERRORS.not_authorised
        else (
            let updated_locks = Big_map.update token_id None store.locks in
            let updated_ledger = Big_map.update (sender, token_id) None store.ledger in
            [ return_tez amt ], 
            { store with ledger = updated_ledger; locks = updated_locks; }
        )
    end

(* Main *)

let main (action, store : parameter * storage) : return =
    match action with 
    | Mint -> ([], mint store ())
    | Transfer params -> ([], { store with ledger = transfer store.ledger store.operators params })
    | Balance_of params -> (balance_of store.ledger params, store)
    | Update_operators params -> ([], { store with operators = update_operators store.operators params })
    | Withdraw params -> withdraw store params

(* Token-metadata Offchain view *)

type token_metadata_value = {
  token_id : nat;
  token_info : (string, bytes) map;
}

(* Constant fields in bytes *)

(* string: 'Locker dNFT' *)
let name = 0x4c6f636b657220644e4654

(* string: 'LOCK' *)
let symbol = 0x4c4f434b

(* string: '0' *)
let decimals = 0x30

(* string: '.' *)
let point = 0x2e

(* string: 'https://image_url.com/thumbnail.png' *)
let thumbnail_uri = 0x68747470733a2f2f696d6167655f75726c2e636f6d2f7468756d626e61696c2e706e67

let token_metadata (token_id, store : nat * storage) : token_metadata_value = 
    match Big_map.find_opt token_id store.locks with
    | None -> failwith FA2_ERRORS.fa2_token_undefined
    | Some amt -> begin
        (* Fetch price of XTZ from harbinger oracle *)
        match ((Tezos.call_view "getPrice" "XTZ-USD" store.harbinger_address) : (timestamp * nat) option) with
        | None -> failwith ERRORS.invalid_view
        | Some (_, price) -> begin
            let amt_nat = (amt / 1mutez) in
            let whole_amt = amt_nat / 1_000_000n in
            let fractional_amt = Option.unopt (is_nat (amt_nat - (whole_amt * 1_000_000n))) in
            (* Build a 'floating point string' to represent locked amount *)
            let locked_amount = join_bytes [ (bytes_of_nat whole_amt); point; (bytes_of_nat fractional_amt); ] in
            (* Price granularity - 1_000_000 *)
            let value = (price * amt_nat) / 1_000_000n in
            let whole_value = value / 1_000_000n in
            let fractional_value = (Option.unopt (is_nat (value - (whole_value * 1_000_000n)))) / 10_000n in
            let locked_value = join_bytes [ (bytes_of_nat whole_value); point; (bytes_of_nat fractional_value); ] in
            let b_token_id = bytes_of_nat token_id in
            (* 
                Construct the SVG data URI (in bytes form) using the helper.
            *)
            let image_uri = build_svg b_token_id locked_amount locked_value in
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
    end