# https://leetcode.com/problems/binary-tree-paths/description/
# Difficulty: Easy
# tags: binary tree

# Problem
# Given the root of a binary tree, return all root-to-leaf paths in any order.

# A leaf is a node with no children.

# Solution, O(n^2) time and space
# DFS, serialize when we reach a leaf

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def binaryTreePaths(self, root: Optional[TreeNode]) -> List[str]:
        res = []
        def dfs(node, pathArr):
            pathArr.append(str(node.val))
            if node.left:
                pathArr.append('->')
                dfs(node.left, pathArr)
                pathArr.pop()
                pathArr.pop()
            if node.right:
                pathArr.append('->')
                dfs(node.right, pathArr)
                pathArr.pop()
                pathArr.pop()
            if not node.left and not node.right:
                res.append(''.join(pathArr))
        dfs(root, [])
        return res