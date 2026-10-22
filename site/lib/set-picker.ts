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
  | "size"
  | "count"
  | "sumAll"
  | "countDistinct"
  | "min"
  | "max"
  | "medianLow"
  | "medianHigh"
  | "mex"
  | "sumAbsDiffToMedian"
  | "kthSmallest"
  | "kthLargest"
  | "sumSmallestK"
  | "sumLargestK"
  | "sumKthSmallestRange"
  | "sumKthLargestRange"
  | "largestLtX"
  | "largestLteX"
  | "smallestGtX"
  | "smallestGteX"
  | "countLtX"
  | "countLteX"
  | "countGtX"
  | "countGteX"
  | "countInValRange"
  | "sumLtX"
  | "sumLteX"
  | "sumGtX"
  | "sumGteX"
  | "sumInValRange"
  | "sumAbsDiffToX";

export const SET_OP_GROUPS: PickerOpGroup[] = [
  {
    id: "updates",
    title: "Updates",
    blurb: "Add or remove values.",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "add", signature: "add(x)", description: "Add one copy of x" },
          {
            id: "remove",
            signature: "remove(x)",
            description: "Remove one copy of x (if present)",
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
        ],
      },
      {
        kind: "uncommon",
        ops: [
          {
            id: "addCount",
            signature: "addCount(x, c)",
            description: "Add c copies of x",
            showArgs: true,
          },
          {
            id: "removeCount",
            signature: "removeCount(x, c)",
            description: "Remove up to c copies of x",
            showArgs: true,
          },
          {
            id: "removeAll",
            signature: "removeAll(x)",
            description: "Remove every copy of x",
          },
        ],
      },
    ],
  },
  {
    id: "whole",
    title: "Whole set",
    blurb: "Questions about everything in the set.",
    tiers: [
      {
        kind: "common",
        ops: [
          {
            id: "size",
            signature: "size()",
            description: "How many values (copies count)",
          },
          {
            id: "count",
            signature: "count(x)",
            description: "How many copies of x",
          },
          { id: "min", signature: "min()", description: "Smallest value" },
          { id: "max", signature: "max()", description: "Largest value" },
        ],
      },
      {
        kind: "uncommon",
        ops: [
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
          {
            id: "countDistinct",
            signature: "countDistinct()",
            description: "How many distinct values",
          },
          {
            id: "sumAll",
            signature: "sumAll()",
            description: "Sum of all values",
          },
        ],
      },
      {
        kind: "rare",
        ops: [
          {
            id: "mex",
            signature: "mex()",
            description: "Smallest non-negative integer not in the set",
          },
        ],
      },
    ],
  },
  {
    id: "rank",
    title: "By rank",
    blurb: "The k-th smallest / largest, 1-indexed.",
    tiers: [
      {
        kind: "common",
        ops: [
          {
            id: "kthSmallest",
            signature: "kthSmallest(k)",
            description: "k-th smallest value",
          },
          {
            id: "kthLargest",
            signature: "kthLargest(k)",
            description: "k-th largest value",
          },
        ],
      },
      {
        kind: "uncommon",
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
        ],
      },
      {
        kind: "rare",
        ops: [
          {
            id: "sumKthSmallestRange",
            signature: "sumKthSmallestRange(i, j)",
            description: "Sum of the i-th..j-th smallest values",
            showArgs: true,
          },
          {
            id: "sumKthLargestRange",
            signature: "sumKthLargestRange(i, j)",
            description:
              "Sum of the i-th..j-th largest (e.g. 5th..8th biggest)",
            showArgs: true,
          },
        ],
      },
    ],
  },
  {
    id: "value",
    title: "By value",
    blurb: "Compare against a value x.",
    tiers: [
      {
        kind: "common",
        ops: [
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
        ],
      },
      {
        kind: "uncommon",
        ops: [
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
            showArgs: true,
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
            showArgs: true,
          },
        ],
      },
      {
        kind: "rare",
        ops: [
          {
            id: "sumAbsDiffToX",
            signature: "sumAbsDiffToX(x)",
            description: "Σ|v − x|: total moves to bring every value to x",
          },
          {
            id: "sumAbsDiffToMedian",
            signature: "sumAbsDiffToMedian()",
            description:
              "Σ|v − median|: min total moves to make all values equal",
          },
        ],
      },
    ],
  },
];

// Ordered lightest to heaviest constant factor; used to break ties between templates.
export const SET_TYPES = [
  "fenwick",
  "blocks",
  "blocks-fenwick",
  "avl",
] as const;
export type SetType = (typeof SET_TYPES)[number];

export const SET_TYPE_LABELS: Record<SetType, string> = {
  fenwick: "Fenwick over values",
  blocks: "Sorted blocks",
  "blocks-fenwick": "Sorted blocks + inner Fenwicks",
  avl: "AVL tree",
};

// What the constructor needs up front: every value that will ever be added, or nothing.
export type SetValues = "offline" | "online";

export interface SetTemplate {
  // Folder under templates/sets holding template.py and/or template.cpp, named by its structure.
  folder: string;
  langs: TemplateLang[];
  operations: SetOpId[];
  dataStructureType: SetType;
  values: SetValues;
  complexities: Partial<Record<SetOpId, string>>;
  build: string;
  memory: MemoryBreakdown;
  usage: Partial<Record<TemplateLang, Usage>>;
}
