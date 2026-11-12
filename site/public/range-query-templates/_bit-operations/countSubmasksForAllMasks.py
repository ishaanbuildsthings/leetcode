# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/countSubmasksForAllMasks.py

from operator import add

# res[mask] = how many of arr's values are submasks of mask (v & mask == v), for every mask below 2^B
# B = number of bits in max(arr), so res has 2^B entries (about 2 * max(arr)); values must be >= 0
# countSubmasksForAllMasks([1, 2, 3]) -> [0, 1, 1, 3]   # res[3] = 3: 1, 2 and 3 all fit inside 3
# O(B * 2^B + N)
def countSubmasksForAllMasks(arr):
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
    for v in arr:
        if v < 0:
            raise ValueError(f"countSubmasksForAllMasks: {v} is negative")
    n = 1 << max(arr, default=0).bit_length()
    res = [0] * n
    for v in arr:
        res[v] += 1
    for lo, hi in bitPairs(n):
        res[hi] = map(add, res[hi], res[lo])
    return res
