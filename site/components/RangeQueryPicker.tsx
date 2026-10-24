"use client";

import { TemplatePicker, type PickerCatalog } from "@/components/TemplatePicker";
import {
  OP_GROUPS,
  DATA_STRUCTURE_TYPES,
  TREE_LAYOUT_LABELS,
  type OpId,
  type RangeQueryTemplate,
  type TemplateView,
  viewOf,
  templateKindLabel,
  isBuiltFromPoints,
} from "@/lib/range-query-picker";
import { RANGE_QUERY_TEMPLATES } from "@/lib/generated/range-query-templates";

// Ops from the "Mod p" tiers. A template with any of them does all its arithmetic mod p, so it is only offered
// once you pick one of them; otherwise a selection like pointGet + pointAdd could land on a mod template.
const MOD_P_OPS = new Set<string>(OP_GROUPS.flatMap((g) => g.tiers.filter((t) => t.kind === "mod").flatMap((t) => t.ops.map((o) => o.id))));
const isModP = (t: RangeQueryTemplate) => t.operations.some((op) => MOD_P_OPS.has(op));

// Ops that change the array (no result to read): the range updates, the sequence edits and every point op but pointGet.
const UPDATE_OPS = new Set<string>(
  OP_GROUPS.filter((g) => g.id === "range-updates" || g.id === "sequence" || g.id === "point")
    .flatMap((g) => g.tiers.flatMap((t) => t.ops.map((o) => o.id)))
    .filter((id) => id !== "pointGet")
);

// What each constructor argument is, by its name in the source ("lo" / "hi" are covered by the sparse sentences).
const CTOR_ARG_NOTES: Record<string, { py: string; cpp: string }> = {
  arr: { py: "arr: the initial array (a list), 0-indexed", cpp: "arr: the initial array (vector<long long>), 0-indexed" },
  a: { py: "a: the initial array (a list), 0-indexed", cpp: "a: the initial array (vector<long long>), 0-indexed" },
  values: {
    py: "values: the nonzero entries, as a list of (index, value) pairs (distinct indices in [lo, hi], any order)",
    cpp: "values: the nonzero entries, as vector<pair<long long, long long>> of (index, value) (distinct indices in [lo, hi], any order)",
  },
  mod: { py: "the modulus p", cpp: "the modulus p" },
  bits: { py: "values live in [0, 2^bits)", cpp: "values live in [0, 2^bits)" },
  allValuesThatWillEverBeInsertedForOfflineCompression: {
    py: "allValuesThatWillEverBeInsertedForOfflineCompression: every value pushBack will ever get (a list; any order, duplicates fine). Only used to compress values: this does NOT add them. N = how many distinct",
    cpp: "allValuesThatWillEverBeInsertedForOfflineCompression: every value pushBack will ever get (vector<long long>; any order, duplicates fine). Only used to compress values: this does NOT add them. N = how many distinct",
  },
  valLo: { py: "valLo: every value a[i] ever holds is >= valLo (any integer, negative is fine)", cpp: "valLo: every value a[i] ever holds is >= valLo (any long long, negative is fine)" },
  valHi: { py: "valHi: every value a[i] ever holds is <= valHi; U = valHi - valLo + 1", cpp: "valHi: every value a[i] ever holds is <= valHi; U = valHi - valLo + 1" },
};

// Which versions compete: dense only, dense and sparse (each sparse version with its own costs and memory), or
// sparse only. Stored as the mode name; "0" / "1" / "2" are older stored values.
const RANGE_CATALOG: PickerCatalog<TemplateView> = {
  title: "Range Query Picker",
  opGroups: OP_GROUPS,
  publicBase: "/range-query-templates",
  githubBase: "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/",
  typeOrder: DATA_STRUCTURE_TYPES,
  modes: {
    ariaLabel: "Sparse versions",
    storageKey: "rangeQueryPicker.sparse",
    options: [
      { mode: "none", label: "No sparse", title: "Only the dense templates (indices 0..n-1)" },
      { mode: "include", label: "Include sparse", title: "Dense templates and their sparse versions together" },
      {
        mode: "only",
        label: "Only sparse",
        title:
          "Only sparse versions: any index range [lo, hi] (e.g. up to 1e18). Templates with updates become dynamic trees where every position starts at 0; static ones are built from given values ((index, value) pairs), every other index 0.",
      },
    ],
    parse: (v) => (v === "2" || v === "only" ? "only" : v === "1" || v === "include" ? "include" : "none"),
    views: (mode) =>
      RANGE_QUERY_TEMPLATES.flatMap((t) => [mode !== "only" ? viewOf(t, false) : null, mode !== "none" ? viewOf(t, true) : null]).filter(
        (t): t is TemplateView => t !== null
      ),
  },
  allowed: (t, picked) => picked.some((op) => MOD_P_OPS.has(op)) || !isModP(t),
  kindLabel: templateKindLabel,
  // The memory lines a template shows, named for its kind of structure: a sparse table has a table, not nodes, and
  // only segment trees (and sqrt blocks) carry lazy tags. "other" is anything outside the main structure.
  memoryGroups: (template) => {
    const { memory, dataStructureType: type } = template;
    const groups: { id: "node" | "tags" | "other"; label: string }[] = [
      { id: "node", label: type === "sparse-table" ? "Table" : type === "sqrt" ? "Blocks" : type === "positions" ? "Lists" : type === "wavelet" ? "Arrays" : "Node data" },
    ];
    const tree = memory.layout !== "none" && (memory.layout !== "sparse" || ["seg-tree", "lazy-seg-tree", "beats"].includes(type));
    if (tree || memory.tags.arrays.length > 0) groups.push({ id: "tags", label: "Lazy tags" });
    if (memory.other.arrays.length > 0) groups.push({ id: "other", label: "Extra arrays" });
    return groups;
  },
  // Sparse versions get no layout label: the card's title ("Sparse seg tree", "Sparse table built from values")
  // already says what they are.
  layoutLabel: (memory) => (memory.layout === "none" || memory.layout === "sparse" ? null : TREE_LAYOUT_LABELS[memory.layout]),
  updateOps: UPDATE_OPS,
  varName: "seg",
  ctorNotes: CTOR_ARG_NOTES,
  ctorComments: (t) =>
    t.file !== "sparse"
      ? []
      : isBuiltFromPoints(t.memory)
        ? [
            "A huge, mostly-zero array a[lo..hi] (e.g. lo = 0, hi = 10^18; negative is fine): lo and hi only say how long it is.",
            "values lists every nonzero entry, all at once; every other index is 0. Nothing is added later: the array never changes.",
            "Costs depend on N = len(values), not on hi - lo.",
          ]
        : [
            "A huge array a[lo..hi] (e.g. lo = 0, hi = 10^18; negative is fine) where every index starts at 0: lo and hi only say how long it is.",
            "Untouched indices read as 0, e.g. the max of an untouched range is 0, not -inf.",
          ],
  // in a sparse version, every query line says what the indices nobody wrote hold
  queryNote: (t) =>
    t.file !== "sparse" ? "" : isBuiltFromPoints(t.memory) ? "indices not given in values count as 0" : "never-updated indices count as 0",
  pairResults: { rangeMode: ["value", "freq"] } satisfies Partial<Record<OpId, [string, string]>>,
};

export function RangeQueryPicker() {
  return <TemplatePicker catalog={RANGE_CATALOG} />;
}
