# https://leetcode.com/problems/maximum-sum-of-distinct-subarrays-with-length-k/description/
# difficulty: medium
# tags: sliding window fixed

# Problem
# You are given an integer array nums and an integer k. Find the maximum subarray sum of all the subarrays of nums that meet the following conditions:

# The length of the subarray is k, and
# All the elements of the subarray are distinct.
# Return the maximum subarray sum of all the subarrays that meet the conditions. If no subarray meets the conditions, return 0.

# A subarray is a contiguous non-empty sequence of elements within an array.

# Solution, O(n) time and O(k) space, standard fixed sliding window

class Solution:
    def maximumSubarraySum(self, nums: List[int], k: int) -> int:
        frqs = Counter(nums[:k])
        l = 0
        r = k - 1
        running = sum(nums[:k])

        res = (
            0 if len(frqs) != k else
            running
        )

        while r < len(nums) - 1:
            r += 1
            gained = nums[r]
            lost = nums[l]
            frqs[gained] += 1
            frqs[lost] -= 1
            if frqs[lost] == 0:
                del frqs[lost]
            running += (gained - lost)
            if len(frqs) == k:
                res = max(res, running)
            l += 1

        return res