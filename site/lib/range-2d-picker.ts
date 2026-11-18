// The 2D range queries tab's operations, and the structure types and manifest decoding it shares with the 3D tab (the picker itself is the shared
// components/TemplatePicker.tsx, set up in components/Range2dPicker.tsx). The templates are written by the generators
// in templates/ultimate-template-tool/range-query-2d-tests/generators; SPEC.md next to them says what exists and why.

import type { MemoryBreakdown, PickerOpGroup, PickerTemplate, TemplateLang } from "@/lib/template-picker";

// lightest constant factor first (the picker's tie-breaker)
export const RANGE_2D_TYPES = [
  "prefix-sum",
  "difference-array",
  "corner-table",
  "sliding-window",
  "hash",
  "bit-counts",
  "square-sparse-table",
  "sparse-table",
  "BIT",
  "seg-tree",
  "seg-tree-kept-tags",
  "rows-of-trees",
  "kd-tree",
  "offline-sweep",
] as const;
export type Range2dType = (typeof RANGE_2D_TYPES)[number];

export const RANGE_2D_TYPE_LABELS: Record<Range2dType, string> = {
  "prefix-sum": "Prefix sums",
  "difference-array": "Difference array",
  "corner-table": "Corner max / min table",
  "sliding-window": "Fixed window size (monotonic queues)",
  hash: "2D hashing",
  "bit-counts": "Prefix counts per bit",
  "square-sparse-table": "Square sparse table",
  "sparse-table": "Sparse table (any rectangle)",
  BIT: "Fenwick tree",
  "seg-tree": "Seg tree",
  "seg-tree-kept-tags": "Seg tree, tags kept in place",
  "rows-of-trees": "One lazy seg tree per row",
  "kd-tree": "K-d tree (lazy tags)",
  "offline-sweep": "Offline sweep",
};

// What the constructor is given. The first four are the switch above the 2D op grid; the 3D grid templates have their
// own tab (lib/range-3d-picker.ts).
export const RANGE_2D_INPUTS = ["grid", "points", "online", "batch", "grid-3d"] as const;
export type Range2dInput = (typeof RANGE_2D_INPUTS)[number];
export const RANGE_2D_MODES = ["grid", "points", "online", "batch"] as const;
export type Range2dMode = (typeof RANGE_2D_MODES)[number];

export const RANGE_2D_INPUT_OPTIONS: { mode: Range2dMode; label: string; title: string }[] = [
  {
    mode: "grid",
    label: "Small grid (R × C)",
    title: "The whole grid fits in memory: built from a list of rows. Costs are in R and C",
  },
  {
    mode: "points",
    label: "Points known up front",
    title:
      "Coordinates can be huge or negative, but you can list every (x, y) that will ever be updated before the first call. Then you call it live. N log N memory, log² N per op",
  },
  {
    mode: "online",
    label: "Nothing known (online)",
    title: "Coordinates arrive as you go, anywhere in a range you give. The heaviest option: log² U per op and per update of memory",
  },
  {
    mode: "batch",
    label: "Whole input known (batch)",
    title:
      "Every update and query is known before anything is answered, and no call depends on an earlier answer: you record them all, then get all the answers. Linear memory",
  },
];

export interface Range2dTemplate extends PickerTemplate {
  dataStructureType: Range2dType;
  input: Range2dInput;
  // cells can be empty (templates with min or max): a min / max over no set cell is "nothing", not a number
  emptyCells: boolean;
  // values must be >= 0
  nonNegative: boolean;
}

export type Range2dRow = [
  folder: string,
  langs: string,
  type: Range2dType,
  input: Range2dInput,
  flags: string,
  opList: number,
  costs: number[],
  build: number,
  memory: number,
];

export interface Range2dManifest {
  costs: string[];
  opLists: string[][];
  memories: MemoryBreakdown[];
  rows: Range2dRow[];
}

export function decodeRange2dTemplates(m: Range2dManifest): Range2dTemplate[] {
  return m.rows.map(([folder, langs, type, input, flags, opList, costs, build, memory]) => {
    const operations = m.opLists[opList];
    return {
      folder,
      file: "template",
      langs: langs.split(" ") as TemplateLang[],
      operations,
      dataStructureType: type,
      input,
      emptyCells: flags.includes("e"),
      nonNegative: flags.includes("n"),
      complexities: Object.fromEntries(operations.map((op, i) => [op, m.costs[costs[i]]])),
      build: m.costs[build],
      memory: m.memories[memory],
    };
  });
}

const CORNER_WORDS: Record<string, string> = { Lte: "≤", Gte: "≥" };
const corner = (kind: "min" | "max", a: "Lte" | "Gte", b: "Lte" | "Gte") => ({
  id: `${kind}${a}${b}`,
  signature: `${kind}${a}${b}(r, c)`,
  description: `${kind} over row ${CORNER_WORDS[a]} r and column ${CORNER_WORDS[b]} c`,
});

export const RANGE_2D_OP_GROUPS: PickerOpGroup[] = [
  {
    id: "point",
    title: "Point operations",
    note: "(r, c) is (x, y) for points",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "pointGet", signature: "pointGet(r, c)", description: "Read one cell" },
          { id: "getAll", signature: "getAll()", description: "Read the whole grid (e.g. after many rectangle adds)" },
          { id: "pointAssign", signature: "pointAssign(r, c, v)", description: "cell = v (can go down as well as up)" },
          { id: "pointAdd", signature: "pointAdd(r, c, v)", description: "cell += v" },
          { id: "pointChmax", signature: "pointChmax(r, c, v)", description: "cell = max(cell, v)" },
          { id: "pointChmin", signature: "pointChmin(r, c, v)", description: "cell = min(cell, v)" },
        ],
      },
    ],
  },
  {
    id: "rect-queries",
    title: "Rectangle queries",
    note: "rows r1..r2, columns c1..c2, inclusive",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "rectSum", signature: "rectSum(r1, c1, r2, c2)", description: "Sum of the rectangle" },
          { id: "sumAll", signature: "sumAll()", description: "Sum of everything" },
          { id: "rectMin", signature: "rectMin(r1, c1, r2, c2)", description: "Min of the rectangle" },
          { id: "minAll", signature: "minAll()", description: "Min of everything" },
          { id: "rectMax", signature: "rectMax(r1, c1, r2, c2)", description: "Max of the rectangle" },
          { id: "maxAll", signature: "maxAll()", description: "Max of everything" },
          { id: "rectGcd", signature: "rectGcd(r1, c1, r2, c2)", description: "Gcd of the rectangle" },
          { id: "gcdAll", signature: "gcdAll()", description: "Gcd of everything" },
        ],
      },
      {
        kind: "bitOps",
        ops: [
          { id: "rectXor", signature: "rectXor(r1, c1, r2, c2)", description: "XOR of the rectangle" },
          { id: "xorAll", signature: "xorAll()", description: "XOR of everything" },
          { id: "rectAnd", signature: "rectAnd(r1, c1, r2, c2)", description: "AND of the rectangle" },
          { id: "andAll", signature: "andAll()", description: "AND of everything" },
          { id: "rectOr", signature: "rectOr(r1, c1, r2, c2)", description: "OR of the rectangle" },
          { id: "orAll", signature: "orAll()", description: "OR of everything" },
        ],
      },
    ],
  },
  {
    id: "corners",
    title: "Corner queries",
    note: "one bound per axis: when this is all you ask, Fenwick trees and plain tables compete. For a corner sum use rectSum from the corner",
    tiers: [
      {
        kind: "topic",
        label: "max",
        ops: [corner("max", "Lte", "Lte"), corner("max", "Lte", "Gte"), corner("max", "Gte", "Lte"), corner("max", "Gte", "Gte")],
      },
      {
        kind: "topic",
        label: "min",
        ops: [corner("min", "Lte", "Lte"), corner("min", "Lte", "Gte"), corner("min", "Gte", "Lte"), corner("min", "Gte", "Gte")],
      },
    ],
  },
  {
    id: "rect-updates",
    title: "Rectangle updates",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "rectAdd", signature: "rectAdd(r1, c1, r2, c2, v)", description: "Every cell of the rectangle += v" },
          { id: "rectAssign", signature: "rectAssign(r1, c1, r2, c2, v)", description: "Every cell of the rectangle = v" },
          { id: "rectChmax", signature: "rectChmax(r1, c1, r2, c2, v)", description: "Every cell = max(cell, v)" },
          { id: "rectChmin", signature: "rectChmin(r1, c1, r2, c2, v)", description: "Every cell = min(cell, v)" },
        ],
      },
    ],
  },
  {
    id: "squares",
    title: "Squares and fixed windows",
    note: "no updates: asking less than any rectangle costs less to build",
    tiers: [
      {
        kind: "topic",
        label: "square: top-left (r, c) and a side",
        ops: [
          { id: "squareMin", signature: "squareMin(r, c, side)", description: "Min of the side × side square" },
          { id: "squareMax", signature: "squareMax(r, c, side)", description: "Max of the square" },
          { id: "squareGcd", signature: "squareGcd(r, c, side)", description: "Gcd of the square" },
          { id: "squareAnd", signature: "squareAnd(r, c, side)", description: "AND of the square" },
          { id: "squareOr", signature: "squareOr(r, c, side)", description: "OR of the square" },
        ],
      },
      {
        kind: "topic",
        label: "one window size h × w, fixed at the build",
        ops: [
          { id: "windowMin", signature: "windowMin(r, c)", description: "Min of the h × w window with top-left (r, c)" },
          { id: "windowMax", signature: "windowMax(r, c)", description: "Max of that window" },
        ],
      },
    ],
  },
  {
    id: "hashing",
    title: "2D hashing",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "rectHash", signature: "rectHash(r1, c1, r2, c2)", description: "Hash of the rectangle: equal rectangles hash equal, wherever they are" },
          {
            id: "rectsEqual",
            signature: "rectsEqual(r1, c1, r2, c2, r3, c3)",
            description: "Is the rectangle equal to the same-size one whose top-left is (r3, c3)",
          },
          { id: "hashAll", signature: "hashAll()", description: "Hash of the whole grid" },
        ],
      },
    ],
  },
];

// ops with nothing to read back (the usage panel calls them without binding a result)
export const RANGE_2D_UPDATE_OPS: ReadonlySet<string> = new Set([
  "pointAssign",
  "pointAdd",
  "pointChmax",
  "pointChmin",
  "rectAdd",
  "rectAssign",
  "rectChmax",
  "rectChmin",
]);

// "Fenwick tree over points known up front", "2D sparse table (any rectangle)"
export function range2dKindLabel(t: Range2dTemplate): string {
  const label = RANGE_2D_TYPE_LABELS[t.dataStructureType];
  if (t.input === "points") return `${label} over points known up front`;
  if (t.input === "online") return `${label}, dynamic (any coordinates)`;
  if (t.input === "batch") return `${label} (whole input up front)`;
  return label.startsWith("2D") ? label : `2D ${label.charAt(0).toLowerCase()}${label.slice(1)}`;
}

// still to add: SPEC.md, section 7, says how each is meant to work
export const RANGE_2D_PLANNED = [
  "rectangle add / assign with any query on a small grid: one lazy seg tree per row",
  "k-d tree over a small grid's cells",
  "sparse table on rows × seg tree on columns",
  "2D hashing with point updates",
  "nothing known: Fenwick tree of hash maps (sum, corner max)",
  "whole input known: corner max, point assign",
  "points known: starting values in the constructor",
];
