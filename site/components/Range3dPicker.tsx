"use client";

import { TemplatePicker, type PickerCatalog } from "@/components/TemplatePicker";
import { RANGE_2D_MANIFEST } from "@/lib/generated/range-2d-templates";
import { RANGE_2D_TYPES, decodeRange2dTemplates, type Range2dTemplate } from "@/lib/range-2d-picker";
import { RANGE_3D_OP_GROUPS, RANGE_3D_UPDATE_OPS, range3dKindLabel } from "@/lib/range-3d-picker";

// The "3d-..." templates of templates/ultimate-template-tool/range-queries-2d (npm run gen:range-queries-2d builds
// the one manifest both tabs read).
const TEMPLATES = decodeRange2dTemplates(RANGE_2D_MANIFEST).filter((t) => t.input === "grid-3d");

const RANGE_3D_CATALOG: PickerCatalog<Range2dTemplate> = {
  title: "3D Range Query Picker",
  siblings: [
    { href: "/templates/range-queries-2d", label: "2D", current: false },
    { href: "/templates/range-queries-3d", label: "3D", current: true },
  ],
  opGroups: RANGE_3D_OP_GROUPS,
  publicBase: "/range-2d-templates",
  githubBase: "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/",
  typeOrder: RANGE_2D_TYPES,
  perType: 2,
  // one kind of input, so no switch is shown
  modes: {
    ariaLabel: "What the constructor is given",
    storageKey: "range3dPicker.input",
    options: [{ mode: "grid-3d", label: "3D grid (X × Y × Z)", title: "Three small sides: the whole grid fits in memory" }],
    parse: () => "grid-3d",
    views: () => TEMPLATES,
  },
  kindLabel: range3dKindLabel,
  memoryGroups: (t) => [
    { id: "node", label: "Trees" },
    ...(t.memory.tags.arrays.length ? [{ id: "tags" as const, label: "Tags" }] : []),
    ...(t.memory.other.arrays.length ? [{ id: "other" as const, label: "Extra arrays" }] : []),
  ],
  layoutLabel: () => null,
  updateOps: RANGE_3D_UPDATE_OPS,
  varName: "ds",
  ctorNotes: {
    X: { py: "X: the first side: x is 0..X-1", cpp: "X: the first side: x is 0..X-1" },
    Y: { py: "Y: the second side: y is 0..Y-1", cpp: "Y: the second side: y is 0..Y-1" },
    Z: { py: "Z: the third side: z is 0..Z-1", cpp: "Z: the third side: z is 0..Z-1" },
  },
  ctorComments: (t) => [
    t.emptyCells ? "Cells can be empty: queries only see cells that have been set." : "Everything starts at 0.",
    ...(t.nonNegative ? ["Values must be >= 0."] : []),
  ],
};

export function Range3dPicker() {
  return <TemplatePicker catalog={RANGE_3D_CATALOG} />;
}
