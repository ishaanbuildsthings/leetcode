class Solution:
    def shortestCompletingWord(self, licensePlate: str, words: List[str]) -> str:
        c = Counter()
        for character in licensePlate:
            if character.isalpha():
                c[character.lower()] += 1
        res = None
        for w in words:
            if res is not None and len(w) >= len(res):
                continue
            c2 = Counter(w.lower())
            bFlag = False
            for character in c:
                if c2[character] < c[character]:
                    bFlag = True
                    break
            if bFlag:
                continue
            if res is None:
                res = w
            else:
                if len(w) < len(res):
                    res = w
        return res