import type { FillIn } from "@/components/TemplatePicker";

// The bisect helpers (templates/ultimate-template-tool/bisects/), on the Misc tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bisects/";

export const BISECTS: FillIn[] = [
  {
    label: "Bisects O(log n) or O(1)",
    title: "First / last index with a value <, <=, >, >= a threshold, for increasing and for decreasing sorted arrays",
    folder: "_bisects",
    file: "bisects",
    ops: [
      ["firstIndexLT(arr, threshold): first index with value < threshold, increasing array; len(arr) if none", "1"],
      ["lastIndexLT(arr, threshold): last index with value < threshold, increasing array; -1 if none", "log(N)"],
      ["firstIndexLTE(arr, threshold): first index with value <= threshold, increasing array; len(arr) if none", "1"],
      ["lastIndexLTE(arr, threshold): last index with value <= threshold, increasing array; -1 if none", "log(N)"],
      ["firstIndexGT(arr, threshold): first index with value > threshold, increasing array; len(arr) if none", "log(N)"],
      ["lastIndexGT(arr, threshold): last index with value > threshold, increasing array; -1 if none", "1"],
      ["firstIndexGTE(arr, threshold): first index with value >= threshold, increasing array; len(arr) if none", "log(N)"],
      ["lastIndexGTE(arr, threshold): last index with value >= threshold, increasing array; -1 if none", "1"],
      ["firstIndexLTDecreasing(arr, threshold): first index with value < threshold, decreasing array; len(arr) if none", "log(N)"],
      ["lastIndexLTDecreasing(arr, threshold): last index with value < threshold, decreasing array; -1 if none", "1"],
      ["firstIndexLTEDecreasing(arr, threshold): first index with value <= threshold, decreasing array; len(arr) if none", "log(N)"],
      ["lastIndexLTEDecreasing(arr, threshold): last index with value <= threshold, decreasing array; -1 if none", "1"],
      ["firstIndexGTDecreasing(arr, threshold): first index with value > threshold, decreasing array; len(arr) if none", "1"],
      ["lastIndexGTDecreasing(arr, threshold): last index with value > threshold, decreasing array; -1 if none", "log(N)"],
      ["firstIndexGTEDecreasing(arr, threshold): first index with value >= threshold, decreasing array; len(arr) if none", "1"],
      ["lastIndexGTEDecreasing(arr, threshold): last index with value >= threshold, decreasing array; -1 if none", "log(N)"],
    ],
    githubUrl: GITHUB,
  },
];
