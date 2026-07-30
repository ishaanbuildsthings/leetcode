class Solution:
    def luckyNumbers (self, matrix: List[List[int]]) -> List[int]:
        rowSmall = defaultdict(lambda: inf)
        colBig = defaultdict(lambda: -inf)
        for i, row in enumerate(matrix):
            rowSmall[i] = min(row)
        for c in range(len(matrix[0])):
            colBig[c] = max(matrix[r][c] for r in range(len(matrix)))
        
        res = []
        for r in range(len(matrix)):
            for c in range(len(matrix[0])):
                if matrix[r][c] == rowSmall[r] and matrix[r][c] == colBig[c]:
                    res.append(matrix[r][c])
        
        return res
