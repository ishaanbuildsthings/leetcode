# https://leetcode.com/problems/average-of-levels-in-binary-tree/description/
# difficulty: easy
# tags: binary tree, bfs

# Problem
# Given the root of a binary tree, return the average value of the nodes on each level in the form of an array. Answers within 10-5 of the actual answer will be accepted.

# Solution, just bfs, O(n) time and space

# Problem

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def averageOfLevels(self, root: Optional[TreeNode]) -> List[float]:
        q = collections.deque()
        q.append(root)

        res = []

        while q:
            length = len(q)
            total = 0
            for _ in range(length):
                popped = q.popleft()
                total += popped.val
                if popped.left:
                    q.append(popped.left)
                if popped.right:
                    q.append(popped.right)
            res.append(total / length)

        return res