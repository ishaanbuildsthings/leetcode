# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfPairORs.py

# sum over every pair i < j of the OR of arr[i] and arr[j] (exact) values must be >= 0; B = number of bits in max(arr)
# Each bit is counted on its own: a pair has bit b unless neither has it
# sumOfPairORs([1, 2, 3]) -> 9   # 1|2 + 1|3 + 2|3 = 3 + 3 + 3
# O(N * B)
def sumOfPairORs(arr):
    for x in arr:
        if x < 0:
            raise ValueError(f"sumOfPairORs: value {x} is negative")
    n = len(arr)
    total = 0
    for b in range(max(arr, default=0).bit_length()):
        zeros = n - sum((x >> b) & 1 for x in arr)
        ways = n * (n - 1) // 2 - zeros * (zeros - 1) // 2
        total += ways << b
    return total
