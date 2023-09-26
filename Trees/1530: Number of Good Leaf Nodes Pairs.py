# https://leetcode.com/problems/number-of-good-leaf-nodes-pairs/
# difficulty: medium
# tags: trees

# problem
# You are given the root of a binary tree and an integer distance. A pair of two different leaf nodes of a binary tree is said to be good if the length of the shortest path between them is less than or equal to distance.

# Return the number of good leaf node pairs in the tree.

# Solution, O(n^2) time, O(n) space
# First create a parent mapping which is n time and space. Then, for each node (if it is a leaf node), do a dfs up to depth distance which is up to n nodes due to the constraint on the number of nodes. This results in n^2 total time.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def countPairs(self, root: TreeNode, distance: int) -> int:
        parents = {} # maps a node to its parent
        allNodes = []
        def dfs(node):
            allNodes.append(node)
            if node.left:
                parents[node.left] = node
                dfs(node.left)
            if node.right:
                parents[node.right] = node
                dfs(node.right)

        dfs(root)

        res = 0

        def explore(node, depth, path):
            nonlocal res
            # base case
            if not node.left and not node.right:
                res += 1

            # max depth
            if depth == distance:
                return

            path.add(node)

            if node in parents and not parents[node] in path:
                explore(parents[node], depth + 1, path)
            if node.left and not node.left in path:
                explore(node.left, depth + 1, path)
            if node.right and not node.right in path:
                explore(node.right, depth + 1, path)

            path.remove(node)

        counter = 0
        for node in allNodes:
            if node.left or node.right:
                continue
            counter += 1
            explore(node, 0, set())

        return int((res - counter) / 2)





