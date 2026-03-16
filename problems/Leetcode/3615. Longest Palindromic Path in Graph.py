class Solution:
    def maxLen(self, n: int, edges: List[List[int]], label: str) -> int:
        g = [[] for _ in range(n)]
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        fmask = (1 << n) - 1
        @cache
        def dp(i, j, mask):
            if i == j:
                return 1
            resHere = -inf if j not in g[i] else 2
            for adj1 in g[i]:
                if (1 << adj1) & mask:
                    continue
                for adj2 in g[j]:
                    if (1 << adj2) & mask:
                        continue
                    if label[adj1] != label[adj2]:
                        continue
                    nmask = mask | (1 << adj1) | (1 << adj2)
                    resHere = max(resHere, 2 + dp(adj1, adj2, nmask))
            return resHere
        res = 1
        for i in range(n):
            for j in range(i + 1, n):
                if label[i] == label[j]:
                    res = max(res, dp(i, j, (1 << i) | (1 << j)))
        return res


            
            