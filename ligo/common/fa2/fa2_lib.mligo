#if !FA2_LIB
#define FA2_LIB

#import "./fa2_errors.mligo" "FA2_ERRORS"

(* Common FA2 storage types *)

type ledger = ((address * nat), nat) big_map

type operator_key = [@layout:comb] {
    owner : address;
    operator : address;
    token_id : nat;
}

type operators = (operator_key, unit) big_map

(* Common FA2 parameter types *)

type transfer_txs = [@layout:comb] {
    to_ : address;
    token_id : nat;
    amount : nat;
} list

type transfer_params = [@layout:comb] {
    from_ : address;
    txs : transfer_txs;
} list

type balance_of_request = {
    owner : address;
    token_id : nat;
}

type balance_of_response = [@layout:comb] {
    request: {
        owner : address;
        token_id : nat;
    };
    balance: nat;
}

type balance_of_params = [@layout:comb] {
    requests: balance_of_request list;
    callback: (balance_of_response list) contract;
}

type update_operator_params = (
    | Add_operator of operator_key
    | Remove_operator of operator_key
) list


(* Utilities *)

let can_transfer (storage_operators : operators) (from_ : address) (token_id : nat) : bool =
    if Tezos.get_sender () = from_ then true 
    else let op_key = { owner = from_; operator = Tezos.get_sender (); token_id = token_id } in
    Big_map.mem op_key storage_operators 
     
let get_balance (storage_ledger : ledger) (account : address) (token_id : nat) : nat =
    match Big_map.find_opt (account, token_id) storage_ledger with
    | Some b -> b
    | None -> 0n

(* Auxillaries *)

let rec process_txs (storage_ledger : ledger) (storage_operators : operators) (from_ : address) (txs : transfer_txs) : ledger =
    match txs with 
    | [] -> storage_ledger
    | h::t -> begin
        if not (can_transfer storage_operators from_ h.token_id) then failwith FA2_ERRORS.fa2_not_operator
        else (
            let balance = get_balance storage_ledger from_ h.token_id in
            match is_nat (balance - h.amount) with
            | None -> failwith FA2_ERRORS.fa2_insufficient_balance
            | Some sender_balance -> begin
                let updated_ledger = Big_map.update (from_, h.token_id) (Some sender_balance) storage_ledger in
                let receiver_balance = (get_balance storage_ledger h.to_ h.token_id) + h.amount in
                let updated_ledger = Big_map.update (h.to_, h.token_id) (Some receiver_balance) updated_ledger in
                process_txs updated_ledger storage_operators from_ t  
            end
        )
    end


let rec transfer_aux (storage_ledger : ledger) (storage_operators : operators) (params : transfer_params) : ledger = 
    match params with
    | [] -> storage_ledger
    | h::t -> transfer_aux (process_txs storage_ledger storage_operators h.from_ h.txs) storage_operators t

let rec update_operators_aux (storage_operators : operators) (params : update_operator_params) : operators =
    match params with
    | [] -> storage_operators
    | h::t -> begin
        let updated_operators = match h with
        | Add_operator op_key -> if Tezos.get_sender () <> op_key.owner 
            then failwith FA2_ERRORS.fa2_not_owner
            else Big_map.update op_key (Some ()) storage_operators
        | Remove_operator op_key -> if Tezos.get_sender () <> op_key.owner 
            then failwith FA2_ERRORS.fa2_not_owner
            else Big_map.update op_key None storage_operators
        in update_operators_aux updated_operators t 
    end

let rec balance_of_aux (storage_ledger : ledger) (requests : balance_of_request list) (response : balance_of_response list) : balance_of_response list =
    match requests with
    | [] -> response
    | h::t -> let balance = get_balance storage_ledger h.owner h.token_id in
        balance_of_aux storage_ledger t ({ request = h; balance = balance }::response)

(* Common FA2 entrypoints *)

let transfer (storage_ledger : ledger) (storage_operators : operators) (params : transfer_params) : ledger =
    transfer_aux storage_ledger storage_operators params

let update_operators (storage_operators : operators) (params : update_operator_params) : operators =
    update_operators_aux storage_operators params

let balance_of (storage_ledger : ledger) (params : balance_of_params) : operation list = 
    let response = balance_of_aux storage_ledger params.requests [] in
    [Tezos.transaction response 0tez params.callback]

#endif