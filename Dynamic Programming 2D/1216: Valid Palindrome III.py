# https://leetcode.com/problems/valid-palindrome-iii/description/
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# Given a string s and an integer k, return true if s is a k-palindrome.

# A string is k-palindrome if it can be transformed into a palindrome by removing at most k characters from it.

# Solution, O(n^2) time and space
# We just calculate the max changes needed. I initially slipped up trying to insert a kChangesLeft parameter as well.

class Solution:
    def isValidPalindrome(self, s: str, k: int) -> bool:
        @cache
        def dp(l, r):
            # base case
            if r - l + 1 <= 1:
                return 0


            if s[l] == s[r]:
                return dp(l + 1, r - 1)

            else:
                return 1 + min(dp(l + 1, r), dp(l, r - 1))

        return dp(0, len(s) - 1) <= k