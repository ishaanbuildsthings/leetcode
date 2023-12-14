# https://leetcode.com/problems/binary-tree-vertical-order-traversal/
# difficulty: medium
# tags: binary tree

# Problem
# Given the root of a binary tree, return the vertical order traversal of its nodes' values. (i.e., from top to bottom, column by column).

# If two nodes are in the same row and column, the order should be from left to right.

# Solution
# DFS, assigning nodes to their columns and depths, then sort each column. There's worst case n columns and log n nodes per column but it is amortized in a way
#* SOLUTION 2, I think we can do BFS with no sorting.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def verticalOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        columns = defaultdict(list) # maps a column to a list of nodes and their depths, [depth, node]

        def dfs(column, depth, node):
            if not node:
                return

            columns[column].append([depth, node])

            if node.left:
                dfs(column - 1, depth + 1, node.left)
            if node.right:
                dfs(column + 1, depth + 1, node.right)

        dfs(0, 0, root)

        res = []
        # can also track the smallest and biggest columns in the dfs to avoid this
        for key in sorted(columns.keys()):
            columns[key].sort(key=lambda x: x[0]) # only sort by depth, since node comparison would cause an error
            res.append([tup[1].val for tup in columns[key]])

        return res