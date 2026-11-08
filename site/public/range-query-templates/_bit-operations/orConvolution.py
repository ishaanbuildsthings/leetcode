# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/orConvolution.py

from operator import add, sub, mul

# c of size 2^B: c[k] = sum of a[i] * b[j] over every i, j with i | j == k
# len(a) == len(b) == 2^B
# orConvolution([1, 2], [3, 4]) -> [3, 18]   # c[1] = a0*b1 + a1*b0 + a1*b1 = 4 + 6 + 8
# O(B * 2^B)
def orConvolution(a, b):
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
    n = len(a)
    if n == 0 or n & (n - 1) or len(b) != n:
        raise ValueError(f"orConvolution: lengths {len(a)} and {len(b)} must be the same power of two")
    a = list(a)
    b = list(b)
    for g in (a, b):
        for lo, hi in bitPairs(n):
            g[hi] = map(add, g[hi], g[lo])
    c = list(map(mul, a, b))
    for lo, hi in bitPairs(n):
        c[hi] = map(sub, c[hi], c[lo])
    return c
