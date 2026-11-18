// The 2D range queries tab's operations, and the structure types and manifest decoding it shares with the 3D tab (the picker itself is the shared
// components/TemplatePicker.tsx, set up in components/Range2dPicker.tsx). The templates are written by the generators
// in templates/ultimate-template-tool/range-query-2d-tests/generators; SPEC.md next to them says what exists and why.

import type { MemoryBreakdown, PickerOpGroup, PickerTemplate, TemplateLang } from "@/lib/template-picker";

// lightest constant factor first (the picker's tie-breaker)
export const RANGE_2D_TYPES = [
  "prefix-sum",
  "difference-array",
  "corner-table",
  "hash",
  "bit-counts",
  "sparse-table",
  "BIT",
  "seg-tree",
  "seg-tree-kept-tags",
  "rows-of-trees",
  "kd-tree",
] as const;
export type Range2dType = (typeof RANGE_2D_TYPES)[number];

export const RANGE_2D_TYPE_LABELS: Record<Range2dType, string> = {
  "prefix-sum": "Prefix sums",
  "difference-array": "Difference array",
  "corner-table": "Corner max / min table",
  hash: "2D hashing",
  "bit-counts": "Prefix counts per bit",
  "sparse-table": "Sparse table (any rectangle)",
  BIT: "Fenwick tree",
  "seg-tree": "Seg tree",
  "seg-tree-kept-tags": "Seg tree, tags kept in place",
  "rows-of-trees": "One lazy seg tree per row",
  "kd-tree": "K-d tree (lazy tags)",
};

// What the constructor is given. The first three are the switch above the 2D op grid; the 3D grid templates have their
// own tab (lib/range-3d-picker.ts).
export const RANGE_2D_INPUTS = ["grid", "compressed", "online", "grid-3d"] as const;
export type Range2dInput = (typeof RANGE_2D_INPUTS)[number];
export const RANGE_2D_MODES = ["grid", "compressed", "online"] as const;
export type Range2dMode = (typeof RANGE_2D_MODES)[number];

export const RANGE_2D_INPUT_OPTIONS: { mode: Range2dMode; label: string; title: string }[] = [
  {
    mode: "grid",
    label: "Small grid (R × C)",
    title: "The whole grid fits in memory: built from a list of rows. Costs are in R and C",
  },
  {
    mode: "compressed",
    label: "Compressed coordinates",
    title:
      "Coordinates can be huge or negative. The constructor takes xs and ys: every x and every y your point ops will use (or a size, to leave that axis as 0..n-1); rectangles can be any integers. Each listed x is a row and each listed y a column of a small grid, and a cell is one point, not a block (a rectangle sum is never an area); costs and memory are a small grid's with X = distinct x's and Y = distinct y's",
  },
  {
    mode: "online",
    label: "Nothing known (online)",
    title: "Coordinates arrive as you go, anywhere in a range you give. The heaviest option: log² U per op and per update of memory",
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
const corner = (kind: "sum" | "min" | "max", a: "Lte" | "Gte", b: "Lte" | "Gte") => ({
  id: `${kind}${a}${b}`,
  signature: `${kind}${a}${b}(r, c)`,
  description: `${kind} over row ${CORNER_WORDS[a]} r and column ${CORNER_WORDS[b]} c`,
});

export const RANGE_2D_OP_GROUPS: PickerOpGroup[] = [
  {
    id: "point",
    title: "Point operations",
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
    tiers: [
      {
        kind: "topic",
        label: "sum",
        ops: [corner("sum", "Lte", "Lte"), corner("sum", "Lte", "Gte"), corner("sum", "Gte", "Lte"), corner("sum", "Gte", "Gte")],
      },
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

// "2D Fenwick tree over compressed coordinates", "2D sparse table (any rectangle)"
export function range2dKindLabel(t: Range2dTemplate): string {
  const label = RANGE_2D_TYPE_LABELS[t.dataStructureType];
  if (t.input === "compressed") return `${label.startsWith("2D") || label.startsWith("K-d") ? label : `2D ${label.charAt(0).toLowerCase()}${label.slice(1)}`} over compressed coordinates`;
  if (t.input === "online") return `${label}, dynamic (any coordinates)`;
  return label.startsWith("2D") ? label : `2D ${label.charAt(0).toLowerCase()}${label.slice(1)}`;
}

// The "(x, y) coordinates" checkbox: the op grid and usage lines say x and y instead of r and c (the same arguments)
export function toXY(text: string): string {
  return text
    .replace(/\brows r1\.\.r2, columns c1\.\.c2\b/g, "x1..x2, y1..y2")
    .replace(/\brow ([≤≥]) r and column ([≤≥]) c\b/g, "x $1 the given x and y $2 the given y")
    .replace(/\br(\d?)\b/g, "x$1")
    .replace(/\bc(\d?)\b/g, "y$1");
}
