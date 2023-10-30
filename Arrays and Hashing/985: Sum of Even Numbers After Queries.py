# https://leetcode.com/problems/sum-of-even-numbers-after-queries/description/
# difficulty: medium

# Problem
# You are given an integer array nums and an array queries where queries[i] = [vali, indexi].

# For each query i, first, apply nums[indexi] = nums[indexi] + vali, then print the sum of the even values of nums.

# Return an integer array answer where answer[i] is the answer to the ith query.


# Solution, O(n + queries) time, O(1) space, just maintain the even sum

class Solution:
    def sumEvenAfterQueries(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        evenSum = 0
        for num in nums:
            if num % 2 == 0:
                evenSum += num
        res = []
        for val, index in queries:
            oldValWasEven = nums[index] % 2 == 0
            oldVal = nums[index]
            nums[index] += val
            if oldValWasEven:
                evenSum -= oldVal
            if nums[index] % 2 == 0:
                evenSum += nums[index]
            res.append(evenSum)

        return res
