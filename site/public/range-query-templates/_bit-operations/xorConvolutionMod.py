# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/xorConvolutionMod.py

from operator import add, sub, mul

# c of size 2^B: c[k] = sum of a[i] * b[j] over every i, j with i ^ j == k, mod mod (mod must be odd)
# len(a) == len(b) == 2^B
# xorConvolutionMod([1, 2], [3, 4], 7) -> [4, 3]   # 11 % 7, 10 % 7
# O(B * 2^B + log(MOD))
def xorConvolutionMod(a, b, mod):
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
        raise ValueError(f"xorConvolutionMod: lengths {len(a)} and {len(b)} must be the same power of two")
    if mod % 2 == 0:
        raise ValueError(f"xorConvolutionMod: mod {mod} is even, so 2^B has no inverse")
    a = [x % mod for x in a]
    b = [x % mod for x in b]
    walshHadamard(a)
    walshHadamard(b)
    c = [x * y % mod for x, y in zip(a, b)]
    walshHadamard(c)
    invN = pow(n, -1, mod)
    return [x * invN % mod for x in c]
