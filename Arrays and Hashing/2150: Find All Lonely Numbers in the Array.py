# https://leetcode.com/problems/find-all-lonely-numbers-in-the-array/
# Difficulty: Medium

# Problem
# You are given an integer array nums. A number x is lonely when it appears only once, and no adjacent numbers (i.e. x + 1 and x - 1) appear in the array.

# Return all lonely numbers in nums. You may return the answer in any order.

# Solution, O(n) time and space, get the counts and also check prior and after numbers

class Solution:
    def findLonely(self, nums: List[int]) -> List[int]:
        counts = collections.Counter(nums)
        res = []
        for num in counts.keys():
            if counts[num] > 1:
                continue
            if num - 1 in counts or num + 1 in counts:
                continue
            res.append(num)
        return res