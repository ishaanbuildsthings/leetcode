import type { FillIn } from "@/components/TemplatePicker";

// The graph templates (templates/ultimate-template-tool/graphs/): one function each, on the Graphs tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/";

export const EULER: FillIn[] = [
  {
    label: "Euler circuit, directed O(V + E)",
    title: "A walk over an [a, b] edge list (a -> b) using every edge once and ending where it started, or None / {} if there isn't one. Optional start; labels 0..n-1 or 1..n",
    folder: "_graphs",
    file: "eulerCircuitDirected",
    ops: [["eulerCircuitDirected(edges, start?) -> [node, ...] (len(edges) + 1, first == last), or None", "V+E"]],
    githubUrl: GITHUB,
  },
  {
    label: "Euler path, directed O(V + E)",
    title: "A walk over an [a, b] edge list (a -> b) using every edge once, or None / {} if there isn't one. Optional start and end, picked from the degrees if left out; a circuit counts. Labels 0..n-1 or 1..n",
    folder: "_graphs",
    file: "eulerPathDirected",
    ops: [["eulerPathDirected(edges, start?, end?) -> [node, ...] (len(edges) + 1), or None", "V+E"]],
    githubUrl: GITHUB,
  },
  {
    label: "Euler circuit, undirected O(V + E)",
    title: "A walk over an undirected [a, b] edge list using every edge once and ending where it started, or None / {} if there isn't one. Optional start; labels 0..n-1 or 1..n",
    folder: "_graphs",
    file: "eulerCircuitUndirected",
    ops: [["eulerCircuitUndirected(edges, start?) -> [node, ...] (len(edges) + 1, first == last), or None", "V+E"]],
    githubUrl: GITHUB,
  },
  {
    label: "Euler path, undirected O(V + E)",
    title: "A walk over an undirected [a, b] edge list using every edge once, or None / {} if there isn't one. Optional start and end, picked from the odd-degree nodes if left out; a circuit counts. Labels 0..n-1 or 1..n",
    folder: "_graphs",
    file: "eulerPathUndirected",
    ops: [["eulerPathUndirected(edges, start?, end?) -> [node, ...] (len(edges) + 1), or None", "V+E"]],
    githubUrl: GITHUB,
  },
];

// Strongly connected components (scc.*)
export const SCC: FillIn[] = [
  {
    label: "Strongly connected components O(V + E)",
    title: "Directed [a, b] edge list (a -> b), plus n and whether labels start at 1 (both required: a node with no edges never shows up in the edge list but is still its own component). Returns each node's component, each component's nodes, and the condensation DAG, ids in reverse topological order",
    folder: "_graphs",
    file: "scc",
    ops: [
      ["buildScc(edges, n, oneIndexed: bool) -> scc", "V+E"],
      ["scc.numComponents -> how many components", "1"],
      ["scc.nodeToComponentId[node] -> its component id", "1"],
      ["scc.componentNodes[compId] -> its nodes, increasing", "1"],
      ["scc.componentAdj[compId] -> components it has edges to (acyclic)", "1"],
    ],
    githubUrl: GITHUB,
  },
];

// Dijkstra (dijkstraDirected.* / dijkstraUndirected.*)
const dijkstra = (kind: "Directed" | "Undirected"): FillIn => ({
  label: `Dijkstra, ${kind.toLowerCase()} O((V + E) log E)`,
  title: `Shortest distances from a source over a weighted [a, b, w] edge list (${kind === "Directed" ? "a -> b" : "both ways"}, w >= 0), plus the previous node on a shortest path. n and oneIndexed are required: a node with no edges never shows up in the edge list`,
  folder: "_graphs",
  file: `dijkstra${kind}`,
  ops: [
    [`dijkstra${kind}(edges, n, oneIndexed: bool, source) -> (dist, prev)`, "V*log(E)+E*log(E)"],
    ["dist[node] -> shortest distance from source to node. None (C++: -1) if node can't be reached. With oneIndexed, dist[0] is an unused placeholder", "1"],
    ["prev[node] -> only for tracing the route itself: the node one step before node on a shortest route. None (C++: -1) for the source and unreachable nodes; prev[0] unused with oneIndexed", "1"],
  ],
  githubUrl: GITHUB,
});
export const DIJKSTRA: FillIn[] = [dijkstra("Directed"), dijkstra("Undirected")];
