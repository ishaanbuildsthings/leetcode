# https://leetcode.com/problems/valid-palindrome-iv/
# difficulty: medium
# tags: two pointers

# problem
# You are given a 0-indexed string s consisting of only lowercase English letters. In one operation, you can change any character of s to any other character.

# Return true if you can make s a palindrome after performing exactly one or two operations, or return false otherwise.

# Solution, O(n) time and O(1) space, iterate from left and right and allow up to 2 changes

class Solution:
    def makePalindrome(self, s: str) -> bool:
        l = 0
        r = len(s) - 1
        changesMade = 0
        while l < r:
            if s[l] != s[r]:
                if changesMade == 2:
                    return False
                changesMade += 1
            l += 1
            r -= 1
        return True