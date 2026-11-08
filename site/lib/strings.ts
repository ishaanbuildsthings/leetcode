import type { FillIn } from "@/components/TemplatePicker";

// The string templates (templates/ultimate-template-tool/strings/): one function per file and per card, on the
// Strings tab. The card's caption is what the function returns; the drawer has the Python / C++ code.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/";

const bigO = (cost: string) => {
  const kind = cost.match(/ (amortized expected|amortized|expected)$/)?.[1];
  const body = cost.replace(/ (amortized expected|amortized|expected)$/, "");
  return `O(${body.replace(/\+/g, " + ").replace(/\*/g, " ").replace(/sqrt\((\w)\)/g, "√$1").replace(/N/g, "n").replace(/M/g, "m")})${kind ? ` ${kind}` : ""}`;
};

const card = (file: string, call: string, returns: string, cost: string): FillIn => ({
  label: `${call} ${bigO(cost)}`,
  title: `-> ${returns}`,
  folder: "_strings",
  file,
  ops: [[`${call} -> ${returns}`, cost]],
  githubUrl: GITHUB,
});

export const ROTATIONS: FillIn[] = [
  card("minRotation", "minRotation(arrOrString)", "the lexicographically smallest rotation (same type as the input) (Duval)", "N"),
  card("maxRotation", "maxRotation(arrOrString)", "the lexicographically largest rotation (same type as the input) (Duval)", "N"),
  card("minRotationIndices", "minRotationIndices(arrOrString)", "every start index giving the smallest rotation (ascending) (Duval)", "N"),
  card("maxRotationIndices", "maxRotationIndices(arrOrString)", "every start index giving the largest rotation (ascending) (Duval)", "N"),
];

export const PATTERN_MATCHING: FillIn[] = [
  card("longestPrefixMatches", "longestPrefixMatches(text, pattern)", "list of size len(text): arr[i] = length of match between pattern and text[i...] (Z-function)", "N+M"),
  card("multiPatternLongestPrefixMatches", "multiPatternLongestPrefixMatches(text, patterns)", "res of len(text): res[idx] = longest L where text[idx : idx + L] is a prefix of some pattern (suffix automaton)", "N+M expected"),
  card("multiPatternLongestPrefixInText", "multiPatternLongestPrefixInText(text, patterns)", "res of len(patterns): res[i] = longest L where patterns[i][:L] appears somewhere in text (suffix automaton)", "N+M expected"),
  card("findMatches", "findMatches(text, pattern)", "list of indices i where text[i...] matches pattern (Z-function)", "N+M"),
  {
    ...card("multiPatternMatches", "multiPatternMatches(text, patterns)", "res of len(patterns): res[i] = list of every idx where text[idx...] matches patterns[i] (Aho-Corasick)", "N+M+N*sqrt(M) expected"),
    note: "Worst case: All patterns of the same length X contribute at most N answers in the result, and with at most √|M| unique pattern sizes we get O(N√|M|) answers.",
  },
  card("multiPatternCounts", "multiPatternCounts(text, patterns)", "res of len(patterns): res[i] = number of times patterns[i] occurs (Aho-Corasick)", "N+M expected"),
];

export const SUBSTRINGS: FillIn[] = [
  card("longestCommonSubstring", "longestCommonSubstring(a, b)", "(length, startInA, startInB) of the longest contiguous run in both (suffix automaton)", "N+M expected"),
  card("countDistinctSubstrings", "countDistinctSubstrings(arrOrString)", "number of distinct non-empty contiguous substrings (suffix automaton)", "N expected"),
  card("distinctSubstringsByLength", "distinctSubstringsByLength(arrOrString)", "list of size n + 1: res[L] = number of distinct contiguous substrings of length L (suffix automaton)", "N expected"),
];

export const Z_FUNCTION: FillIn[] = [
  card("zFunction", "zFunction(arrOrString)", "z list: z[i] = longest common prefix of the entire sequence against the suffix starting at i (z[0] = n)", "N"),
];

export const KMP: FillIn[] = [
  card("properBorders", "properBorders(arrOrString)", "properBorders[i] = longest proper prefix of arrOrString[0..i] that is also a suffix of it", "N"),
];

export const STRINGS_MISC: FillIn[] = [
  {
    ...card("shortestPeriod", "shortestPeriod(arrOrString)", "length of the shortest prefix that repeats a whole number of times to form the sequence: must perfectly divide (n if none) (KMP)", "N"),
    variant: {
      label: "Overflow allowed",
      title: "The last copy may be cut off, so the period doesn't have to divide the length: shortestPeriod(\"abcab\") is 3 (\"abc\" + \"ab\") instead of 5",
      storageKey: "templatePicker.overflow.shortestPeriod",
      on: {
        title: "-> length of the shortest prefix that repeats to form the sequence, last copy may be cut off: overflow allowed (n if none) (KMP)",
        file: "shortestPeriod.overflow",
      },
    },
  },
];

export const PALINDROMES: FillIn[] = [
  {
    ...card(
      "longestPalAroundEachCenter",
      "longestPalAroundEachCenter(arrOrString)",
      "(atI, atIPlusOne): two lists of (l, r), the longest palindrome centered on i / between i and i+1 (Manacher)",
      "N",
    ),
    label: "longest palindromes around i and i+1 O(n)",
    title: "returns two lists of tuples (l, r) for the longest palindrome centered around i, and i+1",
    note: "atI[i] = (l, r) of the longest palindrome centered on index i. atIPlusOne[i] = (l, r) of the longest palindrome centered between i and i+1, or (i+1, i) if there's none.",
  },
];
