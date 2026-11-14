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
    label: "Euler tour path queries (CSES Path Queries)",
    title:
      "Worked example of the entry/exit Euler tour for path sums: +value at tin, -value at tout, so a range sum from the root's entry to a node's entry is the sum on the path root..node; a node update is two point sets",
    folder: "_golden-references",
    file: "EulerTourPathQueries",
    langs: ["cpp"],
    ops: [],
    githubUrl: GITHUB,
  },
];

// the Golden References page, section by section
export const GOLDEN_SECTIONS: MiscSection[] = [
  { title: "Persistent Segment Tree", items: GOLDEN_REFERENCES },
  { title: "Mo's on Tree", items: GOLDEN_MOS_ON_TREE },
  { title: "Euler Tour Path Queries", items: GOLDEN_EULER_PATHS },
];
