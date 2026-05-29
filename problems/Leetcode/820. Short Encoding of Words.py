class Solution:
    def minimumLengthEncoding(self, words: List[str]) -> int:
        def make():
            return defaultdict(lambda : make())
        rt = make()
        saved = []
        for w in list(set(words)):
            curr = rt
            for c in w[::-1]:
                curr = curr[c]
            saved.append(curr)
        res = 0
        for i, w in enumerate(list(set(words))):
            dd = saved[i]
            if not len(dd):
                res += len(w) + 1
        return res
            
