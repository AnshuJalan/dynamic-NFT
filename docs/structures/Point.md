# 👉 Point Structure

- Point structure allows more naturally dynamic token metadata through an `off-chain view` that dynamically creates an external metadata URI (that points to a TZIP-21 json) using values from the contract's storage.
- The state of a dNFT is defined by two properties `prop_1` and `prop_2`, which they can be updated through the `change_state` entrypoint.
- The dynamically created metadata URI takes the form `<metadata url>/<prop_1>/<prop_2>`.

The smart contract code for Point structure can be found at [/smartpy/contracts/point.py](https://github.com/AnshuJalan/tezos-dNFT/blob/master/smartpy/contracts/point.py) and [/ligo/contracts/point.mligo](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/contracts/point.mligo).

## When can you use Point structure?

Point structure is useful when:

- Token metadata depends on a some parameters that are present in the contract's storage.
- Most fields of the metadata JSON change during every update.
- The external metadata storage can be configured such that it can be accessed through an organised URI like `<metadata url>/<prop_1>/<prop_2>`.

### Example

A game character dNFT. The character might have two properties `weapon` and `lives`. Based on the values of the properties different metadata JSON are stored on a server such that they can be access through a URI of the form `<metadata_url>/<weapon>/<lives>`.

An example is provided at [/smartpy/examples/game1.py](https://github.com/AnshuJalan/tezos-dNFT/blob/master/smartpy/examples/game1.py) and [/ligo/examples/game1.mligo](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/examples/game1.mligo).

## Existing aspects you might want to change

- Admin based minting
  - You may want to customise the `mint` entrypoint and make minting permissionless depending on your use-case.
- `change_state` entrypoint
  - This is a reference entrypoint and you may implement your own entrypoint(s) that change the state of the token.
- `prop_1` and `prop_2` state properties and their type (`nat`)
  - The properties are only for reference and you may implement your own set of properties with their own types.
- The form of metadata URI
  - The form `<metadata url>/<prop_1>/<prop_2>` is entirely for reference. The way your URI looks depends on how the metadata for your dNFT is stored.
