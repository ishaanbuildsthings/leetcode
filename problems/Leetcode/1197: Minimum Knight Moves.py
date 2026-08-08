class Solution:
    def minKnightMoves(self, x: int, y: int) -> int:
        x = abs(x)
        y = abs(y)
        x, y = max(x, y), min(x, y)

        bound1 = ceil(x / 2)
        bound2 = ceil((x + y) / 3)
        moves = max(bound1, bound2)

        p1 = (0) + moves % 2 # color we are on after this many moves, we start on x%2==y%2 and alternate
        p2 = (x + y) % 2 # color we want to be on

        if (x, y) == (1, 0):
            return 3
        if (x, y) == (2, 2):
            return 4

        if p1 != p2:
            moves += 1
        
        return moves


        # # edge case
        # if targetX == 0 and targetY == 0:
        #     return 0

        # queue = collections.deque()
        # queue.append([0, 0])
        # level = 0

        # diffs = [ [1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1] ]

        # seen = set() # holds 'x,y'
        # seen.add('0,0')
        # while True:
        #     queueLength = len(queue)
        #     level += 1
        #     for _ in range(queueLength):
        #         x, y = queue.popleft() # pretend real queue O(1)
        #         for rowDiff, colDiff in diffs:
        #             newRow = x + rowDiff
        #             newCol = y + colDiff
        #             if newRow == targetX and newCol == targetY:
        #                 return level
        #             key = f'{newRow},{newCol}'
        #             if key in seen:
        #                 continue
        #             seen.add(key)
        #             queue.append([newRow, newCol])

