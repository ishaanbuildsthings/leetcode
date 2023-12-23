# https://leetcode.com/problems/rearrange-array-elements-by-sign/
# difficulty: medium

# Problem
# You are given a 0-indexed integer array nums of even length consisting of an equal number of positive and negative integers.

# You should rearrange the elements of nums such that the modified array follows the given conditions:

# Every consecutive pair of integers have opposite signs.
# For all integers with the same sign, the order in which they were present in nums is preserved.
# The rearranged array begins with a positive integer.
# Return the modified array after rearranging the elements to satisfy the aforementioned conditions.

# Solution, O(n) time and space
# You can do it in onw array and place pos/neg at the beginning and end, but it doesn't really do anything better

class Solution:
    def rearrangeArray(self, nums: List[int]) -> List[int]:
        pos = []
        neg = []
        for num in nums:
            if num > 0:
                pos.append(num)
            else:
                neg.append(num)
        res = []
        for i in range(len(nums)):
            posNumbersPlacedSoFar = int(i / 2)
            # even numbers go in even indices
            if i % 2 == 0:
                res.append(pos[posNumbersPlacedSoFar])
            else:
                res.append(neg[posNumbersPlacedSoFar])
        return res


