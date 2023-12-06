# https://leetcode.com/problems/calculate-money-in-leetcode-bank/description/?envType=daily-question&envId=2023-12-06
# difficulty: easy
# tags: math

# Problem
# Hercy wants to save money for his first car. He puts money in the Leetcode bank every day.

# He starts by putting in $1 on Monday, the first day. Every day from Tuesday to Sunday, he will put in $1 more than the day before. On every subsequent Monday, he will put in $1 more than the previous Monday.
# Given n, return the total amount of money he will have in the Leetcode bank at the end of the nth day.

# Solution, O(1) time and space, basic math

class Solution:
    def totalMoney(self, n: int) -> int:
        # week1 = 1 + 2 + 3 + 4 + 5 + 6 + 7 28
        # week2 = 35
        fullWeeks = n // 7
        res = 0
        res += 28 * fullWeeks
        # now we need to add 0 7 14 21 28 35 ..., which is 7 * (0 1 2 3 4) which is 7 * the equation
        res += 7 * (fullWeeks*(fullWeeks-1) / 2)

        extraDays = n % 7

        lastWeek = fullWeeks + 1

        nextToAdd = lastWeek
        for day in range(extraDays):
            res += nextToAdd
            nextToAdd += 1

        return int(res)