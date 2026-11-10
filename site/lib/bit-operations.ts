import type { FillIn } from "@/components/TemplatePicker";
import type { RowChoice, RowSection, RowVersion } from "@/components/RowTemplates";
import { BITSETS } from "@/lib/bitset";

// The bit operation templates (templates/ultimate-template-tool/bit-operations/), on the Bit ops & Bitset tab, Python
// and C++: the XOR basis classes, then one function per file and per card (SOS DP, XOR convolution, bit sums). The
// card's caption is what the function returns. B = number of bits in the largest value, N = number of values.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/";
const FOLDER = "_bit-operations";

// "B*2^B+N" -> "O(B*2^B + N)": products keep their * so B*2^B can't be read as one symbol
const bigO = (cost: string) =>
  `O(${cost.replace(/\+/g, " + ").replace(/B\^2/g, "B²").replace(/log\(MOD\)/g, "log MOD")})`;

const card = (file: string, call: string, returns: string, cost: string, note?: string): FillIn => ({
  label: `${call} ${bigO(cost)}`,
  title: `-> ${returns}`,
  folder: FOLDER,
  file,
  ops: [[`${call} -> ${returns}`, cost]],
  ...(note ? { note } : {}),
  githubUrl: GITHUB,
});

// a card whose Mod version (the same function, its answer mod mod) sits behind a "With mod" checkbox instead of on a
// card of its own
const withMod = (base: FillIn, file: string, call: string, returns: string, cost: string): FillIn => ({
  ...base,
  variant: {
    label: "With mod",
    title: `Use ${file}: the same answer, mod mod`,
    storageKey: `templatePicker.mod.${base.file}`,
    on: { label: `${call} ${bigO(cost)}`, file, ops: [[`${call} -> ${returns}`, cost]] },
  },
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

export const SOS_DP: FillIn[] = [
  card("subsetSums", "subsetSums(valueAtMask)", "for each mask: the sum of valueAtMask[sub] over every sub with sub & mask == sub", "B*2^B",
    "valueAtMask: a list of length 2^B with one number per mask, e.g. valueAtMask[x] = how many times x appears in your array; then res[mask] = how many of your values are submasks of mask."),
  card("supersetSums", "supersetSums(valueAtMask)", "for each mask: the sum of valueAtMask[sup] over every sup with sup & mask == mask", "B*2^B",
    "valueAtMask: a list of length 2^B with one number per mask, e.g. valueAtMask[x] = how many times x appears in your array; then res[mask] = how many of your values are supermasks of mask."),
  withMod(
    card("countAndSubsetsEqualToKForAllK", "countAndSubsetsEqualToKForAllK(arr)", "for each k: how many non-empty subsets have (& of all their elements) == k", "B*2^B+N",
      `${MASK_NOTE} Without mod the counts are exact: Python's get as big as 2^N, C++ throws overflow_error past 62 values.`),
    "countAndSubsetsEqualToKForAllKMod", "countAndSubsetsEqualToKForAllKMod(arr, mod)", "for each k: how many non-empty subsets have (& of all their elements) == k, mod mod", "B*2^B+N"),
  withMod(
    card("countOrSubsetsEqualToKForAllK", "countOrSubsetsEqualToKForAllK(arr)", "for each k: how many non-empty subsets have (| of all their elements) == k", "B*2^B+N",
      `${MASK_NOTE} Without mod the counts are exact: Python's get as big as 2^N, C++ throws overflow_error past 62 values.`),
    "countOrSubsetsEqualToKForAllKMod", "countOrSubsetsEqualToKForAllKMod(arr, mod)", "for each k: how many non-empty subsets have (| of all their elements) == k, mod mod", "B*2^B+N"),
  card("countAndPairsEqualToKForAllK", "countAndPairsEqualToKForAllK(arr)", "for each k: how many pairs (i, j) with i < j have arr[i] & arr[j] == k", "B*2^B+N", MASK_NOTE),
  card("countOrPairsEqualToKForAllK", "countOrPairsEqualToKForAllK(arr)", "for each k: how many pairs (i, j) with i < j have arr[i] | arr[j] == k", "B*2^B+N", MASK_NOTE),
  card("sumOfOrPairsEqualToKForAllK", "sumOfOrPairsEqualToKForAllK(arr1, arr2)", "for each k: the sum of arr1[i] × arr2[j] over every i and every j with i | j == k", "B*2^B",
    "arr1 and arr2 both have length 2^B (an OR convolution)."),
  card("sumOfAndPairsEqualToKForAllK", "sumOfAndPairsEqualToKForAllK(arr1, arr2)", "for each k: the sum of arr1[i] × arr2[j] over every i and every j with i & j == k", "B*2^B",
    "arr1 and arr2 both have length 2^B (an AND convolution)."),
];

export const XOR_CONVOLUTION: FillIn[] = [
  withMod(
    card("sumOfXorPairsEqualToKForAllK", "sumOfXorPairsEqualToKForAllK(arr1, arr2)", "for each k: the sum of arr1[i] × arr2[j] over every i and every j with i ^ j == k", "B*2^B",
      "arr1 and arr2 both have length 2^B (an XOR convolution). Without mod, C++ is exact while (sum of |arr1|) · (sum of |arr2|) fits in long long; past that use With mod (mod must be odd)."),
    "sumOfXorPairsEqualToKForAllKMod", "sumOfXorPairsEqualToKForAllKMod(arr1, arr2, mod)", "for each k: the sum of arr1[i] × arr2[j] over every i and every j with i ^ j == k, mod mod", "B*2^B+log(MOD)"),
  card("countXorPairsEqualToKForAllK", "countXorPairsEqualToKForAllK(arr)", "for each k: how many pairs (i, j) with i < j have arr[i] ^ arr[j] == k", "B*2^B+N", MASK_NOTE),
];

const SUM_NOTE = "Values must be >= 0. Without mod, C++ throws overflow_error if the exact answer doesn't fit in long long (the With mod version never does).";

export const BIT_SUMS: FillIn[] = (
  [
    ["sumOfPairXors", "sumOfPairXors(arr)", "sum of arr[i] ^ arr[j] over every pair i < j"],
    ["sumOfPairAnds", "sumOfPairAnds(arr)", "sum of arr[i] & arr[j] over every pair i < j"],
    ["sumOfPairOrs", "sumOfPairOrs(arr)", "sum of arr[i] | arr[j] over every pair i < j"],
    ["sumOfSubarrayXors", "sumOfSubarrayXors(arr)", "sum of the XOR of every non-empty subarray"],
    ["sumOfSubarrayAnds", "sumOfSubarrayAnds(arr)", "sum of the AND of every non-empty subarray"],
    ["sumOfSubarrayOrs", "sumOfSubarrayOrs(arr)", "sum of the OR of every non-empty subarray"],
  ] as const
).map(([file, call, returns]) =>
  withMod(card(file, call, returns, "N*B", SUM_NOTE), `${file}Mod`, `${file}Mod(arr, mod)`, `${returns}, mod mod`, "N*B"),
);

// ---- the Bit ops & Bitset tab as rows (components/RowTemplates.tsx), grouped by what you want to compute

const ALL_CARDS = [...SOS_DP, ...XOR_CONVOLUTION, ...BIT_SUMS];
const byFile = (file: string) => {
  const f = ALL_CARDS.find((c) => c.file === file);
  if (!f) throw new Error(`no bit operations card for ${file}`);
  return f;
};

// what a one-function card shows on its row: its call, what it computes, its cost (and the same for its mod version)
function version(f: FillIn): RowVersion {
  const [op, cost] = f.ops[0];
  const [call, does] = op.split(" -> ");
  return { call, does, cost: bigO(cost), fillIn: { ...f, variant: undefined } };
}
function choice(key: string, title: string, file: string): RowChoice {
  const f = byFile(file);
  const on = f.variant?.on;
  return {
    key,
    title,
    ...version(f),
    ...(on ? { mod: version({ ...f, ...on, variant: undefined } as FillIn) } : {}),
  };
}
// the AND / OR / XOR versions of one function: name(op) gives each one's file
const OPS = [
  ["AND", "And"],
  ["OR", "Or"],
  ["XOR", "Xor"],
] as const;
function byOp(name: (op: string) => string, ops: readonly (readonly [string, string])[] = OPS): RowChoice[] {
  return ops.map(([key, op]) => choice(key, `${key}: ${name(op)}`, name(op)));
}
// a class with many operations: its name and a summary; the drawer lists every operation
function whole(f: FillIn, call: string, does: string): RowChoice {
  return { key: call, call, does, cost: "", fillIn: f };
}

export const BIT_OPS_SECTIONS: RowSection[] = [
  {
    title: "Bitset",
    rows: [
      {
        id: "bitset",
        choices: [whole(BITSETS[0], "DynamicBitset", "n bits, n chosen at runtime (C++ only): read / set / flip single bits, grow and shrink, whole-bitset operations")],
      },
    ],
  },
  {
    title: "XOR basis",
    rows: [
      { id: "xor-basis", choices: [whole(byXorBasis("XorBasis"), "XorBasis", "max / min / kth subset XOR, how many distinct subset XORs, how many subsets make x")] },
      { id: "range-xor-basis", choices: [whole(byXorBasis("RangeXorBasis"), "RangeXorBasis", "max subset XOR / can make x, within any subarray [l, r]")] },
    ],
  },
  {
    title: "Count pairs",
    note: "pairs (i, j) with i < j, for every value k at once",
    rows: [{ id: "count-pairs", choices: byOp((op) => `count${op}PairsEqualToKForAllK`) }],
  },
  {
    title: "Count subsets",
    note: "non-empty subsets, for every value k at once",
    rows: [{ id: "count-subsets", choices: byOp((op) => `count${op}SubsetsEqualToKForAllK`, OPS.slice(0, 2)) }],
  },
  {
    title: "Sum of arr1[i] × arr2[j] over index pairs",
    note: "every i and every j, for every value k at once (a convolution)",
    rows: [{ id: "pair-products", choices: byOp((op) => `sumOf${op}PairsEqualToKForAllK`) }],
  },
  {
    title: "Sums over pairs and subarrays of one array",
    rows: [
      { id: "pair-sums", choices: byOp((op) => `sumOfPair${op}s`) },
      { id: "subarray-sums", choices: byOp((op) => `sumOfSubarray${op}s`) },
    ],
  },
  {
    title: "Submask / supermask sums",
    note: "SOS DP over a list with one number per mask",
    rows: [
      { id: "subset-sums", choices: [choice("sub", "subsetSums", "subsetSums")] },
      { id: "superset-sums", choices: [choice("super", "supersetSums", "supersetSums")] },
    ],
  },
];

function byXorBasis(file: string) {
  const f = XOR_BASIS.find((c) => c.file === file);
  if (!f) throw new Error(`no XOR basis card for ${file}`);
  return f;
}
