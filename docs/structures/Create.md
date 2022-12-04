# 🧱 Create Structure

- Create structure allows for more naturally dynamic token metadata similar to [Point](), but instead of building an external link to a TZIP-21 Json, it builds and serves the JSON through an off-chain view.
- It is useful when most of the fields in the metadata JSON are static or the off-chain datastore needs to be simplified. For instance, if a token has fixed 'symbol' and 'decimals' and a static thumbnailUri, only fields like artifactUri and displayUri need to be dynamically generated. These may be an external link or an SVG (as shown in [SVG]() Structure).
- The state of a dNFT is defined by two properties `prop_1` and `prop_2`, which they can be updated through the `change_state` entrypoint.
- The dynamically created artifact URI takes the form `<base url>/<prop_1>/<prop_2>`.

The smart contract code for Create structure can be found at [/smartpy/contracts/create.py](https://github.com/AnshuJalan/tezos-dNFT/blob/master/smartpy/contracts/create.py) and [/ligo/contracts/create.mligo](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/contracts/create.mligo).

## When can you use Create structure?

Create structure is useful when:

- Token metadata depends on a some parameters that are present in the contract's storage.
- Only some fields of the token metadata are dynamic, while the rest are static.
- The external artifact storage can be configured such that it can be accessed through an organised URI like `<base url>/<prop_1>/<prop_2>`.

### Example

A game character dNFT where only the `artifactUri` and `displayUri` of the metadata JSON are dynamic. The character might have two properties `weapon` and `lives`. Based on the values of the properties different artifacts are stored on a server such that they can be access through a URI of the form `<base_url>/<weapon>/<lives>`.

An example is provided at [/smartpy/examples/game2.py](https://github.com/AnshuJalan/tezos-dNFT/blob/master/smartpy/examples/game2.py) and [/ligo/examples/game2.mligo](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/examples/game2.mligo).

## Existing aspects you might want to change

- Admin based minting
  - You may want to customise the `mint` entrypoint and make minting permissionless depending on your use-case.
- `change_state` entrypoint
  - This is a reference entrypoint and you may implement your own entrypoint(s) that change the state of the token.
- `prop_1` and `prop_2` state properties and their type (`nat`)
  - The properties are only for reference and you may implement your own set of properties with their own types.
- The form of artifact URI
  - The form `<base url>/<prop_1>/<prop_2>` is entirely for reference. The way your URI looks depends on how the artifact for your dNFT is stored.
