# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfSubarrayORs.py

from itertools import groupby

# sum over every non-empty subarray of the OR of all its values (exact) values must be >= 0; B = number of bits in
# max(arr)
# Each bit is counted on its own: a subarray has bit b unless it sits inside a run of values that all lack bit b
# sumOfSubarrayORs([1, 2, 3]) -> 15   # [1] [2] [3] [1,2] [2,3] [1,2,3] -> 1 + 2 + 3 + 3 + 3 + 3
# O(N * B)
def sumOfSubarrayORs(arr):
    for x in arr:
        if x < 0:
            raise ValueError(f"sumOfSubarrayORs: value {x} is negative")
    n = len(arr)
    total = 0
    for b in range(max(arr, default=0).bit_length()):
        ways = n * (n + 1) // 2
        for has, run in groupby((x >> b) & 1 for x in arr):
            if not has:
                length = sum(1 for _ in run)
                ways -= length * (length + 1) // 2
        total += ways << b
    return total
