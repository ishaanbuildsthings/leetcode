# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/countSubsetsByAnd.py

from operator import add, sub

# res of size 2^B: res[v] = number of non-empty subsets (by position) whose AND is exactly v, mod mod
# values must be >= 0; B = number of bits in max(arr), so the list is about 2 * max(arr) long
# countSubsetsByAnd([1, 3], 10**9 + 7) -> [0, 2, 0, 1]   # {1}, {1, 3} AND to 1; {3} ANDs to 3
# O(B * 2^B + N)
def countSubsetsByAnd(arr, mod):
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
            raise ValueError(f"countSubsetsByAnd: value {x} is negative")
    n = 1 << max(arr, default=0).bit_length()
    cnt = [0] * n
    for x in arr:
        cnt[x] += 1
    for lo, hi in bitPairs(n):  # cnt[m] = how many values have every bit of m
        cnt[lo] = map(add, cnt[lo], cnt[hi])
    pow2 = [1] * (len(arr) + 1)
    for i in range(1, len(arr) + 1):
        pow2[i] = pow2[i - 1] * 2 % mod
    res = [pow2[c] - 1 for c in cnt]  # non-empty subsets whose AND has every bit of m
    for lo, hi in bitPairs(n):  # keep only the ones whose AND is exactly m
        res[lo] = map(sub, res[lo], res[hi])
    return [x % mod for x in res]
