# 📑 Documentation

Developers who are new to writing smart contracts on Tezos should start with [Get Started (Smartpy)]() or [Get Started (LIGO)](), depending on the language of choice and then head back to this page and continue reading. If you are accustomed to Tezos contracts, but new to NFTs - it would be nice to give a quick read to the content below to understand the basics of how NFT metadata is represented on Tezos.

For those who are hacking away NFT contracts for a while, you are ready to jump straight to [Understanding Stuctures]().

## What good is dynamic NFT metadata?

The metadata is what gives the NFT meaning. An NFT can represent any unique digital or bodily asset - a piece of art, music, real estate etc. This representation is brought about by the metadata, usually through a set of key-value pairs in JSON format.

Often the NFT represents an entity that evolves over time. Lets say an NFT representing a game character - In most games, the character can be upgraded across levels. It can be given new weapons, new outfits and may be a cool tattoo! In such a case the graphic in the metadata must be updated to display the new look of the character. Thus, we need dynamic NFTs!

## NFTs on Tezos

NFT smart contracts on Tezos follow the **FA2 standard** defined in [TZIP-12](https://gitlab.com/tezos/tzip/-/blob/master/proposals/tzip-12/tzip-12.md). It defines the mandatory entrypoints and the pattern of storing and serving the token metadata.

An FA2 interface library is provided at [/ligo/common/fa2/fa2_lib.mligo](https://github.com/AnshuJalan/tezos-dNFT/blob/master/ligo/common/fa2/fa2_lib.mligo) and [/smartpy/common/fa2/fa2_lib.py](https://github.com/AnshuJalan/tezos-dNFT/blob/master/smartpy/common/fa2/fa2_lib.py).

### Metadata standard

According to TZIP-12, there are [basic and custom](https://gitlab.com/tezos/tzip/-/blob/master/proposals/tzip-12/tzip-12.md#token-metadata-storage-access) methods to store and access token metadata:

- **Basic:** Store the values in a big-map annotated %token_metadata of type `(big_map nat (pair (nat %token_id) (map %token_info string bytes)))`.

- **Custom:** Provide a token_metadata `offchain-view` which takes as parameter the `nat token-id` and returns the `(pair (nat %token_id) (map %token_info string bytes))` value.

For dynamic NFTs, the custom method of using an `offchain-view` is much more relevant as it allows us to form the metadata JSON based on a set of parameters. Developers must read through the technique of creating an off-chain view as specified in [TZIP-16](https://gitlab.com/tezos/tzip/-/blob/master/proposals/tzip-16/tzip-16.md#semantics-of-off-chain-views).

### Rich Metadata

The metadata JSON needs a variety of standardised fields to clearly express what the underlying NFT represents. These fields are specific in [TZIP-21](https://gitlab.com/tezos/tzip/-/blob/master/proposals/tzip-21/tzip-21.md), the **rich metadata** specification.

In repo, we will mostly be dealing with the following fields:

- `name` **(string)**
  - Title of the token.
- `symbol` **(string)**
  - Symbol identifier for the token. Mostly used by wallets.
- `decimals` **(integer)**
  - 0 for NFTs.
- `artifactUri` **(string)**
  - A URI to the actual digital asset.
- `displayUri` **(string)**
  - A URI to an image for the asset. This is shown in the top-level cards on NFT marketplaces.
- `thumbnailUri` **(string)**
  - A scaled down image of the asset. Mostly used by wallets.
- `ttl` **(integer)**
  - The number of seconds the metadata should be cached.

Now, you are now well prepared to delve deeper into the code to make dynamic NFTs by moving onto [Understanding Structures]()!
