# https://leetcode.com/problems/maximum-difference-between-node-and-ancestor/?envType=daily-question&envId=2024-01-11
# difficulty: medium
# tags: trees

# Problem
# Given the root of a binary tree, find the maximum value v for which there exist different nodes a and b where v = |a.val - b.val| and a is an ancestor of b.

# A node a is an ancestor of b if either: any child of a is equal to b or any child of a is an ancestor of b.

# Solution
# Standard tree solution

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def maxAncestorDiff(self, root: Optional[TreeNode]) -> int:
        res = 0
        def dfs(node):
            nonlocal res

            smallestChild = node.val
            largestChild = node.val

            if node.left:
                smallestLeft, largestLeft = dfs(node.left)
                smallestChild = min(smallestChild, smallestLeft)
                largestChild = max(largestChild, largestLeft)
            if node.right:
                smallestRight, largestRight = dfs(node.right)
                smallestChild = min(smallestChild, smallestRight)
                largestChild = max(largestChild, largestRight)

            res = max(res, abs(node.val - smallestChild), abs(node.val - largestChild))

            newSmallest = min(smallestChild, node.val)
            newLargest = max(largestChild, node.val)

            return newSmallest, newLargest

        dfs(root)
        return res