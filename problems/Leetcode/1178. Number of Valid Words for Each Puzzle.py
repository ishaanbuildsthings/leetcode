class Solution:
    def findNumOfValidWords(self, words: List[str], puzzles: List[str]) -> List[int]:
        def toMask(s):
            mask = 0
            for c in s:
                mask |= (1 << (ord(c) - ord('a')))
            return mask
        wordMasks = [toMask(w) for w in words]
        c = Counter(wordMasks)
        res = []
        for puz in puzzles:
            mask = toMask(puz)
            s = mask
            resHere = 0
            while s:
                if s & (1 << (ord(puz[0]) - ord('a'))):
                    resHere += c[s]
                s = (s - 1) & mask
            res.append(resHere)
        return res