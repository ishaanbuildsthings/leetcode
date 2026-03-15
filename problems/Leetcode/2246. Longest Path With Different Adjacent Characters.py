class Solution:
    def longestPath(self, parent: List[int], s: str) -> int:
        children = defaultdict(list)
        for node in range(len(parent)):
            if parent[node] != -1:
                children[parent[node]].append(node)

        res = -inf

        @cache
        def sz(node):
            if not children[node]:
                return 1
            res = 1
            for child in children[node]:
                if s[child] != s[node]:
                    res = max(res, 1 + sz(child))
            return res

        def dfs(node):
            nonlocal res

            sizes = []
            for child in children[node]:
                dfs(child)
                if s[child] == s[node]:
                    continue
                sizes.append(sz(child))
                
            
            bigTwo = sum(heapq.nlargest(2, sizes))

            res = max(res, 1 + bigTwo)
        
        dfs(0)

        return res
            
