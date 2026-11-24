import type { FillIn } from "@/components/TemplatePicker";

// The monotonic stack helpers (templates/ultimate-template-tool/stacks/), on the Misc tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/stacks/";

export const STACKS: FillIn[] = [
  {
    label: "Monotonic stack O(n)",
    title: "For every index, the nearest index to its left or right with a value <, <=, > or >= it",
    folder: "_stacks",
    file: "monotonicStack",
    ops: [
      ["Nearest on the left (-1 if none)", ""],
      ["rightmostOnLeftLtNum(arr): nearest index to the left with value < arr[i]", "N"],
      ["rightmostOnLeftLteNum(arr): nearest index to the left with value <= arr[i]", "N"],
      ["rightmostOnLeftGtNum(arr): nearest index to the left with value > arr[i]", "N"],
      ["rightmostOnLeftGteNum(arr): nearest index to the left with value >= arr[i]", "N"],
      ["Nearest on the right (len(arr) if none)", ""],
      ["leftmostOnRightLtNum(arr): nearest index to the right with value < arr[i]", "N"],
      ["leftmostOnRightLteNum(arr): nearest index to the right with value <= arr[i]", "N"],
      ["leftmostOnRightGtNum(arr): nearest index to the right with value > arr[i]", "N"],
      ["leftmostOnRightGteNum(arr): nearest index to the right with value >= arr[i]", "N"],
    ],
    githubUrl: GITHUB,
  },
];
