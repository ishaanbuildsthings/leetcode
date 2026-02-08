class Solution:
    def filterCharacters(self, s: str, k: int) -> str:
        c = Counter(s)
        res = []
        for v in s:
            if c[v] < k:
                res.append(v)
        return ''.join(res)