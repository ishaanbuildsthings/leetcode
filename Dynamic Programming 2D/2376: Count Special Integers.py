# https://leetcode.com/problems/count-special-integers/description/
# Difficulty: Hard
# Tags: digit dp

# Problem
# We call a positive integer special if all of its digits are distinct.

# Given a positive integer n, return the number of special integers that belong to the interval [1, n].

# Solution, O(log n * 2 * 2^(log n)) space, 10 times that for time.
# We need the typical index and tight for digit dp. We also need a mask of which numbers we have taken, we can only take numbers we have not. Which numbers we have taken also informs us if we have taken a non zero which lets us know if we can take a leading 0 or not.
# can maybe compress the for loop, didn't read problem but lots of digit DP can be compressed

class Solution:
    def countSpecialNumbers(self, n: int) -> int:
        strNum = str(n)
        memo = [[[-1 for _ in range(2)] for _ in range(1024)] for _ in range(len(strNum))]

        def dp(index, mask, tight):
            if index == len(strNum):
                # we don't gain a number if we only took 0s
                return 0 if mask == 0 else 1

            if memo[index][mask][tight] != -1:
                return memo[index][mask][tight]

            # what we can go up to if we are tight
            tightBound = int(strNum[index])
            upperBound = tightBound if tight else 9

            resForThis = 0

            for digit in range(upperBound + 1):
                # skip numbers we already took
                if (mask >> digit) & 1:
                    continue

                # if we were tight, and we took the top digit, we are still tight
                # if we weren't tight, or we broke the tightness, we aren't
                newTight = 1 if tight and digit == int(strNum[index]) else 0

                # we can always take a 0 if we are still leading
                # once we stop leading (our mask is > 0), then we cannot take a 0 anymore
                if digit == 0:
                    # if we have already taken a number, now we need to mark the 0 as taken
                    # to prevent numbers like 100 from being counted as special
                    newMask = mask | 1 if mask > 0 else mask
                else:
                    newMask = mask | (1 << digit)

                resForThis += dp(index + 1, newMask, newTight)

            memo[index][mask][tight] = resForThis
            return resForThis

        return dp(0, 0, 1)
