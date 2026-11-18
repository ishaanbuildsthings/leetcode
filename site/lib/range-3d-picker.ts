// The 3D range queries tab's operations (the picker itself is the shared components/TemplatePicker.tsx, set up in
// components/Range3dPicker.tsx). The templates are the "3d-..." folders the 2D generators write
// (templates/ultimate-template-tool/range-query-2d-tests/generators/gen_3d.py); they share the 2D manifest.

import type { PickerOpGroup } from "@/lib/template-picker";
import { RANGE_2D_TYPE_LABELS, type Range2dTemplate } from "@/lib/range-2d-picker";

const corner = (kind: "min" | "max", side: "Lte" | "Gte") => ({
  id: `${kind}${side}${side}${side}`,
  signature: `${kind}${side}${side}${side}(x, y, z)`,
  description: `${kind} over all three coordinates ${side === "Lte" ? "≤" : "≥"} x, y, z`,
});

export const RANGE_3D_OP_GROUPS: PickerOpGroup[] = [
  {
    id: "point",
    title: "3D point operations",
    note: "one cell (x, y, z) of an X × Y × Z grid",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "pointGet", signature: "pointGet(x, y, z)", description: "Read one cell" },
          { id: "pointAssign", signature: "pointAssign(x, y, z, v)", description: "cell = v (can go down as well as up)" },
          { id: "pointAdd", signature: "pointAdd(x, y, z, v)", description: "cell += v" },
          { id: "pointChmax", signature: "pointChmax(x, y, z, v)", description: "cell = max(cell, v)" },
          { id: "pointChmin", signature: "pointChmin(x, y, z, v)", description: "cell = min(cell, v)" },
        ],
      },
    ],
  },
  {
    id: "box-queries",
    title: "3D box queries",
    note: "x1..x2, y1..y2, z1..z2, inclusive",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "boxSum", signature: "boxSum(x1, y1, z1, x2, y2, z2)", description: "Sum of the box" },
          { id: "sumAll", signature: "sumAll()", description: "Sum of everything" },
          { id: "boxMin", signature: "boxMin(x1, y1, z1, x2, y2, z2)", description: "Min of the box" },
          { id: "minAll", signature: "minAll()", description: "Min of everything" },
          { id: "boxMax", signature: "boxMax(x1, y1, z1, x2, y2, z2)", description: "Max of the box" },
          { id: "maxAll", signature: "maxAll()", description: "Max of everything" },
        ],
      },
    ],
  },
  {
    id: "corners",
    title: "3D corner queries",
    note: "one bound per axis: when this is all you ask, a Fenwick tree is enough",
    tiers: [
      { kind: "topic", label: "max", ops: [corner("max", "Lte"), corner("max", "Gte")] },
      { kind: "topic", label: "min", ops: [corner("min", "Lte"), corner("min", "Gte")] },
    ],
  },
];

// ops with nothing to read back (the usage panel calls them without binding a result)
export const RANGE_3D_UPDATE_OPS: ReadonlySet<string> = new Set(["pointAssign", "pointAdd", "pointChmax", "pointChmin"]);

// "3D seg tree", "3D Fenwick tree"
export function range3dKindLabel(t: Range2dTemplate): string {
  const label = RANGE_2D_TYPE_LABELS[t.dataStructureType];
  return `3D ${label.charAt(0).toLowerCase()}${label.slice(1)}`;
}
