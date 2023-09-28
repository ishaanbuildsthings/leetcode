# https://leetcode.com/problems/count-nodes-equal-to-average-of-subtree/
# difficulty: medium
# tags: trees

# problem
# Given the root of a binary tree, return the number of nodes where the value of the node is equal to the average of the values in its subtree.

# Note:

# The average of n elements is the sum of the n elements divided by n and rounded down to the nearest integer.
# A subtree of root is a tree consisting of root and all of its descendants.

# Solution, O(n) time and O(height) space, just recurse down, each dfs returns its sum and amount

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def averageOfSubtree(self, root: Optional[TreeNode]) -> int:
        res = 0

        # should tell us the sum and amount of its subtree
        def dfs(node):
            nonlocal res
            # base case
            if not node:
                return [0, 0]

            if node.left:
                leftSum, leftAmount = dfs(node.left)
            else:
                leftSum, leftAmount = [0, 0]
            if node.right:
                rightSum, rightAmount = dfs(node.right)
            else:
                rightSum, rightAmount = [0, 0]

            totalSum = node.val + leftSum + rightSum
            totalNodes = 1 + leftAmount + rightAmount
            avg = int(math.floor(totalSum / totalNodes))
            if node.val == avg:
                res += 1
            return totalSum, totalNodes

        dfs(root)
        return res