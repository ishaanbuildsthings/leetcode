import type { FillIn } from "@/components/TemplatePicker";

// The graph templates (templates/ultimate-template-tool/graphs/): one function each, on the Graphs tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/";

export const EULER: FillIn[] = [
  {
    label: "Euler circuit, directed O(N + M)",
    title: "A walk over an [a, b] edge list (a -> b) using every edge once and ending where it started, or None / {} if there isn't one. Optional start; labels 0..n-1 or 1..n",
    folder: "_graphs",
    file: "eulerCircuitDirected",
    ops: [["eulerCircuitDirected(edges, start?) -> [node, ...] (len(edges) + 1, first == last), or None", "N+M"]],
    githubUrl: GITHUB,
  },
  {
    label: "Euler path, directed O(N + M)",
    title: "A walk over an [a, b] edge list (a -> b) using every edge once, or None / {} if there isn't one. Optional start and end, picked from the degrees if left out; a circuit counts. Labels 0..n-1 or 1..n",
    folder: "_graphs",
    file: "eulerPathDirected",
    ops: [["eulerPathDirected(edges, start?, end?) -> [node, ...] (len(edges) + 1), or None", "N+M"]],
    githubUrl: GITHUB,
  },
  {
    label: "Euler circuit, undirected O(N + M)",
    title: "A walk over an undirected [a, b] edge list using every edge once and ending where it started, or None / {} if there isn't one. Optional start; labels 0..n-1 or 1..n",
    folder: "_graphs",
    file: "eulerCircuitUndirected",
    ops: [["eulerCircuitUndirected(edges, start?) -> [node, ...] (len(edges) + 1, first == last), or None", "N+M"]],
    githubUrl: GITHUB,
  },
  {
    label: "Euler path, undirected O(N + M)",
    title: "A walk over an undirected [a, b] edge list using every edge once, or None / {} if there isn't one. Optional start and end, picked from the odd-degree nodes if left out; a circuit counts. Labels 0..n-1 or 1..n",
    folder: "_graphs",
    file: "eulerPathUndirected",
    ops: [["eulerPathUndirected(edges, start?, end?) -> [node, ...] (len(edges) + 1), or None", "N+M"]],
    githubUrl: GITHUB,
  },
];
