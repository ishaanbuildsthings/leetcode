# https://leetcode.com/problems/minimum-score-of-a-path-between-two-cities/description/
# difficulty: medium
# tags: graph, undirected, unconnected

# Solution, O(v+e) time O(v+e) space. Solution is basically counting the smallest edge in a component

class Solution:
    def minScore(self, n: int, roads: List[List[int]]) -> int:
        edgeMap = defaultdict(list)
        roadToDist = {}
        for a, b, dist in roads:
            edgeMap[a].append(b)
            edgeMap[b].append(a)
            roadToDist[min(a, b), max(a, b)] = dist

        res = float('inf')

        seenNodes = set()

        def dfs(node):
            seenNodes.add(node)

            nonlocal res
            for adjNode in edgeMap[node]:


                road = (min(node, adjNode), max(node, adjNode))
                roadDist = roadToDist[road]
                res = min(res, roadDist)
                if adjNode not in seenNodes:
                    dfs(adjNode)

        dfs(1)
        return res
