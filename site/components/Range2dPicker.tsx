"use client";

import { TemplatePicker, type PickerCatalog } from "@/components/TemplatePicker";
import { GENERIC_SPARSE_TABLES_2D } from "@/lib/generic-seg-trees";
import { RANGE_2D_MANIFEST } from "@/lib/generated/range-2d-templates";
import {
  RANGE_2D_INPUT_OPTIONS,
  RANGE_2D_MODES,
  RANGE_2D_OP_GROUPS,
  RANGE_2D_TYPES,
  RANGE_2D_UPDATE_OPS,
  decodeRange2dTemplates,
  toXY,
  range2dKindLabel,
  type Range2dMode,
  type Range2dTemplate,
} from "@/lib/range-2d-picker";

// Written by the generators in templates/ultimate-template-tool/range-query-2d-tests/generators
// (npm run gen:range-queries-2d). An op with no template yet reads "No template covers this selection yet."
const TEMPLATES = decodeRange2dTemplates(RANGE_2D_MANIFEST);
// ops only a grid template has (no (x, y) version): greyed out while the (x, y) box is ticked
const XY_OPS = new Set(TEMPLATES.filter((t) => t.input !== "grid").flatMap((t) => t.operations));
const GRID_ONLY_OPS = new Set(TEMPLATES.flatMap((t) => t.operations).filter((op) => !XY_OPS.has(op)));
const BY_INPUT = Object.fromEntries(RANGE_2D_MODES.map((input) => [input, TEMPLATES.filter((t) => t.input === input)])) as Record<
  Range2dMode,
  Range2dTemplate[]
>;

const RANGE_2D_CATALOG: PickerCatalog<Range2dTemplate> = {
  title: "2D Range Query Picker",
  flag: {
    label: "(x, y) points",
    title: "Write coordinates as (x, y) instead of (r, c). Leaves out the small-grid templates, which are built from grid[r][c]",
    storageKey: "range2dPicker.xy",
    keep: (t) => t.input !== "grid",
    hidesModes: ["grid"],
    fallbackMode: "points",
    disabledOps: GRID_ONLY_OPS,
    disabledTitle: "Only the small-grid templates have this",
    rename: toXY,
  },
  opGroups: RANGE_2D_OP_GROUPS,
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
      py: "points: every (x, y) that will ever hold a value (read, updated, or inside an update rectangle), e.g. [(3, 5), (-4, 7)]. Rectangles' corners are NOT listed: any integers. Repeats are fine",
      cpp: "points: vector<pair<long long, long long>>, every (x, y) that will ever hold a value (read, updated, or inside an update rectangle). Rectangles' corners are NOT listed: any integers. Repeats are fine",
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
