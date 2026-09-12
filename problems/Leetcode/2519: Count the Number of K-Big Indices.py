# https://leetcode.com/problems/count-the-number-of-k-big-indices/description/
# difficulty: hard
# tags: avl tree, segment tree

# Problem
# You are given a 0-indexed integer array nums and a positive integer k.

# We call an index i k-big if the following conditions are satisfied:

# There exist at least k different indices idx1 such that idx1 < i and nums[idx1] < nums[i].
# There exist at least k different indices idx2 such that idx2 > i and nums[idx2] < nums[i].
# Return the number of k-big indices.

# Solution, O(n log n) time, O(n) space
# Maintain two SortedLists, range query as needed on them
# SOLUTION 2, we can also use a segment tree on the values, I have code in my segment tree templates folder for this problem

from sortedcontainers import SortedList

class Solution:
    def kBigIndices(self, nums: List[int], k: int) -> int:
        avlLeft = SortedList()
        avlRight = SortedList(nums)

        res = 0
        for i in range(len(nums)):
            num = nums[i]
            avlRight.remove(num)
            if i > 0:
                avlLeft.add(nums[i - 1])

            rightIdx = avlRight.bisect_left(num) # help find the # of elements in avlRight that are smaller than num
            leftIdx = avlLeft.bisect_left(num)
            if rightIdx >= k and leftIdx >= k:
                res += 1

        return res

