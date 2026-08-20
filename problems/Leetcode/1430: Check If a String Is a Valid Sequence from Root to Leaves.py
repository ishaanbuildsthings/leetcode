# https://leetcode.com/problems/check-if-a-string-is-a-valid-sequence-from-root-to-leaves-path-in-a-binary-tree/
# Difficulty: Medium
# Tags: trees

# Problem
# Given a binary tree where each path going from the root to any leaf form a valid sequence, check if a given string is a valid sequence in such binary tree.

# We get the given string from the concatenation of an array of integers arr and the concatenation of all values of the nodes along a path results in a sequence in the given binary tree.


# Solution, O(n) time, O(height) space
# DFS down all paths that continue the sequence.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isValidSequence(self, root: Optional[TreeNode], arr: List[int]) -> bool:
        def recurse(i, node):
            # base case
            if i == len(arr) - 1:
                if not node.left and not node.right and node.val == arr[i]:
                    return True
                return False

            if node.val != arr[i]:
                return False

            resForThis = False

            if node.left:
                resForThis = recurse(i + 1, node.left)
            if resForThis:
                return True
            if node.right:
                resForThis = recurse(i + 1, node.right)
            return resForThis

        return recurse(0, root)