import smartpy as sp

# Builds an SVG by concatenating different sections of the data URI
# Final sample output given at ../../assets/svg_structure.svg
def build_svg(params):
    sp.set_type(params, sp.TRecord(token_id=sp.TBytes, prop_sum=sp.TBytes))

    return (
        sp.utils.bytes_of_string(DATA_1)
        + params.token_id
        + sp.utils.bytes_of_string(DATA_2)
        + params.prop_sum
        + sp.utils.bytes_of_string(DATA_3)
    )


# Different parts of an SVG data URI
DATA_1 = "data:image/svg+xml;charset=UTF-8,%3c?xml version='1.0' encoding='UTF-8'?%3e%3csvg width='67.733mm' height='67.733mm' version='1.1' viewBox='0 0 67.733 67.733' xmlns='http://www.w3.org/2000/svg' xmlns:cc='http://creativecommons.org/ns%23' xmlns:dc='http://purl.org/dc/elements/1.1/' xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns%23'%3e%3cmetadata%3e%3crdf:RDF%3e%3ccc:Work rdf:about=''%3e%3cdc:format%3eimage/svg+xml%3c/dc:format%3e%3cdc:type rdf:resource='http://purl.org/dc/dcmitype/StillImage'/%3e%3cdc:title/%3e%3c/cc:Work%3e%3c/rdf:RDF%3e%3c/metadata%3e%3cg transform='translate(614.55 35.691)'%3e%3cg transform='matrix(.1959 0 0 .1959 -494.16 -28.699)'%3e%3crect x='-614.55' y='-35.691' width='345.76' height='345.76' fill='%2306f' stroke-width='0'/%3e%3cg transform='translate(0 1.7093)' font-family='Arial' font-size='35.184px' stroke-width='.8796'%3e%3ctext x='-524.93768' y='46.574394' style='line-height:1.25' xml:space='preserve'%3e%3ctspan x='-524.93768' y='46.574394' fill='%23ffffff' font-family='Arial' font-weight='bold' stroke-width='.8796'%3eTOKEN ID%3c/tspan%3e%3c/text%3e%3ctext x='-458.55399' y='103.45695' style='line-height:1.25' xml:space='preserve'%3e%3ctspan x='-458.55399' y='103.45695' fill='%23ffffff' font-family='Arial' stroke-width='.8796'%3e"

DATA_2 = "%3c/tspan%3e%3c/text%3e%3ctext x='-535.28845' y='192.68449' style='line-height:1.25' xml:space='preserve'%3e%3ctspan x='-535.28845' y='192.68449' fill='%23ffffff' font-family='Arial' font-weight='bold' stroke-width='.8796'%3ePROP SUM%3c/tspan%3e%3c/text%3e%3ctext x='-451.31415' y='249.56705' style='line-height:1.25' xml:space='preserve'%3e%3ctspan x='-451.31415' y='249.56705' fill='%23ffffff' font-family='Arial' stroke-width='.8796'%3e"

DATA_3 = "%3c/tspan%3e%3c/text%3e%3c/g%3e%3c/g%3e%3c/g%3e%3c/svg%3e"

# Completed SVG with token-id 21 and prop-sum 11
SAMPLE_BYTES = sp.bytes(
    "0x646174613a696d6167652f7376672b786d6c3b636861727365743d5554462d382c2533633f786d6c2076657273696f6e3d27312e302720656e636f64696e673d275554462d38273f2533652533637376672077696474683d2736372e3733336d6d27206865696768743d2736372e3733336d6d272076657273696f6e3d27312e31272076696577426f783d273020302036372e3733332036372e3733332720786d6c6e733d27687474703a2f2f7777772e77332e6f72672f323030302f7376672720786d6c6e733a63633d27687474703a2f2f6372656174697665636f6d6d6f6e732e6f72672f6e732532332720786d6c6e733a64633d27687474703a2f2f7075726c2e6f72672f64632f656c656d656e74732f312e312f2720786d6c6e733a7264663d27687474703a2f2f7777772e77332e6f72672f313939392f30322f32322d7264662d73796e7461782d6e73253233272533652533636d657461646174612533652533637264663a52444625336525336363633a576f726b207264663a61626f75743d272725336525336364633a666f726d6174253365696d6167652f7376672b786d6c2533632f64633a666f726d617425336525336364633a74797065207264663a7265736f757263653d27687474703a2f2f7075726c2e6f72672f64632f64636d69747970652f5374696c6c496d616765272f25336525336364633a7469746c652f2533652533632f63633a576f726b2533652533632f7264663a5244462533652533632f6d6574616461746125336525336367207472616e73666f726d3d277472616e736c617465283631342e35352033352e363931292725336525336367207472616e73666f726d3d276d6174726978282e3139353920302030202e31393539202d3439342e3136202d32382e36393929272533652533637265637420783d272d3631342e35352720793d272d33352e363931272077696474683d273334352e373627206865696768743d273334352e3736272066696c6c3d2725323330366627207374726f6b652d77696474683d2730272f25336525336367207472616e73666f726d3d277472616e736c617465283020312e37303933292720666f6e742d66616d696c793d27417269616c2720666f6e742d73697a653d2733352e313834707827207374726f6b652d77696474683d272e38373936272533652533637465787420783d272d3532342e39333736382720793d2734362e35373433393427207374796c653d276c696e652d6865696768743a312e32352720786d6c3a73706163653d27707265736572766527253365253363747370616e20783d272d3532342e39333736382720793d2734362e353734333934272066696c6c3d272532336666666666662720666f6e742d66616d696c793d27417269616c2720666f6e742d7765696768743d27626f6c6427207374726f6b652d77696474683d272e3837393627253365544f4b454e2049442533632f747370616e2533652533632f746578742533652533637465787420783d272d3435382e35353339392720793d273130332e343536393527207374796c653d276c696e652d6865696768743a312e32352720786d6c3a73706163653d27707265736572766527253365253363747370616e20783d272d3435382e35353339392720793d273130332e3435363935272066696c6c3d272532336666666666662720666f6e742d66616d696c793d27417269616c27207374726f6b652d77696474683d272e383739362725336532312533632f747370616e2533652533632f746578742533652533637465787420783d272d3533352e32383834352720793d273139322e363834343927207374796c653d276c696e652d6865696768743a312e32352720786d6c3a73706163653d27707265736572766527253365253363747370616e20783d272d3533352e32383834352720793d273139322e3638343439272066696c6c3d272532336666666666662720666f6e742d66616d696c793d27417269616c2720666f6e742d7765696768743d27626f6c6427207374726f6b652d77696474683d272e383739362725336550524f502053554d2533632f747370616e2533652533632f746578742533652533637465787420783d272d3435312e33313431352720793d273234392e353637303527207374796c653d276c696e652d6865696768743a312e32352720786d6c3a73706163653d27707265736572766527253365253363747370616e20783d272d3435312e33313431352720793d273234392e3536373035272066696c6c3d272532336666666666662720666f6e742d66616d696c793d27417269616c27207374726f6b652d77696474683d272e383739362725336531312533632f747370616e2533652533632f746578742533652533632f672533652533632f672533652533632f672533652533632f737667253365"
)
