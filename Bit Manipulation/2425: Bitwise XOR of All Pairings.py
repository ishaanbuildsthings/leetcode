# https://leetcode.com/problems/bitwise-xor-of-all-pairings/description/
# difficulty: medium
# tags: bit manipulation

# problem
# You are given two 0-indexed arrays, nums1 and nums2, consisting of non-negative integers. There exists another array, nums3, which contains the bitwise XOR of all pairings of integers between nums1 and nums2 (every integer in nums1 is paired with every integer in nums2 exactly once).

# Return the bitwise XOR of all integers in nums3.

# Solution, O(n + m) time, O(1) space, just bit XOR if needed, they cancel out

class Solution:
    def xorAllNums(self, nums1: List[int], nums2: List[int]) -> int:
        res = 0
        if len(nums2) % 2 == 1:
            for num in nums1:
                res = res ^ num
        if len(nums1) % 2 == 1:
            for num in nums2:
                res = res ^ num
        return res


