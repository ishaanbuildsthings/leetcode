# https://leetcode.com/problems/number-of-squareful-arrays/description/
# Difficulty: Hard
# Tags: dynamic programming 2d, bit mask

# Problem
# An array is squareful if the sum of every pair of adjacent elements is a perfect square.

# Given an integer array nums, return the number of permutations of nums that are squareful.

# Two permutations perm1 and perm2 are different if there is some index i such that perm1[i] != perm2[i].

# Solution, weak test cases (or maybe just mathematical impossibility) make an n! backtracking solution work. I wasn't sure at the time so I did dp. The dp state is the mask of digits picked, and we know we are done if we have used every digit. We also need to know the last digit, so we can test which digits to select. To initialize the root call I say the previous digit is -1 and add a condition if the previous digit is -1 we can use any leading digit. Also since digits can be duplicated, we divide by the count of each. For instance [2, 2, 2] has 6 permutations, but we divide by 3! to remove symmetry.
# O(n * 2^n) space, O(n * 2^n * n) time.

class Solution:
    def numSquarefulPerms(self, nums: List[int]) -> int:
        # helps know when we have used all numbers
        fullMask = 0
        for bit in range(len(nums)):
            fullMask = fullMask | (1 << bit)

        # memo[mask of digits used][prev digit]
        @cache
        def dp(mask, prevDigit):
            # base case, we have used every number
            if mask == fullMask:
                return 1

            resForThis = 0

            for i, nextNum in enumerate(nums):
                # if we used that number before, skip it
                if mask & (1 << i):
                    continue

                adjSum = prevDigit + nextNum
                # if we don't form a square, and we aren't taking a first number
                if prevDigit != -1 and not int(adjSum ** 0.5) ** 2 == adjSum:
                    continue
                newMask = mask | (1 << i)
                resForThis += dp(newMask, nextNum)

            return resForThis

        permutations = dp(0, -1)
        # we might have repeated digits, like 2, 2, 7
        counts = collections.Counter(nums)
        for key in counts:
            permutations /= math.factorial(counts[key])
        return int(permutations)

