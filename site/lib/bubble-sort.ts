import type { FillIn } from "@/components/TemplatePicker";

// The bubble sort templates (templates/bubble-sort/): one function each, on the Misc tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bubble-sort/";

export const BUBBLE_SORT: FillIn[] = [
  {
    label: "Min swaps to sort",
    title: "Min adjacent swaps to sort an array (the bubble sort swap count): its number of inversions",
    folder: "_bubble-sort",
    file: "MinSwapsToSort",
    ops: [["minAdjacentSwapsToSort(arr)", "N*log(N)"]],
    githubUrl: GITHUB,
  },
  {
    label: "Min swaps to a target",
    title: "Min adjacent swaps to turn an array into a given rearrangement of it (-1 if it isn't one)",
    folder: "_bubble-sort",
    file: "MinSwapsToTarget",
    ops: [["minAdjacentSwapsToTarget(arr, target)", "N*log(N)"]],
    githubUrl: GITHUB,
  },
  {
    label: "Min swaps to a palindrome",
    title: "Min adjacent swaps to turn a string (or array) into a palindrome (-1 if none can be)",
    folder: "_bubble-sort",
    file: "MinSwapsToPalindrome",
    ops: [["minAdjacentSwapsToPalindrome(s)", "N*log(N)"]],
    githubUrl: GITHUB,
  },
];
