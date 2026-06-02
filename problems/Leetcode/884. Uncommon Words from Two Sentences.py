class Solution:
    def uncommonFromSentences(self, s1: str, s2: str) -> List[str]:
        arr1 = s1.split()
        arr2 = s2.split()
        f1 = Counter(arr1)
        for w in arr2:
            f1[w] += 1
        res = []
        for w in f1:
            if f1[w] == 1:
                res.append(w)
        
        return res