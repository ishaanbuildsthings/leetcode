class Solution:
    def prefixConnected(self, words: List[str], k: int) -> int:
        words = [word for word in words if len(word) >= k]
        sz = Counter()
        for w in words:
            sz[w[:k]] += 1
        res = 0
        for k, v in sz.items():
            if v > 1:
                res += 1
        return res