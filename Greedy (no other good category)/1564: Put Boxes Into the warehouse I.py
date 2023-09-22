# https://leetcode.com/problems/put-boxes-into-the-warehouse-i/description/
# Difficulty: Medium
# Tags: Greedy

# Problem
# You are given two arrays of positive integers, boxes and warehouse, representing the heights of some boxes of unit width and the heights of n rooms in a warehouse respectively. The warehouse's rooms are labelled from 0 to n - 1 from left to right where warehouse[i] (0-indexed) is the height of the ith room.

# Boxes are put into the warehouse by the following rules:

# Boxes cannot be stacked.
# You can rearrange the insertion order of the boxes.
# Boxes can only be pushed into the warehouse from left to right only.
# If the height of some room in the warehouse is less than the height of a box, then that box and all other boxes behind it will be stopped before that room.
# Return the maximum number of boxes you can put into the warehouse.

# Solution, O(n log n) time, O(sort) space
# sort the boxes, biggest first. Iterate over each warehouse. Store the biggest box we can, which is one that fits in the warehouse, and is <= the smallest seen warehouse thus far.

class Solution:
    def maxBoxesInWarehouse(self, boxes: List[int], warehouse: List[int]) -> int:
        boxes.sort(reverse=True)
        shortestWarehouseSeen = float('inf')
        i = 0 # box pointer
        res = 0

        # for each warehouse, we will select the largest box that can fit (that is <= shortest warehouse seen)
        for j in range(len(warehouse)):
            shortestWarehouseSeen = min(shortestWarehouseSeen, warehouse[j])
            # increment the box until we're within the height
            while i < len(boxes) and boxes[i] > shortestWarehouseSeen:
                i += 1
            if i == len(boxes):
                return res
            res += 1
            i += 1
        return res