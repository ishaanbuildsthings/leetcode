import type { FillIn, MiscSection } from "@/components/TemplatePicker";

// Golden references (templates/ultimate-template-tool/golden-references/): plain, readable implementations to learn from, on the Golden
// References tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/golden-references/";

export const GOLDEN_REFERENCES: FillIn[] = [
  {
    label: "Persistent segment tree (pointers)",
    title: "Basic implementation of persistent segment tree over indices with pointers, see CSES range queries and copies for more info",
    folder: "_golden-references",
    file: "PersistentSegTree",
    langs: ["cpp"],
    ops: [
      ["Seg(A)", "N"],
      ["pointUpdate(i, v)", "log(N)"],
      ["rangeSum(l, r)", "log(N)"],
      ["Seg copy = seg", "1"],
    ],
    githubUrl: GITHUB,
  },
];

// Mo's on a tree: a full solution kept as a copy in golden-references/ (not a pointer to the problem's own file, which
// may move or change)
export const GOLDEN_MOS_ON_TREE: FillIn[] = [
  {
    label: "Mo's on tree (Codeforces 852I, Dating)",
    title:
      "Reasonable worked example of order/tin/tout for path queries as subarray queries, also shows mo's add/remove/toggle and how we manually add back in the lca for some of the queries",
    folder: "_golden-references",
    file: "MosOnTree",
    langs: ["cpp"],
    ops: [],
    githubUrl: GITHUB,
  },
];

// Euler tour path queries: a full solution kept as a copy in golden-references/
export const GOLDEN_EULER_PATHS: FillIn[] = [
  {
    label: "Euler tour point add + path sum (Library Checker Vertex Add Path Sum)",
    title:
      "Worked example of path sums between any two nodes with the entry/exit Euler tour: path sum = rootSum(a) + rootSum(b) - rootSum(lca) - rootSum(parent of lca), where rootSum(node) is the range sum up to tin[node]; a node add is two point writes",
    folder: "_golden-references",
    file: "EulerTourPointAddPathSum",
    langs: ["cpp"],
    ops: [],
    githubUrl: GITHUB,
  },
];

// Euler paths and circuits (Hierholzer): a full solution kept as a copy in golden-references/
export const GOLDEN_EULER_CIRCUITS: FillIn[] = [
  {
    label: "Euler circuit on a directed graph (CSES De Bruijn Sequence)",
    title:
      "Worked example of Hierholzer: nodes are the (n-1)-bit strings and each n-bit string is an edge from its prefix to its suffix; dfs takes any unused edge and pushes a node to the front of the path only once all its edges are used",
    folder: "_golden-references",
    file: "DeBruijnSequence",
    langs: ["cpp"],
    ops: [],
    githubUrl: GITHUB,
  },
  {
    label: "Euler circuit on an undirected graph (CSES Mail Delivery)",
    title:
      "Worked example of Hierholzer on an undirected graph: check even degrees, then dfs with edge ids and a used array so each edge's second copy is skipped, then check the path holds all m + 1 nodes",
    folder: "_golden-references",
    file: "MailDelivery",
    langs: ["cpp"],
    ops: [],
    githubUrl: GITHUB,
  },
  {
    label: "Euler path on a directed graph (CSES Teleporters Path)",
    title:
      "Worked example of Hierholzer for a directed Euler path: check start has out = in + 1, end has in = out + 1, all others balanced, then dfs from the start and check the path holds all m + 1 nodes",
    folder: "_golden-references",
    file: "TeleportersPath",
    langs: ["cpp"],
    ops: [],
    githubUrl: GITHUB,
  },
];

// Floyd-Warshall: a full solution kept as a copy in golden-references/
export const GOLDEN_FLOYD_WARSHALL: FillIn[] = [
  {
    label: "Floyd-Warshall (LeetCode 1334, Find the City With the Smallest Number of Neighbors at a Threshold Distance)",
    title:
      "Worked example of all-pairs shortest paths as a recurrence over which cities may be middle stops: the best route using stops 0..k either avoids k, or goes through k once and splits into two routes that only use stops 0..k-1",
    folder: "_golden-references",
    file: "FloydWarshallFindTheCity",
    langs: ["py"],
    ops: [],
    githubUrl: GITHUB,
  },
];

// 0-1 BFS: a full solution kept as a copy in golden-references/
export const GOLDEN_ZERO_ONE_BFS: FillIn[] = [
  {
    label: "0-1 BFS (LeetCode 2290, Minimum Obstacle Removal to Reach Corner)",
    title:
      "Worked example of 0-1 BFS: Dijkstra with a deque instead of a heap, 0-cost moves pushed to the front and 1-cost moves to the back; relax on push, skip stale entries on pop",
    folder: "_golden-references",
    file: "ZeroOneBfsMinimumObstacleRemoval",
    langs: ["py"],
    ops: [],
    githubUrl: GITHUB,
  },
];

// Topological sort: a full solution kept as a copy in golden-references/
export const GOLDEN_TOPO_SORT: FillIn[] = [
  {
    label: "Topological sort, Kahn's algorithm (LeetCode 207, Course Schedule)",
    title:
      "Worked example of Kahn's algorithm: count each course's unfinished prerequisites, start from the courses with none, finishing a course lowers the count of every course that needs it; fewer than n finished means a cycle",
    folder: "_golden-references",
    file: "TopoSortCourseSchedule",
    langs: ["py"],
    ops: [],
    githubUrl: GITHUB,
  },
];

// the Golden References page, section by section
export const GOLDEN_SECTIONS: MiscSection[] = [
  { title: "Persistent Segment Tree", items: GOLDEN_REFERENCES },
  { title: "Mo's on Tree", items: GOLDEN_MOS_ON_TREE },
  { title: "Euler Tour Path Queries", items: GOLDEN_EULER_PATHS },
  { title: "Euler Paths & Circuits", items: GOLDEN_EULER_CIRCUITS },
  { title: "Floyd-Warshall", items: GOLDEN_FLOYD_WARSHALL },
  { title: "0-1 BFS", items: GOLDEN_ZERO_ONE_BFS },
  { title: "Topological Sort", items: GOLDEN_TOPO_SORT },
];
