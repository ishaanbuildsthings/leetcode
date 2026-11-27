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

// Topological sort / DAG check (topoSort.*)
export const TOPO_SORT: FillIn[] = [
  {
    label: "Topological sort + DAG check O(V + E)",
    title: "Directed [a, b] edge list (a -> b, a must come before b), plus n and whether labels start at 1 (both required: a node with no edges still has to be in the order). Returns None (C++: {}) if there's a cycle, else every node once with a before b for every edge a -> b: nodes with no incoming edges first",
    folder: "_graphs",
    file: "topoSort",
    ops: [
      ["topoSort(edges, n, oneIndexed: bool) -> [node, ...] sources first, or None if not a DAG (C++: {})", "V+E"],
    ],
    githubUrl: GITHUB,
  },
];

// Floyd-Warshall (floydWarshallDirected.* / floydWarshallUndirected.*, each with a .oneIndexed twin behind the checkbox)
const floydWarshall = (kind: "Directed" | "Undirected"): FillIn => {
  const fn = `floydWarshall${kind}`;
  const edgeWord = kind === "Directed" ? "a -> b" : "both ways";
  return {
    label: `Floyd-Warshall, ${kind.toLowerCase()} O(V^3)`,
    title: `Shortest distance between every pair of nodes over a weighted [a, b, w] edge list (${edgeWord}, w >= 0; negative weights are an error). numNodes is required: a node with no edges never shows up in the edge list. Nodes 0..numNodes-1`,
    folder: "_graphs",
    file: fn,
    ops: [
      [`${fn}(numNodes, edges) -> dist, a numNodes x numNodes matrix`, "V^3+E"],
      ["dist[a][b] -> shortest distance from a to b. INF if b can't be reached from a (Python: float('inf'), C++: LLONG_MAX / 4), 0 for a to itself", "1"],
    ],
    variant: {
      label: "1-indexed",
      title: "Nodes are 1..numNodes instead of 0..numNodes-1. The matrix is (numNodes + 1) x (numNodes + 1) and node 0's row and column are unused (all INF)",
      storageKey: `templatePicker.oneIndexed.${fn}`,
      on: {
        title: `Shortest distance between every pair of nodes over a weighted [a, b, w] edge list (${edgeWord}, w >= 0; negative weights are an error). numNodes is required: a node with no edges never shows up in the edge list. Nodes 1..numNodes`,
        file: `${fn}.oneIndexed`,
        ops: [
          [`${fn}(numNodes, edges) -> dist, a (numNodes + 1) x (numNodes + 1) matrix`, "V^3+E"],
          ["dist[a][b] -> shortest distance from a to b. INF if b can't be reached from a (Python: float('inf'), C++: LLONG_MAX / 4), 0 for a to itself. Row 0 and column 0 are unused (all INF)", "1"],
        ],
      },
    },
    githubUrl: GITHUB,
  };
};
export const FLOYD_WARSHALL: FillIn[] = [floydWarshall("Directed"), floydWarshall("Undirected")];

// Functional graph breakdown (functionalGraph.*, with a .oneIndexed twin behind the checkbox)
export const FUNCTIONAL_GRAPH: FillIn[] = [
  {
    label: "Functional graph breakdown O(V)",
    title: "Every node has exactly one outgoing edge, so each component is one cycle with tails feeding in. Directed [a, b] edge list (a -> b), one edge per node, so no node count. Nodes 0..len(edges)-1",
    folder: "_graphs",
    file: "functionalGraph",
    ops: [
      ["FunctionalGraph(edges) -> fg", "V"],
      ["fg.cycles() -> every cycle, only the nodes on it, in walking order ([1, 2, 3] is 1 -> 2 -> 3 -> 1), each starting at its smallest node, sorted by that node", "1"],
      ["fg.componentId(node) -> which component node is in, for any node: an index into cycles(), 0..len(cycles())-1", "1"],
      ["fg.numEdgesToCrossBeforeCycle(node) -> edges node crosses before being part of a cycle, 0 if it's on one", "1"],
      ["fg.firstCycleNodeHit(node) -> the first cycle node node's walk reaches, itself if it's on a cycle", "1"],
      ["fg.kthNext(node, k) -> where node is after k steps, any k >= 0. O(1) once k reaches the cycle, else O(log V)", "log(V)"],
      ["fg.stepsFromTo(a, b) -> steps to get from a to b, or None (C++: -1) if a never reaches b", "1"],
      ["fg.components() -> per component in componentId order: (cycle, tails), each tail a walk from a node nothing points to, stopping at the first node already listed (included). O(V) total", "1"],
    ],
    variant: {
      label: "1-indexed",
      title: "Nodes are 1..len(edges) instead of 0..len(edges)-1",
      storageKey: "templatePicker.oneIndexed.functionalGraph",
      on: {
        title: "Every node has exactly one outgoing edge, so each component is one cycle with tails feeding in. Directed [a, b] edge list (a -> b), one edge per node, so no node count. Nodes 1..len(edges)",
        file: "functionalGraph.oneIndexed",
      },
    },
    githubUrl: GITHUB,
  },
];
