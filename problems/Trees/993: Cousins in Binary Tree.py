# https://leetcode.com/problems/cousins-in-binary-tree/
# difficulty: easy
# tags: binary tree

# Problem
# Given the root of a binary tree with unique values and the values of two different nodes of the tree x and y, return true if the nodes corresponding to the values x and y in the tree are cousins, or false otherwise.

# Two nodes of a binary tree are cousins if they have the same depth with different parents.

# Note that in a binary tree, the root node is at the depth 0, and children of each depth k node are at the depth k + 1.

# Solution, O(n) time and O(height) space, recurse and check. Added some pruning stuff.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isCousins(self, root: Optional[TreeNode], x: int, y: int) -> bool:
        xParent = None
        xDepth = None
        yParent = None
        yDepth = None

        def dfs(node, depth, parent):
            nonlocal xParent, xDepth, yParent, yDepth
            # pruning
            if depth > max(xDepth if xDepth != None else float('inf'), yDepth if yDepth != None else float('inf')):
                return
            if node.val == x:
                xParent = parent
                xDepth = depth
                return # pruning
            if node.val == y:
                yParent = parent
                yDepth = depth
                # pruning
            if node.left:
                dfs(node.left, depth + 1, node)
            if node.right:
                dfs(node.right, depth + 1, node)

        dummy = TreeNode(None)
        dummy.left = root
        dfs(root, 0, dummy)
        return True if xParent != yParent and xDepth == yDepth else False