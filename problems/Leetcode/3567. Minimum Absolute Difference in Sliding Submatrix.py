class Solution:
    def minAbsDiff(self, grid: List[List[int]], k: int) -> List[List[int]]:
        height = len(grid)
        width = len(grid[0])
        heightSize = height - k + 1
        widthSize = width - k + 1
        res = [[None] * widthSize for _ in range(heightSize)]

        for i in range(len(res)):
            for j in range(len(res[i])):
                # print(f'i={i} j={j}')
                vals = []
                for r in range(i, i + k):
                    for c in range(j, j + k):
                        vals.append(grid[r][c])
                # print(f'init vals: {vals}')
                vals = list(set(vals))
                # print(f'vals: {vals}')
                vals.sort()
                minDiff = inf
                for index in range(len(vals) - 1):
                    minDiff = min(minDiff, abs(vals[index] - vals[index+1]))
                res[i][j] = minDiff if minDiff != inf else 0
        return res