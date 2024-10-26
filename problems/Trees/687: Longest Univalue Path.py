# https://leetcode.com/problems/longest-univalue-path/description/
# difficulty: medium
# tags: trees

# problem
# Given the root of a binary tree, return the length of the longest path, where each node in the path has the same value. This path may or may not pass through the root.

# The length of the path between two nodes is represented by the number of edges between them.

# Solution, O(n) time, O(height) space
# Recurse down. As we bubble up, maintain paths with the same numbers, and update a global variable (easiest implementation imo). Once we meet a different number, we need to reset.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def longestUnivaluePath(self, root: Optional[TreeNode]) -> int:
        res = 1

        # tells us the length of the current path
        def dfs(node):
            nonlocal res
            # base case
            if not node:
                return 0

            longestLeft = dfs(node.left)
            longestRight = dfs(node.right)

            # if we are different
            leftVal = None if not node.left else node.left.val
            rightVal = None if not node.right else node.right.val
            if node.val != leftVal and node.val != rightVal:
                newPathLength = 1
            # if we are the same as only the left
            elif node.val == leftVal and not node.val == rightVal:
                newPathLength = 1 + longestLeft
            # if we are the same as only the right
            elif node.val == rightVal and not node.val == leftVal:
                newPathLength = 1 + longestRight
            # if we are the same as both
            else:
                # we can update the result with a wide path
                res = max(res, 1 + longestLeft + longestRight)
                newPathLength = 1 + max(longestLeft, longestRight)

            res = max(res, newPathLength)
            return newPathLength

        dfs(root)
        return res - 1 # path not # of nodes



