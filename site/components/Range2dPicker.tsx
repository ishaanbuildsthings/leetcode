"use client";

import { TemplatePicker, type PickerCatalog } from "@/components/TemplatePicker";
import { GENERIC_SPARSE_TABLES_2D } from "@/lib/generic-seg-trees";
import { RANGE_2D_MANIFEST } from "@/lib/generated/range-2d-templates";
import {
  RANGE_2D_INPUTS,
  RANGE_2D_INPUT_OPTIONS,
  RANGE_2D_OP_GROUPS,
  RANGE_2D_PLANNED,
  RANGE_2D_TYPES,
  RANGE_2D_UPDATE_OPS,
  decodeRange2dTemplates,
  range2dKindLabel,
  type Range2dInput,
  type Range2dTemplate,
} from "@/lib/range-2d-picker";

// Written by the generators in templates/ultimate-template-tool/range-query-2d-tests/generators
// (npm run gen:range-queries-2d). An op with no template yet reads "No template covers this selection yet."
const TEMPLATES = decodeRange2dTemplates(RANGE_2D_MANIFEST);
const BY_INPUT = Object.fromEntries(RANGE_2D_INPUTS.map((input) => [input, TEMPLATES.filter((t) => t.input === input)])) as Record<
  Range2dInput,
  Range2dTemplate[]
>;

const isMinMax = (op: string) => /^(rect|square|window|box)?(Min|Max)$|^(min|max)(All|Lte|Gte)/.test(op);

const RANGE_2D_CATALOG: PickerCatalog<Range2dTemplate> = {
  title: "2D Range Query Picker",
  opGroups: RANGE_2D_OP_GROUPS,
  planned: RANGE_2D_PLANNED,
  fillIns: GENERIC_SPARSE_TABLES_2D,
  fillInsLabel: "Generic sparse tables",
  publicBase: "/range-2d-templates",
  githubBase: "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/",
  typeOrder: RANGE_2D_TYPES,
  perType: 2,
  modes: {
    ariaLabel: "What you know about the coordinates ahead of time",
    storageKey: "range2dPicker.input",
    options: RANGE_2D_INPUT_OPTIONS,
    parse: (stored) => ((RANGE_2D_INPUTS as readonly string[]).includes(stored ?? "") ? (stored as string) : "grid"),
    views: (mode) => BY_INPUT[mode as Range2dInput] ?? [],
  },
  kindLabel: range2dKindLabel,
  memoryGroups: (t) => [
    { id: "node", label: t.dataStructureType === "BIT" || t.dataStructureType.includes("seg-tree") ? "Trees" : "Tables" },
    ...(t.memory.tags.arrays.length ? [{ id: "tags" as const, label: "Tags" }] : []),
    ...(t.memory.other.arrays.length ? [{ id: "other" as const, label: "Extra arrays" }] : []),
  ],
  layoutLabel: () => null,
  updateOps: RANGE_2D_UPDATE_OPS,
  varName: "ds",
  ctorNotes: (t) => ({
    grid: {
      py: `grid: a list of R rows, each a list of C values${t.emptyCells ? " (None = an empty cell)" : ""}`,
      cpp: `grid: vector<vector<T>>, R rows of C values${t.emptyCells ? "; or construct with (R, C) to start with every cell empty" : ""}`,
    },
    points: {
      py: "points: every (x, y) that will ever be updated, e.g. [(3, 5), (10, 2), (-4, 7)]: any integers, repeats are fine",
      cpp: "points: vector<pair<long long, long long>> of every (x, y) that will ever be updated: any integers, repeats are fine",
    },
    h: { py: "h: the window's height (rows)", cpp: "h: the window's height (rows)" },
    w: { py: "w: the window's width (columns)", cpp: "w: the window's width (columns)" },
    X: { py: "X: the first side: x is 0..X-1", cpp: "X: the first side: x is 0..X-1" },
    Y: { py: "Y: the second side: y is 0..Y-1", cpp: "Y: the second side: y is 0..Y-1" },
    Z: { py: "Z: the third side: z is 0..Z-1", cpp: "Z: the third side: z is 0..Z-1" },
  }),
  ctorComments: (t) => [
    ...(t.emptyCells
      ? ["Cells can be empty: queries only see cells that have been set."]
      : t.input === "points" || t.input === "grid-3d"
        ? ["Everything starts at 0."]
        : []),
    ...(t.nonNegative ? ["Values must be >= 0."] : []),
  ],
  // a min / max over nothing has no number to give back
  queryNote: (t, op) => (t.emptyCells && isMinMax(op) ? "nothing (None in Python, NO_MAX / NO_MIN in C++) when no set cell is inside" : ""),
};

export function Range2dPicker() {
  return <TemplatePicker catalog={RANGE_2D_CATALOG} />;
}
