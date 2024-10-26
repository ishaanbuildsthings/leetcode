# https://leetcode.com/problems/maximum-value-after-insertion/
# Difficulty: Medium

# Problem
# You are given a very large integer n, represented as a string,​​​​​​ and an integer digit x. The digits in n and the digit x are in the inclusive range [1, 9], and n may represent a negative number.

# You want to maximize n's numerical value by inserting x anywhere in the decimal representation of n​​​​​​. You cannot insert x to the left of the negative sign.

# For example, if n = 73 and x = 6, it would be best to insert it between 7 and 3, making n = 763.
# If n = -55 and x = 2, it would be best to insert it before the first 5, making n = -255.
# Return a string representing the maximum value of n​​​​​​ after the insertion.

# Solution, O(n) time, O(1) space
# Just try a different strategy for positive or for negative, they are easy to derive. A few edge cases.

class Solution:
    def maxValue(self, n: str, x: int) -> str:
        # if positive, find the first index on the right smaller than us, then insert
        if n[0] != '-':
            for rightPosition in range(len(n)):
                if int(n[rightPosition]) < x:
                    return n[:rightPosition] + str(x) + n[rightPosition:]
            # edge case
            return n + str(x)


        # if negative, as soon as we find a number on the right bigger than us, insert
        for rightPosition in range(1, len(n)):
            if int(n[rightPosition]) > x:
                return n[:rightPosition] + str(x) + n[rightPosition:]

        # edge case, all values are the same
        return n + str(x)