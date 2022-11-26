(* 
  This is a dummy contract to mimic harbinger oracle in the tests
 *)

type storage = {
    price: nat
}

[@view] let getPrice (_assetId, store : string * storage) : timestamp * nat =
    Tezos.get_now (), store.price

let main ((), store: unit * storage) : operation list * storage = [], store