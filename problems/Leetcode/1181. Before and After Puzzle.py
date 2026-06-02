class Solution:
    def beforeAndAfterPuzzles(self, phrases: List[str]) -> List[str]:
        res = []

        phrases.sort()
        phrases = [p.split(' ') for p in phrases]
    
        for i in range(len(phrases)):
            for j in range(len(phrases)):
                if i == j:
                    continue
                w1 = phrases[i]
                w2 = phrases[j]
                if w1[-1] == w2[0]:
                    newPhrase = [w for w in w1]
                    newPhrase.pop()
                    for x in w2:
                        newPhrase.append(x)
                    res.append(' '.join(newPhrase))
        
        return sorted(list(set(res))) # can probably dedupe in generating the answers