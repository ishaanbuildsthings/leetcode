import type { FillIn } from "@/components/TemplatePicker";
import { BITSETS } from "@/lib/bitset";

// The bit operation templates (templates/ultimate-template-tool/bit-operations/), on the Bit ops & Bitset tab, Python
// and C++, as cards (components/BitOpsCards.tsx): the bitset, the XOR bases (behind an op selector), then one function
// per row, grouped by what you want to compute. B = number of bits in the largest value, N = number of values.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/";
const FOLDER = "_bit-operations";

// "B*2^B+N" -> "O(B*2^B + N)": products keep their * so B*2^B can't be read as one symbol
const bigO = (cost: string) =>
  `O(${cost.replace(/\+/g, " + ").replace(/B\^2/g, "B²").replace(/\*log\(B\)/g, " log B").replace(/log\(MOD\)/g, "log MOD")})`;

const card = (file: string, call: string, returns: string, cost: string, note?: string): FillIn => ({
  label: `${call} ${bigO(cost)}`,
  title: `-> ${returns}`,
  folder: FOLDER,
  file,
  ops: [[`${call} -> ${returns}`, cost]],
  ...(note ? { note } : {}),
  githubUrl: GITHUB,
});

// B comes from max(arr) and the result has a slot for every mask below 2^B
const MASK_NOTE = "B = number of bits in max(arr): the result has 2ᴮ entries (about 2 · max(arr)), so values up to about 2²⁰ fit. Values must be >= 0.";

export const XOR_BASIS: FillIn[] = [
  {
    label: "XorBasis: max / min / kth subset XOR, distinct XOR count, subsets making x",
    title: "Every value some subset XORs to (a linear basis over bits): insert values, then ask what their subsets can make",
    folder: FOLDER,
    file: "XorBasis",
    ops: [
      ["Construct", ""],
      ["XorBasis()  // nothing inserted yet", "1"],
      ["XorBasis(arr)  // inserts every value of arr", "N*B"],
      ["Insert", ""],
      ["insert(x) -> true if x couldn't be made before (the basis grew)", "B"],
      ["merge(other): inserts everything other holds, as if its values were inserted here", "B^2"],
      ["What subsets make", ""],
      ["canMake(x) -> true if some subset XORs to exactly x (0 always: the empty subset)", "B"],
      ["maxXor() -> largest XOR of any subset", "B"],
      ["maxXorWith(x) -> largest x ^ (XOR of some subset)", "B"],
      ["minXorWith(x) -> smallest x ^ (XOR of some subset)", "B"],
      ["minNonzeroXor() -> smallest XOR of a non-empty subset (0 if one XORs to 0), or -1 (C++) / None (Python) if nothing inserted", "B"],
      ["kthSmallestXor(k) -> kth smallest distinct subset XOR, k 0-indexed (k = 0 -> 0), or -1 / None if k >= countDistinctXors()", "B"],
      ["Counts", ""],
      ["countDistinctXors() -> number of distinct subset XORs, 0 included: 2^rank", "1"],
      ["countSubsetsMakingMod(x, mod) -> subsets (by position, empty included) with XOR exactly x, mod mod: 2^(N - rank) or 0", "B+log(N)"],
      ["rank() -> size of the basis (how many inserted values were independent)", "1"],
      ["size() -> how many values were inserted", "1"],
      ["basis() -> the basis values, largest first", "B"],
    ],
    note: "B = number of bits in the largest value inserted (values >= 0; C++ takes long long). Max subset XOR: XorBasis(arr).maxXor()",
    githubUrl: GITHUB,
  },
  {
    label: "XorBasisDeletable: insert and remove values, then the same subset XOR questions",
    title: "An XOR basis of a multiset you can also remove values from, online",
    folder: FOLDER,
    file: "XorBasisDeletable",
    ops: [
      ["Construct", ""],
      ["XorBasisDeletable()  // nothing held yet", "1"],
      ["XorBasisDeletable(arr)  // inserts every value of arr", "N*B^2"],
      ["Insert and remove", ""],
      ["insert(x) -> true if x couldn't be made before (the rank grew)", "B^2"],
      ["remove(x) -> true if a copy of x was held (one copy is removed), false if none (nothing changes)", "B^2"],
      ["What subsets of the held values make", ""],
      ["canMake(x) -> true if some subset XORs to exactly x (0 always: the empty subset)", "B"],
      ["maxXor() -> largest XOR of any subset", "B"],
      ["maxXorWith(x) -> largest x ^ (XOR of some subset)", "B"],
      ["minXorWith(x) -> smallest x ^ (XOR of some subset)", "B"],
      ["minNonzeroXor() -> smallest XOR of a non-empty subset (0 if one XORs to 0), or -1 (C++) / None (Python) if nothing held", "B"],
      ["kthSmallestXor(k) -> kth smallest distinct subset XOR, k 0-indexed (k = 0 -> 0), or -1 / None if k >= countDistinctXors()", "B*log(B)"],
      ["Counts", ""],
      ["countDistinctXors() -> number of distinct subset XORs, 0 included: 2^rank", "B"],
      ["countSubsetsMakingMod(x, mod) -> subsets (by position, empty included) with XOR exactly x, mod mod", "B+log(N)"],
      ["rank() -> size of the basis of the held values", "B"],
      ["size() -> how many values are held (copies and zeros count)", "1"],
      ["basis() -> a basis of the held values, largest first", "B*log(B)"],
    ],
    note: "B = number of bits in the largest value (values >= 0; C++ takes long long). Only reach for this when values get removed: XorBasis does the rest with O(B) inserts.",
    githubUrl: GITHUB,
  },
  {
    label: "RangeXorBasis: max subset XOR / can make x in any subarray [l, r]",
    title: "XOR basis of any subarray, answered online: a prefix basis that keeps the newest elements",
    folder: FOLDER,
    file: "RangeXorBasis",
    ops: [
      ["Construct", ""],
      ["RangeXorBasis(arr)", "N*B"],
      ["Queries on arr[l..r], inclusive", ""],
      ["maxXorInRange(l, r) -> largest XOR of a subset of arr[l..r]", "B"],
      ["maxXorWithInRange(l, r, x) -> largest x ^ (XOR of a subset of arr[l..r])", "B"],
      ["canMakeInRange(l, r, x) -> true if a subset of arr[l..r] XORs to exactly x", "B"],
      ["rankInRange(l, r) -> size of the basis of arr[l..r]", "B"],
      ["countDistinctXorsInRange(l, r) -> number of distinct subset XORs of arr[l..r], 0 included", "B"],
    ],
    note: "B = number of bits in max(arr); memory N · B. Values must be >= 0. No updates: build it once from arr.",
    githubUrl: GITHUB,
  },
];

// ---- the tab's cards (components/BitOpsCards.tsx)

// one function on a card: its call, its cost, what it returns (a number or a list), and the drawer it opens
export type CardFn = { call: string; cost: string; returns: string; fillIn: FillIn };
// a row: the function, and its mod version if there is one (the card's mod switch shows that instead)
export type CardRow = CardFn & { mod?: CardFn };
export type BitCard =
  | { kind: "rows"; id: string; title: string; note?: string; rows: CardRow[] }
  | { kind: "bitset"; id: string; title: string; fillIn: FillIn }
  | { kind: "xor-basis"; id: string; title: string; note?: string };

const fn = (file: string, call: string, returns: string, cost: string, note?: string): CardFn => ({
  call,
  cost: bigO(cost),
  returns,
  fillIn: card(file, call, returns, cost, note),
});
// a row with a Mod twin: the same function, its answer mod mod
const withModRow = (base: CardFn, file: string, call: string, returns: string, cost: string): CardRow => ({
  ...base,
  mod: fn(file, call, returns, cost, base.fillIn.note),
});

const SUM_NOTE = "Values must be >= 0. Without mod, C++ throws overflow_error if the exact answer doesn't fit in long long (the mod version never does).";
const OVERFLOW = "Without mod the counts are exact: Python's get as big as 2^N, C++ throws overflow_error past 62 values.";
const OPS = [
  ["AND", "And", "&"],
  ["OR", "Or", "|"],
  ["XOR", "Xor", "^"],
] as const;

const pairSums: CardRow[] = OPS.map(([, op, sym]) =>
  withModRow(
    fn(`sumOfPair${op}s`, `sumOfPair${op}s(arr)`, `one number: the sum of arr[i] ${sym} arr[j] over every pair i < j`, "N*B", SUM_NOTE),
    `sumOfPair${op}sMod`, `sumOfPair${op}sMod(arr, mod)`, `one number: the sum of arr[i] ${sym} arr[j] over every pair i < j, mod mod`, "N*B",
  ),
);

const subarraySums: CardRow[] = OPS.map(([word, op]) =>
  withModRow(
    fn(`sumOfSubarray${op}s`, `sumOfSubarray${op}s(arr)`, `one number: the sum of the ${word} of every non-empty subarray`, "N*B", SUM_NOTE),
    `sumOfSubarray${op}sMod`, `sumOfSubarray${op}sMod(arr, mod)`, `one number: the sum of the ${word} of every non-empty subarray, mod mod`, "N*B",
  ),
);

const countPairs: CardRow[] = OPS.map(([, op, sym]) =>
  fn(`count${op}PairsEqualToKForAllK`, `count${op}PairsEqualToKForAllK(arr)`,
    `a list, one entry per k < 2^B: how many pairs i < j have arr[i] ${sym} arr[j] == k`, "B*2^B+N", MASK_NOTE),
);

const countSubsets: CardRow[] = OPS.slice(0, 2).map(([word, op]) =>
  withModRow(
    fn(`count${op}SubsetsEqualToKForAllK`, `count${op}SubsetsEqualToKForAllK(arr)`,
      `a list, one entry per k < 2^B: how many non-empty subsets have ${word} == k`, "B*2^B+N", `${MASK_NOTE} ${OVERFLOW}`),
    `count${op}SubsetsEqualToKForAllKMod`, `count${op}SubsetsEqualToKForAllKMod(arr, mod)`,
    `a list, one entry per k < 2^B: how many non-empty subsets have ${word} == k, mod mod`, "B*2^B+N",
  ),
);

const CONV_NOTE: Record<string, string> = {
  And: "arr1 and arr2 both have length 2^B (an AND convolution).",
  Or: "arr1 and arr2 both have length 2^B (an OR convolution).",
  Xor: "arr1 and arr2 both have length 2^B (an XOR convolution). Without mod, C++ is exact while (sum of |arr1|) · (sum of |arr2|) fits in long long; past that use mod (mod must be odd).",
};
const convolutions: CardRow[] = OPS.map(([, op, sym]) => {
  const base = fn(`sumOf${op}PairsEqualToKForAllK`, `sumOf${op}PairsEqualToKForAllK(arr1, arr2)`,
    `a list, one entry per k < 2^B: the sum of arr1[i] × arr2[j] over every i, j with i ${sym} j == k`, "B*2^B", CONV_NOTE[op]);
  return op === "Xor"
    ? withModRow(base, "sumOfXorPairsEqualToKForAllKMod", "sumOfXorPairsEqualToKForAllKMod(arr1, arr2, mod)",
        "a list, one entry per k < 2^B: the sum of arr1[i] × arr2[j] over every i, j with i ^ j == k, mod mod", "B*2^B+log(MOD)")
    : base;
});

const MASKS_NOTE = "B = number of bits in max(arr): the list has 2ᴮ entries (about 2 · max(arr)), so values up to about 2²⁰ fit. Values must be >= 0.";
const masks: CardRow[] = [
  fn("countSubmasksForAllMasks", "countSubmasksForAllMasks(arr)", "a list, one entry per mask < 2^B: how many values of arr are submasks of mask (v & mask == v)", "B*2^B+N", MASKS_NOTE),
  fn("sumSubmasksForAllMasks", "sumSubmasksForAllMasks(arr)", "a list, one entry per mask < 2^B: the sum of the values of arr that are submasks of mask", "B*2^B+N", MASKS_NOTE),
  fn("countSupermasksForAllMasks", "countSupermasksForAllMasks(arr)", "a list, one entry per mask < 2^B: how many values of arr are supermasks of mask (v & mask == mask)", "B*2^B+N", MASKS_NOTE),
  fn("sumSupermasksForAllMasks", "sumSupermasksForAllMasks(arr)", "a list, one entry per mask < 2^B: the sum of the values of arr that are supermasks of mask", "B*2^B+N", MASKS_NOTE),
];

const twoGroups: CardRow[] = [
  fn("maxTwoGroupXorSum", "maxTwoGroupXorSum(arr)", "one number: the max of XOR(A) + XOR(B) over every split of arr into two non-empty groups", "N*B",
    "Values must be >= 0; at least 2 values. Strips the bits of XOR(arr) from every value, then a max subset XOR (XOR basis)."),
  fn("maxTwoGroupAndSum", "maxTwoGroupAndSum(arr)", "one number: the max of AND(A) + AND(B) over every split of arr into two non-empty groups", "B*2^B+N",
    "Values must be >= 0 (up to about 2²⁰: 2ᴮ masks are tried); at least 2 values."),
];

export const BIT_OPS_CARDS: BitCard[] = [
  { kind: "bitset", id: "bitset", title: "Bitset", fillIn: BITSETS[0] },
  { kind: "xor-basis", id: "xor-basis", title: "XOR basis", note: "tick what you need: it picks the basis" },
  { kind: "rows", id: "pair-sums", title: "Sums over pairs", note: "every pair i < j of one array", rows: pairSums },
  { kind: "rows", id: "subarray-sums", title: "Sums over subarrays", note: "every non-empty subarray", rows: subarraySums },
  { kind: "rows", id: "two-groups", title: "Split into two groups", note: "every value in exactly one, both non-empty", rows: twoGroups },
  { kind: "rows", id: "masks", title: "Submasks / supermasks of every mask", note: "SOS DP over arr's values", rows: masks },
  { kind: "rows", id: "count-pairs", title: "Count pairs, for every k at once", note: "pairs i < j", rows: countPairs },
  { kind: "rows", id: "count-subsets", title: "Count subsets, for every k at once", note: "non-empty subsets", rows: countSubsets },
  { kind: "rows", id: "convolutions", title: "Sum of arr1[i] × arr2[j], for every k at once", note: "every i and every j (a convolution)", rows: convolutions },
];

// ---- the XOR basis selector: every op any of the three bases has, and what each one costs there

export type XorOp = { id: string; signature: string; does: string };
export const XOR_BASIS_OP_GROUPS: { title: string; ops: XorOp[] }[] = [
  {
    title: "Updates",
    ops: [
      { id: "insert", signature: "insert(x)", does: "add x (copies count)" },
      { id: "remove", signature: "remove(x)", does: "take one copy of x back out (rare)" },
      { id: "merge", signature: "merge(other)", does: "insert everything another basis holds" },
    ],
  },
  {
    title: "Questions about every value held",
    ops: [
      { id: "canMake", signature: "canMake(x)", does: "does some subset XOR to x?" },
      { id: "maxXor", signature: "maxXor()", does: "largest subset XOR" },
      { id: "maxXorWith", signature: "maxXorWith(x)", does: "largest x ^ (subset XOR)" },
      { id: "minXorWith", signature: "minXorWith(x)", does: "smallest x ^ (subset XOR)" },
      { id: "minNonzeroXor", signature: "minNonzeroXor()", does: "smallest XOR of a non-empty subset" },
      { id: "kthSmallestXor", signature: "kthSmallestXor(k)", does: "kth smallest distinct subset XOR" },
      { id: "countDistinctXors", signature: "countDistinctXors()", does: "how many distinct subset XORs (2^rank)" },
      { id: "countSubsetsMakingMod", signature: "countSubsetsMakingMod(x, mod)", does: "how many subsets XOR to x, mod mod" },
      { id: "rank", signature: "rank()", does: "size of the basis" },
      { id: "size", signature: "size()", does: "how many values are held" },
      { id: "basis", signature: "basis()", does: "the basis values" },
    ],
  },
  {
    title: "Questions about a subarray arr[l..r] (no updates)",
    ops: [
      { id: "maxXorInRange", signature: "maxXorInRange(l, r)", does: "largest subset XOR in arr[l..r]" },
      { id: "maxXorWithInRange", signature: "maxXorWithInRange(l, r, x)", does: "largest x ^ (subset XOR) in arr[l..r]" },
      { id: "canMakeInRange", signature: "canMakeInRange(l, r, x)", does: "does a subset of arr[l..r] XOR to x?" },
      { id: "rankInRange", signature: "rankInRange(l, r)", does: "size of the basis of arr[l..r]" },
      { id: "countDistinctXorsInRange", signature: "countDistinctXorsInRange(l, r)", does: "distinct subset XORs of arr[l..r]" },
    ],
  },
];

export type XorBasisTemplate = { name: string; fillIn: FillIn; build: string; costs: Record<string, string> };
const QUERIES = ["canMake", "maxXor", "maxXorWith", "minXorWith", "minNonzeroXor", "kthSmallestXor", "countDistinctXors",
  "countSubsetsMakingMod", "rank", "size", "basis"];
const each = (ids: string[], cost: string) => Object.fromEntries(ids.map((id) => [id, cost]));
// lightest first: the first one that has every ticked op is the pick
export const XOR_BASIS_TEMPLATES: XorBasisTemplate[] = [
  {
    name: "XorBasis",
    fillIn: byXorBasis("XorBasis"),
    build: bigO("N*B"),
    costs: Object.fromEntries(Object.entries({ ...each(QUERIES, "B"), insert: "B", merge: "B^2", countDistinctXors: "1",
      countSubsetsMakingMod: "B+log(N)", rank: "1", size: "1" }).map(([k, v]) => [k, bigO(v)])),
  },
  {
    name: "XorBasisDeletable",
    fillIn: byXorBasis("XorBasisDeletable"),
    build: bigO("N*B^2"),
    costs: Object.fromEntries(Object.entries({ ...each(QUERIES, "B"), insert: "B^2", remove: "B^2", kthSmallestXor: "B*log(B)",
      countSubsetsMakingMod: "B+log(N)", size: "1", basis: "B*log(B)" }).map(([k, v]) => [k, bigO(v)])),
  },
  {
    name: "RangeXorBasis",
    fillIn: byXorBasis("RangeXorBasis"),
    build: bigO("N*B"),
    costs: each(["maxXorInRange", "maxXorWithInRange", "canMakeInRange", "rankInRange", "countDistinctXorsInRange"], bigO("B")),
  },
];

function byXorBasis(file: string) {
  const f = XOR_BASIS.find((c) => c.file === file);
  if (!f) throw new Error(`no XOR basis card for ${file}`);
  return f;
}
