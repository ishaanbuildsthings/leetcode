# https://leetcode.com/problems/sliding-window-median/description/
# difficulty: hard
# tags: avl tree, heap

# Problem
# The median is the middle value in an ordered integer list. If the size of the list is even, there is no middle value. So the median is the mean of the two middle values.

# For examples, if arr = [2,3,4], the median is 3.
# For examples, if arr = [1,2,3,4], the median is (2 + 3) / 2 = 2.5.
# You are given an integer array nums and an integer k. There is a sliding window of size k which is moving from the very left of the array to the very right. You can only see the k numbers in the window. Each time the sliding window moves right by one position.

# Return the median array for each window in the original array. Answers within 10-5 of the actual value will be accepted.

# Solution, O(n log n) time, O(k) space, just use a SortedList, but we could do a 2-heap solution as well

from sortedcontainers import SortedList

class Solution:
    def medianSlidingWindow(self, nums: List[int], k: int) -> List[float]:
        avl = SortedList()
        for i in range(k):
            avl.add(nums[i])

        def getMedian():
            middleIndex = len(avl) // 2

            if len(avl) % 2 == 1:
                return avl[middleIndex]

            return (avl[middleIndex] + avl[middleIndex - 1]) / 2

        res = []

        r = k - 1

        while r < len(nums):
            median = getMedian()
            res.append(median)
            lostNum = nums[r - k + 1]
            avl.remove(lostNum)
            if r == len(nums) - 1:
                break
            newNum = nums[r + 1]
            avl.add(newNum)
            r += 1
        return res

