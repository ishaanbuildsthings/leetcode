import type { FillIn } from "@/components/TemplatePicker";

// The combinatorics templates (templates/math/), on the Combinatorics tab. ModCalc's file also holds the Stirling
// class, so its ops are on the ModCalc card.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/math/";

export const COMBINATORICS: FillIn[] = [
  {
    label: "ModCalc: factorials, nCk, nPk, stars and bars, Stirling O(1)",
    title: "Factorial and inverse factorial tables mod a prime up to n, then O(1) counting: choose, permute, interleave, identical items into buckets",
    folder: "_combinatorics",
    file: "ModCalc",
    ops: [
      ["ModCalc(n, primeMod)", "N"],
      ["getFactorialWithMod(x)", "1"],
      ["getInverseFactorialWithMod(x)", "1"],
      ["nChooseKWithMod(n, k)", "1"],
      ["nPermuteKWithMod(n, k)", "1"],
      ["interleaveTwoSequencesWithMod(length1, length2)", "1"],
      ["waysToPutIdenticalItemsIntoDistinctBucketsWithMod(items, buckets, allowEmptyBuckets)", "1"],
      ["waysToPutDistinctItemsIntoDistinctBucketsAllowingEmptyWithMod(items, buckets)", "log(N)"],
      ["modMultiply(a, b, ...)", "K"],
      ["modPow(base, exponent)", "log(e)"],
      ["modInv(x)", "log(MOD)"],
      ["MoreAdvancedStirlingStuff(maxItems, maxBuckets, mod)", "N*K"],
      ["waysToPutDistinctItemsIntoIdenticalNonemptyBucketsWithMod(items, buckets)", "1"],
      ["waysToPutDistinctItemsIntoDistinctNonemptyBucketsWithMod(items, buckets)", "1"],
    ],
    note: "ModCalc's n = the largest number you'll take a factorial of (interleaving lengths 500 and 700 needs n = 1200). Stirling (second kind, same file): N = max items, K = max buckets",
    githubUrl: GITHUB,
  },
  {
    label: "Fibonacci: xth term, isFib, list",
    title: "1-indexed (getXthFib(1) -> 0, getXthFib(2) -> 1). Fast doubling for the xth term, exact or mod; isFib by the 5x² ± 4 square test",
    folder: "_combinatorics",
    file: "Fibonacci",
    ops: [
      ["getXthFib(x)", "log(x)"],
      ["getXthFibMod(x, mod)", "log(x)"],
      ["isFib(x)", "1"],
      ["getFibList(n) -> all fibs <= n", "log(n)"],
    ],
    githubUrl: GITHUB,
  },
];
