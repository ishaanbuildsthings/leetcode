# https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/
# Difficulty: Medium
# Tags: lca

# Problem
# Given a binary tree, find the lowest common ancestor (LCA) of two given nodes in the tree.

# According to the definition of LCA on Wikipedia: “The lowest common ancestor is defined between two nodes p and q as the lowest node in T that has both p and q as descendants (where we allow a node to be a descendant of itself).”

# Solution, O(n) time and O(height) space, dfs down, return up which numbers we have seen, or the LCA

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        # we need to bubble to the bottom of our tree, then return up. we should carry information about if we have seen p or q. if at a node we have seen both p and q, we now just carry the LCA
        def dfs(node):
            # base case
            if not node:
                return [False, False]

            leftRes = dfs(node.left)
            rightRes = dfs(node.right)

            # if the leftRes is just the LCA, forward it
            if isinstance(leftRes, TreeNode):
                return leftRes
            # forward right
            if isinstance(rightRes, TreeNode):
                return rightRes
            seenP = leftRes[0] or rightRes[0] or node.val == p.val
            seenQ = leftRes[1] or rightRes[1] or node.val == q.val
            if seenP and seenQ:
                return node
            else:
                return [seenP, seenQ]

        return dfs(root)


