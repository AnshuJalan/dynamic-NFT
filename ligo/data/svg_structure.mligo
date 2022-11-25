#include "./svg_structure_data.mligo"
#include "../common/utils.mligo"

(*
    Builds an SVG by concatenating different sections of the data URI.
    Final sample output given at ./samples/svg_structure.svg
*)
let build_svg (token_id : bytes) (prop_sum : bytes) : bytes = 
    join_bytes [ data_1; token_id; data_2; prop_sum; data_3; ]
