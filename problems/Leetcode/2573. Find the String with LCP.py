class DSU:
    def __init__(self, nodes):
        self.parents = [i for i in range(len(nodes))]
    def unite(self, a, b):
        if self.f(a) == self.f(b):
            return False
        self.parents[self.f(a)] = self.f(b)
    def f(self, a):
        if self.parents[a] == a:
            return a
        self.parents[a] = self.f(self.parents[a])
        return self.parents[a]
class Solution:
    def findTheString(self, lcp: List[List[int]]) -> str:
        uf = DSU(list(range(len(lcp))))
        n = len(lcp)
        for i in range(n):
            for j in range(n):
                width = lcp[i][j]
                if width > 0:
                    uf.unite(i,j)
        rootToLetter = {}
        res = [None] * len(lcp)
        abc = 'abcdefghijklmnopqrstuvwxyz'
        letterI = 0
        for i in range(len(lcp)):
            rt = uf.f(i)
            if not rt in rootToLetter:
                if letterI == 26:
                    return ''
                newLetter = abc[letterI]
                rootToLetter[rt] = newLetter
                res[i] = newLetter
                letterI += 1
            else:
                res[i] = rootToLetter[rt]
        @cache
        def dp(i, j):
            if i == len(lcp) or j == len(lcp):
                return 0
            if res[i] != res[j]:
                return 0
            return 1 + dp(i + 1, j + 1)
        for i in range(len(lcp)):
            for j in range(len(lcp)):
                if lcp[i][j] != dp(i, j):
                    return ''
        return ''.join(res)


        

