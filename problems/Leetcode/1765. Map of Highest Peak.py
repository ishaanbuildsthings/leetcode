class Solution:
    def highestPeak(self, isWater: List[List[int]]) -> List[List[int]]:
        height = len(isWater)
        width = len(isWater[0])
        DIFFS = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]

        q = collections.deque()
        seen = set()
        for r in range(height):
            for c in range(width):
                if isWater[r][c]:
                    q.append((r, c))
                    seen.add((r, c))
        
        res = [[None] * width for _ in range(height)]
        steps = 0

        while q:            
            length = len(q)
            for _ in range(length):
                r, c = q.popleft()
                res[r][c] = steps
                for rowDiff, colDiff in DIFFS:
                    newRow = rowDiff + r
                    newCol = colDiff + c
                    # skip out of bounds
                    if newRow < 0 or newRow == height or newCol < 0 or newCol == width:
                        continue
                    # skip seen elements
                    if (newRow, newCol) in seen:
                        continue
                    seen.add((newRow, newCol))
                    q.append((newRow, newCol))
            steps += 1
        
        return res

        