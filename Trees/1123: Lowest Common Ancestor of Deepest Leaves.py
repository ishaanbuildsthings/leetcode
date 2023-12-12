# https://leetcode.com/problems/lowest-common-ancestor-of-deepest-leaves/description/
# difficulty: medium
# tags: lca, tree

# Problem
# Given the root of a binary tree, return the lowest common ancestor of its deepest leaves.

# Recall that:

# The node of a binary tree is a leaf if and only if it has no children
# The depth of the root of the tree is 0. if the depth of a node is d, the depth of each of its children is d + 1.
# The lowest common ancestor of a set S of nodes, is the node A with the largest depth such that every node in S is in the subtree with root A.

# Solution, O(n) time and space. Get the deepest ones, then do an LCA until we have all of them. We can just add up the count of what is seen rather than track them, since it is a tree, we cannot duplicate seen things. Lee has a really brilliant one pass solution.

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def lcaDeepestLeaves(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        depths = {}
        def dfs(node, depth):
            depths[node] = depth
            if node.left:
                dfs(node.left, depth + 1)
            if node.right:
                dfs(node.right, depth + 1)
        dfs(root, 0)

        maxDepth = max(depths.values())

        deepest = [node for node in depths if depths[node] == maxDepth]
        deepestSet = set(deepest)

        res = None

        def lca(node):
            nonlocal res

            # base case
            if not node.left and not node.right:
                if res == None and len(deepest) == 1 and deepest[0] == node:
                    res = node
                    return 1 if depths[node] == maxDepth else 0

            leftChildSeen = lca(node.left) if node.left else 0
            rightChildSeen = lca(node.right) if node.right else 0
            finalSeen = leftChildSeen + rightChildSeen + (1 if node in deepestSet else 0)

            if finalSeen == len(deepest) and res == None:
                res = node


            return finalSeen

        lca(root)

        return res


