# https://leetcode.com/problems/binary-tree-pruning/description/
# difficulty: medium
# tags: binary tree

# Problem
# Given the root of a binary tree, return the same tree where every subtree (of the given tree) not containing a 1 has been removed.

# A subtree of a node node is node plus every node that is a descendant of node.

# Solution, O(n) time and O(height) space, dfs down, send up if we have seen a 1, and prune as needed

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def pruneTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        dummy = TreeNode(None)
        dummy.left = root

        def dfs(node):
            # base case
            if not node:
                return False

            hasLeftSeenOne = dfs(node.left)
            if not hasLeftSeenOne:
                node.left = None
            hasRightSeenOne = dfs(node.right)
            if not hasRightSeenOne:
                node.right = None

            hasNodeSeenOne = node.val == 1 or hasLeftSeenOne or hasRightSeenOne
            return hasNodeSeenOne

        dfs(dummy)
        return dummy.left
