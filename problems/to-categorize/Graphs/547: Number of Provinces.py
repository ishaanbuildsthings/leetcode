# https://leetcode.com/problems/number-of-provinces/description/
# difficulty: medium
# tags: graphs, unconnected

# Problem
# There are n cities. Some of them are connected, while some are not. If city a is connected directly with city b, and city b is connected directly with city c, then city a is connected indirectly with city c.

# A province is a group of directly or indirectly connected cities and no other cities outside of the group.

# You are given an n x n matrix isConnected where isConnected[i][j] = 1 if the ith city and the jth city are directly connected, and isConnected[i][j] = 0 otherwise.

# Return the total number of provinces.

# Solution, O(n^2) time and O(n) space, it is n^2 because we have at most n^2 edges (each node connected to every other one), and we dfs on every node in the worst case which checks every edge

class Solution:
    def findCircleNum(self, isConnected: List[List[int]]) -> int:
        n = len(isConnected)

        visited = set()
        # explore and mark things as visited
        def dfs(node):
            visited.add(node)
            for adjNode in range(n):
                if adjNode == node:
                    continue
                if isConnected[node][adjNode] and not adjNode in visited:
                    dfs(adjNode)
        res = 0
        for node in range(n):
            if node in visited:
                continue
            dfs(node)
            res += 1
        return res