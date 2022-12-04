# 🪂 Deployment

This folder contains scripts that can be used to deploy the examples at [/ligo/examples](https://github.com/AnshuJalan/tezos-dNFT/tree/master/ligo/examples) and [/smartpy/examples](https://github.com/AnshuJalan/tezos-dNFT/tree/master/smartpy/examples). Contracts that have already been deployed on ghostnet are listed down below.

## How to deploy?

Since this is a node project, you need to first install the dependencies through:

```
$ npm install
```

You can choose to either deploy the examples compiled from LIGO or Smartpy. You need to provide 3 parameters to the run the deploy script - `language` (Smartpy or LIGO), `admin` (for Game1 and Game2) and `harbinger_normaliser_address` (for Locker).

```
$ PRIVATE_KEY=<you_private_key> npm run deploy <language> <admin_address> <harbinger_normaliser_address>
```

> **Note**
> Harbinger Normaliser (Ghostnet): KT1ENe4jbDE1QVG1euryp23GsAeWuEwJutQX

## Deployed contracts

Three 3 examples written in both LIGO and Smartpy have been deployed and the metadata has been verified through [TZComet](https://tzcomet.io/).

| Example  | Pre-compilation Language | Address                                                                                                                  | Metadata Validity                                                                                |
| -------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `Game1`  | `LIGO`                   | [KT1T4gDYwKFic524J3dLQsm6vwyEqz1mEsKM](https://better-call.dev/ghostnet/KT1T4gDYwKFic524J3dLQsm6vwyEqz1mEsKM/operations) | [TZComet](https://tzcomet.io/#/explorer%3Fexplorer-input%3DKT1T4gDYwKFic524J3dLQsm6vwyEqz1mEsKM) |
| `Game2`  | `LIGO`                   | [KT1Pz4EAn3kAunSEz5Ps3cSLhq53mrcLoc1b](https://better-call.dev/ghostnet/KT1Pz4EAn3kAunSEz5Ps3cSLhq53mrcLoc1b/operations) | [TZComet](https://tzcomet.io/#/explorer%3Fexplorer-input%3DKT1Pz4EAn3kAunSEz5Ps3cSLhq53mrcLoc1b) |
| `Locker` | `LIGO`                   | [KT1DcHXDY5DtaYdqjajhDXfcZd69nMYnCFu1](https://better-call.dev/ghostnet/KT1DcHXDY5DtaYdqjajhDXfcZd69nMYnCFu1/operations) | [TZComet](https://tzcomet.io/#/explorer%3Fexplorer-input%3DKT1DcHXDY5DtaYdqjajhDXfcZd69nMYnCFu1) |
| `Game1`  | `Smartpy`                | [KT1AHGKoWQqykfhBnqRcxZrLBuTaNp4UFqih](https://better-call.dev/ghostnet/KT1AHGKoWQqykfhBnqRcxZrLBuTaNp4UFqih/operations) | [TZComet](https://tzcomet.io/#/explorer%3Fexplorer-input%3DKT1AHGKoWQqykfhBnqRcxZrLBuTaNp4UFqih) |
| `Game2`  | `Smartpy`                | [KT1EGcCqPwAZZMzaR5QTN4FhMi8C8St9Td4z](https://better-call.dev/ghostnet/KT1EGcCqPwAZZMzaR5QTN4FhMi8C8St9Td4z/operations) | [TZComet](https://tzcomet.io/#/explorer%3Fexplorer-input%3DKT1EGcCqPwAZZMzaR5QTN4FhMi8C8St9Td4z) |
| `Locker` | `Smartpy`                | [KT1JZjh8sE7Zm22cjSa48569dHpe4uCjdrKu](https://better-call.dev/ghostnet/KT1JZjh8sE7Zm22cjSa48569dHpe4uCjdrKu/operations) | [TZComet](https://tzcomet.io/#/explorer%3Fexplorer-input%3DKT1JZjh8sE7Zm22cjSa48569dHpe4uCjdrKu) |
