# https://leetcode.com/problems/longest-palindrome/
# difficulty: easy
# tags: palindrome, greedy

# Problem

# Given a string s which consists of lowercase or uppercase letters, return the length of the longest palindrome that can be built with those letters.

# Letters are case sensitive, for example, "Aa" is not considered a palindrome here.

# Solution, O(n) time and O(1) space, just greedily select

class Solution:
    def longestPalindrome(self, s: str) -> int:
        counts = collections.Counter(s)

        res = 0
        oddSeen = False
        for key in counts:
            count = counts[key]
            if count % 2 == 0:
                res += count
            else:
                res += (count - 1)
                oddSeen = True
        res += oddSeen
        return res