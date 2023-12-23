# https://leetcode.com/problems/count-asterisks/description/
# Difficulty: Easy

# Problem
# You are given a string s, where every two consecutive vertical bars '|' are grouped into a pair. In other words, the 1st and 2nd '|' make a pair, the 3rd and 4th '|' make a pair, and so forth.

# Return the number of '*' in s, excluding the '*' between each pair of '|'.

# Note that each '|' will belong to exactly one pair.

# Solution, O(n) time, O(1) space
# Maintain a state if we are accepting asterisks or not.

class Solution:
    def countAsterisks(self, s: str) -> int:
        state = 'open'
        res = 0
        asterisks = 0 # accumulate while state is open
        for char in s:
            if char == '*' and state == 'open':
                asterisks += 1
            elif char == '|':
                if state == 'open':
                    res += asterisks
                    asterisks = 0
                    state = 'closed'
                else:
                    state = 'open'
        res += asterisks
        return res