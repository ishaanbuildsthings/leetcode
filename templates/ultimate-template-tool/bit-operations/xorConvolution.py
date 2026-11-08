# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/xorConvolution.py

from operator import add, sub, mul

# c of size 2^B: c[k] = sum of a[i] * b[j] over every i, j with i ^ j == k (exact integers)
# len(a) == len(b) == 2^B
# xorConvolution([1, 2], [3, 4]) -> [11, 10]   # c[0] = a0*b0 + a1*b1, c[1] = a0*b1 + a1*b0
# O(B * 2^B)
def xorConvolution(a, b):
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
    def walshHadamard(g):  # in place: g[k] becomes the sum of g[i] * (-1)^popcount(i & k)
        for lo, hi in bitPairs(len(g)):
            x, y = g[lo], g[hi]
            g[lo] = map(add, x, y)
            g[hi] = map(sub, x, y)
    n = len(a)
    if n == 0 or n & (n - 1) or len(b) != n:
        raise ValueError(f"xorConvolution: lengths {len(a)} and {len(b)} must be the same power of two")
    a = list(a)
    b = list(b)
    walshHadamard(a)
    walshHadamard(b)
    c = list(map(mul, a, b))
    walshHadamard(c)
    return [x // n for x in c]
