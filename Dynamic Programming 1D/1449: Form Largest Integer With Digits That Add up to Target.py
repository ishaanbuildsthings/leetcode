# https://leetcode.com/problems/form-largest-integer-with-digits-that-add-up-to-target/description/
# Difficulty: Hard
# Tags: dynamic programming 1d

# Problem
# Given an array of integers cost and an integer target, return the maximum integer you can paint under the following rules:

# The cost of painting a digit (i + 1) is given by cost[i] (0-indexed).
# The total cost used must be equal to target.
# The integer does not have 0 digits.
# Since the answer may be very large, return it as a string. If there is no way to paint any integer given the condition, return "0".

# Solution, O(target) time and space
# We have a dp of target remaining. We try selecting up to 10 numbers. Our base case is if we get to exactly 0. If we can't make a reduction we return a flag value None. String math exceeded the python limits, so I stored a number which is why I needed to count digits, adding log(5000) time. Can definitely be optimized but still good in time complexity. At the end I convert the number to an array then string join since direct string conversion failed. Each memo tate holds an answer of size 5000.

class Solution:
    def largestNumber(self, cost: List[int], target: int) -> str:
        @cache
        def countDigits(num):
            digits = 0
            while num > 0:
                num = num // 10
                digits += 1
            return digits

        # memo[targetRemaining] tells us the answer to that subproblem

        @cache
        def dp(targetRemaining):
            # base case
            if targetRemaining == 0:
                return 0 # will count as 0 digits
            if targetRemaining < 0:
                return None

            biggestForThis = 0
            for i in range(9):
                ifWeTakeThisDigitDp = dp(targetRemaining - cost[i])

                # couldn't make a valid continuation from that
                if ifWeTakeThisDigitDp == None:
                    continue

                digitCount = countDigits(ifWeTakeThisDigitDp)
                newNum = ((i + 1) * 10**digitCount) + ifWeTakeThisDigitDp
                biggestForThis = max(biggestForThis, newNum)

            if biggestForThis == 0:
                return None

            # if we can't take any digits we are invalid
            return biggestForThis

        resNum = dp(target)
        if resNum == None:
            return '0'

        # overcome max str conversion on a number
        resArray = []
        while resNum:
            lastDigit = resNum % 10
            resArray.append(lastDigit)
            resNum = resNum // 10
        resArray.reverse()
        resArrayStr = [str(num) for num in resArray]
        return ''.join(resArrayStr)
