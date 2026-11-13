# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfPairXORs.py

# sum over every pair i < j of the XOR of arr[i] and arr[j] (exact) values must be >= 0; B = number of bits in max(arr)
# Each bit is counted on its own: a pair has bit b exactly when one of the two has it
# sumOfPairXORs([1, 2, 3]) -> 6   # 1^2 + 1^3 + 2^3 = 3 + 2 + 1
# O(N * B)
def sumOfPairXORs(arr):
    for x in arr:
        if x < 0:
            raise ValueError(f"sumOfPairXORs: value {x} is negative")
    n = len(arr)
    total = 0
    for b in range(max(arr, default=0).bit_length()):
        ones = sum((x >> b) & 1 for x in arr)
        ways = ones * (n - ones)
        total += ways << b
    return total
