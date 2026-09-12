# https://leetcode.com/problems/partition-array-such-that-maximum-difference-is-k/description/
# difficulty: medium

# Problem
# You are given an integer array nums and an integer k. You may partition nums into one or more subsequences such that each element in nums appears in exactly one of the subsequences.

# Return the minimum number of subsequences needed such that the difference between the maximum and minimum values in each subsequence is at most k.

# A subsequence is a sequence that can be derived from another sequence by deleting some or no elements without changing the order of the remaining elements.

# Solution
# We can n log n sort then iterate as needed. We can also do it in O(n) time and space with a hashset (commented out, TLE but I did not investigate)

class Solution:
    def partitionArray(self, nums: List[int], k: int) -> int:
        # numSet = set(nums)
        # numTypes = []
        # for num in range(10**5 + 1):
        #     if num in numSet:
        #         numTypes.append(num)
        # i = 0
        # res = 0
        # while i < len(numTypes):
        #     prevI = i
        #     # could binary search here lol, need to analyze if it is faster or amortized
        #     for j in range(i + 1, len(numTypes)):
        #         if numTypes[j] - numTypes[i] > k:
        #             i = j
        #             res += 1
        #             break
        #     if i == prevI:
        #         i += 1
        # return res + 1
        nums.sort()
        i = 0
        j = 0
        res = 0
        while j < len(nums):
            if nums[j] - nums[i] > k:
                i = j
                res += 1
            j += 1

        return res + 1

