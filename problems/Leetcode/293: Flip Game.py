# https://leetcode.com/problems/flip-game/description/?envType=weekly-question&envId=2024-02-01
# difficulty: easy

# Problem
# You are playing a Flip Game with your friend.

# You are given a string currentState that contains only '+' and '-'. You and your friend take turns to flip two consecutive "++" into "--". The game ends when a person can no longer make a move, and therefore the other person will be the winner.

# Return all possible states of the string currentState after one valid move. You may return the answer in any order. If there is no valid move, return an empty list [].

# Solution, O(n^2) time O(n) space

class Solution:
    def generatePossibleNextMoves(self, currentState: str) -> List[str]:
        res = []
        for i in range(len(currentState) - 1):
            prefix = currentState[i:i+2]
            if prefix != '++':
                continue
            res.append(currentState[:i] + '--' + currentState[i+ 2:])
        return res