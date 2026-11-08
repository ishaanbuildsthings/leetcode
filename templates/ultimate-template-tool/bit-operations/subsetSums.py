# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/subsetSums.py

from operator import add

# g where g[mask] = sum of f[sub] over every submask sub of mask (sub & mask == sub), the zeta transform / SOS DP
# len(f) must be a power of two, 2^B
# subsetSums([1, 2, 3, 4]) -> [1, 3, 4, 10]   # g[3] = f[0] + f[1] + f[2] + f[3]
# Count of array values that are submasks of each mask: subsetSums(counts), counts[x] = occurrences of x
# O(B * 2^B)
def subsetSums(f):
    def bitPairs(n):  # bit by bit: slice pairs (indexes without the bit, the same indexes with it), C-speed adds on slices
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
    n = len(f)
    if n == 0 or n & (n - 1):
        raise ValueError(f"subsetSums: length {n} is not a power of two")
    g = list(f)
    for lo, hi in bitPairs(n):
        g[hi] = map(add, g[hi], g[lo])
    return g
