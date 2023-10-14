# https://leetcode.com/problems/leaf-similar-trees/
# difficulty: easy
# tags: binary tree

# Problem
# Consider all the leaves of a binary tree, from left to right order, the values of those leaves form a leaf value sequence.

# For example, in the given tree above, the leaf value sequence is (6, 7, 4, 9, 8).

# Two binary trees are considered leaf-similar if their leaf value sequence is the same.

# Return true if and only if the two given trees with head nodes root1 and root2 are leaf-similar.

# Solution, O(n + m) time and space. I bet an O(n + m) time and O(h) space solution exists, where we run the two DFS at the same time and check the values one by one. Used json.dumps as it is fast to type, but there are faster ways to compare two lists.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def leafSimilar(self, root1: Optional[TreeNode], root2: Optional[TreeNode]) -> bool:
        arr1 = []
        arr2 = []

        def dfs(node, arr):
            # base case
            if not node.left and not node.right:
                arr.append(node.val)
                return

            if node.left:
                dfs(node.left, arr)
            if node.right:
                dfs(node.right, arr)

        dfs(root1, arr1)
        dfs(root2, arr2)

        return True if json.dumps(arr1) == json.dumps(arr2) else False