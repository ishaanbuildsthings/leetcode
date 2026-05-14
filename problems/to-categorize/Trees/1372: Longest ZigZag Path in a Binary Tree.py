# https://leetcode.com/problems/longest-zigzag-path-in-a-binary-tree/description/
# difficulty: medium
# tags: binary tree, postorder traversal

# Problem
# You are given the root of a binary tree.

# A ZigZag path for a binary tree is defined as follow:

# Choose any node in the binary tree and a direction (right or left).
# If the current direction is right, move to the right child of the current node; otherwise, move to the left child.
# Change the direction from right to left or from left to right.
# Repeat the second and third steps until you can't move in the tree.
# Zigzag length is defined as the number of nodes visited - 1. (A single node has a length of 0).

# Return the longest ZigZag path contained in that tree.

# Solution, O(n) time and O(height) space, standard dfs

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def longestZigZag(self, root: Optional[TreeNode]) -> int:
        res = 1
        def dfs(node):
            nonlocal res
            if not node:
                return [0, 0]
            longestPathIfLeftChildGoesRight = dfs(node.left)[1]
            longestPathIfRightChildGoesLeft = dfs(node.right)[0]
            rootLongestIfGoLeft = 1 + longestPathIfLeftChildGoesRight
            rootLongestIfGoRight = 1 + longestPathIfRightChildGoesLeft
            res = max(res, rootLongestIfGoLeft, rootLongestIfGoRight)
            return [rootLongestIfGoLeft, rootLongestIfGoRight]
        dfs(root)
        return res - 1