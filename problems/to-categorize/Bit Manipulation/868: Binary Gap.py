# https://leetcode.com/problems/binary-gap/description/
# difficulty: easy
# tags: bit manipulation

# Problem
# Given a positive integer n, find and return the longest distance between any two adjacent 1's in the binary representation of n. If there are no two adjacent 1's, return 0.

# Two 1's are adjacent if there are only 0's separating them (possibly no 0's). The distance between two 1's is the absolute difference between their bit positions. For example, the two 1's in "1001" have a distance of 3.

# Solution, O(log n or 1) time, O(1) space, count through bits, used a state variable to track if we can count the gap

class Solution:
    def binaryGap(self, n: int) -> int:
        res = -1
        running = 0
        seenOne = False
        for offset in range(32):
            bit = (n >> offset) & 1
            if not bit:
                if seenOne:
                    running += 1
            else:
                if seenOne:
                    res = max(res, running)
                seenOne = True
                running = 0

        return res + 1 if seenOne else 0

