# https://leetcode.com/problems/number-of-even-and-odd-bits/
# Difficulty: easy
# tags: bit manipulation

# Problem
# You are given a positive integer n.

# Let even denote the number of even indices in the binary representation of n (0-indexed) with value 1.

# Let odd denote the number of odd indices in the binary representation of n (0-indexed) with value 1.

# Return an integer array answer where answer = [even, odd].

# Solution, O(1 or log n) time, O(1) space, count bits

class Solution:
    def evenOddBit(self, n: int) -> List[int]:
        evenBits = 0
        oddBits = 0
        for bit in range(10):
            if (n >> bit) & 1:
                if bit % 2 == 0:
                    evenBits += 1
                else:
                    oddBits += 1
        return [evenBits, oddBits]