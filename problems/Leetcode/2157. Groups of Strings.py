class DSU:
    def __init__(self, nodes):
        self.parents = {}
        self.depths = {}
        self.sizes = {}
        for node in nodes:
            self.parents[node] = node
            self.depths[node] = 1
            self.sizes[node] = 1

    def _find(self, node):
        if self.parents[node] != node:
            self.parents[node] = self._find(self.parents[node])
        return self.parents[node]

    def union(self, a, b):
        aRepParent = self._find(a)
        bRepParent = self._find(b)
        if aRepParent == bRepParent:
            return False

        aDepth = self.depths[aRepParent]
        bDepth = self.depths[bRepParent]
        if aDepth < bDepth:
            self.parents[aRepParent] = bRepParent
            self.sizes[bRepParent] += self.sizes[aRepParent]
            del self.depths[aRepParent]
        elif bDepth < aDepth:
            self.parents[bRepParent] = aRepParent
            self.sizes[aRepParent] += self.sizes[bRepParent]
            del self.depths[bRepParent]
        else:
            self.parents[aRepParent] = bRepParent
            self.sizes[bRepParent] += self.sizes[aRepParent]
            del self.depths[aRepParent]
            self.depths[bRepParent] += 1
        return True

    def uniqueComponents(self):
        return len(self.depths)

    def largestComponent(self):
        return max(self.sizes.values())
class Solution:
    def groupStrings(self, words: List[str]) -> List[int]:
        delMaskToWords = defaultdict(list)
        fullMaskToWords = defaultdict(list)
        for i, w in enumerate(words):
            fmask = 0
            for c in w:
                fmask |= (1 << (ord(c) - ord('a')))
            fullMaskToWords[fmask].append(i)
            for c in w:
                delMask = fmask ^ (1 << (ord(c) - ord('a')))
                delMaskToWords[delMask].append(i)
        
        uf = DSU(range(len(words)))

        # any two words sharing a same full mask are combined
        for k, v in fullMaskToWords.items():
            for i in range(len(v) - 1):
                uf.union(v[i], v[i + 1])
        
        # any two words sharing a deleted mask are combined
        # for instance bat and cat, we can replace b with c
        for k, v in delMaskToWords.items():
            for i in range(len(v) - 1):
                uf.union(v[i], v[i + 1])
        
        # for every deleted mask, if that is another words full mask they combine
        for k, v in delMaskToWords.items():
            v2 = fullMaskToWords[k]
            if v2:
                uf.union(v[0], v2[0])
        
        return [uf.uniqueComponents(), uf.largestComponent()]



