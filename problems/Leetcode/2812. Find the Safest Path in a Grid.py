from collections import deque
from typing import List

class Solution:
    def maximumSafenessFactor(self, grid: List[List[int]]) -> int:
        HEIGHT, WIDTH = len(grid), len(grid[0])
        
        # tells us the distance of a cell from the closest thief
        distances = [[-1] * WIDTH for _ in range(HEIGHT)]
        
        thieves = deque()
        
        handledCells = 0
        
        for r in range(HEIGHT):
            for c in range(WIDTH):
                if grid[r][c] == 1:
                    thieves.append((r, c))
                    handledCells += 1
                    distances[r][c] = 0
                    
        iterations = 0
        
        while handledCells < HEIGHT * WIDTH:
            length = len(thieves)
            iterations += 1
            for _ in range(length):
                r, c = thieves.popleft()
                for rowDiff, colDiff in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    newRow, newCol = r + rowDiff, c + colDiff
                    
                    # if out of bounds, just continue
                    if newRow >= HEIGHT or newRow < 0 or newCol >= WIDTH or newCol < 0:
                        continue
                    
                    # if that cell was handled, just continue
                    if distances[newRow][newCol] != -1:
                        continue
                        
                    distances[newRow][newCol] = iterations
                    handledCells += 1
                    thieves.append((newRow, newCol))
                    
        lower, upper = 0, 0
        for row in range(HEIGHT):
            for col in range(WIDTH):
                upper = max(upper, distances[row][col])
                
        visited = set()
        
        def traverse(r, c, threshold):
            key = r * WIDTH + c
            if distances[r][c] < threshold:
                return False
            
            # base case, we are at the end
            if r == HEIGHT - 1 and c == WIDTH - 1:
                return distances[r][c] >= threshold
            
            visited.add(key)
            
            for rowDiff, colDiff in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                newRow, newCol = r + rowDiff, c + colDiff
                newKey = newRow * WIDTH + newCol
                # if the adj cell is over the threshold, in bounds, and not visited, we can go there
                if 0 <= newRow < HEIGHT and 0 <= newCol < WIDTH and newKey not in visited and distances[newRow][newCol] >= threshold:
                    if traverse(newRow, newCol, threshold):
                        return True
            
            return False

        while lower <= upper:
            m = (lower + upper) // 2
            if traverse(0, 0, m):
                lower = m + 1
            else:
                upper = m - 1
            visited.clear()
            
        return upper
