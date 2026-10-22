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
  | "kthGteX"
  | "kthGtX"
  | "kthLteX"
  | "kthLtX";

export interface Op {
  id: OpId;
  signature: string;
  description: string;
  // Show the arguments on the page; only for ops whose name doesn't explain them.
  showArgs?: true;
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
          { id: "rangeAddArithSeq", signature: "rangeAddArithSeq(l, r, start, step)", description: "a[l] += start, a[l+1] += start+step, …", showArgs: true },
          { id: "rangeMod", signature: "rangeMod(l, r, mod)", description: "a[i] %= mod", showArgs: true },
          { id: "rangeFloorDiv", signature: "rangeFloorDiv(l, r, divisor)", description: "a[i] = ⌊a[i] / divisor⌋", showArgs: true },
          { id: "rangeFloorSqrt", signature: "rangeFloorSqrt(l, r)", description: "a[i] = ⌊√a[i]⌋" },
        ],
      },
      {
        kind: "mod",
        ops: [
          { id: "rangeAddMod", signature: "rangeAddMod(l, r, v)", description: "a[i] += v  (mod p)" },
          { id: "rangeAssignMod", signature: "rangeAssignMod(l, r, v)", description: "a[i] = v  (mod p)" },
          { id: "rangeMultMod", signature: "rangeMultMod(l, r, m)", description: "a[i] = a[i] · m  (mod p)" },
          { id: "rangeAffineMod", signature: "rangeAffineMod(l, r, mult, add)", description: "Multiply then add: a[i] = a[i] · mult + add  (mod p)", showArgs: true },
          { id: "rangeAddArithSeqMod", signature: "rangeAddArithSeqMod(l, r, start, step)", description: "a[l] += start, a[l+1] += start+step, …  (mod p)", showArgs: true },
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
          { id: "countInValRange", signature: "countInValRange(l, r, lo, hi)", description: "# of values in a[l]…a[r] with lo ≤ value ≤ hi", showArgs: true },
          { id: "sumInValRange", signature: "sumInValRange(l, r, lo, hi)", description: "Sum of values in a[l]…a[r] with lo ≤ value ≤ hi", showArgs: true },
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
          { id: "leftmostPrefixSumGteX", signature: "leftmostPrefixSumGteX(l, r, x)", description: "First i in [l, r] with a[l] + … + a[i] ≥ x (needs a[i] ≥ 0; k-th one on a 0/1 array)", showArgs: true },
          { id: "leftmostPrefixSumGtX", signature: "leftmostPrefixSumGtX(l, r, x)", description: "First i in [l, r] with a[l] + … + a[i] > x (needs a[i] ≥ 0)", showArgs: true },
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
  "persistent",
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
  persistent: "Persistent seg tree",
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
  const base = DATA_STRUCTURE_TYPE_LABELS[t.dataStructureType];
  const fc = t.fractionalCascading === undefined ? "" : t.fractionalCascading ? " (FC)" : " (no FC)";
  if (t.file !== "sparse") return base + fc;
  const lower = base === "BIT" ? base : base[0].toLowerCase() + base.slice(1);
  const sparse = base.startsWith("Sparse") ? base : `Sparse ${lower}`; // "Sparse table" is already "sparse"
  return `${sparse}${isBuiltFromPoints(t.memory) ? " built from values" : ""}${fc}`;
}

