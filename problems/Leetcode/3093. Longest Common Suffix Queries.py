class Trie:
    def __init__(self, maxLetters):
        self.maxNodes = maxLetters + 1 # include root
        self.minSize = [inf] * self.maxNodes
        self.minIdx = [inf] * self.maxNodes
        self.children = defaultdict(dict)
        self.nextId = 1
    def add(self, s, i):
        idx = 0
        L = len(s)
        if L < self.minSize[0]:
            self.minSize[0] = L
            self.minIdx[0] = i
        elif L == self.minSize[0]:
            self.minIdx[0] = min(self.minIdx[0], i)

        for c in s:
            cid = ord(c) - ord('a')
            if cid not in self.children[idx]:
                self.children[idx][cid] = self.nextId
                self.nextId += 1
            idx = self.children[idx][cid]
            if L < self.minSize[idx]:
                self.minSize[idx] = L
                self.minIdx[idx] = i
            elif L == self.minSize[idx]:
                self.minIdx[idx] = min(self.minIdx[idx], i)
    def get(self, pf):
        idx = 0
        for c in pf:
            cid = ord(c) - ord('a')
            if cid not in self.children[idx]:
                return self.minIdx[idx]
            idx = self.children[idx][cid]
        return self.minIdx[idx]

class Solution:
    def stringIndices(self, wordsContainer: List[str], wordsQuery: List[str]) -> List[int]:
        sz = sum(len(w) for w in wordsContainer)
        t = Trie(sz)
        for i, w in enumerate(wordsContainer):
            t.add(w[::-1], i)
        res = []
        for q in wordsQuery:
            res.append(t.get(q[::-1]))
        return res
        