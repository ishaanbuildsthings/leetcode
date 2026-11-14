"use client";

import { TemplatePicker, type PickerCatalog } from "@/components/TemplatePicker";
import { GENERIC_TREE_TEMPLATES } from "@/lib/generic-tree-templates";
import { TREE_QUERY_MANIFEST } from "@/lib/generated/tree-query-templates";
import {
  TREE_QUERY_OP_GROUPS,
  TREE_QUERY_PLANNED,
  TREE_STRUCTURE_TYPES,
  TREE_UPDATE_OPS,
  decodeTreeQueryTemplates,
  isTreeModOp,
  treeStructureLabel,
  type TreeQueryTemplate,
} from "@/lib/tree-query-picker";

// Written by the generators in templates/ultimate-template-tool/tree-query-tests/ (npm run gen:tree-queries). The
// shape templates exist; an op with no template yet reads "No template covers this selection yet."
const TEMPLATES = decodeTreeQueryTemplates(TREE_QUERY_MANIFEST);

const TREE_QUERY_CATALOG: PickerCatalog<TreeQueryTemplate> = {
  title: "Tree Query Picker",
  opGroups: TREE_QUERY_OP_GROUPS,
  pane: {
    fixed: ["shape"],
    tabs: [
      // (queries first: they fill the left column, updates the right one)
      { id: "nodes", label: "Node values", groups: ["node-queries", "node-updates"] },
      { id: "edges", label: "Edge values", groups: ["edge-queries", "edge-updates"] },
    ],
  },
  planned: TREE_QUERY_PLANNED,
  fillIns: GENERIC_TREE_TEMPLATES,
  fillInsLabel: "Generic tree templates",
  publicBase: "/tree-query-templates",
  githubBase: "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/",
  typeOrder: TREE_STRUCTURE_TYPES,
  perType: 2,
  allowed: (t, picked) =>
    (picked.some(isTreeModOp) || !t.operations.some(isTreeModOp)) &&
    // a both- template (node values and edge weights in one Tree) only competes when both kinds of op are picked:
    // for one kind alone it is the node- or edge- template with a second structure nobody asked for
    (!t.folder.startsWith("both-") || (picked.some((op) => op.startsWith("node")) && picked.some((op) => op.startsWith("edge")))),
  modes: {
    ariaLabel: "Which templates compete",
    storageKey: "treeQueryPicker.mode",
    options: [{ mode: "all", label: "All", title: "Every template" }],
    parse: () => "all",
    views: () => TEMPLATES,
  },
  // "Lazy seg tree over heavy-light order (node values + edge weights)" for a both- template
  kindLabel: (t) => treeStructureLabel(t.dataStructureType) + (t.folder.startsWith("both-") ? " (node values + edge weights)" : ""),
  memoryGroups: (t) => [
    { id: "node", label: "Tree layout" },
    ...(t.memory.other.arrays.length ? [{ id: "other" as const, label: "Extra arrays" }] : []),
  ],
  layoutLabel: () => null,
  updateOps: TREE_UPDATE_OPS,
  varName: "tree",
  ctorNotes: {
    root: { py: "root: the root node (required), e.g. 0 or 1", cpp: "root: the root node (required), e.g. 0 or 1" },
    mod: {
      py: "the modulus MOD (every value is kept in [0, MOD))",
      cpp: "the modulus MOD (every value is kept in [0, MOD))",
      example: { py: "998244353", cpp: "998244353" },
    },
    bits: { py: "values live in [0, 2^bits)", cpp: "values live in [0, 2^bits)", example: { py: "30", cpp: "30" } },
    valLo: { py: "valLo: every value ever held is >= valLo (negative is fine)", cpp: "valLo: every value ever held is >= valLo (negative is fine)" },
    valHi: { py: "valHi: every value ever held is <= valHi", cpp: "valHi: every value ever held is <= valHi" },
    edges: {
      py: "edges: [(a, b)], or [(a, b, w)] for edge weights; nodes 0..n-1 or 1..n (found from the smallest label)",
      cpp: "edges: vector of {a, b}, or {a, b, w} for edge weights; nodes 0..n-1 or 1..n (found from the smallest label)",
    },
    vals: {
      py: "vals: vals[node] is node's value: length n when 0-indexed, n + 1 when 1-indexed (vals[0] ignored)",
      cpp: "vals: vals[node] is node's value: length n when 0-indexed, n + 1 when 1-indexed (vals[0] ignored)",
    },
  },
};

export function TreeQueryPicker() {
  return <TemplatePicker catalog={TREE_QUERY_CATALOG} />;
}
