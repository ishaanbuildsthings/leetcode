# https://leetcode.com/problems/the-number-of-beautiful-subsets/description/
# difficulty: medium
# tags: backtracking

# Problem
# You are given an array nums of positive integers and a positive integer k.

# A subset of nums is beautiful if it does not contain two integers with an absolute difference equal to k.

# Return the number of non-empty beautiful subsets of the array nums.

# A subset of nums is an array that can be obtained by deleting some (possibly none) elements from nums. Two subsets are different if and only if the chosen indices to delete are different.

# Solution
# standard backtracking

class Solution:
    def beautifulSubsets(self, nums: List[int], k: int) -> int:
        res = 0
        def backtrack(i, curr):
            nonlocal res

            # base
            if i == len(nums):
                res += 1
                return

            # if we skip the current number
            backtrack(i + 1, curr)

            # if we take it
            if not curr[nums[i] - k] and not curr[nums[i] + k]:
                curr[nums[i]] += 1
                backtrack(i + 1, curr)
                curr[nums[i]] -= 1

        backtrack(0, defaultdict(int))
        return res - 1 # empty set


