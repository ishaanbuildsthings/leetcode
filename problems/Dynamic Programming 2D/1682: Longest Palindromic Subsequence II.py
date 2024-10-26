# https://leetcode.com/problems/longest-palindromic-subsequence-ii/description/
# difficulty: medium
# tags: dynamic programming 2d

# Problem
# A subsequence of a string s is considered a good palindromic subsequence if:

# It is a subsequence of s.
# It is a palindrome (has the same value if reversed).
# It has an even length.
# No two consecutive characters are equal, except the two middle ones.
# For example, if s = "abcabcabb", then "abba" is considered a good palindromic subsequence, while "bcb" (not even length) and "bbbb" (has equal consecutive characters) are not.

# Given a string s, return the length of the longest good palindromic subsequence in s.

# Solution, O(n^2 * time) time and space, standard dp

class Solution:
    def longestPalindromeSubseq(self, s: str) -> int:
        @cache
        def dp(l, r, outerChar):
            # base case
            if l >= r:
                return 0

            if s[l] == s[r] != outerChar:
                return 2 + dp(l + 1, r - 1, s[l])

            return max(
                dp(l + 1, r, outerChar),
                dp(l, r - 1, outerChar)
            )

        return dp(0, len(s) - 1, 'G')