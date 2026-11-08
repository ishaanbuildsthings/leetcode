import type { MemoryBreakdown, TemplateLang, TierKind, Usage } from "./template-picker";
import { isBuiltFromPoints } from "./template-picker";

export * from "./template-picker";

export type OpId =
  | "pointGet"
  | "pointAssign"
  | "pointAdd"
  | "pointChmax"
  | "pointChmin"
  | "rangeAdd"
  | "rangeAssign"
  | "rangeReplace"
  | "rangeChmax"
  | "rangeChmin"
  | "rangeAddMod"
  | "rangeAssignMod"
  | "rangeMultMod"
  | "rangeAffineMod"
  | "rangeAddArithSeq"
  | "rangeAddArithSeqMod"
  | "rangeMod"
  | "rangeFloorDiv"
  | "rangeFloorSqrt"
  | "rangeAndApply"
  | "rangeOrApply"
  | "rangeXorApply"
  | "stridedSum"
  | "stridedMin"
  | "stridedMax"
  | "stridedGcd"
  | "stridedXorQuery"
  | "stridedAndQuery"
  | "stridedOrQuery"
  | "stridedAdd"
  | "rangeSum"
  | "rangeSumMod"
  | "rangeMin"
  | "rangeMax"
  | "rangeGcd"
  | "maxSubarraySum"
  | "minSubarraySum"
  | "maxPrefixSum"
  | "maxSuffixSum"
  | "minPrefixSum"
  | "minSuffixSum"
  | "rangeAndQuery"
  | "rangeOrQuery"
  | "rangeXorQuery"
  | "countOccurrences"
  | "leftmostIndexOf"
  | "rightmostIndexOf"
  | "leftmostIndexOfInRange"
  | "rightmostIndexOfInRange"
  | "countDistinct"
  | "allDistinct"
  | "rangeMode"
  | "countInValRange"
  | "sumInValRange"
  | "kthSmallest"
  | "countLtX"
  | "countLteX"
  | "countGtX"
  | "countGteX"
  | "smallestGteX"
  | "smallestGtX"
  | "largestLteX"
  | "largestLtX"
  | "sumLtX"
  | "sumLteX"
  | "sumGtX"
  | "sumGteX"
  | "sumSmallestK"
  | "sumLargestK"
  | "sumKthSmallestRange"
  | "sumKthLargestRange"
  | "sumAbsDiffToX"
  | "xorLtX"
  | "xorLteX"
  | "xorGtX"
  | "xorGteX"
  | "xorInValRange"
  | "maxXorAgainstX"
  | "minXorAgainstX"
  | "kthXor"
  | "countXorLtK"
  | "countXorLteK"
  | "countXorGtK"
  | "countXorGteK"
  | "largestXorLtK"
  | "largestXorLteK"
  | "smallestXorGtK"
  | "smallestXorGteK"
  | "mexXor"
  | "sumXor"
  | "maxXorWithVLtM"
  | "maxXorWithVLteM"
  | "maxXorWithVGtM"
  | "maxXorWithVGteM"
  | "minXorWithVLtM"
  | "minXorWithVLteM"
  | "minXorWithVGtM"
  | "minXorWithVGteM"
  | "maxXorWithVInValRange"
  | "minXorWithVInValRange"
  | "orLtX"
  | "orLteX"
  | "orGtX"
  | "orGteX"
  | "orInValRange"
  | "andLtX"
  | "andLteX"
  | "andGtX"
  | "andGteX"
  | "andInValRange"
  | "rangeMex"
  | "maxAltSubseqSum"
  | "longestEqualRun"
  | "rangeLIS"
  | "isRBS"
  | "rangeFlip"
  | "rangeLNDS"
  | "rangeLDS"
  | "rangeLNIS"
  | "costMonoIncreasing"
  | "costMonoDecreasing"
  | "costStrictIncreasing"
  | "costStrictDecreasing"
  | "doAllElementsAppearEvenFrequency"
  | "leftmostGteX"
  | "leftmostGtX"
  | "rightmostGteX"
  | "rightmostGtX"
  | "leftmostLteX"
  | "leftmostLtX"
  | "rightmostLteX"
  | "rightmostLtX"
  | "leftmostPrefixSumGteX"
  | "leftmostPrefixSumGtX"
  | "rightmostSuffixSumGteX"
  | "rightmostSuffixSumGtX"
  | "leftmostPrefixSumLteX"
  | "leftmostPrefixSumLtX"
  | "rightmostSuffixSumLteX"
  | "rightmostSuffixSumLtX"
  | "kthGteX"
  | "kthGtX"
  | "kthLteX"
  | "kthLtX"
  | "append"
  | "appendLeft"
  | "pop"
  | "popLeft"
  | "hashAll"
  | "sumAll"
  | "minAll"
  | "maxAll"
  | "gcdAll"
  | "xorAll"
  | "andAll"
  | "orAll"
  | "longestPalCenteredAtI"
  | "longestPalCenteredAtIPlusOne"
  | "insertAt"
  | "rangeReverse"
  | "rangeRotateLeft"
  | "rangeRotateRight"
  | "cut"
  | "find"
  | "paste"
  | "split"
  | "trisect"
  | "merge"
  | "insertCopiesAt"
  | "getAll"
  | "size"
  | "rangeHash"
  | "rangeHashReversed"
  | "isPalindrome"
  | "rangesEqual"
  | "rangeTwinSpin"
  | "rangeSortAsc"
  | "rangeSortDesc"
  | "copy";

export interface Op {
  id: OpId;
  signature: string;
  description: string;
}

export interface OpTier {
  kind: TierKind;
  // Overrides the badge text; the kind still sets the color.
  label?: string;
  ops: Op[];
}

export interface OpGroup {
  id: string;
  title: string;
  collapsible?: boolean;
  tiers: OpTier[];
}

export const OP_GROUPS: OpGroup[] = [
  {
    id: "point",
    title: "Point operations",
    tiers: [
      {
        kind: "topic",
        ops: [
          { id: "pointGet", signature: "pointGet(i)", description: "Read a[i]" },
          { id: "pointAssign", signature: "pointAssign(i, v)", description: "a[i] = v" },
          { id: "pointAdd", signature: "pointAdd(i, v)", description: "a[i] += v" },
          { id: "pointChmax", signature: "pointChmax(i, v)", description: "a[i] = max(a[i], v)" },
          { id: "pointChmin", signature: "pointChmin(i, v)", description: "a[i] = min(a[i], v)" },
        ],
      },
    ],
  },
  {
    id: "range-updates",
    title: "Range updates",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "rangeAdd", signature: "rangeAdd(l, r, v)", description: "a[i] += v" },
          { id: "rangeAssign", signature: "rangeAssign(l, r, v)", description: "a[i] = v" },
          { id: "rangeChmax", signature: "rangeChmax(l, r, v)", description: "a[i] = max(a[i], v)" },
          { id: "rangeChmin", signature: "rangeChmin(l, r, v)", description: "a[i] = min(a[i], v)" },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "rangeReplace", signature: "rangeReplace(l, r, x, y)", description: "Every a[i] = x in l..r becomes y (mass change)" },
          { id: "rangeSortAsc", signature: "rangeSortAsc(l, r)", description: "Sort l..r ascending in place" },
          { id: "rangeSortDesc", signature: "rangeSortDesc(l, r)", description: "Sort l..r descending in place" },
          { id: "rangeAddArithSeq", signature: "rangeAddArithSeq(l, r, start, step)", description: "a[l] += start, a[l+1] += start+step, …" },
          { id: "rangeMod", signature: "rangeMod(l, r, mod)", description: "a[i] %= mod" },
          { id: "rangeFloorDiv", signature: "rangeFloorDiv(l, r, divisor)", description: "a[i] = ⌊a[i] / divisor⌋" },
          { id: "rangeFloorSqrt", signature: "rangeFloorSqrt(l, r)", description: "a[i] = ⌊√a[i]⌋" },
          { id: "rangeAddMod", signature: "rangeAddMod(l, r, v)", description: "a[i] = (a[i] + v) % MOD" },
          { id: "rangeAssignMod", signature: "rangeAssignMod(l, r, v)", description: "a[i] = v % MOD" },
          { id: "rangeMultMod", signature: "rangeMultMod(l, r, m)", description: "a[i] = (a[i] · m) % MOD" },
          { id: "rangeAffineMod", signature: "rangeAffineMod(l, r, mult, add)", description: "a[i] = ((a[i] · mult) + add) % MOD" },
          { id: "rangeAddArithSeqMod", signature: "rangeAddArithSeqMod(l, r, start, step)", description: "a[l] += start, a[l+1] += start+step, …  (% MOD)" },
        ],
      },
    ],
  },
  {
    id: "search",
    title: "Search (tree walks)",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "leftmostIndexOf", signature: "leftmostIndexOf(x)", description: "First i with a[i] = x" },
          { id: "rightmostIndexOf", signature: "rightmostIndexOf(x)", description: "Last i with a[i] = x" },
          { id: "leftmostIndexOfInRange", signature: "leftmostIndexOfInRange(l, r, x)", description: "First i in [l, r] with a[i] = x" },
          { id: "rightmostIndexOfInRange", signature: "rightmostIndexOfInRange(l, r, x)", description: "Last i in [l, r] with a[i] = x" },
          { id: "leftmostGteX", signature: "leftmostGteX(l, r, x)", description: "First i in [l, r] with a[i] ≥ x" },
          { id: "leftmostGtX", signature: "leftmostGtX(l, r, x)", description: "First i in [l, r] with a[i] > x" },
          { id: "rightmostGteX", signature: "rightmostGteX(l, r, x)", description: "Last i in [l, r] with a[i] ≥ x" },
          { id: "rightmostGtX", signature: "rightmostGtX(l, r, x)", description: "Last i in [l, r] with a[i] > x" },
          { id: "leftmostLteX", signature: "leftmostLteX(l, r, x)", description: "First i in [l, r] with a[i] ≤ x" },
          { id: "leftmostLtX", signature: "leftmostLtX(l, r, x)", description: "First i in [l, r] with a[i] < x" },
          { id: "rightmostLteX", signature: "rightmostLteX(l, r, x)", description: "Last i in [l, r] with a[i] ≤ x" },
          { id: "rightmostLtX", signature: "rightmostLtX(l, r, x)", description: "Last i in [l, r] with a[i] < x" },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "kthGteX", signature: "kthGteX(l, r, k, x)", description: "Index of the k-th i in [l, r] with a[i] ≥ x" },
          { id: "kthGtX", signature: "kthGtX(l, r, k, x)", description: "Index of the k-th i in [l, r] with a[i] > x" },
          { id: "kthLteX", signature: "kthLteX(l, r, k, x)", description: "Index of the k-th i in [l, r] with a[i] ≤ x" },
          { id: "kthLtX", signature: "kthLtX(l, r, k, x)", description: "Index of the k-th i in [l, r] with a[i] < x" },
        ],
      },
    ],
  },
  {
    id: "range-queries",
    title: "Range queries",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "rangeSum", signature: "rangeSum(l, r)", description: "a[l] + … + a[r]" },
          { id: "rangeMin", signature: "rangeMin(l, r)", description: "min of l..r" },
          { id: "rangeMax", signature: "rangeMax(l, r)", description: "max of l..r" },
          { id: "rangeGcd", signature: "rangeGcd(l, r)", description: "gcd of l..r" },
          { id: "maxSubarraySum", signature: "maxSubarraySum(l, r)", description: "Max sum of non-empty subarray within l..r" },
          { id: "minSubarraySum", signature: "minSubarraySum(l, r)", description: "Min sum of non-empty subarray within l..r" },
          { id: "getAll", signature: "getAll()", description: "Get the whole array (for final answer)" },
        ],
      },
      {
        kind: "topic",
        label: "Whole array",
        ops: [
          { id: "sumAll", signature: "sumAll()", description: "a[0] + … + a[n-1]" },
          { id: "minAll", signature: "minAll()", description: "min of the whole array" },
          { id: "maxAll", signature: "maxAll()", description: "max of the whole array" },
          { id: "gcdAll", signature: "gcdAll()", description: "gcd of the whole array" },
          { id: "xorAll", signature: "xorAll()", description: "xor of the whole array" },
          { id: "andAll", signature: "andAll()", description: "AND of the whole array" },
          { id: "orAll", signature: "orAll()", description: "OR of the whole array" },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "countOccurrences", signature: "countOccurrences(l, r, x)", description: "# of i in [l, r] with a[i] = x" },
          { id: "countDistinct", signature: "countDistinct(l, r)", description: "# of distinct values in l..r" },
          { id: "allDistinct", signature: "allDistinct(l, r)", description: "Are all values in l..r distinct?" },
          { id: "rangeMode", signature: "rangeMode(l, r)", description: "(mode, frequency) of l..r" },
          { id: "costMonoIncreasing", signature: "costMonoIncreasing(l, r)", description: "Min +1 ops to make l..r non-decreasing" },
          { id: "costMonoDecreasing", signature: "costMonoDecreasing(l, r)", description: "Min +1 ops to make l..r non-increasing" },
          { id: "costStrictIncreasing", signature: "costStrictIncreasing(l, r)", description: "Min +1 ops to make l..r strictly increasing" },
          { id: "costStrictDecreasing", signature: "costStrictDecreasing(l, r)", description: "Min +1 ops to make l..r strictly decreasing" },
          { id: "maxAltSubseqSum", signature: "maxAltSubseqSum(l, r)", description: "Max alt subsequence sum  +a − b + c …  in l..r" },
          { id: "longestEqualRun", signature: "longestEqualRun(l, r)", description: "Longest run of equal adjacent values in l..r" },
          { id: "doAllElementsAppearEvenFrequency", signature: "doAllElementsAppearEvenFrequency(l, r)", description: "All vals in l..r even frq?" },
          { id: "rangeSumMod", signature: "rangeSumMod(l, r)", description: "(a[l] + … + a[r]) % MOD" },
        ],
      },
    ],
  },
  {
    id: "sequence",
    title: "Treap-esque operations",
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "size", signature: "size()", description: "How many elements the array has right now" },
          { id: "split", signature: "split(k)", description: "Split into two arrays: 0..k−1 and a[k]… (the original is left empty)" },
          { id: "cut", signature: "cut(l, r)", description: "Remove l..r and get it back as a separate array of the same type" },
          { id: "trisect", signature: "trisect(l, r)", description: "Split into three arrays: 0..l−1, l..r, a[r+1]… (the original is left empty)" },
          { id: "merge", signature: "merge(treap)", description: "Append all of another treap of the same type (that treap ends up empty)" },
          { id: "copy", signature: "copy(l, r)", description: "A copy of l..r as a separate treap (this one is unchanged)" },
          { id: "paste", signature: "paste(i, treap)", description: "Insert all of another treap of the same type starting at index i (that treap ends up empty)" },
          { id: "insertAt", signature: "insertAt(i, val)", description: "Insert val so it becomes a[i] (i = n appends)" },
          { id: "find", signature: "find(x)", description: "Index of x right now, or −1 (the values must be distinct)" },
          { id: "rangeReverse", signature: "rangeReverse(l, r)", description: "Reverse l..r in place" },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "rangeRotateLeft", signature: "rangeRotateLeft(l, r, k)", description: "Cyclic shift l..r left by k (a[l+k] moves to l)" },
          { id: "rangeRotateRight", signature: "rangeRotateRight(l, r, k)", description: "Cyclic shift l..r right by k (a[r−k+1…r] move to the front)" },
          { id: "append", signature: "append(val)", description: "Add val at the end" },
          { id: "appendLeft", signature: "appendLeft(val)", description: "Add val at the front (every index shifts up by 1)" },
          { id: "pop", signature: "pop()", description: "Remove and return the last value" },
          { id: "popLeft", signature: "popLeft()", description: "Remove and return the first value (every index shifts down by 1)" },
          { id: "insertCopiesAt", signature: "insertCopiesAt(i, val, k)", description: "Insert k copies of val so they become i..i+k−1" },
          { id: "rangeTwinSpin", signature: "rangeTwinSpin(l, r)", description: "Swap a[l]↔a[l+1], a[l+2]↔a[l+3], … (an odd last one stays)" },
        ],
      },
    ],
  },
  {
    id: "order",
    title: "Sorted view of a[l..r]",
    tiers: [
      {
        kind: "topic",
        label: "Rank",
        ops: [
          { id: "kthSmallest", signature: "kthSmallest(l, r, k)", description: "k-th smallest of l..r (k = 1 is the min)" },
        ],
      },
      {
        kind: "topic",
        label: "Nearest to x",
        ops: [
          { id: "smallestGteX", signature: "smallestGteX(l, r, x)", description: "Smallest value ≥ x in l..r" },
          { id: "smallestGtX", signature: "smallestGtX(l, r, x)", description: "Smallest value > x in l..r" },
          { id: "largestLteX", signature: "largestLteX(l, r, x)", description: "Largest value ≤ x in l..r" },
          { id: "largestLtX", signature: "largestLtX(l, r, x)", description: "Largest value < x in l..r" },
        ],
      },
      {
        kind: "topic",
        label: "Count",
        ops: [
          { id: "countLtX", signature: "countLtX(l, r, x)", description: "# of values < x in l..r" },
          { id: "countLteX", signature: "countLteX(l, r, x)", description: "# of values ≤ x in l..r" },
          { id: "countGtX", signature: "countGtX(l, r, x)", description: "# of values > x in l..r" },
          { id: "countGteX", signature: "countGteX(l, r, x)", description: "# of values ≥ x in l..r" },
          { id: "countInValRange", signature: "countInValRange(l, r, lo, hi)", description: "# of values in l..r with lo ≤ value ≤ hi" },
        ],
      },
      {
        kind: "topic",
        label: "Sum",
        ops: [
          { id: "sumLtX", signature: "sumLtX(l, r, x)", description: "Sum of the values < x in l..r" },
          { id: "sumLteX", signature: "sumLteX(l, r, x)", description: "Sum of the values ≤ x in l..r" },
          { id: "sumGtX", signature: "sumGtX(l, r, x)", description: "Sum of the values > x in l..r" },
          { id: "sumGteX", signature: "sumGteX(l, r, x)", description: "Sum of the values ≥ x in l..r" },
          { id: "sumInValRange", signature: "sumInValRange(l, r, lo, hi)", description: "Sum of values in l..r with lo ≤ value ≤ hi" },
        ],
      },
      {
        kind: "topic",
        label: "Sum by rank",
        ops: [
          { id: "sumSmallestK", signature: "sumSmallestK(l, r, k)", description: "Sum of the k smallest values in l..r" },
          { id: "sumLargestK", signature: "sumLargestK(l, r, k)", description: "Sum of the k largest values in l..r" },
          { id: "sumKthSmallestRange", signature: "sumKthSmallestRange(l, r, kFrom, kTo)", description: "Sum of the kFrom-th … kTo-th smallest values in l..r (1-indexed ranks)" },
          { id: "sumKthLargestRange", signature: "sumKthLargestRange(l, r, kFrom, kTo)", description: "Sum of the kFrom-th … kTo-th largest values in l..r (1-indexed ranks)" },
        ],
      },
      {
        kind: "topic",
        label: "Distance",
        ops: [
          { id: "sumAbsDiffToX", signature: "sumAbsDiffToX(l, r, x)", description: "Σ |a[i] − x| over l..r" },
        ],
      },
      {
        kind: "topic",
        label: "Mex",
        ops: [
          { id: "rangeMex", signature: "rangeMex(l, r)", description: "Smallest integer ≥ 0 missing from l..r" },
        ],
      },
    ],
  },
  {
    id: "prefix-suffix",
    title: "Prefix / suffix sums",
    collapsible: true,
    tiers: [
      {
        kind: "topic",
        ops: [
          { id: "maxPrefixSum", signature: "maxPrefixSum(l, r)", description: "Max of a[l] + … + a[i] over i in [l, r]" },
          { id: "maxSuffixSum", signature: "maxSuffixSum(l, r)", description: "Max of a[i] + … + a[r] over i in [l, r]" },
          { id: "minPrefixSum", signature: "minPrefixSum(l, r)", description: "Min of a[l] + … + a[i] over i in [l, r]" },
          { id: "minSuffixSum", signature: "minSuffixSum(l, r)", description: "Min of a[i] + … + a[r] over i in [l, r]" },
          { id: "leftmostPrefixSumGteX", signature: "leftmostPrefixSumGteX(l, r, x)", description: "First i in [l, r] with a[l] + … + a[i] ≥ x (needs a[i] ≥ 0)" },
          { id: "leftmostPrefixSumGtX", signature: "leftmostPrefixSumGtX(l, r, x)", description: "First i in [l, r] with a[l] + … + a[i] > x (needs a[i] ≥ 0)" },
          { id: "rightmostSuffixSumGteX", signature: "rightmostSuffixSumGteX(l, r, x)", description: "Last i in [l, r] with a[i] + … + a[r] ≥ x (needs a[i] ≥ 0)" },
          { id: "rightmostSuffixSumGtX", signature: "rightmostSuffixSumGtX(l, r, x)", description: "Last i in [l, r] with a[i] + … + a[r] > x (needs a[i] ≥ 0)" },
          { id: "leftmostPrefixSumLteX", signature: "leftmostPrefixSumLteX(l, r, x)", description: "First i in [l, r] with a[l] + … + a[i] ≤ x" },
          { id: "leftmostPrefixSumLtX", signature: "leftmostPrefixSumLtX(l, r, x)", description: "First i in [l, r] with a[l] + … + a[i] < x" },
          { id: "rightmostSuffixSumLteX", signature: "rightmostSuffixSumLteX(l, r, x)", description: "Last i in [l, r] with a[i] + … + a[r] ≤ x" },
          { id: "rightmostSuffixSumLtX", signature: "rightmostSuffixSumLtX(l, r, x)", description: "Last i in [l, r] with a[i] + … + a[r] < x" },
        ],
      },
    ],
  },
  {
    id: "hashing",
    title: "Hashing (strings)",
    collapsible: true,
    tiers: [
      {
        kind: "topic",
        ops: [
          { id: "rangeHash", signature: "rangeHash(l, r)", description: "Hash of l..r read left to right (equal ranges hash equal)" },
          { id: "rangeHashReversed", signature: "rangeHashReversed(l, r)", description: "Hash of l..r read right to left" },
          { id: "isPalindrome", signature: "isPalindrome(l, r)", description: "Is l..r a palindrome" },
          { id: "rangesEqual", signature: "rangesEqual(l1, r1, l2, r2)", description: "Are l1..r1 and l2..r2 equal" },
          { id: "hashAll", signature: "hashAll()", description: "Hash of the whole array (compares with any structure's hashes this run)" },
          { id: "longestPalCenteredAtI", signature: "longestPalCenteredAtI(i)", description: "(l, r) of the longest odd palindrome centred on a[i]" },
          { id: "longestPalCenteredAtIPlusOne", signature: "longestPalCenteredAtIPlusOne(i)", description: "(l, r) of the longest even palindrome centred between a[i] and a[i+1]; (i+1, i) if none" },
        ],
      },
    ],
  },
  {
    id: "lis",
    title: "LIS",
    collapsible: true,
    tiers: [
      {
        kind: "topic",
        ops: [
          { id: "rangeLIS", signature: "rangeLIS(l, r)", description: "Longest strictly increasing subseq of l..r" },
          { id: "rangeLNDS", signature: "rangeLNDS(l, r)", description: "Longest non-decreasing subseq of l..r" },
          { id: "rangeLDS", signature: "rangeLDS(l, r)", description: "Longest strictly decreasing subseq of l..r" },
          { id: "rangeLNIS", signature: "rangeLNIS(l, r)", description: "Longest non-increasing subseq of l..r" },
        ],
      },
    ],
  },
  {
    id: "brackets",
    title: "Brackets",
    collapsible: true,
    tiers: [
      {
        kind: "topic",
        ops: [
          { id: "isRBS", signature: "isRBS(l, r)", description: "Is l..r a regular (balanced) bracket sequence?" },
          { id: "rangeFlip", signature: "rangeFlip(l, r)", description: "Swap opens and closes in l..r" },
        ],
      },
    ],
  },
  {
    id: "xor",
    title: "XOR",
    collapsible: true,
    tiers: [
      {
        kind: "topic",
        label: "Range update",
        ops: [
          { id: "rangeXorApply", signature: "rangeXorApply(l, r, x)", description: "a[i] ^= x" },
        ],
      },
      {
        kind: "topic",
        label: "Range query",
        ops: [
          { id: "rangeXorQuery", signature: "rangeXorQuery(l, r)", description: "a[l] ^ … ^ a[r]" },
        ],
      },
      {
        kind: "topic",
        label: "By value in a[l..r]",
        ops: [
          { id: "xorLtX", signature: "xorLtX(l, r, x)", description: "XOR of the values < x in l..r (copies count)" },
          { id: "xorLteX", signature: "xorLteX(l, r, x)", description: "XOR of the values ≤ x in l..r (copies count)" },
          { id: "xorGtX", signature: "xorGtX(l, r, x)", description: "XOR of the values > x in l..r (copies count)" },
          { id: "xorGteX", signature: "xorGteX(l, r, x)", description: "XOR of the values ≥ x in l..r (copies count)" },
          { id: "xorInValRange", signature: "xorInValRange(l, r, lowVal, highVal)", description: "XOR of the values in [lowVal, highVal] in l..r (copies count)" },
        ],
      },
      {
        kind: "topic",
        label: "XOR with x over a[l..r]",
        ops: [
          { id: "maxXorAgainstX", signature: "maxXorAgainstX(l, r, x)", description: "Largest v ^ x over the values v in l..r" },
          { id: "minXorAgainstX", signature: "minXorAgainstX(l, r, x)", description: "Smallest v ^ x over the values v in l..r" },
          { id: "kthXor", signature: "kthXor(l, r, x, i)", description: "i-th smallest v ^ x over l..r, 0-indexed: kthXor(l, r, x, 0) is the smallest" },
          { id: "countXorLtK", signature: "countXorLtK(l, r, x, k)", description: "How many v in l..r have v ^ x < k (k is a value, not a rank)" },
          { id: "countXorLteK", signature: "countXorLteK(l, r, x, k)", description: "How many v in l..r have v ^ x ≤ k (k is a value, not a rank)" },
          { id: "countXorGtK", signature: "countXorGtK(l, r, x, k)", description: "How many v in l..r have v ^ x > k (k is a value, not a rank)" },
          { id: "countXorGteK", signature: "countXorGteK(l, r, x, k)", description: "How many v in l..r have v ^ x ≥ k (k is a value, not a rank)" },
          { id: "largestXorLtK", signature: "largestXorLtK(l, r, x, k)", description: "Largest v ^ x over l..r that is < k (k is a value, not a rank)" },
          { id: "largestXorLteK", signature: "largestXorLteK(l, r, x, k)", description: "Largest v ^ x over l..r that is ≤ k (k is a value, not a rank)" },
          { id: "smallestXorGtK", signature: "smallestXorGtK(l, r, x, k)", description: "Smallest v ^ x over l..r that is > k (k is a value, not a rank)" },
          { id: "smallestXorGteK", signature: "smallestXorGteK(l, r, x, k)", description: "Smallest v ^ x over l..r that is ≥ k (k is a value, not a rank)" },
          { id: "mexXor", signature: "mexXor(l, r, x)", description: "Smallest non-negative integer that is no v ^ x over the values v in l..r" },
          { id: "sumXor", signature: "sumXor(l, r, x)", description: "Sum of v ^ x over every value v in l..r" },
        ],
      },
      {
        kind: "topic",
        label: "XOR with x over a[l..r], limit on v",
        ops: [
          { id: "maxXorWithVLtM", signature: "maxXorWithVLtM(l, r, x, m)", description: "Largest v ^ x over the values v < m in l..r" },
          { id: "maxXorWithVLteM", signature: "maxXorWithVLteM(l, r, x, m)", description: "Largest v ^ x over the values v ≤ m in l..r" },
          { id: "maxXorWithVGtM", signature: "maxXorWithVGtM(l, r, x, m)", description: "Largest v ^ x over the values v > m in l..r" },
          { id: "maxXorWithVGteM", signature: "maxXorWithVGteM(l, r, x, m)", description: "Largest v ^ x over the values v ≥ m in l..r" },
          { id: "minXorWithVLtM", signature: "minXorWithVLtM(l, r, x, m)", description: "Smallest v ^ x over the values v < m in l..r" },
          { id: "minXorWithVLteM", signature: "minXorWithVLteM(l, r, x, m)", description: "Smallest v ^ x over the values v ≤ m in l..r" },
          { id: "minXorWithVGtM", signature: "minXorWithVGtM(l, r, x, m)", description: "Smallest v ^ x over the values v > m in l..r" },
          { id: "minXorWithVGteM", signature: "minXorWithVGteM(l, r, x, m)", description: "Smallest v ^ x over the values v ≥ m in l..r" },
          { id: "maxXorWithVInValRange", signature: "maxXorWithVInValRange(l, r, x, lo, hi)", description: "Largest v ^ x over the values v in [lo, hi] in l..r" },
          { id: "minXorWithVInValRange", signature: "minXorWithVInValRange(l, r, x, lo, hi)", description: "Smallest v ^ x over the values v in [lo, hi] in l..r" },
        ],
      },
    ],
  },
  {
    id: "or",
    title: "OR",
    collapsible: true,
    tiers: [
      {
        kind: "topic",
        label: "Range update",
        ops: [
          { id: "rangeOrApply", signature: "rangeOrApply(l, r, x)", description: "a[i] |= x" },
        ],
      },
      {
        kind: "topic",
        label: "Range query",
        ops: [
          { id: "rangeOrQuery", signature: "rangeOrQuery(l, r)", description: "a[l] | … | a[r]" },
        ],
      },
      {
        kind: "topic",
        label: "By value in a[l..r]",
        ops: [
          { id: "orLtX", signature: "orLtX(l, r, x)", description: "OR of the values < x in l..r" },
          { id: "orLteX", signature: "orLteX(l, r, x)", description: "OR of the values ≤ x in l..r" },
          { id: "orGtX", signature: "orGtX(l, r, x)", description: "OR of the values > x in l..r" },
          { id: "orGteX", signature: "orGteX(l, r, x)", description: "OR of the values ≥ x in l..r" },
          { id: "orInValRange", signature: "orInValRange(l, r, lowVal, highVal)", description: "OR of the values in [lowVal, highVal] in l..r" },
        ],
      },
    ],
  },
  {
    id: "and",
    title: "AND",
    collapsible: true,
    tiers: [
      {
        kind: "topic",
        label: "Range update",
        ops: [
          { id: "rangeAndApply", signature: "rangeAndApply(l, r, x)", description: "a[i] &= x" },
        ],
      },
      {
        kind: "topic",
        label: "Range query",
        ops: [
          { id: "rangeAndQuery", signature: "rangeAndQuery(l, r)", description: "a[l] & … & a[r]" },
        ],
      },
      {
        kind: "topic",
        label: "By value in a[l..r]",
        ops: [
          { id: "andLtX", signature: "andLtX(l, r, x)", description: "AND of the values < x in l..r" },
          { id: "andLteX", signature: "andLteX(l, r, x)", description: "AND of the values ≤ x in l..r" },
          { id: "andGtX", signature: "andGtX(l, r, x)", description: "AND of the values > x in l..r" },
          { id: "andGteX", signature: "andGteX(l, r, x)", description: "AND of the values ≥ x in l..r" },
          { id: "andInValRange", signature: "andInValRange(l, r, lowVal, highVal)", description: "AND of the values in [lowVal, highVal] in l..r" },
        ],
      },
    ],
  },
  {
    id: "strided",
    title: "Strided queries (every step-th element)",
    collapsible: true,
    tiers: [
      {
        kind: "common",
        ops: [
          { id: "stridedSum", signature: "stridedSum(l, r, step)", description: "a[l] + a[l+step] + a[l+2·step] + … up to r" },
          { id: "stridedMin", signature: "stridedMin(l, r, step)", description: "min of a[l], a[l+step], … up to r" },
          { id: "stridedMax", signature: "stridedMax(l, r, step)", description: "max of a[l], a[l+step], … up to r" },
          { id: "stridedAdd", signature: "stridedAdd(l, r, step, v)", description: "a[l] += v, a[l+step] += v, … up to r" },
        ],
      },
      {
        kind: "uncommon",
        ops: [
          { id: "stridedGcd", signature: "stridedGcd(l, r, step)", description: "gcd of a[l], a[l+step], … up to r" },
          { id: "stridedXorQuery", signature: "stridedXorQuery(l, r, step)", description: "xor of a[l], a[l+step], … up to r" },
          { id: "stridedAndQuery", signature: "stridedAndQuery(l, r, step)", description: "AND of a[l], a[l+step], … up to r" },
          { id: "stridedOrQuery", signature: "stridedOrQuery(l, r, step)", description: "OR of a[l], a[l+step], … up to r" },
        ],
      },
    ],
  },
];

// Ordered lightest to heaviest constant factor; used to break ties between templates.
export const DATA_STRUCTURE_TYPES = [
  "positions",
  "interval-map",
  "sparse-table",
  "BIT",
  "seg-tree",
  "lazy-seg-tree",
  "merge-sort-tree",
  "wavelet",
  "persistent",
  "persistent-trie",
  "bit-of-trees",
  "bit-of-tries",
  "seg-of-trees",
  "position-trees",
  // treap-likes, lightest first (on a cost tie): one treap; two (even / odd lanes); copies on every update; value trees
  "treap",
  "pair-treap",
  "persistent-treap",
  "sorted-runs",
  "beats",
  "sqrt",
  "sqrt-tries",
  "rolling-hash",
  "manacher",
] as const;

export type DataStructureType = (typeof DATA_STRUCTURE_TYPES)[number];

export const DATA_STRUCTURE_TYPE_LABELS: Record<DataStructureType, string> = {
  positions: "Position lists",
  "interval-map": "Interval map (runs of equal values)",
  "sparse-table": "Sparse table",
  BIT: "BIT",
  "seg-tree": "Seg tree",
  "lazy-seg-tree": "Lazy seg tree",
  "merge-sort-tree": "Merge sort tree",
  wavelet: "Wavelet matrix",
  persistent: "Persistent seg tree",
  "persistent-trie": "Persistent binary trie (appendable)",
  "bit-of-trees": "BIT of value seg trees",
  "bit-of-tries": "BIT of binary tries",
  "seg-of-trees": "Seg tree of value seg trees",
  "position-trees": "Seg tree of positions per value (split / merge)",
  "pair-treap": "Treap pair (even / odd positions)",
  "sorted-runs": "Sorted runs (mergeable value trees)",
  "persistent-treap": "Persistent treap",
  treap: "Implicit treap",
  beats: "Seg tree beats",
  sqrt: "Sqrt decomposition",
  "sqrt-tries": "Sqrt blocks of binary tries (lazy xor / assign)",
  "rolling-hash": "Rolling hash deque",
  manacher: "Manacher's algorithm",
};

export interface RangeQueryTemplate {
  // Folder under templates/ultimate-template-tool/range-queries holding template.py and/or template.cpp.
  folder: string;
  langs: TemplateLang[];
  operations: OpId[];
  dataStructureType: DataStructureType;
  // merge sort trees only: whether queries use fractional cascading (one root search, then prefix counts per level)
  fractionalCascading?: boolean;
  // the constructor needs every value that will ever be added up front (to compress them); costs are then log N, not log U
  valuesOffline?: true;
  // Per-operation cost from the @complexities tag, e.g. "log(N)", "log^2(N) amortized", "log(N)*log(U)", "log(N)+log(U) ?" (a trailing ? marks a bound we are unsure of).
  complexities: Partial<Record<OpId, string>>;
  build: string;
  memory: MemoryBreakdown;
  originalFileUrl?: string;
  // The same operations over any index range [lo, hi]: a dynamic structure where every position starts at 0 (costs
  // use U = size of that range, log U <= 64, and memory sizes are per update), or, for a static template, one built
  // from N given values ((index, value) pairs) with every other index 0 (costs and memory in N).
  sparse?: SparseVariant;
  // letters (a list of characters): lettersSame = this very file takes them for its character ops; letters = a separate
  // file for that (character sentinels, ord() in hashes), listing just those ops
  lettersSame?: boolean;
  letters?: SparseVariant & { operations: OpId[] };
  // (not in the catalog: the drawer reads the usage panel from the code it fetches)
  usage?: Partial<Record<TemplateLang, Usage>>;
}

export interface SparseVariant {
  langs: TemplateLang[];
  operations?: OpId[]; // when it supports fewer than the dense template (a sparse tree has no getAll)
  complexities: Partial<Record<OpId, string>>;
  build: string;
  memory: MemoryBreakdown;
  usage?: Partial<Record<TemplateLang, Usage>>;
}

// One template as the generated manifest stores it (see scripts/build-range-query-templates.mjs): table indices
// instead of op lists, cost strings and memory layouts.
type VariantRow = 0 | readonly [langs: string, opList: number, costList: number, build: number, memory: number, ownOps: number];
export type RangeTemplateRow = readonly [
  folder: string, langs: string, type: DataStructureType, flags: string, originalFileUrl: string,
  opList: number, costList: number, build: number, memory: number, sparse: VariantRow, letters: VariantRow,
];

export function decodeRangeTemplates(data: {
  opNames: readonly OpId[];
  costs: readonly string[];
  opLists: readonly (readonly number[])[];
  costLists: readonly (readonly number[])[];
  memories: readonly MemoryBreakdown[];
  rows: readonly RangeTemplateRow[];
}): RangeQueryTemplate[] {
  const lists = data.opLists.map((l) => l.map((i) => data.opNames[i]));
  const unpack = (list: number, costList: number, build: number, memory: number) => {
    const operations = lists[list];
    const complexities: Partial<Record<OpId, string>> = {};
    data.costLists[costList].forEach((c, i) => (complexities[operations[i]] = data.costs[c]));
    return { operations, complexities, build: data.costs[build], memory: data.memories[memory] };
  };
  const variant = (v: VariantRow) => {
    if (!v) return undefined;
    const { operations, ...rest } = unpack(v[1], v[2], v[3], v[4]);
    return { langs: v[0].split(" ") as TemplateLang[], ...(v[5] ? { operations } : {}), ...rest };
  };
  return data.rows.map(([folder, langs, type, flags, url, list, costList, build, memory, sparse, letters]) => {
    const t: RangeQueryTemplate = {
      folder,
      langs: langs.split(" ") as TemplateLang[],
      dataStructureType: type,
      ...unpack(list, costList, build, memory),
      ...(flags.includes("f") ? { fractionalCascading: true } : flags.includes("F") ? { fractionalCascading: false } : {}),
      ...(flags.includes("o") ? { valuesOffline: true as const } : {}),
      ...(flags.includes("s") ? { lettersSame: true } : {}),
      ...(url ? { originalFileUrl: url } : {}),
    };
    const sv = variant(sparse);
    if (sv) t.sparse = sv;
    const lv = variant(letters);
    if (lv) t.letters = { ...lv, operations: lv.operations ?? t.operations };
    return t;
  });
}

// A template as the picker shows it in the current mode: in sparse mode, its costs / memory / files are the sparse ones.
// chars: offered for characters (the "Values are chars" box), so the usage panel talks about characters
export type TemplateView = RangeQueryTemplate & { file: "template" | "sparse" | "letters"; chars?: boolean };

// Ops that only compare, copy, move or hash values, so they work on letters too (mirrors test_templates.CHAR_SAFE);
// every other op does arithmetic and needs numbers.
export const CHAR_SAFE_OPS: ReadonlySet<string> = new Set([
  "size",
  "pointGet", "pointAssign", "pointChmax", "pointChmin", "rangeAssign", "rangeChmax", "rangeChmin", "rangeSortAsc",
  "rangeSortDesc", "getAll", "append", "appendLeft", "insertAt", "insertCopiesAt",
  "rangeReverse", "rangeRotateLeft", "rangeRotateRight", "cut", "paste", "split", "trisect", "merge",
  "copy", "rangeTwinSpin", "rangeMin", "rangeMax", "countDistinct", "allDistinct", "rangeMode", "countOccurrences",
  "leftmostIndexOf", "rightmostIndexOf", "leftmostIndexOfInRange", "rightmostIndexOfInRange",
  "longestEqualRun", "rangeLIS", "rangeLNDS", "rangeLDS", "rangeLNIS", "isRBS", "rangeFlip", "rangeReplace", "isPalindrome",
  "rangeHash", "rangeHashReversed", "rangesEqual", "doAllElementsAppearEvenFrequency", "kthSmallest",
  "countLtX", "countLteX", "countGtX", "countGteX", "countInValRange", "smallestGtX", "smallestGteX",
  "largestLtX", "largestLteX", "kthLtX", "kthLteX", "kthGtX", "kthGteX",
  ...["leftmost", "rightmost"].flatMap((side) => ["Gt", "Gte", "Lt", "Lte"].map((c) => `${side}${c}X`)),
]);

// A template as it is offered for letters: its letters file, or itself cut down to its character ops when the same
// file takes characters, or nothing (numbers only; sparse versions are for numbers).
export function lettersView(t: TemplateView): TemplateView | null {
  if (t.file === "sparse") return null;
  if (t.letters) return { ...t, ...t.letters, file: "letters", chars: true };
  if (t.lettersSame) return { ...t, operations: t.operations.filter((op) => CHAR_SAFE_OPS.has(op)), chars: true };
  return null;
}

export function viewOf(t: RangeQueryTemplate, sparse: boolean): TemplateView | null {
  if (!sparse) return { ...t, file: "template" };
  if (!t.sparse) return null;
  return { ...t, ...t.sparse, file: "sparse" };
}

// What a card calls the structure: "Lazy seg tree", "Sparse lazy seg tree", "Sparse seg tree beats", for a static
// structure's sparse version "Sparse merge sort tree built from values", and merge sort trees add "(FC)" / "(no FC)".
const BEATS_UPDATES: ReadonlySet<string> = new Set([
  "rangeFloorDiv", "rangeMod", "rangeFloorSqrt", "rangeAndApply", "rangeOrApply", "rangeChmax", "rangeChmin",
]);

export function templateKindLabel(t: TemplateView): string {
  // the movable sqrt blocks (insert / erase / reverse / rotate / cut and paste, with value queries); the sums one also
  // keeps prefix sums and the chmin / chmax tag. Their amortized costs come from re-merging blocks, not beats
  if (t.folder.startsWith("sqrt-movable"))
    return `Sqrt decomposition, movable blocks${t.operations.includes("sumLtX") ? " with sums, chmin / chmax" : ""}`;
  // a wavelet with rangeMex also carries a persistent seg tree for it; its sums / by-value xor / OR / AND are named,
  // OR and AND with how they are kept (a sparse table per level is faster, a seg tree per level lighter)
  const wav = t.dataStructureType === "wavelet";
  const mex = wav && t.operations.includes("rangeMex") ? " + persistent mex tree" : "";
  const kept = !wav
    ? []
    : ([["sumLtX", "sums"], ["xorLtX", "xor"], ["orLtX", "OR"], ["andLtX", "AND"]] as const)
        .filter(([op]) => t.operations.includes(op))
        .map(([op, w]) =>
          op === "orLtX" || op === "andLtX"
            ? `${w} (${t.complexities[op] === "log^2(N)" ? "seg tree per level" : "sparse table per level"})`
            : w,
        );
  const extras = kept.length ? ` with ${kept.join(", ")}` : "";
  // the persistent trees that grow by append are over the value range, not compressed values
  const appendable =
    t.dataStructureType !== "persistent" || !t.operations.includes("append")
      ? ""
      : t.valuesOffline
        ? " (appendable, every value known up front)"
        : " over values (appendable)";
  // a treap with lazy value tags (a pending assign / add / ... for its children) says so; a reverse flag alone doesn't
  // count (that's a treap with reverse, not a lazy treap)
  const lazyTreap =
    (t.dataStructureType === "treap" || t.dataStructureType === "persistent-treap") &&
    t.memory.tags.arrays.some((a) => a.name !== "rev");
  const plainKind = lazyTreap
    ? DATA_STRUCTURE_TYPE_LABELS[t.dataStructureType].replace(/ treap$/, " lazy treap")
    : DATA_STRUCTURE_TYPE_LABELS[t.dataStructureType];
  // a treap or seg tree whose div / mod / sqrt / AND / OR / chmax / chmin updates use the beats technique (descend only
  // where values still change, so the cost is amortized) says "beats", like the seg tree beats do
  const beats =
    t.dataStructureType !== "beats" &&
    t.operations.some((op) => BEATS_UPDATES.has(op) && (t.complexities[op] ?? "").includes("amortized"));
  const kind = !beats
    ? plainKind
    : plainKind.includes(" (")
      ? plainKind.replace(" (", " beats (")
      : `${plainKind} beats`;
  // the merge sort trees with point updates are named by what each node keeps (fractional cascading never applies)
  const inner = (
    [["sortedlist", "sorted lists"], ["treap", "treaps"], ["hashfenwick", "hashed Fenwick trees"], ["offline", "Fenwick trees, every update listed up front"]] as const
  ).find(([key]) => t.folder.startsWith(`merge-sort-tree-updates-${key}`));
  if (inner) return `Merge sort tree with updates (${inner[1]})`;
  // the binary tries name what they keep beyond the counts: each node's smallest last index (for mexXor),
  // per-bit prefix counts (for sumXor), node sums / xors (by-value sums / xors), per-bit latest indices (by-value OR / AND)
  const trieKept =
    !["persistent-trie", "bit-of-tries", "sqrt-tries"].includes(t.dataStructureType)
      ? []
      : ([["mexXor", "last index per node"], ["sumXor", "bit counts"], ["sumLtX", "sums"], ["xorLtX", "xors"], ["orLtX", "OR bit indices"], ["andLtX", "AND bit indices"]] as const).filter(([op]) => t.operations.includes(op)).map(([, w]) => w);
  const base = kind + extras + mex + appendable + (trieKept.length ? ` with ${trieKept.join(", ")}` : "");
  const fc = t.fractionalCascading === undefined ? "" : t.fractionalCascading ? " (FC)" : " (no FC)";
  if (t.file !== "sparse") return base + fc;
  // lowercase the first word after "Sparse", unless it's an acronym ("BIT", "BIT of value seg trees")
  const lower = /^[A-Z]{2,}\b/.test(base) ? base : base[0].toLowerCase() + base.slice(1);
  const sparse = base.startsWith("Sparse") ? base : `Sparse ${lower}`; // "Sparse table" is already "sparse"
  return `${sparse}${isBuiltFromPoints(t.memory) ? " built from values" : ""}${fc}`;
}

