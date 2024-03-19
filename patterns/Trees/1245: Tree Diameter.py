# https://leetcode.com/problems/tree-diameter/
# difficulty: medium
# tags: tree

# Problem
# The diameter of a tree is the number of edges in the longest path in that tree.

# There is an undirected tree of n nodes labeled from 0 to n - 1. You are given a 2D array edges where edges.length == n - 1 and edges[i] = [ai, bi] indicates that there is an undirected edge between nodes ai and bi in the tree.

# Return the diameter of the tree.

# Solution
# O(n) time and space, turn it into a tree (can skip the dictionary entirely), dfs and measure the depths

class Solution:
    def treeDiameter(self, edges: List[List[int]]) -> int:
        edgeMap = defaultdict(list)
        for a, b in edges:
            edgeMap[a].append(b)
            edgeMap[b].append(a)

        children = defaultdict(list)
        def populateChildren(parent, node):
            for neighbor in edgeMap[node]:
                if neighbor != parent:
                    children[node].append(neighbor)
                    populateChildren(node, neighbor)
        populateChildren(-1, 0)

        # could skip making the children dictionary entirely

        res = 0
        # get the max depths
        def dfs(node):
            nonlocal res

            # base case
            if len(children[node]) == 0:
                return 1

            biggest = [0, 0]
            for child in children[node]:
                depthAtThatChild = dfs(child)
                if depthAtThatChild > biggest[1]:
                    biggest[1] = depthAtThatChild
                    if biggest[1] > biggest[0]:
                        biggest[0], biggest[1] = biggest[1], biggest[0]

            res = max(res, biggest[0] + biggest[1])
            return 1 + biggest[0]

        dfs(0)

        return res














