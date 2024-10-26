# https://leetcode.com/problems/minimum-knight-moves/
# difficulty: medium
# tags: matrix bfs

# problem
# In an infinite chess board with coordinates from -infinity to +infinity, you have a knight at square [0, 0].

# A knight has 8 possible moves it can make, as illustrated below. Each move is two squares in a cardinal direction, then one square in an orthogonal direction.

# Return the minimum number of steps needed to move the knight to the square [x, y]. It is guaranteed the answer exists.

# Solution, O(x*y) time and space but really there is a tighter boundary. Better seen hash keys can also be done. Pruning can definitely be added / a greedy direction algorithm. But pretty sure an O(1) solution exists also!

class Solution:
    def minKnightMoves(self, targetX: int, targetY: int) -> int:
        # edge case
        if targetX == 0 and targetY == 0:
            return 0

        queue = collections.deque()
        queue.append([0, 0])
        level = 0

        diffs = [ [1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1] ]

        seen = set() # holds 'x,y'
        seen.add('0,0')
        while True:
            queueLength = len(queue)
            level += 1
            for _ in range(queueLength):
                x, y = queue.popleft() # pretend real queue O(1)
                for rowDiff, colDiff in diffs:
                    newRow = x + rowDiff
                    newCol = y + colDiff
                    if newRow == targetX and newCol == targetY:
                        return level
                    key = f'{newRow},{newCol}'
                    if key in seen:
                        continue
                    seen.add(key)
                    queue.append([newRow, newCol])

