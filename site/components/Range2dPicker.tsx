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
  siblings: [
    { href: "/templates/range-queries-2d", label: "2D", current: true },
    { href: "/templates/range-queries-3d", label: "3D", current: false },
  ],
  flag: {
    label: "(x, y) coordinates",
    title: "Coordinates as (x, y): the compressed-coordinates and online templates, which take any integers. Untick for the small grid, read as grid[r][c]",
    storageKey: "range2dPicker.xy",
    keep: (t) => t.input !== "grid",
    onInModes: ["points", "online"],
    offMode: "grid",
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
    rects: {
      py: "rects: every (x1, y1, x2, y2) a rectAdd will use, e.g. [(0, 0, 10**9, 5)] (repeats are fine); a pointAdd at (x, y) needs (x, y, x, y). Queries are never listed",
      cpp: "rects: vector<array<long long, 4>>, every {x1, y1, x2, y2} a rectAdd will use (repeats are fine); a pointAdd at (x, y) needs {x, y, x, y}. Queries are never listed",
    },
    points: {
      py: "points: every (x, y) a point op (pointGet, pointAdd, ...) will use, e.g. [(10**9, -5), (3, 7)] (repeats are fine); never rectangle or corner coordinates, those can be any integers",
      cpp: "points: vector<pair<long long, long long>>, every (x, y) a point op (pointGet, pointAdd, ...) will use (repeats are fine); never rectangle or corner coordinates, those can be any integers",
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
