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
  | "maxPrefixSum"
  | "maxSuffixSum"
  | "rangeLcm"
  | "rangeAndQuery"
  | "rangeOrQuery"
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
  | "leftmostPrefixSumGteX"
  | "leftmostPrefixSumGtX"
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
          { id: "kthOccurrence", signature: "kthOccurrence(l, r, k)", description: "Index of the k-th occurrence in [l, r] of the value set at build" },
        ],
      },
    ],
  },
];

// Ordered lightest to heaviest constant factor; used to break ties between templates.
export const DATA_STRUCTURE_TYPES = [
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
  "sparse-table": "Sparse table",
  BIT: "BIT",
  "seg-tree": "Seg tree",
  "lazy-seg-tree": "Lazy seg tree",
  "merge-sort-tree": "Merge sort tree",
  persistent: "Persistent seg tree",
  beats: "Seg tree beats",
  sqrt: "Sqrt decomposition",
};

export type TemplateLang = "py" | "cpp";

export const TEMPLATE_LANG_LABELS: Record<TemplateLang, string> = { py: "Python", cpp: "C++" };

export interface RangeQueryTemplate {
  // Folder under templates/range-queries holding template.py and/or template.cpp.
  folder: string;
  langs: TemplateLang[];
  operations: OpId[];
  dataStructureType: DataStructureType;
  // Per-operation cost from the @complexities tag, e.g. "log(N)", "log^2(N) amortized", "log(N)*log(U)", "?" (unknown).
  complexities: Partial<Record<OpId, string>>;
  build: string;
  memory: MemoryBreakdown;
  originalFileUrl?: string;
}

export type TreeLayout = "2n-iterative" | "pow2-iterative" | "4n-recursive" | "none";

export const TREE_LAYOUT_LABELS: Record<TreeLayout, string> = {
  "2n-iterative": "2N iterative tree (n leaves, bottom-up)",
  "pow2-iterative": "Iterative tree, 2·size with size the next power of two (2N to 4N)",
  "4n-recursive": "4N recursive tree",
  none: "Not a segment tree",
};

export const TREE_LAYOUT_SHORT: Record<TreeLayout, string | null> = {
  "2n-iterative": "2N iterative",
  "pow2-iterative": "2N–4N iterative",
  "4n-recursive": "4N recursive",
  none: null,
};

// Every array a template allocates, with its length (e.g. "4*N"), grouped by role. Totals are computed by the generator.
export interface MemoryGroup {
  arrays: { name: string; size: string }[];
  total: string;
}

export interface MemoryBreakdown {
  layout: TreeLayout;
  node: MemoryGroup;
  tags: MemoryGroup;
  other: MemoryGroup;
  note?: string;
  total: string;
}

// Typical contest sizes (N elements, values up to U), used to turn a cost string into a number for ranking.
const SIZES = { N: 2e5, U: 1e9 };
const FACTOR_VALUES: Record<string, number> = {
  "1": 1,
  N: SIZES.N,
  "log(N)": Math.log2(SIZES.N),
  "log^2(N)": Math.log2(SIZES.N) ** 2,
  "sqrt(N)": Math.sqrt(SIZES.N),
  "log(U)": Math.log2(SIZES.U),
  "log(log(U))": Math.log2(Math.log2(SIZES.U)),
};

export function costValue(cost: string): number {
  if (cost === "?") return Infinity;
  return cost
    .replace(/ amortized$/, "")
    .split("+")
    .reduce((sum, term) => sum + term.split("*").reduce((prod, f) => prod * factorValue(f), 1), 0);
}

const isConstant = (f: string) => /^\d+$/.test(f);
const factorValue = (f: string) => (isConstant(f) ? Number(f) : FACTOR_VALUES[f]);

// "36*N" -> "36N", "2*N*log(N)" -> "2N · log N"
function formatTerm(term: string): string {
  const factors = term.split("*");
  const constant = factors.filter(isConstant).reduce((prod, f) => prod * Number(f), 1);
  const rest = factors.filter((f) => !isConstant(f) && f !== "1").map((f) => PRETTY_FACTORS[f]);
  if (rest.length === 0) return String(constant);
  return (constant === 1 ? "" : String(constant)) + rest.join(" · ");
}

// Memory is a count of stored values, shown as a size with an explicit coefficient: "1N", "4N", "1N · log N", "3√N".
export function formatMemory(memory: string): string {
  if (memory === "0") return "0";
  return memory
    .split("+")
    .map((term) => {
      const factors = term.split("*");
      const constant = factors.filter(isConstant).reduce((prod, f) => prod * Number(f), 1);
      const rest = factors.filter((f) => !isConstant(f) && f !== "1").map((f) => PRETTY_FACTORS[f]);
      return rest.length ? `${constant}${rest.join(" · ")}` : String(constant);
    })
    .join(" + ");
}

const PRETTY_FACTORS: Record<string, string> = {
  "1": "1",
  N: "N",
  "log(N)": "log N",
  "log^2(N)": "log² N",
  "sqrt(N)": "√N",
  "log(U)": "log U",
  "log(log(U))": "log log U",
};

export function formatCost(cost: string): string {
  if (cost === "?") return "unknown";
  const amortized = cost.endsWith(" amortized");
  const body = cost
    .replace(/ amortized$/, "")
    .split("+")
    .map(formatTerm)
    .join(" + ");
  return `O(${body})${amortized ? " amortized" : ""}`;
}
