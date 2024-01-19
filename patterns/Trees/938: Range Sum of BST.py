# https://leetcode.com/problems/range-sum-of-bst/description/?envType=daily-question&envId=2024-01-08
# difficulty: easy
# tags: bst, recursion

# Problem
# Given the root node of a binary search tree and two integers low and high, return the sum of values of all nodes with a value in the inclusive range [low, high].

# Solution
# Standard recursion

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def rangeSumBST(self, root: Optional[TreeNode], low: int, high: int) -> int:
        if not root:
            return 0
        return (
            root.val if root.val >= low and root.val <= high else
            0
        ) + self.rangeSumBST(root.left, low, high) + self.rangeSumBST(root.right, low, high)
        # def getSum(node):
        #     if not node:
        #         return 0
        #     if node.val < low or node.val > high:
        #         return getSum(node.left) + getSum(node.right)

        #     return node.val + getSum(node.left) + getSum(node.right)

        # return getSum(root)
