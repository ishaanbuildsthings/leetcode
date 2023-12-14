# https://leetcode.com/problems/shortest-path-visiting-all-nodes/description/?envType=daily-question&envId=2023-09-17
# difficulty: hard
# tags: graphs, dynamic programming 2d, bit mask

# Problem
# You have an undirected, connected graph of n nodes labeled from 0 to n - 1. You are given an array graph where graph[i] is a list of all the nodes connected with node i by an edge.

# Return the length of the shortest path that visits every node. You may start and stop at any node, you may revisit nodes multiple times, and you may reuse edges.

# Solution
# Okay, this was the question that took me a long time to understand the DP solution for, because it isn't a pure DP. We keep a bitmask of nodes we have visited before our current node, kind of like when we use a path set in dfs to detect a cycle. We update the path inside, like we do in dfs. We add this to a set so we don't recurse back to the same situation forever, which happens because we update the path inside the dp call itself. We don't care about the order we visited cells in, just that we visited them, so we use a bitmask. I'm not convinced it can't be done without a set (I consider the cache trick the author used to be equivalent to using a set). I tried something like this for trapping rainwater II, but it fails because we would need to track the entire bitmask path for that and that graph is too big.

class Solution:
    def shortestPathLength(self, graph: list[list[int]]) -> int:
        n = len(graph)
        fullMask = (1 << n) - 1
        seenStates = set()

        @cache
        def dp(node, mask): # mask is like a path
            mask |= 1 << node

            state = (node, mask)
            seenStates.add(state)

            if mask == fullMask:
                seenStates.remove(state)
                return 0

            resForThis = float('inf')
            for adj in graph[node]:
                if (adj, mask) not in seenStates:
                    resForThis = min(resForThis, 1 + dp(adj, mask))
            seenStates.remove(state)
            return resForThis

        return min(dp(node, 0) for node in range(n))