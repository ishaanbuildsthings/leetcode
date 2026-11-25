# https://leetcode.com/problems/find-if-path-exists-in-graph/description/?envType=daily-question&envId=2024-04-21
# difficulty: easy
# tags: graph

# Solution, O(V+E) time and space

class Solution:
    def validPath(self, n: int, edges: List[List[int]], source: int, destination: int) -> bool:
        edgeMap = defaultdict(list)
        for a, b in edges:
            edgeMap[a].append(b)
            edgeMap[b].append(a)

        isValid = False

        seen = set()

        def dfs(node):
            nonlocal isValid

            if node == destination:
                isValid = True

            seen.add(node)

            if isValid:
                return

            for adj in edgeMap[node]:
                if not adj in seen:
                    dfs(adj)

        dfs(source)

        return isValid

