class Solution:
    def cyclicShift(self, n: int, grid: list[list[int]], rowShift: list[int], colShift: list[int]) -> list[list[int]]:
        h = len(grid)
        w = len(grid[0])
        for r in range(h):
            cycle = rowShift[r]
            row = grid[r]
            nrow = row[cycle:] + row[:cycle]
            print(f'row: {row}')
            print(f'nrow: {nrow}')
            grid[r] = nrow

        for c in range(w):
            col = []
            for r in range(h):
                col.append(grid[r][c])
            upShift = colShift[c]
            ncol = col[upShift:] + col[:upShift]
            for r in range(h):
                grid[r][c] = ncol[r]

        return grid