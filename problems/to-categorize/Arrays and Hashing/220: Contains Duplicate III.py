# https://leetcode.com/problems/contains-duplicate-iii/
# difficulty: hard
# tags: avl tree

# Problem
# You are given an integer array nums and two integers indexDiff and valueDiff.

# Find a pair of indices (i, j) such that:

# i != j,
# abs(i - j) <= indexDiff.
# abs(nums[i] - nums[j]) <= valueDiff, and
# Return true if such pair exists or false otherwise.

# Solution, O(n log n) time, O(n) space
# Use a SortedList. For each number, find the closest numbers next to it.

from sortedcontainers import SortedList

class Solution:
    def containsNearbyAlmostDuplicate(self, nums: List[int], indexDiff: int, valueDiff: int) -> bool:
        tups = {} # maps an index to the relevant tuple so we can quickly discard it
        # AVL stores [value, i]
        AVL = SortedList(key=lambda x: (x[0])) # sort ONLY by value
        for i in range(min(indexDiff + 1, len(nums))):
            tup = [nums[i], i]
            AVL.add(tup)
            tups[i] = tup
        for i in range(len(nums)):
            ourTup = tups[i]
            AVL.remove(ourTup)
            idx = AVL.bisect_right([nums[i], None]) # I think the second value isn't conisidered because of how we declared the AVL
            left = idx - 1
            right = idx
            if left >= 0:
                leftVal = AVL[left][0]
                if abs(nums[i] - leftVal) <= valueDiff:
                    return True
            if right < len(AVL):
                rightVal = AVL[right][0]
                if abs(nums[i] - rightVal) <= valueDiff:
                    return True

            AVL.add(ourTup)
            right = i + indexDiff + 1 # the element we add
            if right < len(nums):
                rightTup = [nums[right], right]
                AVL.add(rightTup)
                tups[right] = rightTup
            left = i - indexDiff # the element we lose
            if left >= 0:
                leftTup = tups[left]
                AVL.remove(leftTup)
                del tups[left]

        return False
