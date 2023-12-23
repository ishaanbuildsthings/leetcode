# https://leetcode.com/problems/maximum-distance-between-a-pair-of-values/description/
# difficulty: medium
# tags: two pointers

# Problem
# You are given two non-increasing 0-indexed integer arrays nums1​​​​​​ and nums2​​​​​​.

# A pair of indices (i, j), where 0 <= i < nums1.length and 0 <= j < nums2.length, is valid if both i <= j and nums1[i] <= nums2[j]. The distance of the pair is j - i​​​​.

# Return the maximum distance of any valid pair (i, j). If there are no valid pairs, return 0.

# An array arr is non-increasing if arr[i-1] >= arr[i] for every 1 <= i < arr.length.

# Solution, O(n) time O(1) space, due to the sorted property we can just use two pointers

class Solution:
    def maxDistance(self, nums1: List[int], nums2: List[int]) -> int:
        res = 0
        i = 0
        j = 0
        while i < len(nums1):
            while j < len(nums2) and nums2[j] >= nums1[i]:
                res = max(res, j - i + 1)
                j += 1
            i += 1
        return max(0, res - 1)