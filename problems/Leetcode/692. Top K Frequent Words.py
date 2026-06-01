class Solution:
    def topKFrequent(self, words: List[str], k: int) -> List[str]:
        wToFrq = Counter(words)
        frqToWords = defaultdict(list)
        for w in wToFrq:
            frqToWords[wToFrq[w]].append(w)
        for frq in frqToWords:
            frqToWords[frq].sort()
        

        res = []
        for frq in sorted(frqToWords.keys(), reverse=True):
            for w in frqToWords[frq]:
                res.append(w)
                if len(res) == k:
                    return res