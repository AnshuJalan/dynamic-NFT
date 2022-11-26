#include "./svg_example_data.mligo"
#include "../common/utils.mligo"

(*
    Builds an SVG by concatenating different sections of the data URI.
    Final sample output given at ./samples/svg_example.svg
*)
let build_svg (token_id : bytes) (locked_amount : bytes) (locked_value : bytes) : bytes = 
    join_bytes [ data_1; locked_amount; data_2; locked_value; data_3; token_id; data_4; token_id; data_5; ]
