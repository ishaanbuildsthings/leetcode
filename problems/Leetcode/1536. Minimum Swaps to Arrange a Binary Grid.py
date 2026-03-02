class Solution:
    def minSwaps(self, grid: List[List[int]]) -> int:
        h = len(grid)
        w = len(grid[0])

        lastBlocks = []
        for row in grid:
            
            for c in range(w - 1, -1, -1):
                added = False
                if row[c] == 1:
                    usedWidth = w - c - 1
                    lastBlocks.append(usedWidth)
                    added = True
                    break

            if not added:
                lastBlocks.append(w)
        
        res = 0

        def swap(r1, r2):
            nonlocal res
            dist = r2 - r1
            res += dist
            for i in range(r2, r1, -1):
                lastBlocks[i], lastBlocks[i - 1] = lastBlocks[i - 1], lastBlocks[i]

        for r in range(h):
            # we need to bring some index >= r to this row
            up = w - (r + 1) # can only afford anything with a last block >= up
            found = False
            for r2 in range(r, h):
                if lastBlocks[r2] >= up:
                    swap(r, r2)
                    found = True
                    break
            if not found:
                return -1
        
        return res
