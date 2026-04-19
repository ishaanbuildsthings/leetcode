class Solution:
    def wallsAndGates(self, rooms: List[List[int]]) -> None:
        """
        Do not return anything, modify rooms in-place instead.
        """
        height = len(rooms)
        width = len(rooms[0])
        q = deque()
        seen = set() # could use the input matrix then re-write to reduce space complexity

        for r in range(height):
            for c in range(width):
                if rooms[r][c] == 0:
                    q.append((r, c))
                    seen.add((r, c))
        
        steps = 0
        while q:
            steps += 1
            length = len(q)
            for _ in range(length):
                r, c = q.popleft()
                for rowDiff, colDiff in [[1,0],[-1,0],[0,1],[0,-1]]:
                    newRow = r + rowDiff
                    newCol = c + colDiff
                    if (newRow, newCol) in seen:
                        continue
                    if newRow < 0 or newRow == height or newCol < 0 or newCol == width:
                        continue
                    if rooms[newRow][newCol] in [-1, 0]:
                        continue
                    rooms[newRow][newCol] = steps
                    q.append((newRow, newCol))
                    seen.add((newRow, newCol))
        
