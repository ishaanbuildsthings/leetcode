# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfPairORsMod.py

# sum over every pair i < j of the OR of arr[i] and arr[j], mod mod values must be >= 0; B = number of bits in max(arr)
# Each bit is counted on its own: a pair has bit b unless neither has it
# sumOfPairORsMod([1, 2, 3], 10**9 + 7) -> 9   # 1|2 + 1|3 + 2|3 = 3 + 3 + 3
# O(N * B)
def sumOfPairORsMod(arr, mod):
    for x in arr:
        if x < 0:
            raise ValueError(f"sumOfPairORsMod: value {x} is negative")
    n = len(arr)
    total = 0
    for b in range(max(arr, default=0).bit_length()):
        zeros = n - sum((x >> b) & 1 for x in arr)
        ways = n * (n - 1) // 2 - zeros * (zeros - 1) // 2
        total = (total + ways % mod * pow(2, b, mod)) % mod
    return total % mod
