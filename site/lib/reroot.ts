import type { FillIn } from "@/components/TemplatePicker";

// The reroot DP templates (templates/reroot/): one function each, on the Trees tab. The weighted box swaps in the
// version that takes [a, b, w] edges.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/reroot/";

export const REROOT: FillIn[] = [
  {
    label: "Farthest node from every node O(n)",
    title: "For every node, the farthest other node and its distance (ties go to the smallest id). Labels 0..n-1 or 1..n, detected automatically",
    folder: "_reroot",
    file: "FarthestNode",
    ops: [["farthestNodes(edges) -> [(dist, node), ...]", "N"]],
    variant: {
      label: "Weighted",
      title: "Edges come as [a, b, w] and distance is total edge weight (any int weights). Off: edges are [a, b] and distance is edge count",
      storageKey: "templatePicker.weighted.FarthestNode",
      on: {
        file: "FarthestNode.weighted",
      },
    },
    githubUrl: GITHUB,
  },
  {
    label: "Sum of distances to all nodes O(n)",
    title: "For every node, the sum of its distances to all other nodes. Labels 0..n-1 or 1..n, detected automatically",
    folder: "_reroot",
    file: "SumOfDistances",
    ops: [["sumOfDistances(edges) -> [distSum, ...]", "N"]],
    variant: {
      label: "Weighted",
      title: "Edges come as [a, b, w] and distance is total edge weight (any int weights). Off: edges are [a, b] and distance is edge count",
      storageKey: "templatePicker.weighted.SumOfDistances",
      on: {
        file: "SumOfDistances.weighted",
      },
    },
    githubUrl: GITHUB,
  },
];
