# https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree-iv/description/
# difficulty: medium
# tags: lca, binary tree

# Problem
# Given the root of a binary tree and an array of TreeNode objects nodes, return the lowest common ancestor (LCA) of all the nodes in nodes. All the nodes will exist in the tree, and all values of the tree's nodes are unique.

# Extending the definition of LCA on Wikipedia: "The lowest common ancestor of n nodes p1, p2, ..., pn in a binary tree T is the lowest node that has every pi as a descendant (where we allow a node to be a descendant of itself) for every valid i". A descendant of a node x is a node y that is on the path from node x to some leaf node.

# Solution
# My solution used a seen count which is O(n) time and O(height + nodeSet) space. I used a global variable and early terminate but we could make the function itself return the lca when found.
# * Solution 2, there is a REALLY brilliant solution. If we hit a node in the nodeset, we return that. If both left and right are needed, we return ourself. If only left or right is needed, we return that.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', nodes: 'List[TreeNode]') -> 'TreeNode':
        nodeSet = set(nodes)

        lca = None

        def dfs(node):
            nonlocal lca

            # prune
            if lca != None:
                return

            # base
            if not node:
                return 0

            leftSeen = dfs(node.left)
            # prune
            if lca != None:
                return
            rightSeen = dfs(node.right)
            # prune
            if lca != None:
                return
            middleSeen = 1 if node in nodeSet else 0
            totalSeen = leftSeen + rightSeen + middleSeen
            if totalSeen == len(nodes) and lca == None:
                lca = node

            return totalSeen

        dfs(root)

        return lca