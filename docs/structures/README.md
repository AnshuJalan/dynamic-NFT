# 🏗️ Understanding Structures

**Structures** are essentially smart contract code blueprints to build different types of dNFT. They encompass different metadata storage patterns, metadata source (eg: an external oracle) and complexity of application. There are a total of 5 dNFT structures:

- [Brute structure](https://github.com/AnshuJalan/tezos-dNFT/blob/master/docs/structures/Brute.md) - As the name suggests, a dNFT using the Brute structure requires a manual updation of the metadata.
- [Point structure](https://github.com/AnshuJalan/tezos-dNFT/blob/master/docs/structures/Point.md) - More flexible than Brute, this one allows for dynamically creating a URI that _points_ to the metadata.
- [Create structure](https://github.com/AnshuJalan/tezos-dNFT/blob/master/docs/structures/Create.md) - Adds a pinch of efficiency to Point by avoiding repetition of static fields in the metadata.
- [Oracle structure](https://github.com/AnshuJalan/tezos-dNFT/blob/master/docs/structures/Oracle.md) - Goes a step ahead and allows for dynamic metadata based on some external state received from an _oracle_.
- [SVG structure](https://github.com/AnshuJalan/tezos-dNFT/blob/master/docs/structures/SVG.md) - The most ambitious of all, this enables the dynamic creation of an SVG graphic for the NFT metadata, entirely on the chain.

The code for the different structures are available at [/smartpy/contracts](https://github.com/AnshuJalan/tezos-dNFT/tree/master/smartpy/contracts) and [/ligo/contracts](https://github.com/AnshuJalan/tezos-dNFT/tree/master/ligo/contracts).

## How to choose a structure?

The concise description of the structures given above already provide a brief idea on where they can be used. However, if you need a general set of rules to pick a certain structure, you can base your choice on the three above mentioned aspects - metadata storage pattern, source of metadata and the complexity of your application:

- If your application requires updation of metadata in rare cases, you can avoid complexity and go for the simple `Brute` structure.
  - _Eg:_ Tokenised real estate.
- If your dNFT metadata depends on some parameters that are present in the contract's storage, you can go for either `Point` or `Create` structure.
  - If most fields of your metadata JSON change during an updation, go for `Point`.
  - If only fields are dynamic and the rest are static, go for `Create` for efficiency.
  - _Eg:_ Game characters that have structural updates like change of outfit, weapon etc.
- If your dNFT metadata depends on some parameters that need to brought into the contract from an external oracle, go for `Oracle` structure.
  - _Eg:_ A dNFT that shows the price of an asset
- If your primary artifact is an image that display data taken from the contract's storage, you may go for `SVG` structure.
  - _Eg:_ Playing cards represented as a dNFT. The card shows certain attributes of the entity represented by it.

You may very well choose more than one structure for your dNFT, For instance, you may be taking data from an external oracle and then displaying it on an SVG based graphic (as shown in the [Locker](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/examples/locker.mligo) example).

## Using structures to make your own dNFT

Once you have selected your structure, you need to understand that these are not templates. These are reference units for incorporating a certain metadata storage pattern, metadata source or simply a technique to create a dNFT.

There are some aspects of every structure that the developer might want to change depending on their use-case:

- Admin based minting
  - The NFT is every structure is being minted by an admin address that is stored in the contract. The developer may want to switch to permissionless minting if needed.
- The `states big_map` in the storage with `prop_1` and `prop_2` being the fields on the value side.
  - This is just for reference and you will probably have your own set of state fields.
- `change_state` entrypoint
  - Another aspect that is only for reference. You would need to implement your own set of entrypoints to manipulate the state.
- `IPFS` or `http` based external links for metadata
  - You are not bound to use http or IPFS based links for your metadata. A [variety of options](https://gitlab.com/tezos/tzip/-/blob/master/proposals/tzip-16/tzip-16.md#metadata-uris) are available for the same.
- Limited fields in the metadata JSON
  - You may add more fields in the metadata JSON besides the ones mentioned [here](https://github.com/AnshuJalan/tezos-dNFT/tree/master/docs#rich-metadata)

Refer to the examples at [ligo/examples](https://github.com/AnshuJalan/tezos-dNFT/tree/master/ligo/examples) and [/smartpy/examples](https://github.com/AnshuJalan/tezos-dNFT/tree/master/smartpy/examples) to understand how these structures can be used.
