"use client";

import { TemplatePicker, type CtorNote, type PickerCatalog } from "@/components/TemplatePicker";
import {
  OP_GROUPS,
  DATA_STRUCTURE_TYPES,
  TREE_LAYOUT_LABELS,
  type OpId,
  type RangeQueryTemplate,
  type TemplateView,
  type TemplateLang,
  CHAR_SAFE_OPS,
  lettersView,
  viewOf,
  templateKindLabel,
  isBuiltFromPoints,
  decodeRangeTemplates,
} from "@/lib/range-query-picker";
import {
  RANGE_COST_LISTS,
  RANGE_COSTS,
  RANGE_MEMORIES,
  RANGE_OP_LISTS,
  RANGE_OP_NAMES,
  RANGE_FAST_FOLDERS,
  RANGE_TEMPLATE_ROWS,
} from "@/lib/generated/range-query-templates";
import { FAST_DRAWBACKS, FAST_NO_SANITIZE } from "@/lib/fast-mode";
import { GENERIC_SEG_TREES } from "@/lib/generic-seg-trees";

const RANGE_QUERY_TEMPLATES = decodeRangeTemplates({
  opNames: RANGE_OP_NAMES,
  costs: RANGE_COSTS,
  opLists: RANGE_OP_LISTS,
  costLists: RANGE_COST_LISTS,
  memories: RANGE_MEMORIES,
  rows: RANGE_TEMPLATE_ROWS,
});
const FAST_FOLDERS = new Set<string>(RANGE_FAST_FOLDERS);
const ALL_OPS = OP_GROUPS.flatMap((g) => g.tiers.flatMap((t) => t.ops.map((o) => o.id)));
// The mod p ops (rangeAddMod, ..., rangeSumMod; not rangeMod, which is a[i] %= m). A template with any of them does all
// its arithmetic mod p, so it is only offered once you pick one of them; otherwise a selection like pointGet + pointAdd
// could land on a mod template.
const MOD_P_OPS = new Set<string>(ALL_OPS.filter((id) => id.endsWith("Mod") && id !== "rangeMod"));
const isModP = (t: RangeQueryTemplate) => t.operations.some((op) => MOD_P_OPS.has(op));

// Ops that change the array (no result to read): the range updates, the sequence edits and every point op but pointGet.
const UPDATE_OPS = new Set<string>(
  OP_GROUPS.filter((g) => g.id === "range-updates" || g.id === "sequence" || g.id === "point")
    .flatMap((g) => g.tiers.flatMap((t) => t.ops.map((o) => o.id)))
    .filter((id) => id !== "pointGet")
);

// What each constructor argument is, by its name in the source ("lo" / "hi" are covered by the sparse sentences).
const CTOR_ARG_NOTES: Record<string, CtorNote> = {
  hashBase: { py: "", cpp: "", shown: false },  // (the rolling-hash templates: explained by the example lines, see ctorComments)
  hashMod: { py: "", cpp: "", shown: false },
  cap: { py: "", cpp: "", shown: false },  // (the LCM cap: TemplatePicker explains it, with a one-line example)
  arr: { py: "arr: the initial array (a list), 0-indexed", cpp: "arr: the initial array (vector<long long>), 0-indexed", inCall: true },
  a: { py: "a: the initial array (a list), 0-indexed", cpp: "a: the initial array (vector<long long>), 0-indexed" },
  values: {
    py: "values: the nonzero entries, as a list of (index, value) pairs (distinct indices in [lo, hi], any order)",
    cpp: "values: the nonzero entries, as vector<pair<long long, long long>> of (index, value) (distinct indices in [lo, hi], any order)",
  },
  brackets: {
    py: 'brackets: the sequence, a list of characters like ["(", ")", "("] (a str like "()(" works too)',
    cpp: "brackets: the sequence as vector<char>, e.g. vector<char>(s.begin(), s.end()) for a string s",
  },
  openChar: {
    py: 'which character opens: pass e.g. "[" for square brackets (every other character closes)',
    cpp: "which character opens: pass e.g. '[' for square brackets (every other character closes)",
    example: { py: '"["', cpp: "'['" },
  },
  closeChar: {
    py: 'which character closes: pass e.g. "]" for square brackets (a character that isn\'t openChar counts as this one)',
    cpp: "which character closes: pass e.g. ']' for square brackets (a character that isn't openChar counts as this one)",
    example: { py: '"]"', cpp: "']'" },
  },
  mod: { py: "the modulus p", cpp: "the modulus p", example: { py: "998244353", cpp: "998244353" } },
  bits: { py: "values live in [0, 2^bits)", cpp: "values live in [0, 2^bits)", example: { py: "30", cpp: "30" } },
  cutoff: {
    py: "seg trees are kept for steps up to it (more memory and slower updates, faster big-step queries); left out, it is a quarter of sqrt(n / log n)",
    cpp: "seg trees are kept for steps up to it (more memory and slower updates, faster big-step queries); left out, it is sqrt(n / log n)",
    example: { py: "64", cpp: "64" },
  },
  allValuesThatWillEverBeInsertedForOfflineCompression: {
    py: "allValuesThatWillEverBeInsertedForOfflineCompression: every value append will ever get (a list; any order, duplicates fine). Only used to compress values: this does NOT add them. N = how many distinct",
    cpp: "allValuesThatWillEverBeInsertedForOfflineCompression: every value append will ever get (vector<long long>; any order, duplicates fine). Only used to compress values: this does NOT add them. N = how many distinct",
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
  githubBase: "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/",
  typeOrder: DATA_STRUCTURE_TYPES,
  perType: 3,
  // one that needs every value up front never stands in for one that doesn't, nor a dense one for a sparse one
  noWorse: (s, m) => (!s.valuesOffline || !!m.valuesOffline) && (s.file !== "sparse" ? m.file !== "sparse" : true),
  fastMode: {
    label: "Fast mode",
    explain: () => ({
      how: "Sanitizers are skipped inside the template, so the gain only shows up on LeetCode.",
      drawbacks: FAST_DRAWBACKS,
      noSanitize: FAST_NO_SANITIZE,
    }),
    title:
      "C++ only. Sanitizers are skipped inside the template, so a bad access there goes unreported.",
    has: (t) => FAST_FOLDERS.has(t.folder),
  },
  flag: {
    label: "Values are chars",
    title:
      "The array is a list of characters (any: letters, capitals, digits, brackets like [ or (, ...), not numbers: only templates that take characters are offered (some through a separate characters version of the file), and ops that need numbers (sums, adds, xor, gcd, mod, ...) are greyed out",
    storageKey: "rangeQueryPicker.letters",
    keep: () => true,
    view: lettersView,
    disabledOps: new Set(ALL_OPS.filter((op) => !CHAR_SAFE_OPS.has(op))),
    disabledTitle: "Needs number values: not available with characters",
    // (char is a keyword in C++, so its usage lines say ch)
    rename: (text, lang) => text.replace(/\b(val|v)\b/g, lang === "cpp" ? "ch" : "char"),
  },
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
      { id: "node", label: type === "sparse-table" ? "Table" : type === "sqrt" ? "Blocks" : type === "positions" ? "Lists" : type === "wavelet" || type === "prefix-sum" || type === "difference-array" || type === "agg-deque" ? "Arrays" : "Node data" },
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
  // offered for characters (the box is ticked): the array is a list of characters
  ctorNotes: (t) =>
    t.dataStructureType === "rolling-hash"
      ? {
          ...CTOR_ARG_NOTES,
          arr: {
            py: "arr: the initial array (a list of ints, negatives included, or a string / list of single characters), or leave it out to start empty",
            cpp: "arr: the initial array (a vector of ints, long longs or chars; negatives are fine), or leave it out to start empty",
            inCall: true,
          },
        }
      : t.chars
      ? {
          ...CTOR_ARG_NOTES,
          arr: { py: 'arr: the initial array, a list of characters, e.g. list(s) for a string s, 0-indexed', cpp: "arr: the initial array as vector<char>, e.g. vector<char>(s.begin(), s.end()), 0-indexed", inCall: true },
          a: { py: 'a: the initial array, a list of characters, e.g. list(s) for a string s, 0-indexed', cpp: "a: the initial array as vector<char>, e.g. vector<char>(s.begin(), s.end()), 0-indexed" },
        }
      : CTOR_ARG_NOTES,
  ctorCommentsAfterArgs: (t) => t.dataStructureType === "rolling-hash",
  ctorComments: (t, lang) =>
    t.dataStructureType === "rolling-hash"
      ? rollingHashExamples(t, lang)
      : t.file !== "sparse"
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
  pairResults: {
    rangeMode: ["value", "freq"],
    longestPalCenteredAtI: ["l", "r"],
    longestPalCenteredAtIPlusOne: ["l", "r"],
    cut: ["piece"],
    copy: ["piece"],
    split: ["left", "right"],
    trisect: ["left", "mid", "right"],
  } satisfies Partial<Record<OpId, string[]>>,
  fillIns: GENERIC_SEG_TREES,
  planned: [
    "2D tree queries",
    "persistent seg tree queries",
    "tuple values with a custom comparator",
    "interval tree",
    "2D sparse table",
    "multiset hashing",
    "2D hashing",
    "centroid decomposition",
    "tree paths / subtrees / general tree movement (LCA, path templates)",
    "subset xors, linear bases",
    "custom hash tables",
    "Mo's page, Mo's with updates",
    "all prime / prime factor stuff",
    "DnC DP golden",
    "alien trick golden",
    "LIS things",
    "SOS DP and other bit things",
    "geometry",
  ],
};

// The rolling-hash constructors take an optional base and mod: shown as the constructions, not as "optional" notes.
// Left out, every structure of the run shares one random base (so their hashes compare) and the mod 2^61 - 1.
function rollingHashExamples(t: TemplateView, lang: TemplateLang): string[] {
  const name = t.folder === "rolling-hash-window" ? "RollingHashWindow" : t.folder === "rolling-hash-two-stacks" ? "RollingHashDeque"
    : t.folder === "rolling-hash-palindrome" ? "RollingHashPalindrome" : "RollingHashPalindromeDeque";
  const elem = t.chars ? "char" : "long long";
  return lang === "py"
    ? [
        "Hashing just works for arrays of negatives, large numbers, chars, using the default random base value",
        "If we don't set the base or mod ourselves, they are shared between structures so we can compare hashes",
        "Set hashBase / hashMod only to match something else:",
        `  seg = ${name}(arr, hashBase=911)                       # your base, mod 2^61 - 1`,
        `  seg = ${name}(arr, hashMod=10**9 + 7)                  # the run's base, your prime mod`,
        `  seg = ${name}(arr, hashBase=911, hashMod=10**9 + 7)    # both`,
      ]
    : [
        "Hashing just works for arrays of negatives, large numbers, chars, using the default random base value",
        "If we don't set the base or mod ourselves, they are shared between structures so we can compare hashes",
        "Set hashBase / hashMod only to match something else:",
        `  ${name}<${elem}> seg(arr, 911);                    // your base, mod 2^61 - 1`,
        `  ${name}<${elem}> seg(arr, nullopt, 1000000007);    // the run's base, your prime mod`,
        `  ${name}<${elem}> seg(arr, 911, 1000000007);        // both`,
      ];
}

export function RangeQueryPicker() {
  return <TemplatePicker catalog={RANGE_CATALOG} />;
}
