class Solution:
    def maxEqualRowsAfterFlips(self, matrix: List[List[int]]) -> int:
        tupToCount = defaultdict(int)
        for row in matrix:
            tupToCount[tuple(row)] += 1
        
        res = 0
        for row in matrix:
            tup = tuple(row)
            inverseTup = tuple(1 - val for val in tup)
            res = max(res, tupToCount[tup] + tupToCount[inverseTup])
        
        return restle