# https://leetcode.com/problems/single-row-keyboard/
# difficulty: easy

# Problem
# There is a special keyboard with all keys in a single row.

# Given a string keyboard of length 26 indicating the layout of the keyboard (indexed from 0 to 25). Initially, your finger is at index 0. To type a character, you have to move your finger to the index of the desired character. The time taken to move your finger from index i to index j is |i - j|.

# You want to type a string word. Write a function to calculate how much time it takes to type it with one finger.

# Solution, O(word length) time, O(1) space, we could cache the char positions but it might be slower

class Solution:
    def calculateTime(self, keyboard: str, word: str) -> int:
        res = 0
        pos = 0
        for char in word:
            charPos = keyboard.find(char)
            res += abs(charPos - pos)
            pos = charPos
        return res