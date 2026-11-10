# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/subsetSums.py

from operator import add

# res where res[mask] = sum of valueAtMask[sub] over every submask sub of mask (sub & mask == sub), the zeta transform /
# SOS DP
# len(valueAtMask) must be a power of two, 2^B
# subsetSums([1, 2, 3, 4]) -> [1, 3, 4, 10]   # res[3] = valueAtMask[0] + valueAtMask[1] + valueAtMask[2] +
# valueAtMask[3]
# Count of array values that are submasks of each mask: subsetSums(counts), counts[x] = occurrences of x
# O(B * 2^B)
def subsetSums(valueAtMask):
    def bitPairs(n):
        # bit by bit: slice pairs (indexes without the bit, the same indexes with it), C-speed adds on slices
        half = 1
        while half < n:
            step = 2 * half
            if half <= n // step:
                for off in range(half):
                    yield slice(off, n, step), slice(off + half, n, step)
            else:
                for start in range(0, n, step):
                    yield slice(start, start + half), slice(start + half, start + step)
            half = step
    n = len(valueAtMask)
    if n == 0 or n & (n - 1):
        raise ValueError(f"subsetSums: length {n} is not a power of two")
    res = list(valueAtMask)
    for lo, hi in bitPairs(n):
        res[hi] = map(add, res[hi], res[lo])
    return res
