# https://leetcode.com/problems/largest-odd-number-in-string/description/?envType=daily-question&envId=2023-12-07
# difficulty: easy
# tags: math, work backwards

# Problem
# You are given a string num, representing a large integer. Return the largest-valued odd integer (as a string) that is a non-empty substring of num, or an empty string "" if no odd integer exists.

# A substring is a contiguous sequence of characters within a string.

# Solution, O(n) time, O(1) space

class Solution:
    def largestOddNumber(self, num: str) -> str:
        for i in range(len(num) - 1, -1, -1):
            if int(num[i]) % 2 == 1:
                return num[:i + 1]
        return ''