# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfSubarrayXORs.py

# sum over every non-empty subarray of the XOR of all its values (exact) values must be >= 0; B = number of bits in
# max(arr)
# Each bit is counted on its own: a subarray has bit b exactly when the prefix XORs at its two ends differ in bit b
# sumOfSubarrayXORs([1, 2, 3]) -> 10   # [1] [2] [3] [1,2] [2,3] [1,2,3] -> 1 + 2 + 3 + 3 + 1 + 0
# O(N * B)
def sumOfSubarrayXORs(arr):
    for x in arr:
        if x < 0:
            raise ValueError(f"sumOfSubarrayXORs: value {x} is negative")
    n = len(arr)
    prefix = [0]
    for x in arr:
        prefix.append(prefix[-1] ^ x)
    total = 0
    for b in range(max(arr, default=0).bit_length()):
        ones = sum((p >> b) & 1 for p in prefix)
        ways = ones * (n + 1 - ones)
        total += ways << b
    return total
