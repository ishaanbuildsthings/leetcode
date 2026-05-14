# https://leetcode.com/problems/reach-a-number/description/
# Difficulty: Medium
# Tags: Math

# Problem
# You are standing at position 0 on an infinite number line. There is a destination at position target.

# You can make some number of moves numMoves so that:

# On each move, you can either go left or right.
# During the ith move (starting from i == 1 to i == numMoves), you take i steps in the chosen direction.
# Given the integer target, return the minimum number of moves required (i.e., the minimum numMoves) to reach the destination.

# Solution, O(sqrt(target)) time, O(1) space
# Sum triangle numbers until we >= the target. Then, we can determine if we need to flip 0, 1, or 2 directions to exactly hit it.

class Solution:
    def reachNumber(self, target: int) -> int:
        runningSum = 0
        i = 0
        target = abs(target)
        while runningSum < target:
            runningSum += (i + 1)
            i += 1

        if runningSum == target:
            return i
        if (runningSum - target) % 2 == 0:
            return i
        # if we overshot by an odd amount, and the next step we make is even, we cannot fix the parity
        if i % 2 == 0:
            return i + 1
        return i + 2

        # 0->1
        # 1->3
        # 3->6
        # 6->10
        # 10->15
