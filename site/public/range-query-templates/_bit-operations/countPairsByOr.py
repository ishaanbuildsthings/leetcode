# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/countPairsByOr.py

from operator import add, sub

# res of size 2^B: res[v] = number of pairs i < j with arr[i] | arr[j] == v
# values must be >= 0; B = number of bits in max(arr), so the list is about 2 * max(arr) long
# countPairsByOr([1, 3, 2]) -> [0, 0, 0, 3]
# O(B * 2^B + N)
def countPairsByOr(arr):
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
    for x in arr:
        if x < 0:
            raise ValueError(f"countPairsByOr: value {x} is negative")
    n = 1 << max(arr, default=0).bit_length()
    cnt = [0] * n
    for x in arr:
        cnt[x] += 1
    for lo, hi in bitPairs(n):  # cnt[m] = how many values are submasks of m
        cnt[hi] = map(add, cnt[hi], cnt[lo])
    res = [c * (c - 1) // 2 for c in cnt]  # pairs whose OR is a submask of m
    for lo, hi in bitPairs(n):  # keep only the ones whose OR is exactly m
        res[hi] = map(sub, res[hi], res[lo])
    return res
