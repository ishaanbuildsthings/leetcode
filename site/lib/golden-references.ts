import type { FillIn } from "@/components/TemplatePicker";

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
