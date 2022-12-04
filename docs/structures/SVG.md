# 📊 SVG Structure

- SVG structure is an extension of Create with the difference that the `artifactUri` and `displayUri` are an [SVG data URI](https://en.wikipedia.org/wiki/Data_URI_scheme) that is dynamically generated in the token_metadata off-chain view.
- This is useful when the artifact is an SVG, or can possibly be converted to an SVG and save the overheads of separately maintaining off-chain data.

The smart contract code for SVG structure can be found at [/smartpy/contracts/svg.py](https://github.com/AnshuJalan/tezos-dNFT/blob/master/smartpy/contracts/svg.py) and [/ligo/contracts/svg.mligo](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/contracts/svg.mligo).

## When can you use SVG structure?

SVG structure is useful when:

- The primary artifact is an SVG image that displays some off-chain or on-chain data.
- The artifacts of different NFTs can be paramterised based on the data to be shown. For example, different background colors across different ranges of data.

### Example

- A card based fantasy game NFT. The card represents a character and shows it's attributes.
- An extension of the Defi position example given in [Oracle]() structure, with the artifact being an SVG.

The example given at [/smartpy/examples/locker.py](https://github.com/AnshuJalan/tezos-dNFT/blob/master/smartpy/examples/locker.py) and [/ligo/examples/locker.mligo](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/examples/locker.mligo) combine Oracle and SVG structure.

## Important tools

These are some tools that were used in SVG structure.

- SVG Minifier: https://www.svgminify.com/
- SVG to data URI convertor: https://thehelpertools.com/svgtodataurl
- String to Bytes convertor: https://onlinestringtools.com/convert-string-to-bytes

## Existing aspects you might want to change

- Admin based minting
  - You may want to customise the `mint` entrypoint and make minting permissionless depending on your use-case.
- `change_state` entrypoint
  - This is a reference entrypoint and you may implement your own entrypoint(s) that change the state of the token.
- `prop_1` and `prop_2` state properties and their type (`nat`)
  - The properties are only for reference and you may implement your own set of properties with their own types.
- The form of the data URI
  - The data URI depends entirely on what your SVG artifact looks like.
