# https://leetcode.com/problems/count-positions-on-street-with-required-brightness/
# difficulty: medium
# tags: sweep line

# problem
# You are given an integer n. A perfectly straight street is represented by a number line ranging from 0 to n - 1. You are given a 2D integer array lights representing the street lamp(s) on the street. Each lights[i] = [positioni, rangei] indicates that there is a street lamp at position positioni that lights up the area from [max(0, positioni - rangei), min(n - 1, positioni + rangei)] (inclusive).

# The brightness of a position p is defined as the number of street lamps that light up the position p. You are given a 0-indexed integer array requirement of size n where requirement[i] is the minimum brightness of the ith position on the street.

# Return the number of positions i on the street between 0 and n - 1 that have a brightness of at least requirement[i].

# Solution, O(n) time and space. First find the number of lights at each position with sweep line. Then compare with requirement and get a result (no need to realloc an array for this)

class Solution:
    def meetRequirement(self, n: int, lights: List[List[int]], requirement: List[int]) -> int:
        lightCounters = [0 for _ in range(n + 1)] # to make room for the line sweep
        for light in lights:
            pos, lightRange = light
            leftPosition = pos - lightRange
            leftPosition = max(leftPosition, 0)
            rightPosition = pos + lightRange
            rightPosition = min(n - 1, rightPosition)
            lightCounters[leftPosition] += 1
            lightCounters[rightPosition + 1] -= 1

        lightTotals = [0 for _ in range(n)]
        runningSum = 0
        for i in range(n):
            runningSum += lightCounters[i]
            lightTotals[i] = runningSum

        res = 0
        for i in range(len(lightTotals)):
            if lightTotals[i] >= requirement[i]:
                res += 1
        return res




