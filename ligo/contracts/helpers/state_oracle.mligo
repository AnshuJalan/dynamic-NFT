(* 
  This is a dummy contract to help return a specified state for oracle structure
  in the tests.
 *)

type state = {
    prop_1 : nat;
    prop_2 : nat;
}

type storage = {
    state : state;
}

[@view] let get_state (_token_id, store : nat * storage) : state =
    store.state

let main ((), store: unit * storage) : operation list * storage = [], store