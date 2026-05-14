# https://leetcode.com/problems/check-if-array-pairs-are-divisible-by-k/description/
# difficulty: medium
# tags: functional

# Problem
# Given an array of integers arr of even length n and an integer k.

# We want to divide the array into exactly n / 2 pairs such that the sum of each pair is divisible by k.

# Return true If you can find a way to do that or false otherwise.

# Solution, O(n) time and space
class Solution:
    def canArrange(self, arr: List[int], k: int) -> bool:
        modCounts = Counter(num % k for num in arr)
        return all(
            modCounts[key] == modCounts[k - key] if key != 0
            else modCounts[0] % 2 == 0
            for key in modCounts)