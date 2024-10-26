# https://leetcode.com/problems/max-consecutive-ones-iii/description/
# difficulty: medium
# tags: sliding window variable

# Problem
# Given a binary array nums and an integer k, return the maximum number of consecutive 1's in the array if you can flip at most k 0's.

# Solution, O(n) time and O(1) space, simiarly we can get a speedup by not incrementing l but by remembering the k 0s and "teleporting" the left index as needed.

class Solution:
    def longestOnes(self, nums: List[int], k: int) -> int:
        l = 0
        r = 0
        res = 0
        used = 0
        while r < len(nums):
            newChar = nums[r]
            used += newChar == 0
            while used > k:
                lostChar = nums[l]
                used -= lostChar == 0
                l += 1
            res = max(res, r - l + 1)
            r += 1
        return res
