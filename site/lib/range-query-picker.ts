import type { MemoryBreakdown, TemplateLang, TierKind, Usage } from "./template-picker";
import { isBuiltFromPoints } from "./template-picker";

export * from "./template-picker";

export type OpId =
  | "pointGet"
  | "pointAssign"
  | "pointAdd"
  | "pointChmax"
  | "pointChmin"
  | "rangeAdd"
  | "rangeAssign"
  | "rangeChmax"
  | "rangeChmin"
  | "rangeAddMod"
  | "rangeAssignMod"
  | "rangeMultMod"
  | "rangeAffineMod"
  | "rangeAddArithSeq"
  | "rangeAddArithSeqMod"
  | "rangeMod"
  | "rangeFloorDiv"
  | "rangeFloorSqrt"
  | "rangeAndApply"
  | "rangeOrApply"
  | "rangeXorApply"
  | "rangeSum"
  | "rangeSumMod"
  | "rangeMin"
  | "rangeMax"
  | "rangeGcd"
  | "maxSubarraySum"
  | "maxPrefixSum"
  | "maxSuffixSum"
  | "rangeAndQuery"
  | "rangeOrQuery"
  | "countOccurrences"
  | "countDistinct"
  | "allDistinct"
  | "rangeMode"
  | "countInValRange"
  | "sumInValRange"
  | "kthSmallest"
  | "kthLargest"
  | "medianLow"
  | "medianHigh"
  | "countLtX"
  | "countLteX"
  | "countGtX"
  | "countGteX"
  | "smallestGteX"
  | "smallestGtX"
  | "largestLteX"
  | "largestLtX"
  | "sumLtX"
  | "sumLteX"
  | "sumGtX"
  | "sumGteX"
  | "sumSmallestK"
  | "sumLargestK"
  | "sumKthSmallestRange"
  | "sumKthLargestRange"
  | "sumAbsDiffToX"
  | "sumAbsDiffToMedian"
  | "rangeMex"
  | "maxAltSubseqSum"
  | "longestEqualRun"
  | "rangeLIS"
  | "costMonoIncreasing"
  | "costMonoDecreasing"
  | "costStrictIncreasing"
  | "costStrictDecreasing"
  | "doAllElementsAppearEvenFrequency"
  | "leftmostGteX"
  | "leftmostGtX"
  | "rightmostGteX"
  | "rightmostGtX"
  | "leftmostLteX"
  | "leftmostLtX"
  | "rightmostLteX"
  | "rightmostLtX"
  | "leftmostPrefixSumGteX"
  | "leftmostPrefixSumGtX"
  | "rightmostSuffixSumGteX"
  | "rightmostSuffixSumGtX"
  | "kthGteX"
  | "kthGtX"
  | "kthLteX"
  | "kthLtX"
  | "pushBack"
  | "insertAt"
  | "eraseAt"
  | "eraseRange"
  | "rangeReverse"
  | "rangeRotateLeft"
  | "rangeRotateRight"
  | "moveRange";

export interface Op {
  id: OpId;
  signature: string;
  description: string;
}

export interface OpTier {
  kind: TierKind;
  // Overrides the badge text; the kind still sets the color.
  label?: string;
  ops: Op[];
}

export interface OpGroup {
  id: string;
  title: string;
  blurb: string;
  tiers: OpTier[];
}

export const OP_GROUPS: OpGroup[] = [
  {
    id: "point",
    title: "Point operations",
    blurb: "Read or change a single index.",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "pointGet", signature: "pointGet(i)", description: "Read a[i]" },
          { id: "pointAssign", signature: "pointAssign(i, v)", description: "a[i] = v" },
          { id: "pointAdd", signature: "pointAdd(i, v)", description: "a[i] += v" },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "pointChmax", signature: "pointChmax(i, v)", description: "a[i] = max(a[i], v)" },
          { id: "pointChmin", signature: "pointChmin(i, v)", description: "a[i] = min(a[i], v)" },
        ],
      },
    ],
  },
  {
    id: "range-updates",
    title: "Range updates",
    blurb: "Change every index in [l, r].",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "rangeAdd", signature: "rangeAdd(l, r, v)", description: "a[i] += v" },
          { id: "rangeAssign", signature: "rangeAssign(l, r, v)", description: "a[i] = v" },
          { id: "rangeChmax", signature: "rangeChmax(l, r, v)", description: "a[i] = max(a[i], v)" },
          { id: "rangeChmin", signature: "rangeChmin(l, r, v)", description: "a[i] = min(a[i], v)" },
        ],
      },
      {
        kind: "rare",
        label: "Other",
        ops: [
          { id: "rangeAddArithSeq", signature: "rangeAddArithSeq(l, r, start, step)", description: "a[l] += start, a[l+1] += start+step, …" },
          { id: "rangeMod", signature: "rangeMod(l, r, mod)", description: "a[i] %= mod" },
          { id: "rangeFloorDiv", signature: "rangeFloorDiv(l, r, divisor)", description: "a[i] = ⌊a[i] / divisor⌋" },
          { id: "rangeFloorSqrt", signature: "rangeFloorSqrt(l, r)", description: "a[i] = ⌊√a[i]⌋" },
        ],
      },
      {
        kind: "mod",
        ops: [
          { id: "rangeAddMod", signature: "rangeAddMod(l, r, v)", description: "a[i] += v  (mod p)" },
          { id: "rangeAssignMod", signature: "rangeAssignMod(l, r, v)", description: "a[i] = v  (mod p)" },
          { id: "rangeMultMod", signature: "rangeMultMod(l, r, m)", description: "a[i] = a[i] · m  (mod p)" },
          { id: "rangeAffineMod", signature: "rangeAffineMod(l, r, mult, add)", description: "Multiply then add: a[i] = a[i] · mult + add  (mod p)" },
          { id: "rangeAddArithSeqMod", signature: "rangeAddArithSeqMod(l, r, start, step)", description: "a[l] += start, a[l+1] += start+step, …  (mod p)" },
        ],
      },
      {
        kind: "bitOps",
        ops: [
          { id: "rangeXorApply", signature: "rangeXorApply(l, r, x)", description: "a[i] ^= x" },
          { id: "rangeAndApply", signature: "rangeAndApply(l, r, x)", description: "a[i] &= x" },
          { id: "rangeOrApply", signature: "rangeOrApply(l, r, x)", description: "a[i] |= x" },
        ],
      },
    ],
  },
  {
    id: "sequence",
    title: "Sequence edits",
    blurb: "Change the array's shape: insert, erase, reverse, move pieces. Later indices shift.",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "pushBack", signature: "pushBack(v)", description: "Append v to the end (n grows by 1)" },
          { id: "insertAt", signature: "insertAt(i, v)", description: "Insert v so it becomes a[i] (i = n appends)" },
          { id: "eraseAt", signature: "eraseAt(i)", description: "Remove a[i]" },
          { id: "rangeReverse", signature: "rangeReverse(l, r)", description: "Reverse a[l]…a[r]" },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "eraseRange", signature: "eraseRange(l, r)", description: "Remove a[l]…a[r]" },
          { id: "rangeRotateLeft", signature: "rangeRotateLeft(l, r, k)", description: "Cyclic shift a[l]…a[r] left by k (a[l+k] moves to l)" },
          { id: "rangeRotateRight", signature: "rangeRotateRight(l, r, k)", description: "Cyclic shift a[l]…a[r] right by k (a[r−k+1…r] move to the front)" },
          { id: "moveRange", signature: "moveRange(l, r, i)", description: "Cut a[l]…a[r] out and paste it back starting at index i" },
        ],
      },
    ],
  },
  {
    id: "range-queries",
    title: "Range queries",
    blurb: "Aggregate over [l, r].",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "rangeSum", signature: "rangeSum(l, r)", description: "a[l] + … + a[r]" },
          { id: "rangeMin", signature: "rangeMin(l, r)", description: "min of a[l]…a[r]" },
          { id: "rangeMax", signature: "rangeMax(l, r)", description: "max of a[l]…a[r]" },
          { id: "rangeGcd", signature: "rangeGcd(l, r)", description: "gcd of a[l]…a[r]" },
          { id: "countDistinct", signature: "countDistinct(l, r)", description: "# of distinct values in a[l]…a[r]" },
          { id: "maxSubarraySum", signature: "maxSubarraySum(l, r)", description: "Max sum of a non-empty contiguous subarray within a[l]…a[r]" },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "maxPrefixSum", signature: "maxPrefixSum(l, r)", description: "Max of a[l] + … + a[i] over i in [l, r]" },
          { id: "maxSuffixSum", signature: "maxSuffixSum(l, r)", description: "Max of a[i] + … + a[r] over i in [l, r]" },
          { id: "rangeMode", signature: "rangeMode(l, r)", description: "(mode, frequency) of a[l]…a[r]" },
          { id: "allDistinct", signature: "allDistinct(l, r)", description: "Are all values in a[l]…a[r] distinct?" },
          { id: "countOccurrences", signature: "countOccurrences(l, r, x)", description: "# of i in [l, r] with a[i] = x" },
        ],
      },
      {
        kind: "rare",
        ops: [
          { id: "rangeLIS", signature: "rangeLIS(l, r)", description: "Length of the longest strictly increasing subsequence of a[l]…a[r]" },
          { id: "costMonoIncreasing", signature: "costMonoIncreasing(l, r)", description: "Min +1 increments to make a[l]…a[r] non-decreasing" },
          { id: "costMonoDecreasing", signature: "costMonoDecreasing(l, r)", description: "Min +1 increments to make a[l]…a[r] non-increasing" },
          { id: "costStrictIncreasing", signature: "costStrictIncreasing(l, r)", description: "Min +1 increments to make a[l]…a[r] strictly increasing" },
          { id: "costStrictDecreasing", signature: "costStrictDecreasing(l, r)", description: "Min +1 increments to make a[l]…a[r] strictly decreasing" },
          { id: "maxAltSubseqSum", signature: "maxAltSubseqSum(l, r)", description: "Max alternating subsequence sum  +a − b + c …  in a[l]…a[r]" },
          { id: "longestEqualRun", signature: "longestEqualRun(l, r)", description: "Longest run of equal adjacent values in a[l]…a[r]" },
          { id: "doAllElementsAppearEvenFrequency", signature: "doAllElementsAppearEvenFrequency(l, r)", description: "Does every value in a[l]…a[r] appear an even # of times? (xor hashing)" },
        ],
      },
      {
        kind: "mod",
        ops: [{ id: "rangeSumMod", signature: "rangeSumMod(l, r)", description: "(a[l] + … + a[r])  mod p" }],
      },
      {
        kind: "bitOps",
        ops: [
          { id: "rangeAndQuery", signature: "rangeAndQuery(l, r)", description: "a[l] & … & a[r]" },
          { id: "rangeOrQuery", signature: "rangeOrQuery(l, r)", description: "a[l] | … | a[r]" },
        ],
      },
    ],
  },
  {
    id: "order",
    title: "Sorted view of a[l..r]",
    blurb: "Treat a[l]…a[r] as a sorted multiset (static array).",
    tiers: [
      {
        kind: "topic",
        label: "Rank",
        ops: [
          { id: "kthSmallest", signature: "kthSmallest(l, r, k)", description: "k-th smallest of a[l]…a[r] (k = 1 is the min)" },
          { id: "kthLargest", signature: "kthLargest(l, r, k)", description: "k-th largest of a[l]…a[r] (k = 1 is the max)" },
          { id: "medianLow", signature: "medianLow(l, r)", description: "Lower median: the ⌈len/2⌉-th smallest" },
          { id: "medianHigh", signature: "medianHigh(l, r)", description: "Upper median: the (⌊len/2⌋+1)-th smallest" },
        ],
      },
      {
        kind: "topic",
        label: "Nearest to x",
        ops: [
          { id: "smallestGteX", signature: "smallestGteX(l, r, x)", description: "Smallest value ≥ x in a[l]…a[r] (none if there isn't one)" },
          { id: "smallestGtX", signature: "smallestGtX(l, r, x)", description: "Smallest value > x in a[l]…a[r] (none if there isn't one)" },
          { id: "largestLteX", signature: "largestLteX(l, r, x)", description: "Largest value ≤ x in a[l]…a[r] (none if there isn't one)" },
          { id: "largestLtX", signature: "largestLtX(l, r, x)", description: "Largest value < x in a[l]…a[r] (none if there isn't one)" },
        ],
      },
      {
        kind: "topic",
        label: "Count",
        ops: [
          { id: "countLtX", signature: "countLtX(l, r, x)", description: "# of values < x in a[l]…a[r]" },
          { id: "countLteX", signature: "countLteX(l, r, x)", description: "# of values ≤ x in a[l]…a[r]" },
          { id: "countGtX", signature: "countGtX(l, r, x)", description: "# of values > x in a[l]…a[r]" },
          { id: "countGteX", signature: "countGteX(l, r, x)", description: "# of values ≥ x in a[l]…a[r]" },
          { id: "countInValRange", signature: "countInValRange(l, r, lo, hi)", description: "# of values in a[l]…a[r] with lo ≤ value ≤ hi" },
        ],
      },
      {
        kind: "topic",
        label: "Sum",
        ops: [
          { id: "sumLtX", signature: "sumLtX(l, r, x)", description: "Sum of the values < x in a[l]…a[r]" },
          { id: "sumLteX", signature: "sumLteX(l, r, x)", description: "Sum of the values ≤ x in a[l]…a[r]" },
          { id: "sumGtX", signature: "sumGtX(l, r, x)", description: "Sum of the values > x in a[l]…a[r]" },
          { id: "sumGteX", signature: "sumGteX(l, r, x)", description: "Sum of the values ≥ x in a[l]…a[r]" },
          { id: "sumInValRange", signature: "sumInValRange(l, r, lo, hi)", description: "Sum of values in a[l]…a[r] with lo ≤ value ≤ hi" },
        ],
      },
      {
        kind: "topic",
        label: "Sum by rank",
        ops: [
          { id: "sumSmallestK", signature: "sumSmallestK(l, r, k)", description: "Sum of the k smallest values in a[l]…a[r]" },
          { id: "sumLargestK", signature: "sumLargestK(l, r, k)", description: "Sum of the k largest values in a[l]…a[r]" },
          { id: "sumKthSmallestRange", signature: "sumKthSmallestRange(l, r, kFrom, kTo)", description: "Sum of the kFrom-th … kTo-th smallest values in a[l]…a[r] (1-indexed ranks)" },
          { id: "sumKthLargestRange", signature: "sumKthLargestRange(l, r, kFrom, kTo)", description: "Sum of the kFrom-th … kTo-th largest values in a[l]…a[r] (1-indexed ranks)" },
        ],
      },
      {
        kind: "topic",
        label: "Distance",
        ops: [
          { id: "sumAbsDiffToMedian", signature: "sumAbsDiffToMedian(l, r)", description: "Min total ±1 moves to make a[l]…a[r] all equal (Σ |a[i] − median|)" },
          { id: "sumAbsDiffToX", signature: "sumAbsDiffToX(l, r, x)", description: "Σ |a[i] − x| over a[l]…a[r]" },
        ],
      },
      {
        kind: "topic",
        label: "Mex",
        ops: [
          { id: "rangeMex", signature: "rangeMex(l, r)", description: "Smallest integer ≥ 0 missing from a[l]…a[r]" },
        ],
      },
    ],
  },
  {
    id: "search",
    title: "Search (tree walks)",
    blurb: "Descend the tree to find an index.",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "leftmostGteX", signature: "leftmostGteX(l, r, x)", description: "First i in [l, r] with a[i] ≥ x" },
          { id: "leftmostGtX", signature: "leftmostGtX(l, r, x)", description: "First i in [l, r] with a[i] > x" },
          { id: "rightmostGteX", signature: "rightmostGteX(l, r, x)", description: "Last i in [l, r] with a[i] ≥ x" },
          { id: "rightmostGtX", signature: "rightmostGtX(l, r, x)", description: "Last i in [l, r] with a[i] > x" },
          { id: "leftmostLteX", signature: "leftmostLteX(l, r, x)", description: "First i in [l, r] with a[i] ≤ x" },
          { id: "leftmostLtX", signature: "leftmostLtX(l, r, x)", description: "First i in [l, r] with a[i] < x" },
          { id: "rightmostLteX", signature: "rightmostLteX(l, r, x)", description: "Last i in [l, r] with a[i] ≤ x" },
          { id: "rightmostLtX", signature: "rightmostLtX(l, r, x)", description: "Last i in [l, r] with a[i] < x" },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "kthGteX", signature: "kthGteX(l, r, k, x)", description: "Index of the k-th i in [l, r] with a[i] ≥ x" },
          { id: "kthGtX", signature: "kthGtX(l, r, k, x)", description: "Index of the k-th i in [l, r] with a[i] > x" },
          { id: "kthLteX", signature: "kthLteX(l, r, k, x)", description: "Index of the k-th i in [l, r] with a[i] ≤ x" },
          { id: "kthLtX", signature: "kthLtX(l, r, k, x)", description: "Index of the k-th i in [l, r] with a[i] < x" },
          { id: "leftmostPrefixSumGteX", signature: "leftmostPrefixSumGteX(l, r, x)", description: "First i in [l, r] with a[l] + … + a[i] ≥ x (needs a[i] ≥ 0; k-th one on a 0/1 array)" },
          { id: "leftmostPrefixSumGtX", signature: "leftmostPrefixSumGtX(l, r, x)", description: "First i in [l, r] with a[l] + … + a[i] > x (needs a[i] ≥ 0)" },
          { id: "rightmostSuffixSumGteX", signature: "rightmostSuffixSumGteX(l, r, x)", description: "Last i in [l, r] with a[i] + … + a[r] ≥ x (needs a[i] ≥ 0)" },
          { id: "rightmostSuffixSumGtX", signature: "rightmostSuffixSumGtX(l, r, x)", description: "Last i in [l, r] with a[i] + … + a[r] > x (needs a[i] ≥ 0)" },
        ],
      },
    ],
  },
];

// Ordered lightest to heaviest constant factor; used to break ties between templates.
export const DATA_STRUCTURE_TYPES = [
  "positions",
  "sparse-table",
  "BIT",
  "seg-tree",
  "lazy-seg-tree",
  "merge-sort-tree",
  "wavelet",
  "persistent",
  "bit-of-trees",
  "treap",
  "beats",
  "sqrt",
] as const;

export type DataStructureType = (typeof DATA_STRUCTURE_TYPES)[number];

export const DATA_STRUCTURE_TYPE_LABELS: Record<DataStructureType, string> = {
  positions: "Position lists",
  "sparse-table": "Sparse table",
  BIT: "BIT",
  "seg-tree": "Seg tree",
  "lazy-seg-tree": "Lazy seg tree",
  "merge-sort-tree": "Merge sort tree",
  wavelet: "Wavelet matrix",
  persistent: "Persistent seg tree",
  "bit-of-trees": "BIT of value seg trees",
  treap: "Implicit treap",
  beats: "Seg tree beats",
  sqrt: "Sqrt decomposition",
};

export interface RangeQueryTemplate {
  // Folder under templates/range-queries holding template.py and/or template.cpp.
  folder: string;
  langs: TemplateLang[];
  operations: OpId[];
  dataStructureType: DataStructureType;
  // merge sort trees only: whether queries use fractional cascading (one root search, then prefix counts per level)
  fractionalCascading?: boolean;
  // the constructor needs every value that will ever be added up front (to compress them); costs are then log N, not log U
  valuesOffline?: true;
  // Per-operation cost from the @complexities tag, e.g. "log(N)", "log^2(N) amortized", "log(N)*log(U)", "log(N)+log(U) ?" (a trailing ? marks a bound we are unsure of).
  complexities: Partial<Record<OpId, string>>;
  build: string;
  memory: MemoryBreakdown;
  originalFileUrl?: string;
  // The same operations over any index range [lo, hi]: a dynamic structure where every position starts at 0 (costs
  // use U = size of that range, log U <= 64, and memory sizes are per update), or, for a static template, one built
  // from N given values ((index, value) pairs) with every other index 0 (costs and memory in N).
  sparse?: SparseVariant;
  usage: Partial<Record<TemplateLang, Usage>>;
}

export interface SparseVariant {
  langs: TemplateLang[];
  complexities: Partial<Record<OpId, string>>;
  build: string;
  memory: MemoryBreakdown;
  usage: Partial<Record<TemplateLang, Usage>>;
}

// A template as the picker shows it in the current mode: in sparse mode, its costs / memory / files are the sparse ones.
export type TemplateView = RangeQueryTemplate & { file: "template" | "sparse" };

export function viewOf(t: RangeQueryTemplate, sparse: boolean): TemplateView | null {
  if (!sparse) return { ...t, file: "template" };
  if (!t.sparse) return null;
  return { ...t, ...t.sparse, file: "sparse" };
}

// What a card calls the structure: "Lazy seg tree", "Sparse lazy seg tree", "Sparse seg tree beats", for a static
// structure's sparse version "Sparse merge sort tree built from values", and merge sort trees add "(FC)" / "(no FC)".
export function templateKindLabel(t: TemplateView): string {
  // a wavelet with rangeMex also carries a persistent seg tree for it
  const mex = t.dataStructureType === "wavelet" && t.operations.includes("rangeMex") ? " + persistent mex tree" : "";
  // the persistent trees that grow by pushBack are over the value range, not compressed values
  const appendable =
    t.dataStructureType !== "persistent" || !t.operations.includes("pushBack")
      ? ""
      : t.valuesOffline
        ? " (appendable, every value known up front)"
        : " over values (appendable)";
  const base = DATA_STRUCTURE_TYPE_LABELS[t.dataStructureType] + mex + appendable;
  const fc = t.fractionalCascading === undefined ? "" : t.fractionalCascading ? " (FC)" : " (no FC)";
  if (t.file !== "sparse") return base + fc;
  // lowercase the first word after "Sparse", unless it's an acronym ("BIT", "BIT of value seg trees")
  const lower = /^[A-Z]{2,}\b/.test(base) ? base : base[0].toLowerCase() + base.slice(1);
  const sparse = base.startsWith("Sparse") ? base : `Sparse ${lower}`; // "Sparse table" is already "sparse"
  return `${sparse}${isBuiltFromPoints(t.memory) ? " built from values" : ""}${fc}`;
}

