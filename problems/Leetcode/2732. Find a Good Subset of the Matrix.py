class Solution:
    def goodSubsetofBinaryMatrix(self, grid: List[List[int]]) -> List[int]:
        c = Counter()
        tupToI = {}
        for i, row in enumerate(grid):
            tup = tuple(row)
            if max(tup) == 0:
                return [i]
            tupToI[tup] = i
            c[tup] += 1
        
        for k1 in c:
            for k2 in c:
                if k1 == k2:
                    continue
                if max(a + b for a, b in zip(k1, k2)) == 1:
                    return sorted([tupToI[k1], tupToI[k2]])
        
        return []
