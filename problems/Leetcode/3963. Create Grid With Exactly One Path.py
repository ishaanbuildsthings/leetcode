class Solution:
    def createGrid(self, m: int, n: int) -> list[str]:
        res = [['#'] * n for _ in range(m)]

        for r in range(m):
            res[r][0] = '.'
        for c in range(n):
            res[-1][c] = '.'

        res = [''.join(row) for row in res]
        return res