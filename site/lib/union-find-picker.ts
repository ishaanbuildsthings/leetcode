// The Union find tab's operations, structure types and manifest decoding (the picker itself is the shared
// components/TemplatePicker.tsx, set up in components/UnionFindPicker.tsx).

import type { MemoryBreakdown, PickerOpGroup, PickerTemplate, TemplateLang } from "@/lib/template-picker";

// lightest constant factor first (the picker's tie-breaker)
export const UNION_FIND_TYPES = ["dsu", "dsu-nocompress", "dsu-rollback", "remove-only-set", "hdlt"] as const;
export type UnionFindType = (typeof UNION_FIND_TYPES)[number];

export const UNION_FIND_TYPE_LABELS: Record<UnionFindType, string> = {
  dsu: "Union find",
  "dsu-nocompress": "Union find, no path compression",
  "dsu-rollback": "Rollback union find",
  "remove-only-set": "Remove-only set (starts full)",
  hdlt: "Fully dynamic connectivity (HDLT)",
};

// what each extra in a folder name (compress-values-members, ...) is called on a card
export const UNION_FIND_EXTRA_LABELS: Record<string, string> = {
  values: "sum / min / max",
  merge: "your own merge",
  members: "member list",
  grow: "add elements",
};

export interface UnionFindTemplate extends PickerTemplate {
  dataStructureType: UnionFindType;
  // the extras in its folder name (none for the remove-only set and HDLT)
  extras: string[];
}

export type UnionFindRow = [
  folder: string,
  langs: string,
  type: UnionFindType,
  opList: number,
  costs: number[],
  build: number,
  memory: number,
];

export interface UnionFindManifest {
  costs: string[];
  opLists: string[][];
  memories: MemoryBreakdown[];
  rows: UnionFindRow[];
}

export function decodeUnionFindTemplates(m: UnionFindManifest): UnionFindTemplate[] {
  return m.rows.map(([folder, langs, type, opList, costs, build, memory]) => {
    const operations = m.opLists[opList];
    return {
      folder,
      file: "template",
      langs: langs.split(" ") as TemplateLang[],
      operations,
      dataStructureType: type,
      complexities: Object.fromEntries(operations.map((op, i) => [op, m.costs[costs[i]]])),
      build: m.costs[build],
      memory: m.memories[memory],
      extras: type.startsWith("dsu") ? folder.split("-").slice(1) : [],
    };
  });
}

export const UNION_FIND_OP_GROUPS: PickerOpGroup[] = [
  {
    id: "union",
    title: "Union",
    tiers: [
      {
        kind: "common",
        ops: [
          {
            id: "unite",
            signature: "unite(i, j)",
            description: "Merge i's and j's components",
          },
        ],
      },
    ],
  },
  {
    id: "undo",
    title: "Undo / remove",
    tiers: [
      {
        kind: "common",
        ops: [
          {
            id: "rollbackLastUnion",
            signature: "rollbackLastUnion()",
            description: "Undo the most recent unite, even one that merged nothing",
          },
          {
            id: "removeEdge",
            signature: "removeEdge(i, j)",
            description: "Delete one edge between i and j: its component can split in two",
          },
        ],
      },
    ],
  },
  {
    id: "queries",
    title: "Queries",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "areUnioned", signature: "areUnioned(i, j)", description: "Are i and j in the same component" },
          { id: "size", signature: "size(i)", description: "How many elements are in i's component" },
          { id: "numComponents", signature: "numComponents()", description: "How many components there are" },
          { id: "largestSize", signature: "largestSize()", description: "Size of the biggest component" },
          { id: "find", signature: "find(i)", description: "The representative (root) of i's component" },
          {
            id: "parent",
            signature: "parent(i)",
            description: "i's parent pointer, to walk the merge tree yourself (only in union finds without path compression)",
          },
          { id: "elementsInGroup", signature: "elementsInGroup(i)", description: "Every element in i's component" },
          { id: "groups", signature: "groups()", description: "Every component's elements" },
          { id: "sizes", signature: "sizes()", description: "Every component's size, biggest first" },
          { id: "roots", signature: "roots()", description: "One representative per component" },
        ],
      },
    ],
  },
  {
    id: "component",
    title: "Per component",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "componentSum", signature: "componentSum(i)", description: "Sum of the values in i's component" },
          { id: "componentMin", signature: "componentMin(i)", description: "Smallest value in i's component" },
          { id: "componentMax", signature: "componentMax(i)", description: "Largest value in i's component" },
          {
            id: "componentData",
            signature: "componentData(i)",
            description: "Your own Node per component: fill in baseFn and combine, like the generic seg tree",
          },
        ],
      },
    ],
  },
  {
    id: "elements",
    title: "Elements",
    tiers: [
      {
        kind: "common",
        ops: [{ id: "add", signature: "add(val)", description: "A new element in its own component (you can start empty)" }],
      },
    ],
  },
  {
    id: "remove-only-set",
    title: "Remove-only set (starts full)",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "remove", signature: "remove(x)", description: "Remove x; 1 if it was there, else 0" },
          { id: "smallestGteX", signature: "smallestGteX(x)", description: "Smallest value ≥ x still in the set, from any x" },
          { id: "smallestGtX", signature: "smallestGtX(x)", description: "Smallest value > x still in the set, from any x" },
          { id: "largestLteX", signature: "largestLteX(x)", description: "Largest value ≤ x still in the set, from any x" },
          { id: "largestLtX", signature: "largestLtX(x)", description: "Largest value < x still in the set, from any x" },
          { id: "contains", signature: "contains(x)", description: "Is x still in the set" },
          { id: "popInValRange", signature: "popInValRange(lo, hi)", description: "Remove every value in [lo, hi] and return them in order" },
          { id: "min", signature: "min()", description: "Smallest value still in the set" },
          { id: "max", signature: "max()", description: "Largest value still in the set" },
          { id: "popMin", signature: "popMin()", description: "Remove and return the smallest value" },
          { id: "popMax", signature: "popMax()", description: "Remove and return the largest value" },
        ],
      },
    ],
  },
];
