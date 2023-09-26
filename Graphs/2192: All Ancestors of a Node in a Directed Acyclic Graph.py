# https://leetcode.com/problems/all-ancestors-of-a-node-in-a-directed-acyclic-graph/description/
# difficulty: medium
# tags: graphs, directed, acylic, connected

# problem
# You are given a positive integer n representing the number of nodes of a Directed Acyclic Graph (DAG). The nodes are numbered from 0 to n - 1 (inclusive).

# You are also given a 2D integer array edges, where edges[i] = [fromi, toi] denotes that there is a unidirectional edge from fromi to toi in the graph.

# Return a list answer, where answer[i] is the list of ancestors of the ith node, sorted in ascending order.

# A node u is an ancestor of another node v if u can reach v via a set of edges.

# Solution, O(V^2 + E) time, O(V + E) space
# Generate reverse direction edges, which is O(edges) time and O(edges) space. Then for each element, dfs up to the top using a seen path, which takes O(V) time and space. Sorting each one gets amortized as worst case n log n which is dominated by n^2.

class Solution:
    def getAncestors(self, n: int, edges: List[List[int]]) -> List[List[int]]:
        edgeMap = defaultdict(list)
        for fromNode, toNode in edges:
            edgeMap[toNode].append(fromNode)
        def dfs(node, currAncestors, seenNodes):
            seenNodes.add(node)
            for nextNode in edgeMap[node]:
                if nextNode in seenNodes:
                    continue
                currAncestors.append(nextNode)
                dfs(nextNode, currAncestors, seenNodes)
            return currAncestors


        res = []
        for node in range(n):
            layer = dfs(node, [], set())
            layer.sort()
            res.append(layer)
        return res
