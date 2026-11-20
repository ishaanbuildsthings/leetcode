# https://leetcode.com/problems/longest-square-streak-in-an-array/
# difficulty: medium
# tags: graphs

# Problem
# You are given an integer array nums. A subsequence of nums is called a square streak if:

# The length of the subsequence is at least 2, and
# after sorting the subsequence, each element (except the first element) is the square of the previous number.
# Return the length of the longest square streak in nums, or return -1 if there is no square streak.

# A subsequence is an array that can be derived from another array by deleting some or no elements without changing the order of the remaining elements.

# Solution
# We basically get chains, O(n) time and space, just test each chain, run time is same but I think caching should improve it?

class Solution:
    def longestSquareStreak(self, nums: List[int]) -> int:
        numSet = set(nums)
        seen = set()

        def recurse(num):
            seen.add(num)
            if num * num in numSet:
                return 1 + recurse(num * num)
            return 1


        res = -1
        for num in nums:
            if num in seen:
                continue
            ifStartAtThisNum = recurse(num)
            res = max(res, ifStartAtThisNum)
        return res if res >= 2 else -1


