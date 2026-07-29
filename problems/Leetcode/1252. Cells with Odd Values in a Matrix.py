class Solution:
    def oddCells(self, m: int, n: int, indices: List[List[int]]) -> int:
        rowIncs = Counter()
        colIncs = Counter()
        for r, c in indices:
            rowIncs[r] += 1
            colIncs[c] += 1
        
        res = 0
        for r in range(m):
            for c in range(n):
                res += (rowIncs[r] + colIncs[c]) % 2
        return res