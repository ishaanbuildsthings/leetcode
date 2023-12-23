# https://leetcode.com/problems/sum-of-absolute-differences-in-a-sorted-array/description/?envType=daily-question&envId=2023-11-25
# difficulty: medium
# tags: prefix, postfix

# Problem
# You are given an integer array nums sorted in non-decreasing order.

# Build and return an integer array result with the same length as nums such that result[i] is equal to the summation of absolute differences between nums[i] and all the other elements in the array.

# In other words, result[i] is equal to sum(|nums[i]-nums[j]|) where 0 <= j < nums.length and j != i (0-indexed).

# Solution, easy prefix postfix. Here is a clean O(n) time and O(1) space:
# Solution 2 below, a messier O(1) space where I reuse the output array
class Solution:
    def getSumAbsoluteDifferences(self, nums: List[int]) -> List[int]:
        postfixSum = sum(nums)
        result = []
        prefixSum = 0
        for i in range(len(nums)):
            postfixSum -= nums[i]
            leftContribution = (nums[i] * i) - prefixSum
            rightContribution = (postfixSum) - (nums[i] * (len(nums) - i - 1))
            prefixSum += nums[i]
            result.append(leftContribution + rightContribution)
        return result


# Solution 2
class Solution:
    def getSumAbsoluteDifferences(self, nums: List[int]) -> List[int]:
        res = [0] * len(nums)

        runningSum = 0
        for i in range(len(nums) -1, -1, -1):
            runningSum += nums[i]
            res[i] = runningSum

        prefix = 0

        for i in range(len(nums)):
            absDiffLeft = (nums[i] * i) - prefix

            totalSumRight = res[i + 1] if i < len(nums) - 1 else 0
            absDiffRight = totalSumRight - (nums[i] * (len(nums) - i - 1))

            res[i] = absDiffLeft + absDiffRight

            prefix += nums[i]

        return res

