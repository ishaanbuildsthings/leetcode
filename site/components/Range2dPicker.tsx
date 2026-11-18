"use client";

import { TemplatePicker, type PickerCatalog } from "@/components/TemplatePicker";
import { GENERIC_SPARSE_TABLES_2D } from "@/lib/generic-seg-trees";
import { RANGE_2D_MANIFEST } from "@/lib/generated/range-2d-templates";
import {
  RANGE_2D_INPUT_OPTIONS,
  RANGE_2D_MODES,
  RANGE_2D_OP_GROUPS,
  RANGE_2D_PLANNED,
  RANGE_2D_TYPES,
  RANGE_2D_UPDATE_OPS,
  decodeRange2dTemplates,
  range2dKindLabel,
  type Range2dMode,
  type Range2dTemplate,
} from "@/lib/range-2d-picker";

// Written by the generators in templates/ultimate-template-tool/range-query-2d-tests/generators
// (npm run gen:range-queries-2d). An op with no template yet reads "No template covers this selection yet."
const TEMPLATES = decodeRange2dTemplates(RANGE_2D_MANIFEST);
const BY_INPUT = Object.fromEntries(RANGE_2D_MODES.map((input) => [input, TEMPLATES.filter((t) => t.input === input)])) as Record<
  Range2dMode,
  Range2dTemplate[]
>;

const RANGE_2D_CATALOG: PickerCatalog<Range2dTemplate> = {
  title: "2D Range Query Picker",
  intro:
    "(r, c) and (x, y) are fully interchangeable: both mean (first coordinate, second coordinate), so use whichever you think in. The one exception is a template built from a grid, which reads it as grid[r][c].",
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
    parse: (stored) => ((RANGE_2D_MODES as readonly string[]).includes(stored ?? "") ? (stored as string) : "grid"),
    views: (mode) => BY_INPUT[mode as Range2dMode] ?? [],
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
  }),
  ctorComments: (t) => [
    ...(t.emptyCells
      ? ["Cells can be empty: queries only see cells that have been set."]
      : t.input === "points"
        ? ["Everything starts at 0."]
        : []),
    ...(t.nonNegative ? ["Values must be >= 0."] : []),
  ],
};

export function Range2dPicker() {
  return <TemplatePicker catalog={RANGE_2D_CATALOG} />;
}
