# https://leetcode.com/problems/amount-of-time-for-binary-tree-to-be-infected/?envType=daily-question&envId=2024-01-10
# difficulty: medium
# tags: trees, bfs

# Problem
# You are given the root of a binary tree with unique values, and an integer start. At minute 0, an infection starts from the node with value start.

# Each minute, a node becomes infected if:

# The node is currently uninfected.
# The node is adjacent to an infected node.
# Return the number of minutes needed for the entire tree to be infected.

# Solution
# Standard bfs

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def amountOfTime(self, root: Optional[TreeNode], start: int) -> int:
        edge = defaultdict(list)
        startNode = None
        def dfs(node):
            nonlocal startNode

            if node.val == start:
                startNode = node

            if node.left:
                edge[node].append(node.left)
                edge[node.left].append(node)
                dfs(node.left)
            if node.right:
                edge[node].append(node.right)
                edge[node.right].append(node)
                dfs(node.right)
        dfs(root)

        q = collections.deque()
        q.append(startNode)
        seen = {startNode} # dont need a set can use the previous node
        res = 0
        while q:
            length = len(q)
            for _ in range(length):
                popped = q.popleft()
                for adj in edge[popped]:
                    if adj in seen:
                        continue
                    q.append(adj)
                    seen.add(adj)
            res += 1
        return res - 1





