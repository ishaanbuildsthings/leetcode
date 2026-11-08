# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/sumOfPairAndsMod.py

# sum over every pair i < j of the AND of arr[i] and arr[j], mod mod
# values must be >= 0; B = number of bits in max(arr)
# Each bit is counted on its own: a pair has bit b exactly when both have it
# sumOfPairAndsMod([1, 2, 3], 10**9 + 7) -> 3   # 1&2 + 1&3 + 2&3 = 0 + 1 + 2
# O(N * B)
def sumOfPairAndsMod(arr, mod):
    for x in arr:
        if x < 0:
            raise ValueError(f"sumOfPairAndsMod: value {x} is negative")
    total = 0
    for b in range(max(arr, default=0).bit_length()):
        ones = sum((x >> b) & 1 for x in arr)
        ways = ones * (ones - 1) // 2
        total = (total + ways % mod * pow(2, b, mod)) % mod
    return total % mod
