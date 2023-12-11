# https://leetcode.com/problems/binary-tree-tilt/description/
# difficulty: easy
# tags: binary tree

# Problem
# Given the root of a binary tree, return the sum of every tree node's tilt.

# The tilt of a tree node is the absolute difference between the sum of all left subtree node values and all right subtree node values. If a node does not have a left child, then the sum of the left subtree node values is treated as 0. The rule is similar if the node does not have a right child.

# Solution, O(n) time O(height) space
# There is probably a cool math way to do this where we assess how many right and left parents we have, but this is just faster and easier and same complexities.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def findTilt(self, root: Optional[TreeNode]) -> int:
        res = 0
        def dfs(node):
            nonlocal res

            # base case
            if not node:
                return 0 # returns sum

            leftSum = dfs(node.left)
            rightSum = dfs(node.right)
            diff = abs(leftSum - rightSum)
            res += diff
            return leftSum + rightSum + node.val

        dfs(root)
        return res
