const BASE = 26;
const MOD = 10 ** 9 + 7;

const cache = {}; // maps e to results
// calculates 26^e % MOD
function modPow(e, base = BASE) {
  if (e in cache) {
    return cache[e];
  }
  let current = 1;
  for (let i = 1; i <= e; i++) {
    // (a * b) % c =   ((a%c)*(b%c)) % c
    current = (current * base) % MOD;
  }
  cache[e] = current;
  return current;
}

for (let i = 0; i < 10000; i++) {
  modPow(i);
}

console.log(cache);
