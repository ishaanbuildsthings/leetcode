import type { FillIn } from "@/components/TemplatePicker";

// The bisect helpers (templates/ultimate-template-tool/bisects/), on the Misc tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bisects/";

export const BISECTS: FillIn[] = [
  {
    label: "Bisects O(log n)",
    title: "First / last index with a value <, <=, >, >= a threshold, for increasing and for decreasing sorted arrays",
    folder: "_bisects",
    file: "bisects",
    ops: [
      ["firstIndexLT / LTE / GT / GTE(arr, threshold), increasing; len(arr) if none", "log(N)"],
      ["lastIndexLT / LTE / GT / GTE(arr, threshold), increasing; -1 if none", "log(N)"],
      ["firstIndex...Decreasing(arr, threshold), decreasing; len(arr) if none", "log(N)"],
      ["lastIndex...Decreasing(arr, threshold), decreasing; -1 if none", "log(N)"],
    ],
    githubUrl: GITHUB,
  },
];
