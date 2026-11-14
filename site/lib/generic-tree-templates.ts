import type { FillIn } from "@/components/TemplatePicker";

// The generic tree templates you fill in yourself (templates/ultimate-template-tool/generic-trees/, written by
// tree-query-tests/gen_tree_generic.py): the tree query picker's "Generic tree templates" menu lists them. You write what
// a stretch of values is summed up as and how two stretches join; there are no identity values to give.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-trees/";
const REVERSE = {
  reverseToggle: true,
  reverseLabel: "order matters on a path",
  reverseTitle:
    "Tick this when reading a path a -> b gives a different answer than b -> a (max subarray sum, hashing, ...): the template then also needs nodeReverse / edgeReverse, the data of a stretch read backwards",
  reverseKey: "treeQueryPicker.genericWithReverse",
} as const;
// (the C++ files are in fast mode, like every tree template, and that covers the functions filled in)
const CPP_NOTE =
  "C++ is in fast mode: sanitizers are skipped in the tree and in the functions you fill in (each starts with LEETCODE_NO_SANITIZE), so a bad access in them goes unreported on LeetCode. To debug with sanitizers, put #define LEETCODE_NO_SANITIZE above the template. A helper your functions call, or a constructor of your data or tag struct, needs LEETCODE_NO_SANITIZE too to stay fast.";
const EDGE_NOTE =
  "An edge is named by its two ends in either order. An edge query with no edges (the path a..a, the edges below a leaf) raises, since there is no identity value to return; an edge update there does nothing.";

const nodeOps = (lazy: boolean): [string, string][] => [
  ["nodeGet(node)", lazy ? "log(N)" : "1"],
  ["nodeAssign(node, val)", "log(N)"],
  ...(lazy ? ([["nodeUpdate(node, tag)", "log(N)"]] as [string, string][]) : []),
  ["nodePathQuery(a, b)", "log^2(N)"],
  ...(lazy ? ([["nodePathUpdate(a, b, tag)", "log^2(N)"]] as [string, string][]) : []),
  ["nodeSubtreeQuery(node)", "log(N)"],
  ...(lazy ? ([["nodeSubtreeUpdate(node, tag)", "log(N)"]] as [string, string][]) : []),
];
const edgeOps = (lazy: boolean): [string, string][] => [
  ["edgeGet(a, b)", lazy ? "log(N)" : "1"],
  ["edgeAssign(a, b, w)", "log(N)"],
  ...(lazy ? ([["edgeUpdate(a, b, tag)", "log(N)"]] as [string, string][]) : []),
  ["edgePathQuery(a, b)", "log^2(N)"],
  ...(lazy ? ([["edgePathUpdate(a, b, tag)", "log^2(N)"]] as [string, string][]) : []),
  ["edgeSubtreeQuery(node)", "log(N)"],
  ...(lazy ? ([["edgeSubtreeUpdate(node, tag)", "log(N)"]] as [string, string][]) : []),
];
const BUILD: [string, string] = ["build", "N"];

// shapeOps: every tree shape op the Tree also has (lca, kthAncestor, ...), as [signature, cost], listed under the value ops
const family = (kind: "Nodes" | "Edges" | "Both", lazy: boolean, shapeOps: [string, string][]): FillIn => {
  const what = { Nodes: "node values", Edges: "edge weights", Both: "node values + edge weights" }[kind];
  const fill = {
    Nodes: "NodeData, nodeLeaf(v, node) and nodeCombine",
    Edges: "EdgeData, edgeLeaf(w, a, b) and edgeCombine",
    Both: "NodeData / EdgeData, nodeLeaf / edgeLeaf and nodeCombine / edgeCombine (two separate merges: node queries and edge queries never see each other)",
  }[kind];
  const tags = { Nodes: "a NodeTag, nodeApply and nodeCompose", Edges: "an EdgeTag, edgeApply and edgeCompose", Both: "a tag, apply and compose for each" }[kind];
  return {
    label: `Generic ${lazy ? "lazy " : ""}tree: ${what}`,
    title: lazy
      ? `Fill in ${fill}, plus ${tags}: a tag applied to one, to a path or to a subtree`
      : `Fill in ${fill}: get, assign, path query, subtree query`,
    folder: "_generic",
    file: `Generic${lazy ? "Lazy" : ""}Tree${kind}`,
    cppLevels: true,
    ...REVERSE,
    ops: [
      ...(kind === "Edges" ? [] : ([["Node values", ""], ...nodeOps(lazy)] as [string, string][])),
      ...(kind === "Nodes" ? [] : ([["Edge weights", ""], ...edgeOps(lazy)] as [string, string][])),
      BUILD,
      ["Tree shape (no values)", ""],
      ...shapeOps,
    ],
    note: kind === "Nodes" ? undefined : EDGE_NOTE,
    cppNote: CPP_NOTE,
    githubUrl: GITHUB,
  };
};

export const genericTreeTemplates = (shapeOps: [string, string][]): FillIn[] => [
  family("Nodes", false, shapeOps),
  family("Nodes", true, shapeOps),
  family("Edges", false, shapeOps),
  family("Edges", true, shapeOps),
  family("Both", false, shapeOps),
  family("Both", true, shapeOps),
];
