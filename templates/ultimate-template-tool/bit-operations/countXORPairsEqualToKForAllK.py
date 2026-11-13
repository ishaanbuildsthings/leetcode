# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/countXORPairsEqualToKForAllK.py

from operator import add, sub, mul

# res of size 2^B: res[v] = number of pairs i < j with arr[i] ^ arr[j] == v values must be >= 0; B = number of bits in
# max(arr), so the list is about 2 * max(arr) long
# countXORPairsEqualToKForAllK([1, 3, 2]) -> [0, 1, 1, 1]   # 1^3 = 2, 1^2 = 3, 3^2 = 1
# O(B * 2^B + N)
def countXORPairsEqualToKForAllK(arr):
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
    for x in arr:
        if x < 0:
            raise ValueError(f"countXORPairsEqualToKForAllK: value {x} is negative")
    n = 1 << max(arr, default=0).bit_length()
    cnt = [0] * n
    for x in arr:
        cnt[x] += 1
    walshHadamard(cnt)
    sq = [c * c for c in cnt]
    walshHadamard(sq)
    sq[0] -= n * len(arr)  # drop each i paired with itself (still scaled by n)
    return [x // (2 * n) for x in sq]  # / n undoes the transform, / 2 counts each unordered pair once
