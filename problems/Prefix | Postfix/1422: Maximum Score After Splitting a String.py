# https://leetcode.com/problems/maximum-score-after-splitting-a-string/description/
# difficulty: easy
# tags: prefix, postfix

# Problem
# Given a string s of zeros and ones, return the maximum score after splitting the string into two non-empty substrings (i.e. left substring and right substring).

# The score after splitting a string is the number of zeros in the left substring plus the number of ones in the right substring.

# Solution, O(n) time and O(1) space. Standard two pass. There is a brilliant one pass solution in the solutions tab though.

class Solution:
    def maxScore(self, s: str) -> int:
        rightOnes = s.count('1')
        leftZeroes = 0

        res = 0
        for i in range(len(s) - 1):
            if s[i] == '0':
                leftZeroes += 1
            elif s[i] == '1':
                rightOnes -= 1
            res = max(res, leftZeroes + rightOnes)

        return res

