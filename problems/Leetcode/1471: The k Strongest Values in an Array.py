# https://leetcode.com/problems/the-k-strongest-values-in-an-array/description/
# difficulty: medium
# tags: two pointers, quickselect

# Problem
# Given an array of integers arr and an integer k.

# A value arr[i] is said to be stronger than a value arr[j] if |arr[i] - m| > |arr[j] - m| where m is the median of the array.
# If |arr[i] - m| == |arr[j] - m|, then arr[i] is said to be stronger than arr[j] if arr[i] > arr[j].

# Return a list of the strongest k values in the array. return the answer in any arbitrary order.

# Median is the middle value in an ordered integer list. More formally, if the length of the list is n, the median is the element in position ((n - 1) / 2) in the sorted list (0-indexed).

# For arr = [6, -3, 7, 2, 11], n = 5 and the median is obtained by sorting the array arr = [-3, 2, 6, 7, 11] and the median is arr[m] where m = ((5 - 1) / 2) = 2. The median is 6.
# For arr = [-7, 22, 17, 3], n = 4 and the median is obtained by sorting the array arr = [-7, 3, 17, 22] and the median is arr[m] where m = ((4 - 1) / 2) = 1. The median is 3.

# Solution, O(n log n) time, O(sort) space, there's better solutions, I just wrote what first came to mind. There is even a linear! See solutions tab.

class Solution:
    def getStrongest(self, arr: List[int], k: int) -> List[int]:
        arr.sort()
        if len(arr) % 2 == 1:
            midpoint = len(arr) // 2
            median = arr[midpoint]
        else:
            leftMidpoint = int((len(arr) / 2) - 1)
            median = arr[leftMidpoint] # bad question

        res = []
        l = 0
        r = len(arr) - 1
        for _ in range(k):
            leftDistance = abs(arr[l] - median)
            rightDistance = abs(arr[r] - median)
            if leftDistance > rightDistance:
                res.append(arr[l])
                l += 1
            else:
                res.append(arr[r])
                r -= 1
        return res