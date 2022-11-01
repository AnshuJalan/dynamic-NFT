(* Types *)

type operator_key = [@layout:comb] {
    owner : address;
    operator : address;
    token_id : nat;
}

type operator_params = (
    | Add_operator of operator_key 
    | Remove_operator of operator_key
) list 

type storage = {
    ledger : (address * nat, nat) big_map;
    operators : (operator_key, unit) big_map;
}

type transfer_group = [@layout:comb] { 
    to_ : address; 
    token_id : 
    nat; amount : nat; 
} list 

type transfer_params = { from_ : address; txs : transfer_group } list

type balance_of_cb_param = [@layout:comb] {  
    request : { owner : address; token_id : nat };
    balance : nat;
} 

type balance_of_params = [@layout:comb] {
    requests : { owner : address; token_id : nat } list;
    callback : (balance_of_cb_param list) contract;
}

type parameter = 
    | Transfer of transfer_params
    | Balance_of of balance_of_params
    | Update_operators of operator_params

type return = operation list * storage

(* Utilities *)

let can_transfer (store : storage) (from_ : address) (token_id : nat) : bool = 
    if Tezos.get_sender () = from_ then true
    else match Big_map.find_opt { owner = from_; operator = Tezos.get_sender (); token_id = token_id; } store.operators with
    | None -> false
    | Some _ -> true

let get_balance (store : storage) (addr : address) (token_id : nat) : nat =
    match Big_map.find_opt (addr, token_id) store.ledger with
    | None -> 0n
    | Some b -> b

(* Transfer Entrypoint *)

let rec process_transfers (store : storage) (from_ : address) (tg : transfer_group) : storage =
    match tg with 
    | [] -> store
    | h::t -> begin
        if not (can_transfer store from_ h.token_id) then failwith "FA2_NOT_OPERATOR"
        else (
            match is_nat((get_balance store from_ h.token_id) - h.amount) with
            | None -> failwith "FA2_INSUFFICIENT_BALANCE"
            | Some balance_left -> 
                let ledger = Big_map.update (from_, h.token_id) (Some balance_left) store.ledger in 
                let ledger = Big_map.update (h.to_, h.token_id) (Some ((get_balance store h.to_ h.token_id) + h.amount)) ledger in
                process_transfers { store with ledger = ledger } from_ t
        )
    end

let rec transfer_aux (store : storage) (params : transfer_params) : storage = 
    match params with 
    | [] -> store
    | h::t -> transfer_aux (process_transfers store h.from_ h.txs) t

let transfer (store, params : storage * transfer_params) = transfer_aux store params

(* Balance_of Entrypoint *)

let rec balance_of_aux (store : storage) (requests: { owner : address; token_id : nat } list) (cb_params : balance_of_cb_param list) : balance_of_cb_param list =
    match requests with
    | [] -> cb_params
    | h::t -> balance_of_aux store t ({ request = h; balance = get_balance store h.owner h.token_id; }::cb_params)

let balance_of (store, params : storage * balance_of_params) : return =
    let txn_params = balance_of_aux store params.requests [] in
    ([Tezos.transaction txn_params 0mutez params.callback], store)

(* Update_operators Entrypoint *)

let rec update_operators_aux (store : storage) (params : operator_params) : storage = 
    match params with 
    | [] -> store
    | h::t -> begin
        let operators = match h with
            | Add_operator op -> if op.owner <> Tezos.get_sender () 
                then failwith "FA2_NOT_OWNER"
                else Big_map.update op (Some unit) store.operators
            | Remove_operator op -> if op.owner <> Tezos.get_sender () 
                then failwith "FA2_NOT_OWNER" 
                else Big_map.update op None store.operators
        in update_operators_aux { store with operators = operators } t
    end
        

let update_operators (store, params : storage * operator_params) : storage =
    update_operators_aux store params

(* Main *)

let main (action, store : parameter * storage) : return =
    match action with 
    | Transfer params -> ([], transfer (store, params))
    | Balance_of params -> balance_of (store, params)
    | Update_operators params -> ([], update_operators (store, params))