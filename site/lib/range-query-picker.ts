export type OpId =
  | "pointGet"
  | "pointSet"
  | "pointAdd"
  | "pointChmax"
  | "pointChmin"
  | "rangeAdd"
  | "rangeAssign"
  | "rangeChmax"
  | "rangeChmin"
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
  | "rangeMin"
  | "rangeMax"
  | "countMin"
  | "countMax"
  | "rangeGcd"
  | "maxSubarraySum"
  | "rangeLcm"
  | "rangeAndQuery"
  | "rangeOrQuery"
  | "rangeXorQuery"
  | "countValue"
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
  | "kthOccurrence"
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

export type TierKind = "common" | "uncommon" | "rare" | "bitOps";

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
          { id: "pointSet", signature: "pointSet(i, v)", description: "a[i] = v" },
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
          { id: "rangeMultMod", signature: "rangeMultMod(l, r, m)", description: "a[i] = a[i] · m  (mod p)" },
          { id: "rangeAffineMod", signature: "rangeAffineMod(l, r, m, b)", description: "Multiply then add: a[i] = a[i] · m + b  (mod p)", showArgs: true },
          { id: "rangeAddArithSeq", signature: "rangeAddArithSeq(l, r, start, step)", description: "a[l] += start, a[l+1] += start+step, …", showArgs: true },
          { id: "rangeAddArithSeqMod", signature: "rangeAddArithSeqMod(l, r, start, step)", description: "Same, under mod p", showArgs: true },
          { id: "rangeMod", signature: "rangeMod(l, r, mod)", description: "a[i] %= mod", showArgs: true },
          { id: "rangeFloorDiv", signature: "rangeFloorDiv(l, r, divisor)", description: "a[i] = ⌊a[i] / divisor⌋", showArgs: true },
          { id: "rangeFloorSqrt", signature: "rangeFloorSqrt(l, r)", description: "a[i] = ⌊√a[i]⌋" },
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
          { id: "maxSubarraySum", signature: "maxSubarraySum(l, r)", description: "Max sum of a contiguous subarray within a[l]…a[r]" },
          { id: "countInValRange", signature: "countInValRange(l, r, lo, hi)", description: "# of values in a[l]…a[r] with lo ≤ value ≤ hi", showArgs: true },
          { id: "sumInValRange", signature: "sumInValRange(l, r, lo, hi)", description: "Sum of values in a[l]…a[r] with lo ≤ value ≤ hi", showArgs: true },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "countMin", signature: "countMin(l, r)", description: "# of values in a[l]…a[r] equal to the min" },
          { id: "countMax", signature: "countMax(l, r)", description: "# of values in a[l]…a[r] equal to the max" },
          { id: "rangeLcm", signature: "rangeLcm(l, r)", description: "lcm of a[l]…a[r]" },
          { id: "rangeMode", signature: "rangeMode(l, r)", description: "(mode, frequency) of a[l]…a[r]" },
          { id: "allDistinct", signature: "allDistinct(l, r)", description: "Are all values in a[l]…a[r] distinct?" },
          { id: "countValue", signature: "countValue(l, r)", description: "# of times the value set at build appears in a[l]…a[r]" },
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
        kind: "bitOps",
        ops: [
          { id: "rangeXorQuery", signature: "rangeXorQuery(l, r)", description: "a[l] ^ … ^ a[r]" },
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
          { id: "kthOccurrence", signature: "kthOccurrence(l, r, k)", description: "Index of the k-th occurrence in [l, r] of the value set at build" },
        ],
      },
    ],
  },
];

// Ordered lightest to heaviest constant factor; used to break ties between templates.
export const TEMPLATE_KINDS = [
  "sparse-table",
  "BIT",
  "seg-tree",
  "lazy-seg-tree",
  "merge-sort-tree",
  "persistent",
  "beats",
  "sqrt",
] as const;

export type TemplateKind = (typeof TEMPLATE_KINDS)[number];

export const TEMPLATE_KIND_LABELS: Record<TemplateKind, string> = {
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
  file: string;
  lang: "py" | "cpp";
  ops: OpId[];
  kind: TemplateKind;
  // Per-op cost from the @complexity tag, e.g. "logN", "log2N~" (amortized), "logN*logV", "?" (unknown).
  complexity: Partial<Record<OpId, string>>;
  build: string;
  source: string;
}

// Typical contest sizes, used to turn a cost string into a number for ranking.
const SIZES = { N: 2e5, V: 1e9 };
const FACTOR_VALUES: Record<string, number> = {
  "1": 1,
  logN: Math.log2(SIZES.N),
  log2N: Math.log2(SIZES.N) ** 2,
  sqrtN: Math.sqrt(SIZES.N),
  N: SIZES.N,
  NlogN: SIZES.N * Math.log2(SIZES.N),
  NsqrtN: SIZES.N * Math.sqrt(SIZES.N),
  logV: Math.log2(SIZES.V),
  loglogV: Math.log2(Math.log2(SIZES.V)),
};

export function costValue(cost: string): number {
  if (cost === "?") return Infinity;
  return cost
    .replace(/~$/, "")
    .split("+")
    .reduce((sum, term) => sum + term.split("*").reduce((prod, f) => prod * FACTOR_VALUES[f], 1), 0);
}

const PRETTY_FACTORS: Record<string, string> = {
  "1": "1",
  logN: "log N",
  log2N: "log² N",
  sqrtN: "√N",
  N: "N",
  NlogN: "N log N",
  NsqrtN: "N√N",
  logV: "log V",
  loglogV: "log log V",
};

export function formatCost(cost: string): string {
  if (cost === "?") return "unknown";
  const amortized = cost.endsWith("~");
  const body = cost
    .replace(/~$/, "")
    .split("+")
    .map((term) => term.split("*").map((f) => PRETTY_FACTORS[f]).join(" · "))
    .join(" + ");
  return `O(${body})${amortized ? " amortized" : ""}`;
}
