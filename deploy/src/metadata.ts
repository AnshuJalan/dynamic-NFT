import { MetadataStore } from "./types";

const toBytes = (data: string): string => {
  const byteArray = new TextEncoder().encode(data);
  let s = "0x";
  byteArray.forEach(function (byte) {
    s += ("0" + (byte & 0xff).toString(16)).slice(-2);
  });
  return s;
};

// TZIP-16 Metadata stored at /smartpy/examples/metadata
export const smartpy: MetadataStore = {
  game1: toBytes("ipfs://QmYTWQ3qr5Ko6P9GhsMgPqT7miwHmj5TKJWYkyPngPxNpj"),
  game2: toBytes("ipfs://QmdqNeUM75Z8DuMKAAQszEfjKiPv2CwjYTwUZxz4trL8ZT"),
  locker: toBytes("ipfs://QmYMA1iwLzqcx7zLzbgHrquX75EDMcMYLy8yva8SAxGRFL"),
};

// TZIP-16 Metadata stored at /ligo/examples/metadata
export const ligo: MetadataStore = {
  game1: toBytes("ipfs://QmV8vUwf28iiA8W923uNvA2HDUUfVhdXjNCLPXqbsRpVYB"),
  game2: toBytes("ipfs://QmStBdmfphi3e11qgaWCqd8cHDR2uBV49x2RHSKQ2Pmsw6"),
  locker: toBytes("ipfs://QmYWi1pQFNEV99pkQaLuiBAASjRstpi6CHkJwKY3dkwuRV"),
};
