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

// What you know about the values ahead of time decides which templates can work: every value (offline) or nothing.
// Knowing more never rules a template out.
const USABLE: Record<string, SetTemplate["values"][]> = {
  known: ["offline", "online"],
  unknown: ["online"],
};

const CTOR_ARG_NOTES: Record<string, { py: string; cpp: string }> = {
  allValuesThatWillEverBeInsertedForOfflineCompression: {
    py: "allValuesThatWillEverBeInsertedForOfflineCompression: every value you will ever add (a list; any order, duplicates fine). Only used to compress values: this does NOT add them, the multiset starts empty. N = how many distinct",
    cpp: "allValuesThatWillEverBeInsertedForOfflineCompression: every value you will ever add (vector<long long>; any order, duplicates fine). Only used to compress values: this does NOT add them, the multiset starts empty. N = how many distinct",
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
        label: "All values known",
        title:
          "You know every value that will ever be added (queries' x can still be anything): every structure works, including the Fenwick over compressed values",
      },
      {
        mode: "unknown",
        label: "Nothing known",
        title:
          "Values aren't known ahead: only comparison-based structures (AVL tree, sorted blocks)",
      },
    ],
    parse: (v) => (v && v in USABLE ? v : "known"),
    views: (mode) => VIEWS.filter((t) => USABLE[mode].includes(t.values)),
  },
  // Fenwick and AVL come with and without mex (it costs them an extra array); sorted blocks always have it for free
  kindLabel: (t) => {
    const extras = [
      ...(t.operations.includes("sumAll") ? ["sums"] : []),
      ...(t.operations.includes("mex") &&
      (t.dataStructureType === "fenwick" || t.dataStructureType === "avl")
        ? ["mex"]
        : []),
    ];
    return (
      SET_TYPE_LABELS[t.dataStructureType] +
      (extras.length ? ` with ${extras.join(" + ")}` : "") +
      (t.values === "offline" ? " (offline)" : "")
    );
  },
  memoryGroups: (t) => {
    const groups: { id: "node" | "tags" | "other"; label: string }[] = [
      {
        id: "node",
        label: t.dataStructureType === "blocks" ? "Blocks" : "Node data",
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
      : [],
};

export function SetPicker() {
  return <TemplatePicker catalog={SET_CATALOG} />;
}
