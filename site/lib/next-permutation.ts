import type { FillIn } from "@/components/TemplatePicker";

// The next permutation templates (templates/next-permutation/): one function each, on the Misc tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/";

export const NEXT_PERMUTATION: FillIn[] = [
  {
    label: "Next permutation O(n)",
    title: "",
    folder: "_next-permutation",
    file: "NextPermutation",
    ops: [["nextPermutation(sequence)", "N"]],
    variant: {
      label: "In place",
      title: "Rearranges your list (C++: vector or string) in place and returns true / false: consecutive calls cost O(1) amortized only when the values are distinct; with repeats it's about O(n / (k + 1)) amortized, k = how many values differ from the most common one (999 zeros and one 1: O(n) every call). Off: returns a new sequence (O(n) per call)",
      storageKey: "templatePicker.inPlace.NextPermutation",
      on: {
        label: "Next permutation O(1) amortized (distinct values)",
        file: "NextPermutation.inplace",
        ops: [["nextPermutation(sequence)", "1 amortized"]],
      },
    },
    githubUrl: GITHUB,
  },
  {
    label: "Previous permutation O(n)",
    title: "",
    folder: "_next-permutation",
    file: "PrevPermutation",
    ops: [["prevPermutation(sequence)", "N"]],
    variant: {
      label: "In place",
      title: "Rearranges your list (C++: vector or string) in place and returns true / false: consecutive calls cost O(1) amortized only when the values are distinct; with repeats it's about O(n / (k + 1)) amortized, k = how many values differ from the most common one (999 zeros and one 1: O(n) every call). Off: returns a new sequence (O(n) per call)",
      storageKey: "templatePicker.inPlace.PrevPermutation",
      on: {
        label: "Previous permutation O(1) amortized (distinct values)",
        file: "PrevPermutation.inplace",
        ops: [["prevPermutation(sequence)", "1 amortized"]],
      },
    },
    githubUrl: GITHUB,
  },
  {
    label: "Next permutation, steps ahead O(n log n)",
    title: "",
    folder: "_next-permutation",
    file: "NextPermutationSteps",
    ops: [["nextPermutation(sequence, steps)", "N*log(N)"]],
    githubUrl: GITHUB,
  },
];

