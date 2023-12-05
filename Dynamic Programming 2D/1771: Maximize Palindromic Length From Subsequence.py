# https://leetcode.com/problems/maximize-palindrome-length-from-subsequences/
# Difficulty: hard
# Tags: dynamic programming 2d, subsequence, palindrome

# Problem
# You are given two strings, word1 and word2. You want to construct a string in the following manner:

# Choose some non-empty subsequence subsequence1 from word1.
# Choose some non-empty subsequence subsequence2 from word2.
# Concatenate the subsequences: subsequence1 + subsequence2, to make the string.
# Return the length of the longest palindrome that can be constructed in the described manner. If no palindromes can be constructed, return 0.

# A subsequence of a string s is a string that can be made by deleting some (possibly none) characters from s without changing the order of the remaining characters.

# A palindrome is a string that reads the same forward as well as backward.

# Solution
# I combined the strings then did a LPS where we have to take at least one from the left and one from the right. O((n+m)^2) time and space.

class Solution:
    def longestPalindrome(self, word1: str, word2: str) -> int:
        word = word1 + word2

        @cache
        def dp(l, r, lTaken, rTaken):
            # base case
            if l > r:
                return 0 if lTaken and rTaken else float('-inf')

            # pruning
            if not lTaken and l >= len(word1):
                return float('-inf')
            if not rTaken and r < len(word1):
                return float('-inf')

            # if they are the same, we must take them
            if word[l] == word[r]:
                newLTaken = lTaken or l < len(word1)
                newRTaken = rTaken or r >= len(word1)
                if l == r:
                    return 1 + dp(l + 1, r - 1, newLTaken, newRTaken)
                return 2 + dp(l + 1, r - 1, newLTaken, newRTaken)

            # if they are different, we have two options
            # skip left
            option1 = dp(l + 1, r, lTaken, rTaken)
            option2 = dp(l, r - 1, lTaken, rTaken)

            return max(option1, option2)

        res = dp(0, len(word) - 1, False, False)
        dp.cache_clear() # leetcode
        return max(res, 0)
