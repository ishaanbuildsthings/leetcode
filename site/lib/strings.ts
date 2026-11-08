import type { FillIn } from "@/components/TemplatePicker";

// The string templates (templates/ultimate-template-tool/strings/): one function per file and per card, on the
// Strings tab. The card's caption is what the function returns; the drawer has the Python / C++ code.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/";

const card = (file: string, call: string, returns: string, cost: string): FillIn => ({
  label: call,
  title: `-> ${returns}`,
  folder: "_strings",
  file,
  ops: [[`${call} -> ${returns}`, cost]],
  githubUrl: GITHUB,
});

export const ROTATIONS: FillIn[] = [
  card("minRotation", "minRotation(arrOrString)", "the lexicographically smallest rotation (same type as the input)", "N"),
  card("maxRotation", "maxRotation(arrOrString)", "the lexicographically largest rotation (same type as the input)", "N"),
  card("minRotationIndices", "minRotationIndices(arrOrString)", "every start index giving the smallest rotation (ascending)", "N"),
  card("maxRotationIndices", "maxRotationIndices(arrOrString)", "every start index giving the largest rotation (ascending)", "N"),
];

export const PATTERN_MATCHING: FillIn[] = [
  card("zFunction", "zFunction(arrOrString)", "z list: z[i] = longest common prefix of the entire sequence against the suffix starting at i (z[0] = n)", "N"),
  card("longestPrefixMatches", "longestPrefixMatches(text, pattern)", "list of size len(text): arr[i] = length of match between pattern and text[i...]", "N+M"),
  card("findMatches", "findMatches(text, pattern)", "list of indices i where text[i...] matches pattern (Z-function)", "N+M"),
  card("findMatchesKmp", "findMatchesKmp(text, pattern)", "list of indices i where text[i...] matches pattern (KMP)", "N+M"),
  card("prefixFunction", "prefixFunction(arrOrString)", "pi list: pi[i] = longest proper prefix that is also a suffix of arrOrString[0..i]", "N"),
  card("shortestPeriod", "shortestPeriod(arrOrString)", "length of the shortest prefix that repeats to form the whole sequence (n if none)", "N"),
];
