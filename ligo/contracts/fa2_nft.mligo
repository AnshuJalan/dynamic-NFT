#include "../common/fa2/fa2_lib.mligo"

(* FA2 NFT types *)

type storage = {
    ledger : ledger;
    operators : operators;
}

type parameter =
    | Transfer of transfer_params
    | Balance_of of balance_of_params
    | Update_operators of update_operator_params

type return = operation list * storage

(* Main *)

let main (action, store : parameter * storage) : return =
    match action with 
    | Transfer params -> ([], { store with ledger = transfer store.ledger store.operators params })
    | Balance_of params -> (balance_of store.ledger params, store)
    | Update_operators params -> ([], { store with operators = update_operators store.operators params })