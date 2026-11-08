import type { FillIn } from "@/components/TemplatePicker";

// The bit operation templates (templates/ultimate-template-tool/bit-operations/), on the Bit ops & Bitset tab, Python
// and C++: the XOR basis classes, then one function per file and per card (SOS DP, XOR convolution, bit sums). The
// card's caption is what the function returns. B = number of bits in the largest value, N = number of values.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/";
const FOLDER = "_bit-operations";

const bigO = (cost: string) =>
  `O(${cost.replace(/\+/g, " + ").replace(/\*/g, " ").replace(/2\^B/g, "2ᴮ").replace(/B\^2/g, "B²").replace(/log\(MOD\)/g, "log MOD")})`;

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
  card("subsetSums", "subsetSums(f)", "g: g[mask] = sum of f[sub] over every submask sub of mask (len(f) = 2^B)", "B*2^B"),
  card("supersetSums", "supersetSums(f)", "g: g[mask] = sum of f[sup] over every supermask sup of mask (len(f) = 2^B)", "B*2^B"),
  card("countSubsetsByAnd", "countSubsetsByAnd(arr, mod)", "res: res[v] = number of non-empty subsets whose AND is exactly v, mod mod", "B*2^B+N", MASK_NOTE),
  card("countSubsetsByOr", "countSubsetsByOr(arr, mod)", "res: res[v] = number of non-empty subsets whose OR is exactly v, mod mod", "B*2^B+N", MASK_NOTE),
  card("countPairsByAnd", "countPairsByAnd(arr)", "res: res[v] = number of pairs i < j with arr[i] & arr[j] == v", "B*2^B+N", MASK_NOTE),
  card("countPairsByOr", "countPairsByOr(arr)", "res: res[v] = number of pairs i < j with arr[i] | arr[j] == v", "B*2^B+N", MASK_NOTE),
  card("orConvolution", "orConvolution(a, b)", "c: c[k] = sum of a[i] * b[j] over every i | j == k (len(a) = len(b) = 2^B)", "B*2^B"),
  card("andConvolution", "andConvolution(a, b)", "c: c[k] = sum of a[i] * b[j] over every i & j == k (len(a) = len(b) = 2^B)", "B*2^B"),
];

export const XOR_CONVOLUTION: FillIn[] = [
  card("xorConvolution", "xorConvolution(a, b)", "c: c[k] = sum of a[i] * b[j] over every i ^ j == k (len(a) = len(b) = 2^B)", "B*2^B",
    "C++ is exact while (sum of |a|) · (sum of |b|) fits in long long; past that use xorConvolutionMod."),
  card("xorConvolutionMod", "xorConvolutionMod(a, b, mod)", "c: c[k] = sum of a[i] * b[j] over every i ^ j == k, mod mod (mod odd)", "B*2^B+log(MOD)"),
  card("countPairsByXor", "countPairsByXor(arr)", "res: res[v] = number of pairs i < j with arr[i] ^ arr[j] == v", "B*2^B+N", MASK_NOTE),
];

const SUM_NOTE = "Values must be >= 0. C++ throws overflow_error if the exact answer doesn't fit in long long: use the Mod version.";

export const BIT_SUMS: FillIn[] = [
  card("sumOfPairXors", "sumOfPairXors(arr)", "sum of arr[i] ^ arr[j] over every pair i < j", "N*B", SUM_NOTE),
  card("sumOfPairAnds", "sumOfPairAnds(arr)", "sum of arr[i] & arr[j] over every pair i < j", "N*B", SUM_NOTE),
  card("sumOfPairOrs", "sumOfPairOrs(arr)", "sum of arr[i] | arr[j] over every pair i < j", "N*B", SUM_NOTE),
  card("sumOfSubarrayXors", "sumOfSubarrayXors(arr)", "sum of the XOR of every non-empty subarray", "N*B", SUM_NOTE),
  card("sumOfSubarrayAnds", "sumOfSubarrayAnds(arr)", "sum of the AND of every non-empty subarray", "N*B", SUM_NOTE),
  card("sumOfSubarrayOrs", "sumOfSubarrayOrs(arr)", "sum of the OR of every non-empty subarray", "N*B", SUM_NOTE),
  card("sumOfPairXorsMod", "sumOfPairXorsMod(arr, mod)", "sum of arr[i] ^ arr[j] over every pair i < j, mod mod", "N*B"),
  card("sumOfPairAndsMod", "sumOfPairAndsMod(arr, mod)", "sum of arr[i] & arr[j] over every pair i < j, mod mod", "N*B"),
  card("sumOfPairOrsMod", "sumOfPairOrsMod(arr, mod)", "sum of arr[i] | arr[j] over every pair i < j, mod mod", "N*B"),
  card("sumOfSubarrayXorsMod", "sumOfSubarrayXorsMod(arr, mod)", "sum of the XOR of every non-empty subarray, mod mod", "N*B"),
  card("sumOfSubarrayAndsMod", "sumOfSubarrayAndsMod(arr, mod)", "sum of the AND of every non-empty subarray, mod mod", "N*B"),
  card("sumOfSubarrayOrsMod", "sumOfSubarrayOrsMod(arr, mod)", "sum of the OR of every non-empty subarray, mod mod", "N*B"),
];
