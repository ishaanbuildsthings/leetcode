"use client";

import {
  TemplatePicker,
  type PickerCatalog,
} from "@/components/TemplatePicker";
import {
  NUMERIC_SET_OPS,
  SET_OP_GROUPS,
  SET_TYPES,
  SET_TYPE_LABELS,
  decodeSetTemplates,
  type SetTemplate,
} from "@/lib/set-picker";
import {
  SET_COSTS,
  SET_MEMORIES,
  SET_OP_LISTS,
  SET_OP_NAMES,
  SET_TEMPLATE_ROWS,
} from "@/lib/generated/set-templates";

type SetView = SetTemplate & { file: "template" | "distinct" };

const VIEWS: SetView[] = decodeSetTemplates({
  opNames: SET_OP_NAMES,
  costs: SET_COSTS,
  opLists: SET_OP_LISTS,
  memories: SET_MEMORIES,
  rows: SET_TEMPLATE_ROWS,
}).map((t) => ({ ...t, file: "template" }));

// Knowing every value ahead (offline) allows everything, including the Fenwick tree on compressed values. Online
// allows the comparison-based structures plus the value seg tree, which only needs a [lo, hi] all values lie in.
const USABLE: Record<string, SetTemplate["values"][]> = {
  known: ["offline", "online-range", "online-bits", "online"],
  unknown: ["online-range", "online-bits", "online"],
};

// These structures come with and without mex (it costs them one more field per node / array); the sorted lists find
// mex from their keys for free, so theirs always has it.
const OPTIONAL_MEX = new Set([
  "fenwick",
  "value-tree",
  "avl",
  "treap",
  "splay",
  "trie",
]);

const CTOR_ARG_NOTES: Record<string, { py: string; cpp: string }> = {
  allValuesThatWillEverBeInsertedForOfflineCompression: {
    py: "allValuesThatWillEverBeInsertedForOfflineCompression: every value you will ever add (a list; any order, duplicates fine). Only used to compress values: this does NOT add them, the multiset starts empty. N = how many distinct",
    cpp: "allValuesThatWillEverBeInsertedForOfflineCompression: every value you will ever add (vector<long long>; any order, duplicates fine). Only used to compress values: this does NOT add them, the multiset starts empty. N = how many distinct",
  },
  lo: {
    py: "lo: every value added is >= lo (any integer, negative is fine)",
    cpp: "lo: every value added is >= lo (any long long, negative is fine)",
  },
  hi: {
    py: "hi: every value added is <= hi",
    cpp: "hi: every value added is <= hi",
  },
};

const SET_CATALOG: PickerCatalog<SetView> = {
  title: "Set Picker",
  opGroups: SET_OP_GROUPS,
  publicBase: "/set-templates",
  githubBase:
    "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/",
  remoteBase:
    "https://raw.githubusercontent.com/ishaanbuildsthings/leetcode/main/templates/sets",
  typeOrder: SET_TYPES,
  onePerType: true,
  modes: {
    ariaLabel: "What you know about the values ahead of time",
    storageKey: "setPicker.values",
    options: [
      {
        mode: "known",
        label: "All values ever added known (offline, compressed)",
        title:
          "You know every value that will ever be added (queries' x can still be anything): every structure works, including the Fenwick tree on compressed values",
      },
      {
        mode: "unknown",
        label: "All values ever added not known (online)",
        title:
          "Values arrive as you go: sorted lists, AVL tree, treap, splay tree, pb_ds, and the value seg tree (which needs a range [lo, hi] all values lie in)",
      },
    ],
    // "range" was an older third mode; it now lives under online
    parse: (v) => (v === "range" ? "unknown" : v && v in USABLE ? v : "known"),
    views: (mode) => VIEWS.filter((t) => USABLE[mode].includes(t.values)),
  },
  variant: {
    file: "distinct",
    label:
      "Want fast build O(U/64)? Restriction: no duplicates in the structure (so no O(U) frequency array is needed)",
    title:
      "Use the version without duplicates: adding a value that is already in the set does nothing, so there is no count per value and building is just the bit trie (about U / 63 words)",
    of: (t) =>
      t.distinct ? ({ ...t.distinct } as Partial<SetView>) : undefined,
  },
  flag: {
    label: "Values are tuples",
    title:
      "Values are tuples / pairs (anything that compares), not numbers: only templates that just compare values are offered, and ops that need numbers (sums, mex, bitwise, shifts) are greyed out",
    storageKey: "setPicker.tuples",
    keep: (t) => t.keys === "any",
    disabledOps: NUMERIC_SET_OPS,
    disabledTitle: "Needs number values: not available with tuples",
  },
  // "AVL tree — counts + sums + xor, mex": what it keeps (counts, and sums / xor / OR / AND), mex where it's optional,
  // and what it needs to know up front
  kindLabel: (t) => {
    const kept = (
      [
        ["sumAll", "sums"],
        ["xorOfAll", "xor"],
        ["orOfAll", "OR"],
        ["andOfAll", "AND"],
      ] as const
    )
      .filter(([op]) => t.operations.includes(op))
      .map(([, word]) => word);
    const parts = [
      kept.length ? `counts + ${kept.join(" + ")}` : "counts only",
    ];
    // what it caches (kept current on every update); "mex" alone = computed per query
    if (t.tracks.includes("mex")) parts.push("mex cached");
    else if (
      OPTIONAL_MEX.has(t.dataStructureType) &&
      t.operations.includes("mex")
    )
      parts.push("mex");
    if (t.tracks.includes("minmax")) parts.push("min/max cached");
    if (t.tracks.includes("medians")) parts.push("medians cached");
    if (t.tracks.includes("mode")) parts.push("mode");
    if (t.tracks.includes("gaps")) parts.push("gaps");
    if (t.tracks.includes("vbound")) parts.push("value bounds per node");
    if (t.tracks.includes("sumxor")) parts.push("bit counts");
    if (t.tracks.includes("mask")) parts.push("xorAll");
    if (t.tracks.includes("shift")) parts.push("shiftAll");
    if (t.values === "offline") parts.push("offline");
    if (t.file === "distinct") parts.push("no duplicates");
    return `${SET_TYPE_LABELS[t.dataStructureType]} — ${parts.join(", ")}`;
  },
  memoryGroups: (t) => {
    const groups: { id: "node" | "tags" | "other"; label: string }[] = [
      {
        id: "node",
        label: t.dataStructureType.startsWith("blocks")
          ? "Blocks"
          : "Node data",
      },
    ];
    if (t.memory.tags.arrays.length > 0)
      groups.push({ id: "tags", label: "Lazy tags" });
    if (t.memory.other.arrays.length > 0)
      groups.push({ id: "other", label: "Extra arrays" });
    return groups;
  },
  layoutLabel: () => null,
  updateOps: new Set(["add", "addCount", "clear", "xorAll", "shiftAll"]),
  varName: "ms",
  pairResults: { mode: ["value", "freq"] },
  ctorNotes: CTOR_ARG_NOTES,
  ctorComments: (t) =>
    t.values === "offline"
      ? [
          "Offline: the constructor only learns which values can appear; the multiset starts empty, so add() each value yourself. Query arguments (x, lo, hi) can be anything.",
        ]
      : t.values === "online-range"
        ? [
            "Every value added must lie in [lo, hi]; query arguments can be anything.",
          ]
        : t.values === "online-bits"
          ? [
              "Every value added must lie in [0, 2^bits) (bits = 30 covers 10^9); so must x in the XOR queries. Other query arguments can be anything.",
            ]
          : [],
};

export function SetPicker() {
  return <TemplatePicker catalog={SET_CATALOG} />;
}
