# https://leetcode.com/problems/maximum-number-of-pairs-in-array/description/
# difficulty: easy

# Problem
# You are given a 0-indexed integer array nums. In one operation, you may do the following:

# Choose two integers in nums that are equal.
# Remove both integers from nums, forming a pair.
# The operation is done on nums as many times as possible.

# Return a 0-indexed integer array answer of size 2 where answer[0] is the number of pairs that are formed and answer[1] is the number of leftover integers in nums after doing the operation as many times as possible.

# Solution, O(n) time and space, just use the counts

class Solution:
    def numberOfPairs(self, nums: List[int]) -> List[int]:
        counts = collections.Counter(nums)
        res = [0, 0]
        for key in counts:
            frq = counts[key]
            res[0] += frq // 2
            res[1] += 1 if frq % 2 == 1 else 0
        return res