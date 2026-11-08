// The Union find tab's operations, structure types and manifest decoding (the picker itself is the shared
// components/TemplatePicker.tsx, set up in components/UnionFindPicker.tsx).

import type { MemoryBreakdown, PickerOpGroup, PickerTemplate, TemplateLang } from "@/lib/template-picker";

// lightest constant factor first (the picker's tie-breaker)
export const UNION_FIND_TYPES = ["dsu", "dsu-nocompress", "dsu-rollback", "next-free", "hdlt"] as const;
export type UnionFindType = (typeof UNION_FIND_TYPES)[number];

export const UNION_FIND_TYPE_LABELS: Record<UnionFindType, string> = {
  dsu: "Union find",
  "dsu-nocompress": "Union find, no path compression",
  "dsu-rollback": "Rollback union find",
  "next-free": "Next free index",
  hdlt: "Fully dynamic connectivity (HDLT)",
};

// what each extra in a folder name (compress-values-edges, ...) is called on a card
export const UNION_FIND_EXTRA_LABELS: Record<string, string> = {
  values: "sum / min / max",
  merge: "your own merge",
  members: "member list",
  edges: "edge counts",
  potential: "weighted",
  time: "time queries",
  grow: "add elements",
};

export interface UnionFindTemplate extends PickerTemplate {
  dataStructureType: UnionFindType;
  // the extras in its folder name (none for next free and HDLT)
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
            description: "Merge i's and j's components (in HDLT: adds an edge and returns its id, for removeEdge)",
          },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          {
            id: "uniteAUnderB",
            signature: "uniteAUnderB(a, b)",
            description: "Merge with b's root staying the root: no union by size, so you pick which side survives",
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
            signature: "removeEdge(e)",
            description: "Delete an edge (by the id unite returned): its component can split in two",
          },
          {
            id: "removeEdgeBetween",
            signature: "removeEdgeBetween(u, v)",
            description: "Delete one edge between u and v: its component can split in two",
          },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "checkpoint", signature: "checkpoint()", description: "A point to roll back to later" },
          { id: "rollbackTo", signature: "rollbackTo(k)", description: "Undo every unite since checkpoint() returned k" },
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
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "elementsInGroup", signature: "elementsInGroup(i)", description: "Every element in i's component" },
          { id: "groups", signature: "groups()", description: "Every component's elements" },
          { id: "sizes", signature: "sizes()", description: "Every component's size, biggest first" },
          { id: "roots", signature: "roots()", description: "One representative per component" },
          {
            id: "componentId",
            signature: "componentId(u)",
            description: "A handle shared by exactly u's component (good until the next change)",
          },
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
            id: "edgeCount",
            signature: "edgeCount(i)",
            description: "How many unites touched i's component, merging or not (its edges)",
          },
          { id: "isTree", signature: "isTree(i)", description: "Does i's component have no cycle (edges = size − 1)" },
        ],
      },
      {
        kind: "uncommon",
        ops: [
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
    id: "weighted",
    title: "Weighted (potential)",
    tiers: [
      {
        kind: "common",
        ops: [
          {
            id: "uniteWeighted",
            signature: "uniteWeighted(i, j, w)",
            description: "Merge, recording value[j] − value[i] = w",
          },
          {
            id: "diff",
            signature: "diff(i, j)",
            description: "value[j] − value[i] from what's been recorded, or none if not together",
          },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          {
            id: "uniteAUnderBWeighted",
            signature: "uniteAUnderBWeighted(a, b, w)",
            description: "uniteAUnderB, recording value[b] − value[a] = w",
          },
        ],
      },
    ],
  },
  {
    id: "history",
    title: "History",
    tiers: [
      {
        kind: "common",
        ops: [
          {
            id: "firstConnectedTime",
            signature: "firstConnectedTime(i, j)",
            description: "After how many unites i and j first ended up together",
          },
          {
            id: "connectedAt",
            signature: "connectedAt(i, j, t)",
            description: "Were i and j together after the first t unites",
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
    id: "next-free",
    title: "Next free index",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "nextFree", signature: "nextFree(i)", description: "Smallest index ≥ i not taken yet" },
          { id: "prevFree", signature: "prevFree(i)", description: "Largest index ≤ i not taken yet" },
          { id: "take", signature: "take(i)", description: "Mark i taken" },
          { id: "takeRange", signature: "takeRange(l, r)", description: "Take every free index in l..r and return them" },
          { id: "isFree", signature: "isFree(i)", description: "Is i still free" },
        ],
      },
    ],
  },
];
