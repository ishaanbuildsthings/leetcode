# https://leetcode.com/problems/largest-substring-between-two-equal-characters/
# difficulty: easy

# Problem
# Given a string s, return the length of the longest substring between two equal characters, excluding the two characters. If there is no such substring return -1.

# A substring is a contiguous sequence of characters within a string.

# Solution, O(1*n) time and O(26) space, just count the outer positions of each letter

ABC = 'abcdefghijklmnopqrstuvwxyz'

class Solution:
    def maxLengthBetweenEqualCharacters(self, s: str) -> int:
        outers = defaultdict(lambda: [float('inf'), float('-inf')])
        for i, c in enumerate(s):
            outers[c][0] = min(outers[c][0], i)
            outers[c][1] = max(outers[c][1], i)
        res = max(outers[c][1] - outers[c][0] - 1 for c in ABC)
        return res if res != float('-inf') else -1