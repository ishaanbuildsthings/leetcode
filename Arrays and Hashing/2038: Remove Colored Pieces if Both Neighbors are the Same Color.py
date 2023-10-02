# https://leetcode.com/problems/remove-colored-pieces-if-both-neighbors-are-the-same-color/description/?envType=daily-question&envId=2023-10-02
# difficulty: medium

# problem
# There are n pieces arranged in a line, and each piece is colored either by 'A' or by 'B'. You are given a string colors of length n where colors[i] is the color of the ith piece.

# Alice and Bob are playing a game where they take alternating turns removing pieces from the line. In this game, Alice moves first.

# Alice is only allowed to remove a piece colored 'A' if both its neighbors are also colored 'A'. She is not allowed to remove pieces that are colored 'B'.
# Bob is only allowed to remove a piece colored 'B' if both its neighbors are also colored 'B'. He is not allowed to remove pieces that are colored 'A'.
# Alice and Bob cannot remove pieces from the edge of the line.
# If a player cannot make a move on their turn, that player loses and the other player wins.
# Assuming Alice and Bob play optimally, return true if Alice wins, or return false if Bob wins.

# Solution, O(n) time and O(1) space
# There is no interference or strategy, just count how many A and B can do.

class Solution:
    def winnerOfGame(self, colors: str) -> bool:
        aPicks = 0
        bPicks = 0
        i = 0
        while i < len(colors):
            firstChar = colors[i]
            sequenceLength = 1
            j = i + 1
            while j < len(colors):
                if colors[j] != firstChar:
                    break
                sequenceLength += 1
                j += 1
            if sequenceLength > 2:
                if firstChar == 'A':
                    aPicks += sequenceLength - 2
                else:
                    bPicks += sequenceLength - 2
            i = j
        if aPicks > bPicks:
            return True
        return False