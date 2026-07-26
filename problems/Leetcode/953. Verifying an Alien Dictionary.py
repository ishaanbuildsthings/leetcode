class Solution:
    def isAlienSorted(self, words: List[str], order: str) -> bool:
        cToIndex = {
            c : i for i, c in enumerate(order)
        }
        # -1 if w1 < w2, 0 if ==, else 1
        def customSort(w1, w2):
            if w1 == w2:
                return 0
            for i in range(len(w1)):
                c1 = w1[i]
                if i == len(w2):
                    return 1
                c2 = w2[i]
                i1 = cToIndex[c1]
                i2 = cToIndex[c2]
                if i1 < i2:
                    return -1
                elif i1 > i2:
                    return 1
        
        for i in range(len(words) - 1):
            w1 = words[i]
            w2 = words[i + 1]
            result = customSort(w1, w2)
            if result == 1:
                return False
        
        return True
