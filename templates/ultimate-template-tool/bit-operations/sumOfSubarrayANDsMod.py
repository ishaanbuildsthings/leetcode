# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfSubarrayANDsMod.py

from itertools import groupby

# sum over every non-empty subarray of the AND of all its values, mod mod values must be >= 0; B = number of bits in
# max(arr)
# Each bit is counted on its own: a subarray has bit b exactly when it sits inside a run of values that all have bit b
# sumOfSubarrayANDsMod([1, 2, 3], 10**9 + 7) -> 8   # [1] [2] [3] [1,2] [2,3] [1,2,3] -> 1 + 2 + 3 + 0 + 2 + 0
# O(N * B)
def sumOfSubarrayANDsMod(arr, mod):
    for x in arr:
        if x < 0:
            raise ValueError(f"sumOfSubarrayANDsMod: value {x} is negative")
    total = 0
    for b in range(max(arr, default=0).bit_length()):
        ways = 0
        for has, run in groupby((x >> b) & 1 for x in arr):
            if has:
                length = sum(1 for _ in run)
                ways += length * (length + 1) // 2
        total = (total + ways % mod * pow(2, b, mod)) % mod
    return total % mod
