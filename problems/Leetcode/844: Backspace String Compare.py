# https://leetcode.com/problems/backspace-string-compare/?envType=daily-question&envId=2023-10-19
# Difficulty: Easy
# tags: work backwards, two pointers, stack

# Problem
# Given two strings s and t, return true if they are equal when both are typed into empty text editors. '#' means a backspace character.

# Note that after backspacing an empty text, the text will continue empty.

# Solution
# O(1) space can be done by iterating backwards.

class Solution:
    def backspaceCompare(self, s: str, t: str) -> bool:
        stackS = []
        stackT = []
        for char in s:
            if char == '#' and stackS:
                stackS.pop()
            else:
                if char != '#':
                    stackS.append(char)
        for char in t:
            if char == '#' and stackT:
                stackT.pop()
            else:
                if char != '#':
                    stackT.append(char)
        return ''.join(stackS) == ''.join(stackT)


