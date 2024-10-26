# https://leetcode.com/problems/construct-string-from-binary-tree/description/?envType=daily-question&envId=2023-12-08
# difficulty: easy
# tags: binary tree

# Problem
# Given the root of a binary tree, construct a string consisting of parenthesis and integers from a binary tree with the preorder traversal way, and return it.

# Omit all the empty parenthesis pairs that do not affect the one-to-one mapping relationship between the string and the original binary tree.

# Solution, standard stuff, can simplify code, O(n) time and O(height) space

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def tree2str(self, root: Optional[TreeNode]) -> str:
        resArr = []
        def dfs(node):
            resArr.append(f'{node.val}')

            if node.left:
                resArr.append('(')
                dfs(node.left)
                resArr.append(')')
            else:
                if node.right:
                    resArr.append('()')
            if node.right:
                resArr.append('(')
                dfs(node.right)
                resArr.append(')')
        dfs(root)
        return ''.join(resArr)