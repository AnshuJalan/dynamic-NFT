import fs from "fs";
import { validateAddress, validateContractAddress } from "@taquito/utils";

import * as metadata from "./metadata";
import { DeployParams } from "./types";
import { getGameStorage, getLockerStorage } from "./storage";

export const deploy = async ({
  tezos,
  language,
  admin,
  harbingerAddress,
}: DeployParams): Promise<void> => {
  try {
    // Validate command line inputs
    if (language !== "smartpy" && language !== "ligo") {
      throw "Invalid language!";
    } else if (validateAddress(admin) !== 3 && validateContractAddress(admin) !== 3) {
      throw "Invalid admin address!";
    } else if (validateContractAddress(harbingerAddress) !== 3) {
      throw "Invalid harbinger address!";
    }

    // Read Michelson files
    const game1Code = fs
      .readFileSync(`${__dirname}/../../${language}/examples/michelson/game1.tz`)
      .toString();
    const game2Code = fs
      .readFileSync(`${__dirname}/../../${language}/examples/michelson/game2.tz`)
      .toString();
    const lockerCode = fs
      .readFileSync(`${__dirname}/../../${language}/examples/michelson/locker.tz`)
      .toString();

    console.log("=======================================");
    console.log(`  Deploying dNFT Examples (${language})`);
    console.log("=======================================\n");

    let op;

    console.log(">> Deploying Game 1 ");

    op = await tezos.contract.originate({
      code: game1Code,
      storage: getGameStorage(admin, metadata[language].game1),
    });
    await op.confirmation();

    console.log(">>> Deployed at: ", op.contractAddress);

    console.log(">> Deploying Game 2 ");

    op = await tezos.contract.originate({
      code: game2Code,
      storage: getGameStorage(admin, metadata[language].game2),
    });
    await op.confirmation();

    console.log(">> Deployed at: ", op.contractAddress);

    console.log(">> Deploying Locker ");

    op = await tezos.contract.originate({
      code: lockerCode,
      storage: getLockerStorage(harbingerAddress, metadata[language].locker),
    });
    await op.confirmation();

    console.log(">> Deployed at: ", op.contractAddress);

    console.log("\n=======================================");
    console.log(`          Deployed Examples`);
    console.log("=======================================");
  } catch (err: any) {
    throw err;
  }
};
