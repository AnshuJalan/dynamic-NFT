# 🎨 Dynamic NFTs (dNFT) on Tezos

A dynamic NFT or dNFT is a non-fungible token whose metadata can be updated based on external conditions that originate off-chain (like through an oracle) or on-chain through state changes in the NFT smart contract itself. Dynamic NFTs unlock a whole new world of possibilities for what can be tokenised on the blockchain - A house under construction with the NFT metadata updating as it is built out; a complex game character with the metadata relecting its evolution; tokenised CDPs in Defi with the dNFT showing the latest state of your portfolio. The list goes on!

This repo contains extensive smart contract blueprints for creating a dynamic NFT on [Tezos](https://tezos.com), an energy efficient blockchain that's leading the NFT space. These blueprints are referred to as `structures` and they can be thought of as different techniques of incorporating dynamic metadata in an NFT smart contract.

## Overview

Smart contracts in the repository are written in the two most popular languages on Tezos - [LIGO](https://ligolang.org)(Cameligo syntax) and [Smartpy](https://smartpy.io). Both have their own separate folders with equivalent layouts for the ease of the viewer.

A total of 5 named `structures` or **dNFT blueprints** are provided:

- `Brute structure` - As the name suggests, a dNFT using the Brute structure requires a manual updation of the metadata.
- `Point structure` - More flexible than Brute, this one allows for dynamically creating a URI that _points_ to the metadata.
- `Create structure` - Adds a pinch of efficiency to Point by avoiding repetition of static fields in the metadata.
- `Oracle structure` - Goes a step ahead and allows for dynamic metadata based on some external state received from an _oracle_.
- `SVG structure` - The most ambitious of all, this enables the dynamic creation of an SVG graphic for the NFT metadata, entirely on the chain.

Each of these structure can be used in a different context depending upon the use-case of the developer. A deeper explanation is provided in the '[How to choose a structure?]()' section. Also, a total of 3 examples are provided that properly display how the structures can be used by developers in their projects.

If you are a beginner in your understanding of smart contracts on Tezos, you can either choose [Get Started (LIGO)]() or [Get Started (Smartpy)](), depending on your language of choice. If you are already comfortable with Tezos contract, you can head to the [main documentation]().

### Folder layout

```
\
|————— assets/ # images used as NFT graphic
|————— docs/ # markdown files for documentation
|————— ligo/ # structures and examples in LIGO
|————— smartpy/ # structures and examples in Smartpy
|————— .gitignore
|————— LICENSE
```

## Prerequisites

These are the set of general concepts and language specific tooling that you are expected to understand before delving deeper into the code in this repo.

### General concepts

- [TZIP 12](https://gitlab.com/tezos/tzip/-/blob/master/proposals/tzip-12/tzip-12.md)
  - FA2 multiasset standard on Tezos is a set of defined rules that will be used for creating non-fungible tokens contracts.
  - This standard also defines how the token metadata should be incorporated in the contract.
- [TZIP 16](https://gitlab.com/tezos/tzip/-/blob/master/proposals/tzip-16/tzip-16.md)
  - The contract metadata standard which introduces `offchain views` that are used to deliver the token metadata dynamically.
- [TZIP 21](https://gitlab.com/tezos/tzip/-/blob/master/proposals/tzip-21/tzip-21.md)
  - The standard for _rich token metadata_, this elaborately defines the fields that can be added to the metadata JSON.

### For LIGO developers

- [LIGO](https://www.ligolang.org/docs/intro/introduction?lang=cameligo) - Cameligo syntax [version: 0.52.0]
- [Flextesa](https://tezos.gitlab.io/flextesa/) - Tezos sandbox for testing out the contracts [version: oxheadalpha/flextesa:20221123]
- [Docker](https://docs.docker.com/get-started/overview/) - For running flextesa and LIGO images [version: 20.10.14]
- [Taquito](https://tezostaquito.io/docs/quick_start/) - For deploying contracts and sending transactions on flextesa [version: 14.0.0]
- [Typescript](https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html) - For test scripts [version: 4.8.4]

### For Smartpy developers

- [Python](https://www.python.org/doc/) - required for understanding Smartpy itself and also the utility functions written in pure python [version: 2.7.4]
- [Smartpy](https://smartpy.io/docs) [version: 0.9.0]

## Disclaimer

_The code is provided as is. The smart contracts are not formally auditted by a third party. Users are advised to do their own research before using the code in this repository . The author is not liable for any failure or loss of funds._
