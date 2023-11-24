# https://leetcode.com/problems/count-stepping-numbers-in-range/description/
# Difficulty: Hard
# Tags: digit dp

# Problem
# Given two positive integers low and high represented as strings, find the count of stepping numbers in the inclusive range [low, high].

# A stepping number is an integer such that all of its adjacent digits have an absolute difference of exactly 1.

# Return an integer denoting the count of stepping numbers in the inclusive range [low, high].

# Since the answer may be very large, return it modulo 109 + 7.

# Note: A stepping number should not have a leading zero.

# Solution, O(2 * 2 * log(high) * 10) space, and 10 times that for time complexity.

# We need to know the last digit that was taken, so we know what current digit we can take. We need to know if we have taken a non zero, to know if we can only take a 1 (our last digit was 0) or if we can take any number. We need to know the index we are inserting at to know if we are done, and we need tight to know if we are bounded.
# can maybe compress the for loop, didn't read problem but lots of digit DP can be compressed

class Solution:
    def countSteppingNumbers(self, low: str, high: str) -> int:
        # gets us the above and below numbers for a digit, or returns every non-zero digit if the previous is -1, which represents taking our first ever digit. if only 0s have been taken, we can take any number
        def getNewDigits(digit, nonZeroTaken):
            if not nonZeroTaken:
                return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            if digit == -1:
                return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            if digit == 0:
                return [1]
            elif digit == 9:
                return [8]
            else:
                return [digit - 1, digit + 1]

        MOD = (10**9) + 7
        # memo[last digit][index][non zero taken][tight]
        memo = [[[[-1 for _ in range(2)] for _ in range(2)] for _ in range(len(high))] for _ in range(10)]

        def dp(lastDigit, i, nonZeroTaken, tight, strNum):
            # base case, we filled all the numbers
            if i == len(strNum):
                if nonZeroTaken:
                    return 1
                return 0

            if memo[lastDigit][i][nonZeroTaken][tight] != -1:
                return memo[lastDigit][i][nonZeroTaken][tight]

            resForThis = 0

            boundaryDigit = int(strNum[i]) # relevant if tight
            newPossibleDigits = getNewDigits(lastDigit, nonZeroTaken) # not checked based on tight

            for newDigit in newPossibleDigits:
                # can never take a digit if it breaks a tight boundary
                if tight and newDigit > boundaryDigit:
                    continue
                if tight and newDigit == boundaryDigit:
                    newTight = tight
                else:
                    newTight = 0
                if nonZeroTaken:
                    newNonZeroTaken = 1
                else:
                    if newDigit != 0:
                        newNonZeroTaken = 1
                    else:
                        newNonZeroTaken = 0
                resForThis = (resForThis + dp(newDigit, i + 1, newNonZeroTaken, newTight, strNum))

            memo[lastDigit][i][nonZeroTaken][tight] = resForThis
            return resForThis

        highCount = dp(-1, 0, 0, 1, high)
        memo = [[[[-1 for _ in range(2)] for _ in range(2)] for _ in range(len(high))] for _ in range(10)]
        lowCount = dp(-1, 0, 0, 1, str(int(low) - 1))
        return (highCount - lowCount) % MOD