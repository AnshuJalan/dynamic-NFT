# 🔮 Oracle Structure

- Oracle structure allows for fetching a `state` from an on-chain oracle and dynamically building the token metadata using the retrieved values. The
  metadata is then served through an offchain view.
- It's useful when the metadata depends on some off-chain data that needs to be put on-chain in a decentralised way through an oracle.
- The state of a dNFT is defined by two properties `prop_1` and `prop_2`, both of which come from the oracle.
- The `artifactUri` and `displayUri` are dynamically created and they take the form `<base url>/<prop_1>/<prop_2>`.

The smart contract code for Oracle structure can be found at [/smartpy/contracts/oracle.py](https://github.com/AnshuJalan/tezos-dNFT/blob/master/smartpy/contracts/oracle.py) and [/ligo/contracts/oracle.mligo](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/contracts/oracle.mligo).

A dummy oracle is provided at [/ligo/contracts/helpers/state_oracle.mligo](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/contracts/helpers/state_oracle.mligo) and [/smartpy/contracts/helpers/state_oracle.py](https://github.com/AnshuJalan/tezos-dNFT/blob/master/smartpy/contracts/helpers/state_oracle.py).

## When can you use Oracle structure?

Oracle structure is useful when:

- Token metadata depends on a some external parameters that need to brought into the contract through an oracle.
- The external artifact or metadata storage can be configured such that it can be accessed through an organised URI like `<base url>/<prop_1>/<prop_2>`.

### Example

A tokenised Defi position NFT which displays the market value of the collateral in the position. Here the price of the collateral is taken from an oracle and used to create the artifact or metadata URI.

A related example is given at [/smartpy/examples/locker.py](https://github.com/AnshuJalan/tezos-dNFT/blob/master/smartpy/examples/locker.py) and [/ligo/examples/locker.mligo](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/examples/locker.mligo).

## Existing aspects you might want to change

- Admin based minting
  - You may want to customise the `mint` entrypoint and make minting permissionless depending on your use-case.
- Dummy oracle
  - The oracle is provided for reference and you would want to modify the calling of oracle view and type of data received, based on your application.
  - You may also decide on what kind of data is the oracle going to provide. As shown in the structure, it might be a state that is used to create field values in metadata JSON or it may be the entire JSON itself that is returned by the oracle.
