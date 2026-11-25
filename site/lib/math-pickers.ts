import type { PickerOpGroup } from "@/components/OpPicker";

// The Math tab's two op pickers (templates/ultimate-template-tool/combinatorics/ModCalc.* and Fibonacci.*): one row per op,
// with a worked example. Costs are in the op's own argument names.
export const MATH_GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/combinatorics/";

const PRIME = "mod must be prime";

export const MODCALC_GROUPS: PickerOpGroup[] = [
  {
    title: "Factorials and choosing",
    setup: { call: "calc = ModCalc()  or  calc = ModCalc(mod=998244353)", returns: "mod 10^9 + 7 unless you pass one; builds nothing: the factorial tables grow lazily inside the calls", cost: "1" },
    ops: [
      { id: "getFactorialWithMod", call: "getFactorialWithMod(x)", returns: "x! % mod", example: "getFactorialWithMod(5) -> 120", note: "0 once x >= mod; works for any mod", cost: "1 amortized", grows: "bigger x" },
      { id: "getInverseFactorialWithMod", call: "getInverseFactorialWithMod(x)", returns: "1 / x! % mod", example: "getInverseFactorialWithMod(5) -> 808333339 (that times 120 is 1 mod 1e9 + 7)", note: `needs x < mod; ${PRIME}`, cost: "1 amortized", grows: "bigger x" },
      { id: "nChooseKWithMod", call: "nChooseKWithMod(n, k)", returns: "ways to pick k of n, order ignored", example: "nChooseKWithMod(5, 2) -> 10", note: `0 if k < 0 or k > n; ${PRIME}`, cost: "1 amortized", grows: "bigger n (k doesn't matter)" },
      { id: "nPermuteKWithMod", call: "nPermuteKWithMod(n, k)", returns: "ways to pick k of n in order", example: "nPermuteKWithMod(5, 2) -> 20", note: `0 if k < 0 or k > n; ${PRIME}`, cost: "1 amortized", grows: "bigger n (k doesn't matter)" },
      { id: "interleaveTwoSequencesWithMod", call: "interleaveTwoSequencesWithMod(length1, length2)", returns: "ways to merge them, each keeping its order", example: "interleaveTwoSequencesWithMod(2, 1) -> 3 (aab, aba, baa)", note: PRIME, cost: "1 amortized", grows: "bigger length1 + length2" },
    ],
  },
  {
    title: "Putting items into buckets (no Stirling)",
    setup: { call: "calc = ModCalc()  or  calc = ModCalc(mod=998244353)", returns: "mod 10^9 + 7 unless you pass one; builds nothing: the factorial tables grow lazily inside the calls", cost: "1" },
    ops: [
      {
        id: "waysToPutIdenticalItemsIntoDistinctBucketsWithMod",
        call: "waysToPutIdenticalItemsIntoDistinctBucketsWithMod(items, buckets, allowEmptyBuckets: bool — required)",
        returns: "count",
        example: "(3, 2, True) -> 4: 3+0, 2+1, 1+2, 0+3;  (3, 2, False) -> 2: 2+1, 1+2",
        note: `stars and bars; ${PRIME}`,
        cost: "1 amortized",
        grows: "bigger items + buckets",
      },
      {
        id: "waysToPutDistinctItemsIntoDistinctBucketsWithMod",
        call: "waysToPutDistinctItemsIntoDistinctBucketsWithMod(items, buckets, allowEmptyBuckets: bool — required)",
        returns: "count",
        example: "(3, 2, True) -> 8 (2^3);  (3, 2, False) -> 6",
        note: "O(log items) with empty buckets allowed (any mod); O(buckets * log items) without (mod must be prime)",
        cost: "buckets*log(items)",
        grows: "bigger buckets (already inside this cost)",
      },
    ],
  },
  {
    title: "Mod arithmetic",
    setup: { call: "calc = ModCalc()  or  calc = ModCalc(mod=998244353)", returns: "mod 10^9 + 7 unless you pass one; builds nothing", cost: "1" },
    ops: [
      { id: "modPow", call: "modPow(base, exponent)", returns: "base^exponent % mod", example: "modPow(2, 10) -> 1024", note: "works for any mod", cost: "log(exponent)" },
      { id: "modInv", call: "modInv(x)", returns: "1 / x % mod", example: "modInv(2) -> 500000004 (that times 2 is 1 mod 1e9 + 7)", note: `x must not be a multiple of mod; ${PRIME}`, cost: "log(mod)" },
    ],
  },
];

export const FIBONACCI_GROUPS: PickerOpGroup[] = [
  {
    title: "",
    ops: [
      { id: "getXthFib", call: "getXthFib(x)", returns: "the xth Fibonacci number, 1-indexed", example: "getXthFib(1) -> 0, getXthFib(2) -> 1, getXthFib(10) -> 34", note: "needs x >= 1; C++ overflows past x = 94", cost: "log(x)" },
      { id: "getXthFibMod", call: "getXthFibMod(x, mod)", returns: "getXthFib(x) % mod", example: "getXthFibMod(10, 7) -> 6", note: "needs x >= 1; any mod", cost: "log(x)" },
      { id: "isFib", call: "isFib(x)", returns: "True if x is a Fibonacci number", example: "isFib(21) -> True, isFib(22) -> False", cost: "1" },
      { id: "getFibList", call: "getFibList(n)", returns: "every Fibonacci number <= n, in order", example: "getFibList(10) -> [0, 1, 1, 2, 3, 5, 8]", note: "[] if n < 0", cost: "log(n)" },
    ],
  },
];

// Stirling numbers (Stirling.*): the same two counts from a formula (nothing built, each call pays) or a growing table
// (each call is a lookup once the table covers it)
const BOTH = [
  {
    suffix: "Identical",
    method: "waysToPutDistinctItemsIntoIdenticalBucketsWithMod",
    example: "(3, 2, False) -> 3: {a}{bc}, {b}{ac}, {c}{ab};  (3, 2, True) -> 4: those, plus {abc}{}",
  },
  {
    suffix: "Distinct",
    method: "waysToPutDistinctItemsIntoDistinctBucketsWithMod",
    example: "(3, 2, False) -> 6;  (3, 2, True) -> 8 (2^3)",
  },
];
export const STIRLING_GROUPS: PickerOpGroup[] = [
  {
    title: "StirlingByFormula: every call pays, no table to build",
    setup: { call: "calc = StirlingByFormula()  or  calc = StirlingByFormula(mod=998244353)", returns: "mod 10^9 + 7 unless you pass one (must be prime)", cost: "1" },
    ops: BOTH.map((o) => ({
      id: `formula${o.suffix}`,
      call: `${o.method}(items, buckets, allowEmptyBuckets: bool — required)`,
      returns: "count",
      example: o.example,
      note: `buckets * log items on every call; needs buckets < mod; ${PRIME}`,
      cost: "buckets*log(items)",
      grows: "bigger buckets (already inside this cost)",
    })),
  },
  {
    title: "StirlingByTable: grows lazily with the calls you make, then every call is a lookup",
    setup: { call: "calc = StirlingByTable()  or  calc = StirlingByTable(mod=1000)", returns: "mod 10^9 + 7 unless you pass one (any mod); builds nothing: the table grows lazily inside the calls", cost: "1" },
    ops: BOTH.map((o) => ({
      id: `table${o.suffix}`,
      call: `${o.method}(items, buckets, allowEmptyBuckets: bool — required)`,
      returns: "count",
      example: o.example,
      note: "growing costs largest items * largest buckets in total over all calls, and that much memory; a call the table already covers is O(1); works for any mod",
      cost: "1 amortized",
      grows: "bigger items or bigger buckets",
    })),
  },
];
