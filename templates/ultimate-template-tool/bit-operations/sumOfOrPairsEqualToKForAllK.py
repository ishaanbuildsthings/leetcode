# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfOrPairsEqualToKForAllK.py

from operator import add, sub, mul

# c of size 2^B: c[k] = sum of arr1[i] * arr2[j] over every i and every j with i | j == k
# len(arr1) == len(arr2) == 2^B
# sumOfOrPairsEqualToKForAllK([1, 2], [3, 4]) -> [3, 18]   # c[1] = arr1[0]*arr2[1] + arr1[1]*arr2[0] + arr1[1]*arr2[1]
# = 4 + 6 + 8
# O(B * 2^B)
def sumOfOrPairsEqualToKForAllK(arr1, arr2):
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
    n = len(arr1)
    if n == 0 or n & (n - 1) or len(arr2) != n:
        raise ValueError(
            f"sumOfOrPairsEqualToKForAllK: lengths {len(arr1)} and {len(arr2)} must be the same power of two")
    arr1 = list(arr1)
    arr2 = list(arr2)
    for g in (arr1, arr2):
        for lo, hi in bitPairs(n):
            g[hi] = map(add, g[hi], g[lo])
    c = list(map(mul, arr1, arr2))
    for lo, hi in bitPairs(n):
        c[hi] = map(sub, c[hi], c[lo])
    return c
