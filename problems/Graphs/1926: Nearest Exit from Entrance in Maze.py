# https://leetcode.com/problems/nearest-exit-from-entrance-in-maze/description/
# difficulty: medium
# tags: graph, bfs

# Solution, O(n*m) time and space

class Solution:
    def nearestExit(self, maze: List[List[str]], entrance: List[int]) -> int:
        height = len(maze)
        width = len(maze[0])

        q = collections.deque()
        q.append((entrance[0], entrance[1]))
        seen = {(entrance[0], entrance[1])}

        DIFFS = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]

        steps = 0
        while q:
            qLength = len(q)
            for _ in range(qLength):
                r, c = q.popleft()
                for rowDiff, colDiff in DIFFS:
                    newRow = r + rowDiff
                    newCol = c + colDiff

                    if newRow < 0 or newRow == height or newCol < 0 or newCol == width:
                        continue
                    if maze[newRow][newCol] == '+':
                        continue
                    if (newRow, newCol) in seen:
                        continue
                    if newRow == 0 or newRow == height - 1 or newCol == 0 or newCol == width - 1:
                        return steps + 1

                    q.append((newRow, newCol))
                    seen.add((newRow, newCol))

            steps += 1


        return -1
