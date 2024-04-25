# https://leetcode.com/problems/remove-palindromic-subsequences/description/
# difficulty: easy
# tags: palindrome, subsequence

# Solution, O(n) time O(1) space
class Solution:
    def removePalindromeSub(self, s: str) -> int:
        return 1 if all(
            s[i] == s[(len(s)) - i - 1]
            for i in range(len(s) // 2)
        ) else 2