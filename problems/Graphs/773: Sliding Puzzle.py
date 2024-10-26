# https://leetcode.com/problems/sliding-puzzle/
# Difficulty: Hard
# Tags: bfs

# Problem
# On an 2 x 3 board, there are five tiles labeled from 1 to 5, and an empty square represented by 0. A move consists of choosing 0 and a 4-directionally adjacent number and swapping it.

# The state of the board is solved if and only if the board is [[1,2,3],[4,5,0]].

# Given the puzzle board board, return the least number of moves required so that the state of the board is solved. If it is impossible for the state of the board to be solved, return -1.

# Solution, O(1) time and space
# I just did a brute force bfs. I used a hash of states but you could stringify.

import copy

class Solution:
    def slidingPuzzle(self, board: List[List[int]]) -> int:
        HEIGHT = 2
        WIDTH = 3
        def getHash(boardState):
            hash = 0
            exponent = 0
            for r in range(HEIGHT):
                for c in range(WIDTH):
                    hash += (10**exponent) * boardState[r][c]
                    exponent += 1
            return hash
        SOLVED_HASH = getHash([[1,2,3],[4,5,0]])

        seenStates = set() # don't duplicate board states

        diffs = [ [1,0], [0,1], [-1,0], [0,-1] ]

        queue = [board] # fake queue
        result = 0

        while len(queue):
            queueLength = len(queue)
            for i in range(queueLength):
                boardState = queue.pop(0)
                boardHash = getHash(boardState)
                if boardHash == SOLVED_HASH:
                    return result
                seenStates.add(getHash(boardState))
                # find the 0
                for r in range(HEIGHT):
                    for c in range(WIDTH):
                        if boardState[r][c] == 0:
                            zeroR = r
                            zeroC = c
                            break

                for rowDiff, colDiff in diffs:
                    newRow = zeroR + rowDiff
                    newCol = zeroC + colDiff
                    # skip out of bounds swaps
                    if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                        continue
                    newBoard = copy.deepcopy(boardState)
                    # swap them
                    newBoard[zeroR][zeroC] = newBoard[newRow][newCol]
                    newBoard[newRow][newCol] = 0
                    # don't add to queue if we have seen this board
                    if getHash(newBoard) in seenStates:
                        continue
                    queue.append(newBoard)
            result += 1
        return -1






