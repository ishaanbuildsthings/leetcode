# https://leetcode.com/problems/maximum-average-subtree/
# difficulty: medium
# tags: tree, binary tree

# Problem
# Given the root of a binary tree, return the maximum average value of a subtree of that tree. Answers within 10-5 of the actual answer will be accepted.

# A subtree of a tree is any node of that tree plus all its descendants.

# The average value of a tree is the sum of its values, divided by the number of nodes.

# Solution, O(n) time, O(height) space, standard DFS, I used a global variable.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def maximumAverageSubtree(self, root: Optional[TreeNode]) -> float:
        res = 0

        def dfs(node):
            nonlocal res

            # base case
            if not node.left and not node.right:
                res = max(res, node.val)
                return [1, node.val] # size and weight

            totalSize = 1
            totalWeight = node.val

            if node.left:
                lSize, lWeight = dfs(node.left)
                totalSize += lSize
                totalWeight += lWeight
            if node.right:
                rSize, rWeight = dfs(node.right)
                totalSize += rSize
                totalWeight += rWeight

            finalAvg = totalWeight / totalSize
            res = max(res, finalAvg)
            return [totalSize, totalWeight]

        dfs(root)
        return res