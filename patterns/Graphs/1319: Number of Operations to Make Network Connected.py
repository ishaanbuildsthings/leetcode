# https://leetcode.com/problems/number-of-operations-to-make-network-connected/
# difficulty: medium
# tags: graph, disconnected, directed

# Problem
# There are n computers numbered from 0 to n - 1 connected by ethernet cables connections forming a network where connections[i] = [ai, bi] represents a connection between computers ai and bi. Any computer can reach any other computer directly or indirectly through the network.

# You are given an initial computer network connections. You can extract certain cables between two directly connected computers, and place them between any pair of disconnected computers to make them directly connected.

# Return the minimum number of times you need to do this in order to make all the computers connected. If it is not possible, return -1.

# Solution, it's just the number of components minus one
class Solution:
    def makeConnected(self, n: int, connections: List[List[int]]) -> int:
        if len(connections) < n - 1:
            return -1

        edgeMap = defaultdict(list)
        for a, b in connections:
            edgeMap[a].append(b)
            edgeMap[b].append(a)

        seen = set()
        def dfs(node):
            seen.add(node)
            for neighbor in edgeMap[node]:
                if neighbor in seen:
                    continue
                dfs(neighbor)

        components = 0
        for node in range(n):
            if node in seen:
                continue
            dfs(node)
            components += 1

        return components - 1



