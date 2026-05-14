# https://leetcode.com/problems/minimum-moves-to-convert-string/description/
# difficulty: easy

# Problem
# You are given a string s consisting of n characters which are either 'X' or 'O'.

# A move is defined as selecting three consecutive characters of s and converting them to 'O'. Note that if a move is applied to the character 'O', it will stay the same.

# Return the minimum number of moves required so that all the characters of s are converted to 'O'.

# Solution, O(n) time O(1) space
class Solution:
    def minimumMoves(self, s: str) -> int:
        res = 0
        i = 0
        while i < len(s):
            if s[i] == 'X':
                res += 1
                i += 3
            else:
                i += 1

        return res