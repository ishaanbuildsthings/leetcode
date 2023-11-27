# https://leetcode.com/problems/diagonal-traverse-ii/description/?envType=daily-question&envId=2023-11-22
# difficulty: medium
# tags: bfs

# Problem
# Given a 2D integer array nums, return all elements of nums in diagonal order as shown in the below images.

# Solution, O(total elements) time, O(longest diagonal) space
# I did a BFS always going right first if I can. I think if we visualize the diagonals as parts of certain groups there are simpler solutions.

class Solution:
    def findDiagonalOrder(self, nums: List[List[int]]) -> List[int]:
        height = len(nums)

        q = collections.deque() # holds (r, c)
        q.append((0, 0))
        seen = set()
        seen.add((0, 0))

        res = []

        DIFFS = [ [1, 0], [0, 1] ]

        while q:
            length = len(q)
            for _ in range(length):
                popped = q.popleft()
                r, c = popped
                res.append(nums[r][c])
                for rowDiff, colDiff in DIFFS:
                    newRow = r + rowDiff
                    newCol = c + colDiff
                    # skip seen cells
                    if (newRow, newCol) in seen:
                        continue
                    # skip out of bounds
                    if newRow == height:
                        continue
                    bucket = nums[newRow]
                    if len(bucket) <= newCol:
                        continue
                    seen.add((newRow, newCol))
                    q.append((newRow, newCol))
        return res

