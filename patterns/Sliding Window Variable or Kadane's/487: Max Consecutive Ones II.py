# https://leetcode.com/problems/max-consecutive-ones-ii/description/
# difficulty: medium
# tags: sliding window variable

# Problem
# Given a binary array nums, return the maximum number of consecutive 1's in the array if you can flip at most one 0.
# We can speed it up to a one pass by storing the index of the 0, to "teleport" the left pointer instead of incrementing it one by one

# Solution, normal sliding window, O(n) time O(1) space, I solved this in like 20 seconds!

class Solution:
    def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
        l = 0
        r = 0
        res = 0
        used = 0
        while r < len(nums):
            newChar = nums[r]
            used += newChar == 0
            while used > 1:
                lostChar = nums[l]
                used -= lostChar == 0
                l += 1
            res = max(res, r - l + 1)
            r += 1
        return res
