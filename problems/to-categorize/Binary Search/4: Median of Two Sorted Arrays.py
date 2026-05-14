# https://leetcode.com/problems/median-of-two-sorted-arrays/
# Difficulty: Hard
# Tags: binary search

# Problem
# Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.

# The overall run time complexity should be O(log (m+n)).

# Solution
# O(log(min(n,m))) time (if we binary search on the shorter array), O(1) space
# We can binary search on one array for the amount of elements to include in the left. We compute the amount of elements to include for the second array as a result. We check if the ends of the left regions are smaller than the beginnings of the right regions, otherwise we adjust.

class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        # if odd amount of elements, left region should have (n-1)/2 + 1 elements, otherwise n/2
        if (len(nums1) + len(nums2)) % 2 == 0:
            leftRegionAmount = (len(nums1) + len(nums2)) / 2
            medianType = 'even'
        else:
            leftRegionAmount = (len(nums1) + len(nums2) - 1)/2 + 1
            medianType = 'odd'
        leftRegionAmount = int(leftRegionAmount)

        l = max(0, leftRegionAmount - len(nums2)) # in the worst case, if we include every element from nums2 in the left region, we still might need to include some from nums1
        r = min(leftRegionAmount, len(nums1))

        # do a binary search on nums 1 to determine some left region, the remaining elements will be pulled from nums2, m is the value such that we include all values to the left of m
        while l <= r:
            m = int((r + l) // 2)
            # amount of elements for the left region
            amountOfElementsInNums1 = m
            amountOfElementsInNums2 = leftRegionAmount - m
            endingRegion1 = nums1[amountOfElementsInNums1 - 1] if amountOfElementsInNums1 > 0 else float('-inf')
            endingRegion2 = nums2[amountOfElementsInNums2 - 1] if amountOfElementsInNums2 > 0 else float('-inf')
            nextRegion1 = nums1[amountOfElementsInNums1] if amountOfElementsInNums1 < len(nums1) else float('inf')
            nextRegion2 = nums2[amountOfElementsInNums2] if amountOfElementsInNums2 < len(nums2) else float('inf')

            if endingRegion1 <= nextRegion2 and endingRegion2 <= nextRegion1:
                if medianType ==  'even':
                    biggest = max(endingRegion1, endingRegion2)
                    smallest = min(nextRegion1, nextRegion2)
                    return (biggest + smallest) / 2
                return max(endingRegion1, endingRegion2)

            # if we are too big in nums1, we need to shift to the left
            if endingRegion1 > nextRegion2:
                r = m - 1
            else:
                l = m + 1
        return r

