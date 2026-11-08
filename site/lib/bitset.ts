import type { FillIn } from "@/components/TemplatePicker";

// The bitset templates (templates/bitset/): C++ only, on the Bitset tab. N = number of bits, L = r - l + 1 for a
// range, K = number of set bits.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bitset/";

export const BITSETS: FillIn[] = [
  {
    label: "Fixed-size bitset (std::bitset wrapper)",
    title: "Size fixed at compile time, clearer names over std::bitset at zero cost. Strings read in array order (\"1101\" -> bits 0, 1, 3). No lastSet / prevSetBefore",
    folder: "_bitset",
    file: "FixedBitset",
    langs: ["cpp"],
    ops: [
      ["get / set / unset / toggle / assign(i)", "1"],
      ["setAll / unsetAll / toggleAll", "N/64"],
      ["count / hasAny / isEmpty / isFull", "N/64"],
      ["rangeSet / rangeUnset / rangeToggle / countRange(l, r)", "N/64"],
      ["firstSet / nextSetAfter(i) / firstUnset / nextUnsetAfter(i)", "N/64"],
      ["forEachSet(f)", "N/64+K"],
      ["& | ^ ~ << >>, isSubsetOf, intersects", "N/64"],
      ["orWithShiftedUp(k): b |= b << k", "N/64"],
      ["toString / toMask", "N"],
    ],
    note: "Every method inlines to the plain std::bitset call; single-bit ops add one bounds check",
    githubUrl: GITHUB,
  },
  {
    label: "Dynamic-size bitset (own 64-bit words)",
    title: "Size chosen at runtime, can append / pop / resize. Adds lastSet / prevSetBefore, range ops that only touch their words, and an in-place b |= b << k",
    folder: "_bitset",
    file: "DynamicBitset",
    langs: ["cpp"],
    ops: [
      ["get / set / unset / toggle / assign(i)", "1"],
      ["append(on) / pop()", "1 amortized"],
      ["resize(newN)", "N/64"],
      ["setAll / unsetAll / toggleAll", "N/64"],
      ["count / hasAny / isEmpty / isFull", "N/64"],
      ["rangeSet / rangeUnset / rangeToggle / countRange(l, r)", "L/64+1"],
      ["firstSet / lastSet / nextSetAfter(i) / prevSetBefore(i) / firstUnset / nextUnsetAfter(i)", "N/64"],
      ["forEachSet(f)", "N/64+K"],
      ["&= |= ^= <<= >>=, isSubsetOf, intersects (& | ^ ~ << >> copy)", "N/64"],
      ["orWithShiftedUp(k): b |= b << k, no temporary", "N/64"],
      ["toString", "N"],
      ["toMask", "N/64"],
    ],
    note: "Searches stop at the first word with a hit, so they cost the distance to the answer / 64; N/64 is the worst case",
    githubUrl: GITHUB,
  },
];
