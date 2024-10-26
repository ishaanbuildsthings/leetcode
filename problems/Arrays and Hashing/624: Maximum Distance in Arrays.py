# https://leetcode.com/problems/maximum-distance-in-arrays/description/
# difficulty: medium

# Problem
# You are given m arrays, where each array is sorted in ascending order.

# You can pick up two integers from two different arrays (each array picks one) and calculate the distance. We define the distance between two integers a and b to be their absolute difference |a - b|.

# Return the maximum distance.

# Solution, O(n * m) time, O(1) space, for each array we compare each number to previous mins and maxes, and update accordingly.

class Solution:
    def maxDistance(self, arrays: List[List[int]]) -> int:
        smallest = float('inf')
        largest = float('-inf')
        res = float('-inf')
        for arr in arrays:
            localSmallest = min(arr)
            localLargest = max(arr)
            bestIfLargestHere = localLargest - smallest
            bestIfSmallestHere = largest - localSmallest
            res = max(res, bestIfLargestHere, bestIfSmallestHere)
            smallest = min(smallest, localSmallest)
            largest = max(largest, localLargest)
        return res