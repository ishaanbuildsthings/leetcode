class Solution:
    def numEquivDominoPairs(self, dominoes: List[List[int]]) -> int:
        c = Counter()
        res = 0
        
        for a, b in dominoes:
            res += c[(min(a, b), max(a, b))]
            c[(min(a, b), max(a, b))] += 1

        return res