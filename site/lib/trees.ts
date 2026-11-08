import type { FillIn } from "@/components/TemplatePicker";

// The tree templates (templates/ultimate-template-tool/trees/): one function each, on the Trees tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/trees/";

export const TREES: FillIn[] = [
  {
    label: "Edge list to rooted tree O(n)",
    title: "Roots an [a, b] edge list at any node you pass and returns children lists, sized to the largest label (0..n-1 or 1..n)",
    folder: "_trees",
    file: "edgeListToTree",
    ops: [["edgeListToTree(edgeList, root) -> children", "N"]],
    githubUrl: GITHUB,
  },
  {
    label: "Weighted edge list to rooted tree O(n)",
    title: "Edges come as [a, b, w]; returns children[node] = [(child, weight), ...]. Root is 0, or 1 with zeroIndexed off",
    folder: "_trees",
    file: "weightedEdgeListToTree",
    ops: [["edgeListToTree(edgeList, zeroIndexed=True) -> children", "N"]],
    githubUrl: GITHUB,
  },
  {
    label: "Find centroids O(n)",
    title: "The 1 or 2 centroids of an unrooted [a, b] edge list, sorted. Removing one leaves every piece at most n/2. Labels 0..n-1 or 1..n",
    folder: "_trees",
    file: "findCentroids",
    ops: [["findCentroids(edgeList) -> [centroid, ...]", "N"]],
    githubUrl: GITHUB,
  },
  {
    label: "All subtree hashes O(n log n)",
    title: "A random 64-bit hash of every node's subtree: two nodes match exactly when their subtrees are the same shape (rooted, children unordered)",
    folder: "_trees",
    file: "getAllSubtreeHashes",
    ops: [["subtreeHashes(children, root) -> [hash, ...]", "N*log(N)"]],
    githubUrl: GITHUB,
  },
];
