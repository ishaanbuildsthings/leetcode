class Solution:
    def sortMatrix(self, grid: List[List[int]]) -> List[List[int]]:
        # handle bottom left
        height = len(grid)
        width = len(grid[0])
        for r in range(height):
            bucket = []
            offset = 0
            while True:
                newRow = r + offset
                newCol = offset
                if newCol >= width or newRow >= height:
                    break
                bucket.append(grid[newRow][newCol])
                offset += 1
            bucket.sort(reverse=True)
            offset = 0
            while True:
                newRow = r + offset
                newCol = offset
                if newCol >= width or newRow >= height:
                    break
                grid[newRow][newCol] = bucket[offset]
                offset += 1
        
        # handle tr
        for c in range(1, width):
            offset = 0
            bucket = []
            while True:
                newRow = offset
                newCol = c + offset
                if newCol >= width or newRow >= height:
                    break
                bucket.append(grid[newRow][newCol])
                offset += 1
            bucket.sort()
            offset = 0
            while True:
                newRow = offset
                newCol = c + offset
                if newCol >= width or newRow >= height:
                    break
                grid[newRow][newCol] = bucket[offset]
                offset += 1
        return grid
                
                
                