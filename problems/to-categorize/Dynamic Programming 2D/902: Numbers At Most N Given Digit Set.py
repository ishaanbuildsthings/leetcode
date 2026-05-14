# https://leetcode.com/problems/numbers-at-most-n-given-digit-set/description/
# Difficulty: Hard
# Tags: digit dp

# Problem
# Given an array of digits which is sorted in non-decreasing order. You can write numbers using each digits[i] as many times as we want. For example, if digits = ['1','3','5'], we may write numbers such as '13', '551', and '1351315'.

# Return the number of positive integers that can be generated that are less than or equal to a given integer n.

# Solution, log(n) * 2 * 2 space, 10 times that for time.
# We need the typical index and tight. We also need to know if we are leading zeroes / if a non zero is taken. We can always add a 0 as a digit if we haven't used a non zero yet, this lets us access numbers shorter than n.
# can probably compress the for loop in some way

class Solution:
    def atMostNGivenDigitSet(self, digits: List[str], n: int) -> int:
        digits.insert(0, '0') # we can always use a 0 at the beginning
        strNum = str(n)
        @cache
        # memo[i][tight][is leading zeroes]
        def dp(i, tight, isLeadingZeroes):
            # base case
            if i == len(strNum):
                return 1

            resForThis = 0
            upperBoundary = int(strNum[i]) if tight else int(digits[-1])
            lowerBoundary = 0 if isLeadingZeroes else 1
            for digit in range(lowerBoundary, upperBoundary + 1):
                # only allowed to use digits in the given array
                if not str(digit) in digits:
                    continue
                # cannot use a 0 if we arent leading 0s
                if digit == 0 and not isLeadingZeroes:
                    continue
                newIsLeadingZeroes = isLeadingZeroes and digit == 0
                newTight = tight and digit == upperBoundary
                resForThis += dp(i + 1, newTight, newIsLeadingZeroes)
            return resForThis
        return dp(0, True, True) - 1 # don't count the number that is all 0s