class Solution:
    def finishTime(self, n: int, edges: List[List[int]], baseTime: List[int]) -> int:
        children = defaultdict(list)
        for a, b in edges:
            children[a].append(b)

        def dfs(node):
            if not children[node]:
                return baseTime[node]
            mn = inf
            mx = -inf
            for c in children[node]:
                t = dfs(c)
                mn = min(mn, t)
                mx = max(mx, t)
            time = (mx - mn) + baseTime[node] + mx
            return time

        return dfs(0)