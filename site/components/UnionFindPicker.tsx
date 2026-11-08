"use client";

import { TemplatePicker, type PickerCatalog } from "@/components/TemplatePicker";
import {
  UNION_FIND_EXTRA_LABELS,
  UNION_FIND_OP_GROUPS,
  UNION_FIND_TYPES,
  UNION_FIND_TYPE_LABELS,
  decodeUnionFindTemplates,
  type UnionFindTemplate,
} from "@/lib/union-find-picker";
import { UNION_FIND_MANIFEST } from "@/lib/generated/union-find-templates";

const VIEWS = decodeUnionFindTemplates(UNION_FIND_MANIFEST);

const CTOR_ARG_NOTES = {
  vals: {
    py: "vals: the elements (any values: numbers, strings, tuples, ...); everything works on their indices 0..n-1",
    cpp: "vals: the elements (a vector of any type: numbers, strings, pairs, ...); everything works on their indices 0..n-1",
  },
  baseFn: {
    py: "baseFn(v, i): the Node of element i alone (fill it in above the class)",
    cpp: "baseFn(v, i): the Node of element i alone (fill it in above the struct)",
  },
  combine: {
    py: "combine(big, small): the Node of two components merged, the bigger one first (fill it in above the class)",
    cpp: "combine(big, small): the Node of two components merged, the bigger one first (fill it in above the struct)",
  },
  n: { py: "n: indices 0..n-1, all free to start", cpp: "n: indices 0..n-1, all free to start" },
};

const UNION_FIND_CATALOG: PickerCatalog<UnionFindTemplate> = {
  title: "Union Find Picker",
  opGroups: UNION_FIND_OP_GROUPS,
  publicBase: "/union-find-templates",
  githubBase: "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/",
  typeOrder: UNION_FIND_TYPES,
  perType: 2,
  // one switch, nothing to choose (the picker always has one): every template competes
  modes: {
    ariaLabel: "Union finds",
    storageKey: "unionFindPicker.mode",
    options: [{ mode: "all", label: "All", title: "Every union find" }],
    parse: () => "all",
    views: () => VIEWS,
  },
  // "Rollback union find — weighted, edge counts"
  kindLabel: (t) =>
    UNION_FIND_TYPE_LABELS[t.dataStructureType] +
    (t.extras.length ? ` — ${t.extras.map((e) => UNION_FIND_EXTRA_LABELS[e]).join(", ")}` : ""),
  memoryGroups: (t) => [
    {
      id: "node",
      label: t.dataStructureType === "hdlt" ? "Forests" : t.dataStructureType === "next-free" ? "Jump arrays" : "Parents and sizes",
    },
    ...(t.memory.other.arrays.length ? [{ id: "other" as const, label: "Extra arrays" }] : []),
  ],
  layoutLabel: () => null,
  updateOps: new Set(["rollbackLastUnion", "rollbackTo", "take"]),
  varName: "dsu",
  ctorNotes: CTOR_ARG_NOTES,
  ctorComments: (t) =>
    t.extras.includes("values") ? ["vals must be numbers here: componentSum / Min / Max are over them."] : [],
};

export function UnionFindPicker() {
  return <TemplatePicker catalog={UNION_FIND_CATALOG} />;
}
