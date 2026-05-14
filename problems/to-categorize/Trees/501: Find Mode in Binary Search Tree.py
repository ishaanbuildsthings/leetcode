# https://leetcode.com/problems/find-mode-in-binary-search-tree/description/
# difficulty: easy
# tags: bst

# Problem
# Given the root of a binary search tree (BST) with duplicates, return all the mode(s) (i.e., the most frequently occurred element) in it.

# If the tree has more than one mode, return them in any order.

# Assume a BST is defined as follows:

# The left subtree of a node contains only nodes with keys less than or equal to the node's key.
# The right subtree of a node contains only nodes with keys greater than or equal to the node's key.
# Both the left and right subtrees must also be binary search trees.

# Solution, O(n) time and space, I just iterated and stored them in an array then counted. we can do O(h) space without the array, and O(1) space with morris. To do O(h) space just use nonlocal variables tracking the streak and current number and update things as needed


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def findMode(self, root: Optional[TreeNode]) -> List[int]:
        arr = []
        def dfs(node):
            if not node:
                return
            dfs(node.left)
            arr.append(node.val)
            dfs(node.right)
        dfs(root)
        res = []
        maxLength = 1
        prev = None
        currLength = 0
        for i in range(len(arr)):
            curr = arr[i]
            if curr == prev:
                currLength += 1
                if currLength == maxLength:
                    res.append(curr)
                elif currLength > maxLength:
                    res = [curr]
                    maxLength = currLength
            else:
                prev = curr
                currLength = 1
                if currLength == maxLength:
                    res.append(curr)
        return res
