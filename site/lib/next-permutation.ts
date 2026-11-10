import type { FillIn } from "@/components/TemplatePicker";

// The next permutation templates (templates/ultimate-template-tool/next-permutation/): one function each, on the Misc tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/next-permutation/";

export const NEXT_PERMUTATION: FillIn[] = [
  {
    label: "Next permutation O(n)",
    title: "",
    folder: "_next-permutation",
    file: "NextPermutation",
    ops: [["nextPermutation(arr)", "N"]],
    variant: {
      label: "In place: O(1) amortized if values are distinct enough",
      title: "Moves your list (C++: vector) to the next permutation in place, with looping behavior around to the lexicographical smallest permutation if we step past the lexicographical max: consecutive calls cost O(1) amortized only when the values are distinct; with repeats it's about O(n / (k + 1)) amortized, k = how many values differ from the most common one (999 zeros and one 1: O(n) every call). Off: returns a new vector / string (Python: list / string) with the next larger permutation, with looping behavior around to the lexicographical smallest permutation if we step past the lexicographical max (O(n) per call)",
      storageKey: "templatePicker.inPlace.NextPermutation",
      on: {
        file: "NextPermutation.inplace",
        ops: [["nextPermutation(arr)", "1 amortized"]],
      },
    },
    githubUrl: GITHUB,
  },
  {
    label: "Previous permutation O(n)",
    title: "",
    folder: "_next-permutation",
    file: "PrevPermutation",
    ops: [["prevPermutation(arr)", "N"]],
    variant: {
      label: "In place: O(1) amortized if values are distinct enough",
      title: "Moves your list (C++: vector) to the previous permutation in place, with looping behavior around to the lexicographical largest permutation if we step past the lexicographical min: consecutive calls cost O(1) amortized only when the values are distinct; with repeats it's about O(n / (k + 1)) amortized, k = how many values differ from the most common one (999 zeros and one 1: O(n) every call). Off: returns a new vector / string (Python: list / string) with the previous permutation, with looping behavior around to the lexicographical largest permutation if we step past the lexicographical min (O(n) per call)",
      storageKey: "templatePicker.inPlace.PrevPermutation",
      on: {
        file: "PrevPermutation.inplace",
        ops: [["prevPermutation(arr)", "1 amortized"]],
      },
    },
    githubUrl: GITHUB,
  },
  {
    label: "Next permutation, steps ahead O(n log n)",
    title: "Needs steps >= 0. O(n log n) while steps fits in 64 bits; a far larger steps in Python also pays for big integers",
    folder: "_next-permutation",
    file: "NextPermutationSteps",
    ops: [["nextPermutation(arr, steps)", "N*log(N)"]],
    githubUrl: GITHUB,
  },
];

