# https://leetcode.com/problems/replace-all-digits-with-characters/
# difficulty: easy

# Problem
# You are given a 0-indexed string s that has lowercase English letters in its even indices and digits in its odd indices.

# There is a function shift(c, x), where c is a character and x is a digit, that returns the xth character after c.

# For example, shift('a', 5) = 'f' and shift('x', 0) = 'x'.
# For every odd index i, you want to replace the digit s[i] with shift(s[i-1], s[i]).

# Return s after replacing all digits. It is guaranteed that shift(s[i-1], s[i]) will never exceed 'z'.

# Solution, just construct the array, O(n) time and space

class Solution:
    def replaceDigits(self, s: str) -> str:
        def getNewChar(oldChar, shiftAmount):
            newOrd = ord(oldChar) + shiftAmount
            newChar = chr(newOrd)
            return newChar

        resArr = []
        for i in range(0, len(s), 2):
            char = s[i]
            if i + 1 == len(s):
                resArr.append(char)
                break
            num = int(s[i + 1])
            newChar = getNewChar(char, num)
            resArr.append(char)
            resArr.append(newChar)

        return ''.join(resArr)