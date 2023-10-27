# https://leetcode.com/problems/step-by-step-directions-from-a-binary-tree-node-to-another/description/
# difficulty: medium
# tags: binary tree

# Problem
# You are given the root of a binary tree with n nodes. Each node is uniquely assigned a value from 1 to n. You are also given an integer startValue representing the value of the start node s, and a different integer destValue representing the value of the destination node t.

# Find the shortest path starting from node s and ending at node t. Generate step-by-step directions of such path as a string consisting of only the uppercase letters 'L', 'R', and 'U'. Each letter indicates a specific direction:

# 'L' means to go from a node to its left child node.
# 'R' means to go from a node to its right child node.
# 'U' means to go from a node to its parent node.
# Return the step-by-step directions of the shortest path from node s to node t.

# Solution, I am writing this a while after solving so I don't fully remember. I think I created pointers (made more than needed, since children already exist), then traversed through, accumulating the path and joining it

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def getDirections(self, root: Optional[TreeNode], startValue: int, destValue: int) -> str:
        pointerMap = defaultdict(dict) # pointerMap[node]['L'] tells us that node
        startNode = None
        def populatePointer(node):
            nonlocal startNode
            if node.val == startValue:
                startNode = node
            if node.left:
                pointerMap[node]['L'] = node.left
                pointerMap[node.left]['U'] = node
                populatePointer(node.left)
            if node.right:
                pointerMap[node]['R'] = node.right
                pointerMap[node.right]['U'] = node
                populatePointer(node.right)
        populatePointer(root)

        resArr = []

        # tells us if that direction has the target
        seen = set()
        def dfs(node, path):
            if node.val == destValue:
                return True
            seen.add(node)
            for adjDir in pointerMap[node]:
                adj = pointerMap[node][adjDir]
                if adj in seen:
                    continue
                path.append(adjDir)
                if dfs(adj, path):
                    return True
                path.pop()

        path = []
        dfs(startNode, path)
        return ''.join(path)
