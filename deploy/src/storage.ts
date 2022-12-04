import { MichelsonMap } from "@taquito/taquito";

import { Game, Locker } from "./types";

export const getGameStorage = (admin: string, metadataUri: string): Game => {
  const metadata = MichelsonMap.fromLiteral({});
  metadata.set("", metadataUri);
  return {
    admin,
    ledger: MichelsonMap.fromLiteral({}),
    operators: MichelsonMap.fromLiteral({}),
    player_states: MichelsonMap.fromLiteral({}),
    metadata,
  };
};

export const getLockerStorage = (harbingerAddress: string, metadataUri: string): Locker => {
  const metadata = MichelsonMap.fromLiteral({});
  metadata.set("", metadataUri);
  return {
    ledger: MichelsonMap.fromLiteral({}),
    operators: MichelsonMap.fromLiteral({}),
    locks: MichelsonMap.fromLiteral({}),
    lock_count: 0,
    harbinger_address: harbingerAddress,
    metadata,
  };
};
