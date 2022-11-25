(*               Game character dNFT based on Point Structure

  A simple (and kinda pointless) game where characters are represented using
  a dNFT. Each character has two dynamic properties, lives and weapon. A character
  can switch its weapon and attack other characters. Each weapon inflicts a
  different level of damage.

  The two properties are used to dynamically generate a URI that points to the
  token metadata. The graphic of the character is expected to change, based on
  the lives left and weapon in hand.
 
  NOTE: 'player' and 'character' are used interchangeably in the code & comments.
*)

#include "../common/utils.mligo"
#include "../common/constants.mligo"
#include "../common/fa2/fa2_lib.mligo"
#import "../common/errors.mligo" "ERRORS"
#import "../common/fa2/fa2_errors.mligo" "FA2_ERRORS"

(* Game 1 storage types *)

type weapon = 
    | Sword
    | Pistol
    | Rifle

type player_state = {
    lives : nat;
    weapon : weapon;
}

type player_states = (nat, player_state) big_map

type storage = {
    admin : address;
    ledger : ledger;
    operators : operators;
    player_states : player_states;
    metadata: (string, bytes) big_map;
}

(* Game 1 parameter types *)

type mint_params = { 
    address : address;
    token_id : nat;
}

type change_weapon_params = {
    token_id : nat;
    weapon : weapon;
}

type attack_params = {
    attacker_id : nat;
    victim_id : nat;
}

type parameter =
    | Mint of mint_params
    | Transfer of transfer_params
    | Balance_of of balance_of_params
    | Update_operators of update_operator_params
    | Change_weapon of change_weapon_params
    | Attack of attack_params

type return = operation list * storage

(* Entrypoints *)

let mint (store : storage) (params : mint_params) : storage =
    if Tezos.get_sender () <> store.admin then failwith ERRORS.not_authorised
    else if Big_map.mem params.token_id store.player_states then failwith ERRORS.token_id_already_exists
    else
        let state = { lives = 3n; weapon = Sword; } in
        let updated_ledger = Big_map.update (params.address, params.token_id) (Some 1n) store.ledger in
        let updated_states = Big_map.update params.token_id (Some state) store.player_states in
        { store with ledger = updated_ledger; player_states = updated_states; }

(* 
    Allows a player to switch between the 3 weapons.
*)
let change_weapon (store : storage) (params : change_weapon_params) : player_states =
    match Big_map.find_opt params.token_id store.player_states with
    | None -> failwith FA2_ERRORS.fa2_token_undefined
    | Some s -> begin
        if (get_balance store.ledger (Tezos.get_sender ()) params.token_id) = 0n then failwith ERRORS.not_authorised
        else Big_map.update params.token_id (Some  { s with weapon = params.weapon; }) store.player_states
    end

(* 
    Using `attack` one player can attack another using the current in-hand weapon.
    Damage inflicted: Sword -> 1, Pistol -> 2, Rifle -> 3
*)
let attack (store : storage) (params : attack_params) : player_states =
    let attacker = Big_map.find_opt params.attacker_id store.player_states in
    let victim = Big_map.find_opt params.victim_id store.player_states in
    match (attacker, victim) with
    | Some sa, Some sv -> begin
        if (get_balance store.ledger (Tezos.get_sender ()) params.attacker_id) = 0n then failwith ERRORS.not_authorised
        else if sv.lives = 0n then failwith ERRORS.victim_already_dead 
        else (
            let damage = match sa.weapon with Sword -> 1n | Pistol -> 2n | Rifle -> 3n in
            let lives_left = match is_nat (sv.lives - damage) with None -> 0n | Some l -> l in
            Big_map.update params.victim_id (Some { sv with lives = lives_left; }) store.player_states
        )
    end
    | _ -> failwith FA2_ERRORS.fa2_token_undefined   

(* Main *)

let main (action, store : parameter * storage) : return =
    match action with 
    | Mint params -> ([], mint store params)
    | Transfer params -> ([], { store with ledger = transfer store.ledger store.operators params })
    | Balance_of params -> (balance_of store.ledger params, store)
    | Update_operators params -> ([], { store with operators = update_operators store.operators params })
    | Change_weapon params -> ([], { store with player_states = change_weapon store params })
    | Attack params -> ([], { store with player_states = attack store params })

(* Token-metadata Offchain view *)

type token_metadata_value = {
  token_id : nat;
  token_info : (string, bytes) map;
}

let token_metadata (token_id, store : nat * storage) : token_metadata_value = 
    match Big_map.find_opt token_id store.player_states with
    | None -> failwith FA2_ERRORS.fa2_token_undefined
    | Some s -> begin
        let b_weapon = bytes_of_nat (match s.weapon with Sword -> 0n | Pistol -> 1n | Rifle -> 2n) in
        let b_lives = bytes_of_nat s.lives in
        let b_token_id = bytes_of_nat token_id in
        (* 
            Contruct a URI (in bytes form) that points to a TZIP-21 based metadata JSON.

            The metadata URI generated is a dummy one. To get a better idea, here's
            what the image that the 'artifactUri' for token-id 21, with 2 lives left and pistol
            as a weapon may look like:
            >> https://gateway.pinata.cloud/ipfs/QmdxHSsGvT6WwYZz4k331C7HpxTiJArv7BwJQj5GahZJoZ
            A more well-made graphic will possibly include a figurine with a dynamic weapon
            and changing body structure based on lives left.
        *)
        let metadata_uri = join_bytes [ metadata_url; slash; b_lives; slash; b_weapon; slash; b_token_id; ] in
        { token_id = token_id; token_info = Map.literal [ ("", metadata_uri) ]; }
    end