import type { FillIn } from "@/components/TemplatePicker";

// Longest increasing / decreasing subsequence (templates/ultimate-template-tool/lis/), on the Misc tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/lis/";

export const LIS: FillIn[] = [
  {
    label: "Longest increasing subsequence O(n log n)",
    title: "Strictly / non-strictly increasing and decreasing: each returns (length, one longest subsequence)",
    folder: "_lis",
    file: "lis",
    ops: [
      ["strictlyIncreasingLis(nums) -> (length, seq): each value > the one before", "N*log(N)"],
      ["monoIncreasingLis(nums) -> (length, seq): each value >= the one before", "N*log(N)"],
      ["strictlyDecreasingLis(nums) -> (length, seq): each value < the one before", "N*log(N)"],
      ["monoDecreasingLis(nums) -> (length, seq): each value <= the one before", "N*log(N)"],
    ],
    githubUrl: GITHUB,
  },
];
