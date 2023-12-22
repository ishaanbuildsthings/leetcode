# https://leetcode.com/problems/minimum-limit-of-balls-in-a-bag/
# difficulty: medium
# tags: binary search

# Problem
# You are given an integer array nums where the ith bag contains nums[i] balls. You are also given an integer maxOperations.

# You can perform the following operation at most maxOperations times:

# Take any bag of balls and divide it into two new bags with a positive number of balls.
# For example, a bag of 5 balls can become two new bags of 1 and 4 balls, or two new bags of 2 and 3 balls.
# Your penalty is the maximum number of balls in a bag. You want to minimize your penalty after the operations.

# Return the minimum possible penalty after performing the operations.

# Solution, O(n * log*max(nums)) time and O(1) space, binary search on the penalty and see if it is doable, to split a bag into multiple under a certain size, there's no efficiency by splitting in half over and over, or anything like that

class Solution:
    def minimumSize(self, nums: List[int], maxOperations: int) -> int:
        def isPenaltyDoable(penalty):
            opsUsed = 0
            for bag in nums:
                if bag / penalty == bag // penalty:
                    opsUsed += (bag / penalty) - 1
                    continue
                opsUsed += bag // penalty
                # prune
                if opsUsed > maxOperations:
                    return False
            return opsUsed <= maxOperations

        # 9 -> 2 ops

        # 6|3
        # 3|3


        # 4|5
        # 4|2|3


        # 1 2 | 3 4 | 5 6 | 7 8
        l = 1
        r = max(nums)
        while l <= r:
            m = (r + l) // 2 # m is the max penalty we will validate
            isDoable = isPenaltyDoable(m)
            if isDoable:
                r = m - 1
            else:
                l = m + 1
        return r + 1

