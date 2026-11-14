import {
  tierOps,
  type MemoryBreakdown,
  type PickerOp,
  type PickerOpGroup,
  type PickerOpTier,
  type PickerTemplate,
  type TemplateLang,
} from "@/lib/template-picker";
import { DATA_STRUCTURE_TYPE_LABELS, type DataStructureType } from "@/lib/range-query-picker";

// The Tree queries picker (/templates/tree-queries): every op it will offer, grouped like the range picker. Templates
// are not generated yet, so nothing matches; the grid is the full menu of what's planned.
//
// One tree: Tree(edges, root, vals) with root required and vals optional. edges is [(a, b)], or [(a, b, w)] when
// edges carry a weight (an edge's weight is its value). Nodes are 0..n-1 or 1..n, found from the smallest label in the
// edge list (from root when there are no edges); vals[node] is node's value, so vals has length n (0-indexed) or n + 1
// (1-indexed, vals[0] ignored). Node ops and edge ops are named by what they act on
// and can be picked together: the template then keeps node values and edge values side by side, each edge stored at
// its child endpoint. A path a..b includes both ends; an edge query on a path covers the edges between a and b; a
// subtree's edges are the edges with both ends inside it. Node and edge ops come from one spec (valueGroups), so the
// two lists always match.

type Target = "node" | "edge";

const SHAPE: PickerOpGroup = {
  id: "shape",
  title: "Tree shape (no values)",
  tiers: [
    {
      kind: "topic",
      label: "Ancestors & distance",
      ops: [
        { id: "lca", signature: "lca(a, b)", description: "Lowest common ancestor of a and b" },
        { id: "unweightedDist", signature: "unweightedDist(a, b)", description: "Number of edges on the path a..b" },
        { id: "depth", signature: "depth(node)", description: "Edges from the root to node (the root is depth 0)" },
        { id: "parent", signature: "parent(node)", description: "node's parent (-1 for the root)" },
        { id: "kthAncestor", signature: "kthAncestor(node, k)", description: "The node k steps above node (k = 0 is node; -1 if past the root)" },
        { id: "isAncestor", signature: "isAncestor(a, b)", description: "Is a an ancestor of b? (true when a == b)" },
        { id: "subtreeSize", signature: "subtreeSize(node)", description: "Number of nodes in node's subtree (node included)" },
        { id: "countAtDepthInSubtree", signature: "countAtDepthInSubtree(node, d)", description: "Number of nodes in node's subtree at depth d (the root is depth 0)" },
      ],
    },
    {
      kind: "topic",
      label: "As if rooted at r",
      ops: [
        { id: "lcaRootedAt", signature: "lcaRootedAt(r, a, b)", description: "LCA of a and b if the tree were rooted at r instead" },
        { id: "parentRootedAt", signature: "parentRootedAt(r, node)", description: "node's parent if the tree were rooted at r (-1 when node == r)" },
        { id: "subtreeSizeRootedAt", signature: "subtreeSizeRootedAt(r, node)", description: "Size of node's subtree if the tree were rooted at r" },
      ],
    },
    {
      kind: "topic",
      label: "Paths",
      ops: [
        { id: "kthNodeOnPath", signature: "kthNodeOnPath(a, b, k)", description: "The kth node walking a -> b (k = 0 is a, k = unweightedDist(a, b) is b; -1 if k is past b)" },
        { id: "nextNodeOnPath", signature: "nextNodeOnPath(a, b)", description: "The neighbor of a one step toward b (-1 if a == b)" },
        { id: "isOnPath", signature: "isOnPath(a, b, node)", description: "Does the path a..b pass through node? (a and b count)" },
        { id: "unweightedDistToPath", signature: "unweightedDistToPath(a, b, node)", description: "Fewest edges from node to any node on the path a..b (0 if node is on it)" },
        { id: "unweightedDistBetweenPaths", signature: "unweightedDistBetweenPaths(a, b, c, d)", description: "Fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)" },
        { id: "median", signature: "median(a, b, c)", description: "The one node that lies on all three paths between a, b and c" },
        { id: "pathIntersection", signature: "pathIntersection(a, b, c, d)", description: "The shared part of paths a..b and c..d as its two end nodes (p, q); p == q if they share one node; (-1, -1) if they share none" },
        { id: "pathNodes", signature: "pathNodes(a, b)", description: "Every node on the path a..b, in order from a (O(length))" },
      ],
    },
  ],
};

// one op per target: the id and signature get the target's prefix ("node" / "edge")
const op = (p: string, name: string, args: string, description: string): PickerOp => ({
  id: `${p}${name}`,
  signature: `${p}${name}(${args})`,
  description,
});

// the same op done mod a fixed MOD, behind a checkbox under it (id + "Mod"; the values stay in [0, MOD))
const withMod = (o: PickerOp): PickerOp => ({
  ...o,
  modVariant: {
    id: `${o.id}Mod`,
    signature: o.signature.replace("(", "Mod("),
    description: `${o.description}, all mod MOD`,
  },
});

function valueGroups(t: Target): PickerOpGroup[] {
  const p = t;
  const Title = t === "node" ? "Node" : "Edge";
  const vals = t === "node" ? "node values" : "edge weights";
  const one = t === "node" ? "node" : "edge";
  const kindWord = t === "node" ? "value" : "weight";
  const v = t === "node" ? "val" : "weight";
  // one edge is named by its two ends, in either order: (a, b) and (b, a) are the same edge
  const at = t === "node" ? "node" : "a, b";
  const atText = t === "node" ? "node" : "a - b";
  const note = t === "node" ? undefined : "(a, b can be either order)";
  // the value an update brings: x for nodes, w (a weight) for edges
  const xv = t === "node" ? "x" : "w";
  const onPath = "on the path a..b";
  const inSub = t === "node" ? "in node's subtree" : "inside node's subtree";

  // the queries paths and subtrees both have
  // (moreCommon: path-only ops that belong at the top, beside Sum / Min / Max)
  const shared = (where: "Path" | "Subtree", moreCommon: PickerOp[] = []): PickerOpTier[] => {
    const args = where === "Path" ? "a, b" : "node";
    const w = where === "Path" ? onPath : inSub;
    const q = (name: string, extra: string, description: string) =>
      op(p, `${where}${name}`, extra ? `${args}, ${extra}` : args, description);
    // on a path these are answered with bitsets (one bit per distinct value), so memory grows with how many there are
    const smallSet = where === "Path" ? " (bitsets: for up to a few thousand distinct values)" : "";
    return [
      {
        kind: "common",
        ops: [
          { ...q("Sum", "", `Sum of the ${vals} ${w}`), modVariant: q("SumMod", "", `Sum of the ${vals} ${w}, mod MOD`) },
          q("Min", "", `Min ${one} ${kindWord} ${w}`),
          q("Max", "", `Max ${one} ${kindWord} ${w}`),
          q("Gcd", "", `Gcd of the ${vals} ${w}`),
          ...moreCommon,
        ],
      },
      {
        kind: "topic",
        label: "Rank",
        ops: [
          q("KthSmallest", "k", `kth smallest of the ${vals} ${w} (1-indexed: k = 1 is the min)`),
          q("KthLargest", "k", `kth largest of the ${vals} ${w} (1-indexed: k = 1 is the max)`),
        ],
      },
      {
        kind: "topic",
        label: "Count",
        ops: [
          q("CountLtX", "x", `How many ${vals} ${w} are < x`),
          q("CountLteX", "x", `How many ${vals} ${w} are ≤ x`),
          q("CountGtX", "x", `How many ${vals} ${w} are > x`),
          q("CountGteX", "x", `How many ${vals} ${w} are ≥ x`),
          q("CountInValRange", "low, high", `How many ${vals} ${w} are in [low, high]`),
        ],
      },
      {
        kind: "topic",
        label: "Sum",
        ops: [
          q("SumLtX", "x", `Sum of the ${vals} ${w} that are < x`),
          q("SumLteX", "x", `Sum of the ${vals} ${w} that are ≤ x`),
          q("SumGtX", "x", `Sum of the ${vals} ${w} that are > x`),
          q("SumGteX", "x", `Sum of the ${vals} ${w} that are ≥ x`),
          q("SumInValRange", "low, high", `Sum of the ${vals} ${w} in [low, high]`),
        ],
      },
      {
        kind: "topic",
        label: "Sum by rank (1-indexed)",
        ops: [
          q("SumSmallestK", "k", `Sum of the k smallest ${vals} ${w}`),
          q("SumLargestK", "k", `Sum of the k largest ${vals} ${w}`),
          q("SumKthSmallestRange", "kFrom, kTo", `Sum of the kFrom-th … kTo-th smallest ${vals} ${w}`),
          q("SumKthLargestRange", "kFrom, kTo", `Sum of the kFrom-th … kTo-th largest ${vals} ${w}`),
        ],
      },
      {
        kind: "topic",
        label: "Distance sums",
        ops: [
          q("SumAbsDiffToX", "x", `Σ |${v} − x| over the ${vals} ${w}`),
          q("SumAbsDiffToMedian", "", `Σ |${v} − median| over the ${vals} ${w} (the fewest ±1 steps to make them all equal)`),
        ],
      },
      {
        kind: "topic",
        label: "Nearest to x",
        ops: [
          q("SmallestGteX", "x", `Smallest of the ${vals} ${w} that is ≥ x`),
          q("SmallestGtX", "x", `Smallest of the ${vals} ${w} that is > x`),
          q("LargestLteX", "x", `Largest of the ${vals} ${w} that is ≤ x`),
          q("LargestLtX", "x", `Largest of the ${vals} ${w} that is < x`),
        ],
      },
      {
        kind: "topic",
        label: "Frequency",
        ops: [
          q("CountOccurrences", "x", `How many ${vals} ${w} equal x`),
          q("CountDistinct", "", `Number of distinct ${vals} ${w}${smallSet}`),
          q("AllDistinct", "", `Are all the ${vals} ${w} distinct?${smallSet}`),
          // (a path has no fast online mode or mex: those are offline only, so only subtrees offer them)
          ...(where === "Subtree" ? [q("Mode", "", `(mode, frequency) of the ${vals} ${w}`)] : []),
          q("AllEvenFrequency", "", `Does every value appear an even number of times ${w}?`),
          ...(where === "Subtree" ? [q("Mex", "", `Smallest integer ≥ 0 missing from the ${vals} ${w}`)] : []),
        ],
      },
      {
        kind: "topic",
        label: "Bit ops",
        collapsible: true,
        ops: [
          q("XOR", "", `XOR of the ${vals} ${w}`),
          q("AND", "", `AND of the ${vals} ${w}`),
          q("OR", "", `OR of the ${vals} ${w}`),
          q("MaxXorAgainstX", "x", `Largest ${v} ^ x over the ${vals} ${w}`),
          q("MinXorAgainstX", "x", `Smallest ${v} ^ x over the ${vals} ${w}`),
        ],
      },
    ];
  };

  const PATH = "Path a..b";
  const SUB = "Subtree of node";
  const ONE = t === "node" ? "One node" : "One edge";
  const inSection = (section: string, tiers: PickerOpTier[]) => tiers.map((tier) => ({ ...tier, section }));

  // the tree version of an arithmetic-sequence add: how far below node each value sits sets what it gets
  const byDepth =
    t === "node"
      ? "Every node u in node's subtree gets start + step · (depth(u) − depth(node)) added"
      : "Every edge inside node's subtree gets start + step · k added, k = edges between node and the edge's top end";
  const updates: PickerOpGroup = {
    id: `${t}-updates`,
    title: `${Title} updates`,
    note,
    tiers: [
      {
        kind: "topic",
        label: ONE,
        ops: [
          op(p, "Assign", `${at}, ${xv}`, `${v}(${atText}) = ${xv}`),
          op(p, "Add", `${at}, ${xv}`, `${v}(${atText}) += ${xv}`),
          op(p, "Chmax", `${at}, ${xv}`, `${v}(${atText}) = max(${v}, ${xv})`),
          op(p, "Chmin", `${at}, ${xv}`, `${v}(${atText}) = min(${v}, ${xv})`),
        ],
      },
      ...inSection(PATH, [
        {
          kind: "common",
          ops: [
            op(p, "PathAssign", `a, b, ${xv}`, `${v} = ${xv} for every ${one} ${onPath}`),
            withMod(op(p, "PathAdd", `a, b, ${xv}`, `${v} += ${xv} for every ${one} ${onPath}`)),
            op(p, "PathChmax", `a, b, ${xv}`, `${v} = max(${v}, ${xv}) for every ${one} ${onPath}`),
            op(p, "PathChmin", `a, b, ${xv}`, `${v} = min(${v}, ${xv}) for every ${one} ${onPath}`),
            op(p, "PathXORApply", `a, b, ${xv}`, `${v} ^= ${xv} for every ${one} ${onPath}`),
            op(p, "PathORApply", `a, b, ${xv}`, `${v} |= ${xv} for every ${one} ${onPath}`),
            op(p, "PathANDApply", `a, b, ${xv}`, `${v} &= ${xv} for every ${one} ${onPath}`),
            withMod(op(p, "PathAddArithSeq", "a, b, start, step", `Walking a -> b, the ${one}s get start, start + step, ... added`)),
            op(p, "PathMultMod", "a, b, m", `${v} = (${v} · m) % MOD for every ${one} ${onPath}`),
            op(p, "PathAffineMod", "a, b, mult, add", `${v} = (${v} · mult + add) % MOD for every ${one} ${onPath}`),
          ],
        },
      ]),
      ...inSection(SUB, [
        {
          kind: "common",
          ops: [
            op(p, "SubtreeAssign", `node, ${xv}`, `${v} = ${xv} for every ${one} ${inSub}`),
            withMod(op(p, "SubtreeAdd", `node, ${xv}`, `${v} += ${xv} for every ${one} ${inSub}`)),
            op(p, "SubtreeChmax", `node, ${xv}`, `${v} = max(${v}, ${xv}) for every ${one} ${inSub}`),
            op(p, "SubtreeChmin", `node, ${xv}`, `${v} = min(${v}, ${xv}) for every ${one} ${inSub}`),
            op(p, "SubtreeXORApply", `node, ${xv}`, `${v} ^= ${xv} for every ${one} ${inSub}`),
            op(p, "SubtreeORApply", `node, ${xv}`, `${v} |= ${xv} for every ${one} ${inSub}`),
            op(p, "SubtreeANDApply", `node, ${xv}`, `${v} &= ${xv} for every ${one} ${inSub}`),
            withMod(op(p, "SubtreeAddByDepth", "node, start, step", byDepth)),
            op(p, "SubtreeMultMod", "node, m", `${v} = (${v} · m) % MOD for every ${one} ${inSub}`),
            op(p, "SubtreeAffineMod", "node, mult, add", `${v} = (${v} · mult + add) % MOD for every ${one} ${inSub}`),
          ],
        },
      ]),
    ],
  };

  const firstOn = `First ${one} walking a -> b`;
  const lastOn = `Last ${one} walking a -> b`;
  const nearest = t === "node" ? "Nearest ancestor of node (node included)" : "Nearest edge above node (toward the root)";
  // what a search returns: the node itself, or an edge named by its lower (child) end
  const found = t === "node" ? "-1 if none" : "returns the edge's child end; -1 if none";
  // the first node walking a -> b whose prefix sum crosses x, and the last whose suffix sum does (the ≥ / > ones need
  // values ≥ 0 so the sums only grow)
  const none = found.replace("none", "no such one");
  const cmps = [["Gte", "≥"], ["Gt", ">"], ["Lte", "≤"], ["Lt", "<"]] as const;
  const cmpsEq = [...cmps, ["Eq", "="]] as const;
  const needs = (c: string) => (c.startsWith("G") ? `needs ${v} ≥ 0; ` : "");
  const prefixSearch = [
    ...cmps.map(([c, sym]) =>
      op(p, `PathFirstPrefixSum${c}X`, "a, b, x", `${firstOn} where the sum from a to it is ${sym} x (${needs(c)}${none})`),
    ),
    ...cmps.map(([c, sym]) =>
      op(p, `PathLastSuffixSum${c}X`, "a, b, x", `${lastOn} where the sum from it to b is ${sym} x (${needs(c)}${none})`),
    ),
  ];
  const queries: PickerOpGroup = {
    id: `${t}-queries`,
    title: `${Title} queries`,
    note,
    tiers: [
      { kind: "topic", label: ONE, ops: [op(p, "Get", at, `${v}(${atText})`)] },
      ...inSection(PATH, [
        ...shared("Path", [
          op(p, "PathMaxSubarraySum", "a, b", "Max sum of a non-empty stretch of the path"),
          op(p, "PathMinSubarraySum", "a, b", "Min sum of a non-empty stretch of the path"),
          op(p, "PathLongestEqualRun", "a, b", `Longest run of equal adjacent ${vals} along the path`),
        ]),
        {
          kind: "topic",
          label: "Prefix / suffix sums (path is a -> b)",
          collapsible: true,
          ops: [
            op(p, "PathMaxPrefixSum", "a, b", `Max sum of a prefix of the path`),
            op(p, "PathMinPrefixSum", "a, b", `Min sum of a prefix of the path`),
            op(p, "PathMaxSuffixSum", "a, b", `Max sum of a suffix of the path`),
            op(p, "PathMinSuffixSum", "a, b", `Min sum of a suffix of the path`),
            ...prefixSearch,
          ],
        },
        {
          kind: "topic",
          label: "Hashing",
          collapsible: true,
          ops: [
            op(p, "PathHash", "a, b", `Hash of the ${vals} read a -> b (equal sequences hash equal)`),
            op(p, "PathHashReversed", "a, b", `Hash of the ${vals} read b -> a (equal to ${p}PathHash(b, a))`),
            op(p, "PathIsPalindrome", "a, b", `Do the ${vals} read the same a -> b and b -> a?`),
            op(p, "PathsEqual", "a, b, c, d", `Do the ${vals} read a -> b equal those read c -> d?`),
          ],
        },
        {
          kind: "topic",
          label: "Search",
          ops: [
            ...cmpsEq.map(([c, sym]) => op(p, `PathFirst${c}X`, "a, b, x", `${firstOn} with ${v} ${sym} x (${found})`)),
            ...cmpsEq.map(([c, sym]) => op(p, `PathLast${c}X`, "a, b, x", `${lastOn} with ${v} ${sym} x (${found})`)),
            ...cmpsEq.map(([c, sym]) => op(p, `NearestAncestor${c}X`, "node, x", `${nearest} with ${v} ${sym} x (${found})`)),
          ],
        },
      ]),
      ...inSection(SUB, shared("Subtree")),
    ],
  };

  return [updates, queries];
}

export const TREE_QUERY_OP_GROUPS: PickerOpGroup[] = [SHAPE, ...valueGroups("node"), ...valueGroups("edge")];

// the ops that change values
export const TREE_UPDATE_OPS = new Set([
  ...TREE_QUERY_OP_GROUPS.filter((g) => g.id.endsWith("-updates")).flatMap((g) => g.tiers.flatMap((tier) => tierOps(tier).map((o) => o.id))),
]);

// what each implementation is, lightest first (the picker's tie-breaker); the same list as TYPES in
// scripts/build-tree-query-templates.mjs. The two shape templates, then the value templates: each is named for the
// range structure it keeps the values in, in the range picker's order.
const VALUE_STRUCTURE_TYPES = [
  "prefix-sum", "difference-array", "positions", "interval-map", "sparse-table", "BIT", "seg-tree", "lazy-seg-tree", "beats",
  "merge-sort-tree", "wavelet", "persistent", "bit-of-trees", "bit-of-tries", "seg-of-trees", "position-trees", "sqrt",
  "sqrt-tries",
] as const satisfies readonly DataStructureType[];
// structures of the tree templates' own (no range template inside): a Fenwick tree whose prefixes are root paths; a
// persistent seg tree with a version per node
const OWN_STRUCTURE_TYPES = ["euler-fenwick", "persistent-paths", "bitset-seg-tree", "run-seg-tree", "root-prefix"] as const;
export const TREE_STRUCTURE_TYPES = ["heavy-light", "heavy-light-lca-table", ...VALUE_STRUCTURE_TYPES, ...OWN_STRUCTURE_TYPES] as const;
export type TreeStructureType = (typeof TREE_STRUCTURE_TYPES)[number];

const SHAPE_LABELS = {
  "heavy-light": "Heavy-light decomposition",
  "heavy-light-lca-table": "Heavy-light decomposition + O(1) lca table",
  "euler-fenwick": "Fenwick tree on the Euler tour (single-log path queries)",
  "persistent-paths": "Persistent seg tree, a version per node (its path from the root)",
  "bitset-seg-tree": "Seg tree of bitsets, a bit per distinct value (for few distinct values)",
  "run-seg-tree": "Seg tree of runs that knows which way a path piece is read",
  "root-prefix": "Sums from the root + O(1) lca table (fixed values, O(1) queries)",
} as const;

// "Lazy seg tree over heavy-light order": the range structure, laid over the tree's positions
export const treeStructureLabel = (type: TreeStructureType): string =>
  type in SHAPE_LABELS
    ? SHAPE_LABELS[type as keyof typeof SHAPE_LABELS]
    : `${DATA_STRUCTURE_TYPE_LABELS[type as DataStructureType]} over heavy-light order`;

// A template with one of these keeps every value mod MOD, so it is only offered once one of them is picked (else a
// plain selection like nodeGet + nodeAdd could land on a mod template).
export const isTreeModOp = (op: string) => /Mod$/.test(op);

export interface TreeQueryTemplate extends PickerTemplate {
  dataStructureType: TreeStructureType;
}

export type TreeQueryRow = [
  folder: string,
  langs: string,
  type: TreeStructureType,
  opList: number,
  costs: number[],
  build: number,
  memory: number,
];

// lib/generated/tree-query-templates.ts: shared tables plus one short row per template
export interface TreeQueryManifest {
  costs: string[];
  opLists: string[][];
  memories: MemoryBreakdown[];
  rows: TreeQueryRow[];
}

export function decodeTreeQueryTemplates(m: TreeQueryManifest): TreeQueryTemplate[] {
  return m.rows.map(([folder, langs, type, opList, costs, build, memory]) => {
    const operations = m.opLists[opList];
    return {
      folder,
      file: "template",
      langs: langs.split(" ") as TemplateLang[],
      operations,
      dataStructureType: type,
      complexities: Object.fromEntries(operations.map((op, i) => [op, m.costs[costs[i]]])),
      build: m.costs[build],
      memory: m.memories[memory],
    };
  });
}

// planned after these ops
export const TREE_QUERY_PLANNED = [
  "rerooting for value queries: subtree of node when rooted at r",
];
