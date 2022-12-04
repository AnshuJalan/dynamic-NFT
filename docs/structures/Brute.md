# 💪 Brute Structure

- Brute structure is where the entirety of token metadata is stored in the contract's storage itself in a `token_metadata` `big_map` as specified in TZIP-12.
- Metdata updates are done manually through an entrypoint (`update_token_metadata` in the structure contract) by an `admin`.

The smart contract code for Brute structure can be found at [/smartpy/contracts/brute.py](https://github.com/AnshuJalan/tezos-dNFT/blob/master/smartpy/contracts/brute.py) and [/ligo/contracts/brute.mligo](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/contracts/brute.mligo).

## When can you use Brute structure?

Brute structure is useful when:

- Token metadata updates are infrequent.
- Token metadata depends entirely on data stored on off-chain servers or its generation requires extensive computation that is not possible on-chain.

### Example

A real estate tokenised as a dNFT right from the get go. The dNFT metadata fields change depending on the initial construction status, renovations and any damage that may occur with time. It will usually be some administrative party that has all the data related to the real estate stored on its servers that administers the dNFT smart contract.

## Existing aspects you might want to change

- Admin based minting
  - You may want to customise the `mint` entrypoint and make minting permissionless depending on your use-case.
- `update_token_metadata` entrypoint
  - This is a reference entrypoint and you may implement your own entrypoint(s) that update the token metadata.
  - You may even do permissionless updates by integrating a form of zk-proof for running the off-chain computation required to generate the metadata.
