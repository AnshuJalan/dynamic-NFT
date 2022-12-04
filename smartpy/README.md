# 🧑‍💻 Get Started (Smartpy)

Smartpy is a python based library to write smart contracts on Tezos. If you are a complete beginner, you may want to start with this [video tutorial](https://www.youtube.com/watch?v=yZs06D4tjI4&t=1427s&ab_channel=TZAPAC). You can also read the docs [here](https://smartpy.io/docs/).

The content below explains some of the important concepts around the tooling used, that you must know in order to understand Smartpy based structures.

> **Warning**
> You must use Smartpy cli version [0.9.0](https://smartpy.io/docs/releases/#v090) to compile the contracts. Download this specific release using `sh <(curl -s https://smartpy.io/releases/20220208-48ec25e86a7834c3098dd72313c6d539acba201a/cli/install.sh)`

## Folder layout

```
\
 |————— common/ # common utilities used across structures and examples
 .
 |————— contracts/ # smart contracts for the structures
 |————————— metadata/ # TZIP-16 based metadata for the structures
 |————————— michelson/ # compiled michelson
 .
 |————— data/ # utilites for the SVG based structures and examples
 .
 |————— examples/ # smart contracts for the examples
 |————————— metadata/ # TZIP-16 based metadata for the examples
 |————————— michelson/ # compiled michelson
```

## Tools required

- [Smartpy Cli](https://smartpy.io/docs/cli/) [version: 0.9.0]
- [Python](https://www.python.org/doc/) - Internal dependency of Smartpy [version: 2.7.4]
- [NodeJS](https://nodejs.org/en/docs/) - Internal dependency of Smartpy [version: 14.17.1]

## Compiling and testing

A helper shell script `compile.sh` is provided in both `/contracts` and `/examples` folders to assist the simultaneous compilation, testing and metadata generation. You can run the script through:

```
$ bash compile.sh
```

## Generating off-chain views

In Smartpy there's an inbuilt utility to simultaneously compile an `offchain-view` and build the TZIP-16 JSON. The shell script referred above automates the entire process for the structures and examples. Incase you want to understand the mechanism for customisation, you can read through the [Build Metadata](https://smartpy.io/docs/helpers/metadata_builder/#build-metadata) section in Smartpy docs.
