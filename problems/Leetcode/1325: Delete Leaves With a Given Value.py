# https://leetcode.com/problems/delete-leaves-with-a-given-value/
# difficulty: medium
# tags: binary tree

# Problem
# Given a binary tree root and an integer target, delete all the leaf nodes with value target.

# Note that once you delete a leaf node with value target, if its parent node becomes a leaf node and has the value target, it should also be deleted (you need to continue doing that until you cannot).

# Solution, O(n) time, O(height) space, standard dfs

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def removeLeafNodes(self, root: Optional[TreeNode], target: int) -> Optional[TreeNode]:
        # tells us if the entire subtree is all the target value
        def dfs(node):
            # base cases
            if not node:
                return True
            if not node.left and not node.right:
                return node.val == target

            allFromLeft = dfs(node.left)
            allFromRight = dfs(node.right)
            if allFromLeft:
                node.left = None
            if allFromRight:
                node.right = None
            if allFromLeft and allFromRight and node.val == target:
                return True
            return False

        dummy = TreeNode(None)
        dummy.left = root
        dfs(dummy)
        return dummy.left