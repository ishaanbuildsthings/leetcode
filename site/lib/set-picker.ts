// The ordered-multiset picker: operations, structure types and template shape. Shared picker types and formatting
// live in ./template-picker.
import type {
  MemoryBreakdown,
  PickerOpGroup,
  TemplateLang,
  Usage,
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
  | "sumLtX"
  | "sumLteX"
  | "sumGtX"
  | "sumGteX"
  | "sumInValRange";

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
            id: "pop",
            signature: "pop(i)",
            description:
              "Remove and return the value at sorted position i (0-indexed)",
          },
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
];

// Ops that need the values to be numbers (sums, mex); with tuple values they are greyed out.
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
]);

// Ordered lightest to heaviest constant factor; used to break ties between templates.
export const SET_TYPES = [
  "fastset",
  "fenwick",
  "value-tree",
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
  blocks: "Sorted list (√N blocks)",
  "blocks-fenwick": "Sorted list (√N blocks, Fenwick in each block)",
  avl: "AVL tree",
  pbds: "pb_ds order-statistics tree (C++)",
  treap: "Treap",
  splay: "Splay tree",
};

// What the constructor needs up front: every value that will ever be added, a range [lo, hi] all values lie in, or
// nothing.
export type SetValues = "offline" | "online-range" | "online";

export interface SetTemplate {
  // Folder under templates/sets holding template.py and/or template.cpp, named by its structure.
  folder: string;
  langs: TemplateLang[];
  operations: SetOpId[];
  dataStructureType: SetType;
  values: SetValues;
  // any: works with any comparable values (tuples, pairs, ...); numbers: needs numeric values
  keys: "any" | "numbers";
  // FastSet only: a no-duplicates version (distinct.*) with no count per value, so building is just the bit trie
  distinct?: {
    langs: TemplateLang[];
    operations: SetOpId[];
    complexities: Partial<Record<SetOpId, string>>;
    build: string;
    memory: MemoryBreakdown;
    usage: Partial<Record<TemplateLang, Usage>>;
  };
  complexities: Partial<Record<SetOpId, string>>;
  build: string;
  memory: MemoryBreakdown;
  usage: Partial<Record<TemplateLang, Usage>>;
}
