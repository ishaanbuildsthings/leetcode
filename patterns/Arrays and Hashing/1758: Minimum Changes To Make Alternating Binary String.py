# https://leetcode.com/problems/minimum-changes-to-make-alternating-binary-string/description/?envType=daily-question&envId=2023-12-24
# difficulty: easy

# Problem
# You are given a string s consisting only of the characters '0' and '1'. In one operation, you can change any '0' to '1' or vice versa.

# The string is called alternating if no two adjacent characters are equal. For example, the string "010" is alternating, while the string "0100" is not.

# Return the minimum number of operations needed to make s alternating.

# Solution, O(n) time O(1) space
class Solution:
    def minOperations(self, s: str) -> int:
        startWithZero = 0
        startWithOne = 0
        for i in range(len(s)):
            if i % 2 == 0:
                startWithZero += s[i] == '1'
                startWithOne += s[i] == '0'
            else:
                startWithZero += s[i] == '0'
                startWithOne += s[i] == '1'
        return min(startWithZero, startWithOne)


