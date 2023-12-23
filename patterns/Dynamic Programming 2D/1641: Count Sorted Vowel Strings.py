# https://leetcode.com/problems/count-sorted-vowel-strings/description/
# difficulty: medium
# tags: dynamic programming 2d, digit dp

# Problem
# Given an integer n, return the number of strings of length n that consist only of vowels (a, e, i, o, u) and are lexicographically sorted.

# A string s is lexicographically sorted if for all valid i, s[i] is the same as or comes before s[i+1] in the alphabet.

# Solution, O(5 * 5 * n) time, O(5 * n) space
# Standard digit DP style solution
# can probably save on some iterations in the for loop, maybe start from the prev, reading this problem back later so not 100% sure but seems like it

class Solution:
    def countVowelStrings(self, n: int) -> int:
        @cache
        def dp(prev, i):
            # base case
            if i == n:
                return 1

            resForThis = 0

            for vowel in 'AEIOU':
                if vowel < prev:
                    continue
                resForThis += dp(vowel, i + 1)

            return resForThis
        return dp('A', 0)
