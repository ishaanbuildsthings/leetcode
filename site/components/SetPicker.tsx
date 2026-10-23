"use client";

import {
  TemplatePicker,
  type PickerCatalog,
} from "@/components/TemplatePicker";
import {
  SET_OP_GROUPS,
  SET_TYPES,
  SET_TYPE_LABELS,
  type SetTemplate,
} from "@/lib/set-picker";
import { SET_TEMPLATES } from "@/lib/generated/set-templates";

type SetView = SetTemplate & { file: "template" };

const VIEWS: SetView[] = SET_TEMPLATES.map((t) => ({ ...t, file: "template" }));

// Knowing every value ahead (offline) allows everything, including the Fenwick tree on compressed values. Online
// allows the comparison-based structures plus the value seg tree, which only needs a [lo, hi] all values lie in.
const USABLE: Record<string, SetTemplate["values"][]> = {
  known: ["offline", "online-range", "online"],
  unknown: ["online-range", "online"],
};

// These structures come with and without mex (it costs them one more field per node / array); the sorted lists find
// mex from their keys for free, so theirs always has it.
const OPTIONAL_MEX = new Set([
  "fenwick",
  "value-tree",
  "avl",
  "treap",
  "splay",
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
  typeOrder: SET_TYPES,
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
  // "AVL tree — counts + sums, mex": what it keeps (counts only, or counts and sums), mex where it's optional, and
  // what it needs to know up front
  kindLabel: (t) => {
    const parts = [
      t.operations.includes("sumAll") ? "counts + sums" : "counts only",
    ];
    if (OPTIONAL_MEX.has(t.dataStructureType) && t.operations.includes("mex"))
      parts.push("mex");
    if (t.values === "offline") parts.push("offline");
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
  updateOps: new Set(["add", "addCount"]),
  varName: "ms",
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
        : [],
};

export function SetPicker() {
  return <TemplatePicker catalog={SET_CATALOG} />;
}
