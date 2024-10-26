# https://leetcode.com/problems/count-number-of-homogenous-substrings/description/?envType=daily-question&envId=2023-11-09
# difficulty: medium
# tags: kadane's

# Problem
# Given a string s, return the number of homogenous substrings of s. Since the answer may be too large, return it modulo 109 + 7.

# A string is homogenous if all the characters of the string are the same.

# A substring is a contiguous sequence of characters within a string.

# Solution, O(n) time, O(1) space. Just iterate, track the current width, and accumulate the result.

MOD = 10**9 + 7

class Solution:
    def countHomogenous(self, s: str) -> int:
        res = 0
        width = 1
        for i in range(len(s)):
            if i == 0:
                res += 1
                continue
            if s[i] == s[i - 1]:
                width += 1
            else:
                width = 1
            res = (res + width) % MOD
        return res

