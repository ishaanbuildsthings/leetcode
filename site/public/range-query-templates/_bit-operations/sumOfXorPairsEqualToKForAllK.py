# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfXorPairsEqualToKForAllK.py

from operator import add, sub, mul

# c of size 2^B: c[k] = sum of arr1[i] * arr2[j] over every i and every j with i ^ j == k (exact integers)
# len(arr1) == len(arr2) == 2^B
# sumOfXorPairsEqualToKForAllK([1, 2], [3, 4]) -> [11, 10]   # c[0] = arr1[0]*arr2[0] + arr1[1]*arr2[1], c[1] =
# arr1[0]*arr2[1] + arr1[1]*arr2[0]
# O(B * 2^B)
def sumOfXorPairsEqualToKForAllK(arr1, arr2):
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
    def walshHadamard(g):  # in place: g[k] becomes the sum of g[i] * (-1)^popcount(i & k)
        for lo, hi in bitPairs(len(g)):
            x, y = g[lo], g[hi]
            g[lo] = map(add, x, y)
            g[hi] = map(sub, x, y)
    n = len(arr1)
    if n == 0 or n & (n - 1) or len(arr2) != n:
        raise ValueError(
            f"sumOfXorPairsEqualToKForAllK: lengths {len(arr1)} and {len(arr2)} must be the same power of two")
    arr1 = list(arr1)
    arr2 = list(arr2)
    walshHadamard(arr1)
    walshHadamard(arr2)
    c = list(map(mul, arr1, arr2))
    walshHadamard(c)
    return [x // n for x in c]
