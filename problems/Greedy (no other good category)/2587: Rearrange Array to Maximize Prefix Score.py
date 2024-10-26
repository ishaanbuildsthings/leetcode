# https://leetcode.com/problems/rearrange-array-to-maximize-prefix-score/
# difficulty: medium
# tags: greedy

# Problem
# You are given a 0-indexed integer array nums. You can rearrange the elements of nums to any order (including the given order).

# Let prefix be the array containing the prefix sums of nums after rearranging it. In other words, prefix[i] is the sum of the elements from 0 to i in nums after rearranging it. The score of nums is the number of positive integers in the array prefix.

# Return the maximum score you can achieve.

# Solution, sort then iterate, O(n log n) time, O(sort space)

class Solution:
    def maxScore(self, nums: List[int]) -> int:
        nums.sort(reverse=True)
        running = 0
        res = 0
        for num in nums:
            running += num
            if running > 0:
                res += 1
            else:
                return res
        return res