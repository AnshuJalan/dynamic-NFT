import { TezosToolkit } from "@taquito/taquito";
import { InMemorySigner } from "@taquito/signer";

import { deploy } from "./deploy";

const tezos = new TezosToolkit("https://ghostnet.smartpy.io");

tezos.setProvider({
  signer: new InMemorySigner(process.env.PRIVATE_KEY as string),
});

(async () => {
  try {
    await deploy({
      tezos,
      language: process.argv[2],
      admin: process.argv[3],
      harbingerAddress: process.argv[4],
    });
  } catch (err) {
    console.error(err);
  }
})();
