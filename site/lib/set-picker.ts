// The ordered-multiset picker: operations, structure types and template shape. Shared picker types and formatting
// live in ./template-picker.
import type {
  MemoryBreakdown,
  PickerOpGroup,
  TemplateLang,
} from "./template-picker";

export type SetOpId =
  | "add"
  | "addCount"
  | "remove"
  | "removeCount"
  | "removeAll"
  | "popMin"
  | "popMax"
  | "pop"
  | "clear"
  | "removeInValRange"
  | "sumAbsDiffToMedian"
  | "sumAbsDiffToX"
  | "medianLow"
  | "medianHigh"
  | "size"
  | "min"
  | "max"
  | "mex"
  | "sumAll"
  | "countDistinct"
  | "mode"
  | "minAdjacentDiff"
  | "maxXor"
  | "minXor"
  | "kthXor"
  | "countXorLtK"
  | "countXorLteK"
  | "countXorGtK"
  | "countXorGteK"
  | "largestXorLtK"
  | "largestXorLteK"
  | "smallestXorGtK"
  | "smallestXorGteK"
  | "mexXor"
  | "sumXor"
  | "maxXorWithVLtM"
  | "maxXorWithVLteM"
  | "maxXorWithVGtM"
  | "maxXorWithVGteM"
  | "minXorWithVLtM"
  | "minXorWithVLteM"
  | "minXorWithVGtM"
  | "minXorWithVGteM"
  | "maxXorWithVInValRange"
  | "minXorWithVInValRange"
  | "xorAll"
  | "maxGap"
  | "kth"
  | "sumSmallestK"
  | "sumLargestK"
  | "sumKthSmallestRange"
  | "sumKthLargestRange"
  | "count"
  | "firstIndex"
  | "lastIndex"
  | "countLtX"
  | "countLteX"
  | "countGtX"
  | "countGteX"
  | "largestLteX"
  | "smallestGteX"
  | "largestLtX"
  | "smallestGtX"
  | "countInValRange"
  | "countDistinctInValRange"
  | "sumLtX"
  | "sumLteX"
  | "sumGtX"
  | "sumGteX"
  | "sumInValRange"
  | "xorOfAll"
  | "xorOfLtX"
  | "xorOfLteX"
  | "xorOfGtX"
  | "xorOfGteX"
  | "xorOfInValRange"
  | "xorOfSmallestK"
  | "xorOfLargestK"
  | "xorOfKthSmallestRange"
  | "xorOfKthLargestRange"
  | "orOfAll"
  | "orOfLtX"
  | "orOfLteX"
  | "orOfGtX"
  | "orOfGteX"
  | "orOfInValRange"
  | "orOfSmallestK"
  | "orOfLargestK"
  | "orOfKthSmallestRange"
  | "orOfKthLargestRange"
  | "andOfAll"
  | "andOfLtX"
  | "andOfLteX"
  | "andOfGtX"
  | "andOfGteX"
  | "andOfInValRange"
  | "andOfSmallestK"
  | "andOfLargestK"
  | "andOfKthSmallestRange"
  | "andOfKthLargestRange"
  | "shiftAll";

export const SET_OP_GROUPS: PickerOpGroup[] = [
  {
    id: "updates",
    title: "Add / remove",
    tiers: [
      {
        kind: "topic",
        ops: [
          { id: "add", signature: "add(x)", description: "Add one copy of x" },
          {
            id: "addCount",
            signature: "addCount(val, cnt)",
            description: "Add cnt copies of val",
          },
          {
            id: "remove",
            signature: "remove(x)",
            description: "Remove one copy of x (if present)",
          },
          {
            id: "removeCount",
            signature: "removeCount(val, cnt)",
            description: "Remove up to cnt copies of val",
          },
          {
            id: "removeAll",
            signature: "removeAll(val)",
            description: "Remove every copy of val",
          },
          {
            id: "removeInValRange",
            signature: "removeInValRange(lo, hi)",
            description: "Remove every value in [lo, hi]",
          },
          {
            id: "popMin",
            signature: "popMin()",
            description: "Remove and return the smallest value",
          },
          {
            id: "popMax",
            signature: "popMax()",
            description: "Remove and return the largest value",
          },
          {
            id: "xorAll",
            signature: "xorAll(y)",
            description: "Replace every value v by v ^ y",
          },
          {
            id: "shiftAll",
            signature: "shiftAll(d)",
            description: "Add d to every value (d may be negative)",
          },
          {
            id: "pop",
            signature: "pop(i)",
            description:
              "Remove and return the value at sorted position i (0-indexed)",
          },
        ],
      },
    ],
  },
  {
    id: "whole",
    title: "Whole set",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "size",
            signature: "size()",
            description: "How many values (copies count)",
          },
          { id: "min", signature: "min()", description: "Smallest value" },
          { id: "max", signature: "max()", description: "Largest value" },
          {
            id: "mex",
            signature: "mex()",
            description: "Smallest non-negative integer not in the set",
          },
          {
            id: "sumAll",
            signature: "sumAll()",
            description: "Sum of all values",
          },
          {
            id: "countDistinct",
            signature: "countDistinct()",
            description: "How many distinct values",
          },
          {
            id: "mode",
            signature: "mode()",
            description: "(most frequent value, its count)",
          },
        ],
      },
    ],
  },
  {
    id: "hoisting",
    title: "Hoisting",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "clear",
            signature: "clear()",
            description:
              "Empty it, to reuse instead of building a new one (no other op pays for this)",
          },
        ],
      },
    ],
  },
  {
    id: "rank",
    title: "By rank",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "kth",
            signature: "kth(i)",
            description:
              "Value at sorted position i (0-indexed: kth(0) is the min)",
          },
        ],
      },
    ],
  },
  {
    id: "indices",
    title: "Indices",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "firstIndex",
            signature: "firstIndex(x)",
            description:
              "Position of the first copy of x in sorted order (0-indexed), or -1 if x isn't in the set",
          },
          {
            id: "lastIndex",
            signature: "lastIndex(x)",
            description:
              "Position of the last copy of x in sorted order (0-indexed), or -1 if x isn't in the set",
          },
        ],
      },
    ],
  },
  {
    id: "value",
    title: "By value",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "count",
            signature: "count(x)",
            description: "How many copies of x",
          },
          {
            id: "countLtX",
            signature: "countLtX(x)",
            description: "How many values < x",
          },
          {
            id: "countLteX",
            signature: "countLteX(x)",
            description: "How many values ≤ x",
          },
          {
            id: "countGtX",
            signature: "countGtX(x)",
            description: "How many values > x",
          },
          {
            id: "countGteX",
            signature: "countGteX(x)",
            description: "How many values ≥ x",
          },
          {
            id: "largestLteX",
            signature: "largestLteX(x)",
            description: "Largest value ≤ x (floor)",
          },
          {
            id: "smallestGteX",
            signature: "smallestGteX(x)",
            description: "Smallest value ≥ x (ceiling)",
          },
          {
            id: "largestLtX",
            signature: "largestLtX(x)",
            description: "Largest value < x",
          },
          {
            id: "smallestGtX",
            signature: "smallestGtX(x)",
            description: "Smallest value > x",
          },
          {
            id: "countInValRange",
            signature: "countInValRange(lo, hi)",
            description: "How many values in [lo, hi]",
          },
          {
            id: "countDistinctInValRange",
            signature: "countDistinctInValRange(lo, hi)",
            description: "How many distinct values in [lo, hi]",
          },
        ],
      },
    ],
  },
  {
    id: "sums",
    title: "Sums",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "sumSmallestK",
            signature: "sumSmallestK(k)",
            description: "Sum of the k smallest values",
          },
          {
            id: "sumLargestK",
            signature: "sumLargestK(k)",
            description: "Sum of the k largest values",
          },
          {
            id: "sumKthSmallestRange",
            signature: "sumKthSmallestRange(kFrom, kTo)",
            description:
              "Sum of the kFrom-th..kTo-th smallest values (1-indexed ranks)",
          },
          {
            id: "sumKthLargestRange",
            signature: "sumKthLargestRange(kFrom, kTo)",
            description:
              "Sum of the kFrom-th..kTo-th largest (e.g. 5th..8th biggest)",
          },
          {
            id: "sumLtX",
            signature: "sumLtX(x)",
            description: "Sum of the values < x",
          },
          {
            id: "sumLteX",
            signature: "sumLteX(x)",
            description: "Sum of the values ≤ x",
          },
          {
            id: "sumGtX",
            signature: "sumGtX(x)",
            description: "Sum of the values > x",
          },
          {
            id: "sumGteX",
            signature: "sumGteX(x)",
            description: "Sum of the values ≥ x",
          },
          {
            id: "sumInValRange",
            signature: "sumInValRange(lo, hi)",
            description: "Sum of the values in [lo, hi]",
          },
        ],
      },
    ],
  },
  {
    id: "median",
    title: "Median",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "sumAbsDiffToMedian",
            signature: "sumAbsDiffToMedian()",
            description:
              "Σ|v − median|: min total moves to make all values equal",
          },
          {
            id: "sumAbsDiffToX",
            signature: "sumAbsDiffToX(x)",
            description: "Σ|v − x|: total moves to bring every value to x",
          },
          {
            id: "medianLow",
            signature: "medianLow()",
            description: "Lower median (the ⌈n/2⌉-th smallest)",
          },
          {
            id: "medianHigh",
            signature: "medianHigh()",
            description: "Upper median (the (⌊n/2⌋+1)-th smallest)",
          },
        ],
      },
    ],
  },
  {
    id: "xorOf",
    title: "XOR of values",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "xorOfAll",
            signature: "xorOfAll()",
            description: "XOR of all values (copies count: an even count cancels)",
          },
          {
            id: "xorOfLtX",
            signature: "xorOfLtX(x)",
            description: "XOR of the values < x",
          },
          {
            id: "xorOfLteX",
            signature: "xorOfLteX(x)",
            description: "XOR of the values ≤ x",
          },
          {
            id: "xorOfGtX",
            signature: "xorOfGtX(x)",
            description: "XOR of the values > x",
          },
          {
            id: "xorOfGteX",
            signature: "xorOfGteX(x)",
            description: "XOR of the values ≥ x",
          },
          {
            id: "xorOfInValRange",
            signature: "xorOfInValRange(lo, hi)",
            description: "XOR of the values in [lo, hi]",
          },
          {
            id: "xorOfSmallestK",
            signature: "xorOfSmallestK(k)",
            description: "XOR of the k smallest values",
          },
          {
            id: "xorOfLargestK",
            signature: "xorOfLargestK(k)",
            description: "XOR of the k largest values",
          },
          {
            id: "xorOfKthSmallestRange",
            signature: "xorOfKthSmallestRange(kFrom, kTo)",
            description: "XOR of the kFrom-th..kTo-th smallest values (1-indexed ranks)",
          },
          {
            id: "xorOfKthLargestRange",
            signature: "xorOfKthLargestRange(kFrom, kTo)",
            description: "XOR of the kFrom-th..kTo-th largest values (1-indexed ranks)",
          },
        ],
      },
    ],
  },
  {
    id: "orOf",
    title: "OR of values",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "orOfAll",
            signature: "orOfAll()",
            description: "OR of all values (0 if empty)",
          },
          {
            id: "orOfLtX",
            signature: "orOfLtX(x)",
            description: "OR of the values < x",
          },
          {
            id: "orOfLteX",
            signature: "orOfLteX(x)",
            description: "OR of the values ≤ x",
          },
          {
            id: "orOfGtX",
            signature: "orOfGtX(x)",
            description: "OR of the values > x",
          },
          {
            id: "orOfGteX",
            signature: "orOfGteX(x)",
            description: "OR of the values ≥ x",
          },
          {
            id: "orOfInValRange",
            signature: "orOfInValRange(lo, hi)",
            description: "OR of the values in [lo, hi]",
          },
          {
            id: "orOfSmallestK",
            signature: "orOfSmallestK(k)",
            description: "OR of the k smallest values",
          },
          {
            id: "orOfLargestK",
            signature: "orOfLargestK(k)",
            description: "OR of the k largest values",
          },
          {
            id: "orOfKthSmallestRange",
            signature: "orOfKthSmallestRange(kFrom, kTo)",
            description: "OR of the kFrom-th..kTo-th smallest values (1-indexed ranks)",
          },
          {
            id: "orOfKthLargestRange",
            signature: "orOfKthLargestRange(kFrom, kTo)",
            description: "OR of the kFrom-th..kTo-th largest values (1-indexed ranks)",
          },
        ],
      },
    ],
  },
  {
    id: "andOf",
    title: "AND of values",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "andOfAll",
            signature: "andOfAll()",
            description: "AND of all values (−1, every bit set, if empty)",
          },
          {
            id: "andOfLtX",
            signature: "andOfLtX(x)",
            description: "AND of the values < x",
          },
          {
            id: "andOfLteX",
            signature: "andOfLteX(x)",
            description: "AND of the values ≤ x",
          },
          {
            id: "andOfGtX",
            signature: "andOfGtX(x)",
            description: "AND of the values > x",
          },
          {
            id: "andOfGteX",
            signature: "andOfGteX(x)",
            description: "AND of the values ≥ x",
          },
          {
            id: "andOfInValRange",
            signature: "andOfInValRange(lo, hi)",
            description: "AND of the values in [lo, hi]",
          },
          {
            id: "andOfSmallestK",
            signature: "andOfSmallestK(k)",
            description: "AND of the k smallest values",
          },
          {
            id: "andOfLargestK",
            signature: "andOfLargestK(k)",
            description: "AND of the k largest values",
          },
          {
            id: "andOfKthSmallestRange",
            signature: "andOfKthSmallestRange(kFrom, kTo)",
            description: "AND of the kFrom-th..kTo-th smallest values (1-indexed ranks)",
          },
          {
            id: "andOfKthLargestRange",
            signature: "andOfKthLargestRange(kFrom, kTo)",
            description: "AND of the kFrom-th..kTo-th largest values (1-indexed ranks)",
          },
        ],
      },
    ],
  },
  {
    id: "xor",
    title: "XOR with x",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "maxXor",
            signature: "maxXor(x)",
            description: "Largest v ^ x over the values v",
          },
          {
            id: "minXor",
            signature: "minXor(x)",
            description: "Smallest v ^ x over the values v",
          },
          {
            id: "kthXor",
            signature: "kthXor(x, i)",
            description: "i-th smallest v ^ x (0-indexed)",
          },
          {
            id: "countXorLtK",
            signature: "countXorLtK(x, k)",
            description: "How many v have v ^ x < k",
          },
          {
            id: "countXorLteK",
            signature: "countXorLteK(x, k)",
            description: "How many v have v ^ x ≤ k",
          },
          {
            id: "countXorGtK",
            signature: "countXorGtK(x, k)",
            description: "How many v have v ^ x > k",
          },
          {
            id: "countXorGteK",
            signature: "countXorGteK(x, k)",
            description: "How many v have v ^ x ≥ k",
          },
          {
            id: "largestXorLtK",
            signature: "largestXorLtK(x, k)",
            description: "Largest v ^ x that is < k",
          },
          {
            id: "largestXorLteK",
            signature: "largestXorLteK(x, k)",
            description: "Largest v ^ x that is ≤ k",
          },
          {
            id: "smallestXorGtK",
            signature: "smallestXorGtK(x, k)",
            description: "Smallest v ^ x that is > k",
          },
          {
            id: "smallestXorGteK",
            signature: "smallestXorGteK(x, k)",
            description: "Smallest v ^ x that is ≥ k",
          },
          {
            id: "mexXor",
            signature: "mexXor(x)",
            description: "Smallest non-negative integer that is no v ^ x",
          },
          {
            id: "sumXor",
            signature: "sumXor(x)",
            description: "Sum of v ^ x over every value v",
          },
        ],
      },
    ],
  },
  {
    id: "xorLimit",
    title: "XOR with x, limit on v",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "maxXorWithVLtM",
            signature: "maxXorWithVLtM(x, m)",
            description: "Largest v ^ x over the values v < m",
          },
          {
            id: "maxXorWithVLteM",
            signature: "maxXorWithVLteM(x, m)",
            description: "Largest v ^ x over the values v ≤ m",
          },
          {
            id: "maxXorWithVGtM",
            signature: "maxXorWithVGtM(x, m)",
            description: "Largest v ^ x over the values v > m",
          },
          {
            id: "maxXorWithVGteM",
            signature: "maxXorWithVGteM(x, m)",
            description: "Largest v ^ x over the values v ≥ m",
          },
          {
            id: "minXorWithVLtM",
            signature: "minXorWithVLtM(x, m)",
            description: "Smallest v ^ x over the values v < m",
          },
          {
            id: "minXorWithVLteM",
            signature: "minXorWithVLteM(x, m)",
            description: "Smallest v ^ x over the values v ≤ m",
          },
          {
            id: "minXorWithVGtM",
            signature: "minXorWithVGtM(x, m)",
            description: "Smallest v ^ x over the values v > m",
          },
          {
            id: "minXorWithVGteM",
            signature: "minXorWithVGteM(x, m)",
            description: "Smallest v ^ x over the values v ≥ m",
          },
          {
            id: "maxXorWithVInValRange",
            signature: "maxXorWithVInValRange(x, lo, hi)",
            description: "Largest v ^ x over the values v in [lo, hi]",
          },
          {
            id: "minXorWithVInValRange",
            signature: "minXorWithVInValRange(x, lo, hi)",
            description: "Smallest v ^ x over the values v in [lo, hi]",
          },
        ],
      },
    ],
  },
  {
    id: "gaps",
    title: "Gaps",
    tiers: [
      {
        kind: "topic",
        ops: [
          {
            id: "minAdjacentDiff",
            signature: "minAdjacentDiff()",
            description:
              "Smallest difference between two values (0 if some value repeats)",
          },
          {
            id: "maxGap",
            signature: "maxGap()",
            description:
              "Largest difference between neighbouring distinct values",
          },
        ],
      },
    ],
  },
];

// Ops that need the values to be numbers (sums, mex, gaps, bitwise, shifts); with tuple values they are greyed out.
export const NUMERIC_SET_OPS: ReadonlySet<SetOpId> = new Set<SetOpId>([
  "sumAll",
  "sumSmallestK",
  "sumLargestK",
  "sumKthSmallestRange",
  "sumKthLargestRange",
  "sumLtX",
  "sumLteX",
  "sumGtX",
  "sumGteX",
  "sumInValRange",
  "sumAbsDiffToX",
  "sumAbsDiffToMedian",
  "mex",
  "minAdjacentDiff",
  "maxGap",
  "maxXor",
  "minXor",
  "kthXor",
  "countXorLtK",
  "countXorLteK",
  "countXorGtK",
  "countXorGteK",
  "largestXorLtK",
  "largestXorLteK",
  "smallestXorGtK",
  "smallestXorGteK",
  "mexXor",
  "sumXor",
  "maxXorWithVLtM",
  "maxXorWithVLteM",
  "maxXorWithVGtM",
  "maxXorWithVGteM",
  "minXorWithVLtM",
  "minXorWithVLteM",
  "minXorWithVGtM",
  "minXorWithVGteM",
  "maxXorWithVInValRange",
  "minXorWithVInValRange",
  "xorAll",
  "shiftAll",
  "xorOfAll",
  "xorOfLtX",
  "xorOfLteX",
  "xorOfGtX",
  "xorOfGteX",
  "xorOfInValRange",
  "xorOfSmallestK",
  "xorOfLargestK",
  "xorOfKthSmallestRange",
  "xorOfKthLargestRange",
  "orOfAll",
  "orOfLtX",
  "orOfLteX",
  "orOfGtX",
  "orOfGteX",
  "orOfInValRange",
  "orOfSmallestK",
  "orOfLargestK",
  "orOfKthSmallestRange",
  "orOfKthLargestRange",
  "andOfAll",
  "andOfLtX",
  "andOfLteX",
  "andOfGtX",
  "andOfGteX",
  "andOfInValRange",
  "andOfSmallestK",
  "andOfLargestK",
  "andOfKthSmallestRange",
  "andOfKthLargestRange",
]);

// Ordered lightest to heaviest constant factor; used to break ties between templates.
export const SET_TYPES = [
  "fastset",
  "fenwick",
  "value-tree",
  "trie",
  "blocks",
  "blocks-fenwick",
  "avl",
  "pbds",
  "treap",
  "splay",
] as const;
export type SetType = (typeof SET_TYPES)[number];

export const SET_TYPE_LABELS: Record<SetType, string> = {
  fastset: "Bit trie (FastSet) on [lo, hi]",
  fenwick: "Fenwick tree on values",
  "value-tree": "Value seg tree on [lo, hi]",
  trie: "Binary trie on [0, 2^bits)",
  blocks: "Sorted list (√N blocks)",
  "blocks-fenwick": "Sorted list (√N blocks, Fenwick in each block)",
  avl: "AVL tree",
  pbds: "pb_ds order-statistics tree (C++)",
  treap: "Treap",
  splay: "Splay tree",
};

// What the constructor needs up front: every value that will ever be added, a range [lo, hi] all values lie in, or
// nothing.
export type SetValues = "offline" | "online-range" | "online-bits" | "online";

// A template as the generated manifest stores it (scripts/build-set-templates.mjs): its op list and memory layout are
// indexes into shared tables, its costs one character per op (an index into the cost table), in its op list's order.
export type SetTemplateRow = [
  folder: string,
  langs: string,
  type: SetType,
  values: SetValues,
  keys: "any" | "numbers",
  tracks: string,
  opList: number,
  costs: string,
  build: number,
  memory: number,
  distinct?: [
    langs: string,
    opList: number,
    costs: string,
    build: number,
    memory: number,
  ],
];

const COST_CODE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_";

// The manifest's rows as templates. Templates with the same op list share its array.
export function decodeSetTemplates(data: {
  opNames: readonly SetOpId[];
  costs: readonly string[];
  opLists: readonly (readonly number[])[];
  memories: readonly MemoryBreakdown[];
  rows: readonly SetTemplateRow[];
}): SetTemplate[] {
  const lists = data.opLists.map((l) => l.map((i) => data.opNames[i]));
  const costOf = new Map([...COST_CODE].map((c, i) => [c, data.costs[i]]));
  const unpack = (list: number, codes: string, build: number, memory: number) => {
    const operations = lists[list];
    const complexities: Partial<Record<SetOpId, string>> = {};
    operations.forEach((op, i) => (complexities[op] = costOf.get(codes[i])));
    return {
      operations,
      complexities,
      build: data.costs[build],
      memory: data.memories[memory],
    };
  };
  return data.rows.map(
    ([folder, langs, type, values, keys, tracks, list, codes, build, memory, distinct]) => ({
      folder,
      langs: langs.split(" ") as TemplateLang[],
      dataStructureType: type,
      values,
      keys,
      tracks: tracks ? tracks.split(" ") : [],
      ...unpack(list, codes, build, memory),
      ...(distinct && {
        distinct: {
          langs: distinct[0].split(" ") as TemplateLang[],
          ...unpack(distinct[1], distinct[2], distinct[3], distinct[4]),
        },
      }),
    }),
  );
}

export interface SetTemplate {
  // Folder under templates/sets holding template.py and/or template.cpp, named by its structure.
  folder: string;
  langs: TemplateLang[];
  operations: SetOpId[];
  dataStructureType: SetType;
  values: SetValues;
  // any: works with any comparable values (tuples, pairs, ...); numbers: needs numeric values
  keys: "any" | "numbers";
  // what this variant keeps current on every update (cached min / max, medians, mex); [] = nothing beyond the counts
  tracks: string[];
  // FastSet only: a no-duplicates version (distinct.*) with no count per value, so building is just the bit trie
  distinct?: {
    langs: TemplateLang[];
    operations: SetOpId[];
    complexities: Partial<Record<SetOpId, string>>;
    build: string;
    memory: MemoryBreakdown;
  };
  complexities: Partial<Record<SetOpId, string>>;
  build: string;
  memory: MemoryBreakdown;
}
