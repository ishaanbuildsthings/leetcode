# https://leetcode.com/problems/v2063owels-of-all-substrings/description/
# difficulty: medium

# Problem
# Given a string word, return the sum of the number of vowels ('a', 'e', 'i', 'o', and 'u') in every substring of word.

# A substring is a contiguous (non-empty) sequence of characters within a string.

# Note: Due to the large constraints, the answer may not fit in a signed 32-bit integer. Please be careful during the calculations.

# Solution, O(n) time and O(1) space, just count the contribution

class Solution:
    def countVowels(self, word: str) -> int:
        res = 0
        for i in range(len(word)):
            if word[i] not in 'aeiou':
                continue
            left = i + 1
            right = len(word) - i
            res += left * right
        return res