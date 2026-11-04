import type { FillIn } from "@/components/TemplatePicker";

// The bubble sort templates (templates/bubble-sort/): one function each, on the Misc tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bubble-sort/";

export const BUBBLE_SORT: FillIn[] = [
  {
    label: "Min swaps to sort O(n log n)",
    title: "",
    folder: "_bubble-sort",
    file: "MinSwapsToSort",
    ops: [["minAdjacentSwapsToSort(arr)", "N*log(N)"]],
    githubUrl: GITHUB,
  },
  {
    label: "Min swaps to reach a target state O(n log n)",
    title: "",
    folder: "_bubble-sort",
    file: "MinSwapsToTarget",
    ops: [["minAdjacentSwapsToTarget(arr, target)", "N*log(N)"]],
    githubUrl: GITHUB,
  },
  {
    label: "Min swaps to a palindrome O(n log n)",
    title: "",
    folder: "_bubble-sort",
    file: "MinSwapsToPalindrome",
    ops: [["minAdjacentSwapsToPalindrome(s)", "N*log(N)"]],
    githubUrl: GITHUB,
  },
];
