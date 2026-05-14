# https://leetcode.com/problems/shifting-letters-ii/
# difficulty: medium
# tags: sweep line

# Problem
# You are given a string s of lowercase English letters and a 2D integer array shifts where shifts[i] = [starti, endi, directioni]. For every i, shift the characters in s from the index starti to the index endi (inclusive) forward if directioni = 1, or shift the characters backward if directioni = 0.

# Shifting a character forward means replacing it with the next letter in the alphabet (wrapping around so that 'z' becomes 'a'). Similarly, shifting a character backward means replacing it with the previous letter in the alphabet (wrapping around so that 'a' becomes 'z').

# Return the final string after all such shifts to s are applied.

# Solution, O(n) time and O(n) space since we return a string, just standard sweep line

def getCode(letter):
    return ord(letter) - ord('a')

class Solution:
    def shiftingLetters(self, s: str, shifts: List[List[int]]) -> str:
        sweep = [0 for _ in range(len(s) + 1)]
        for start, end, dir in shifts:
            sweep[start] += (1 if dir else -1)
            sweep[end + 1] -= (1 if dir else -1)
        running = 0
        for i in range(len(sweep)):
            running += sweep[i]
            sweep[i] = running
        sweep.pop()

        for i in range(len(s)):
            char = s[i]
            newOrd = (getCode(char) + sweep[i]) % 26
            sweep[i] = chr(newOrd + ord('a'))
        return ''.join(sweep)

