export const toBytes = (data: string): string => {
  const byteArray = new TextEncoder().encode(data);
  let s = "0x";
  byteArray.forEach(function (byte) {
    s += ("0" + (byte & 0xff).toString(16)).slice(-2);
  });
  return s;
};
