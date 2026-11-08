import type { FillIn } from "@/components/TemplatePicker";

// The one-off string templates (templates/strings/): one card each, on the Strings tab.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/strings/";

export const STRINGS: FillIn[] = [
  {
    label: "Min / max lexicographic rotation (Duval) O(n)",
    title: "Smallest or largest rotation of a string or array, or every start index that gives it",
    folder: "_strings",
    file: "minAndMaxLexRotationDuvals",
    ops: [
      ["minRotation(stringOrArray)", "N"],
      ["maxRotation(stringOrArray)", "N"],
      ["minRotationIndices(stringOrArray)", "N"],
      ["maxRotationIndices(stringOrArray)", "N"],
    ],
    githubUrl: GITHUB + "min-max-lex-duvals-rotations/",
  },
  {
    label: "Z-function O(n)",
    title: "z[i] = longest common prefix of the whole sequence and the suffix starting at i; plus pattern matching",
    folder: "_strings",
    file: "zFunction",
    ops: [
      ["zFunction(arrOrString)", "N"],
      ["longestPrefixMatches(pattern, text)", "N + M"],
      ["findMatches(pattern, text)", "N + M"],
    ],
    githubUrl: GITHUB + "z-function/",
  },
  {
    label: "Prefix function (pi / KMP) O(n)",
    title: "pi[i] = longest proper prefix that is also a suffix ending at i; plus KMP matching and shortest period",
    folder: "_strings",
    file: "prefixFunction",
    ops: [
      ["prefixFunction(arrOrString)", "N"],
      ["findMatchesKmp(pattern, text)", "N + M"],
      ["shortestPeriod(arrOrString)", "N"],
    ],
    githubUrl: GITHUB + "prefix-function/",
  },
];
