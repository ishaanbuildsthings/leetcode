# https://leetcode.com/problems/longest-palindrome-by-concatenating-two-letter-words/description/
# difficulty: medium

# Problem
# You are given an array of strings words. Each element of words consists of two lowercase English letters.

# Create the longest possible palindrome by selecting some elements from words and concatenating them in any order. Each element can be selected at most once.

# Return the length of the longest palindrome that you can create. If it is impossible to create any palindrome, return 0.

# A palindrome is a string that reads the same forward and backward.

# Solution, O(words) space and time, just use a counter, can probably make some small optimizations like decrementing from the counter with the mirror etc

class Solution:
    def longestPalindrome(self, words: List[str]) -> int:
        frqs = Counter(words)
        res = 0
        oddSeen = False
        for key in frqs:
            if key == key[::-1]:
                if frqs[key] % 2 == 1:
                    oddSeen = True
                res += 2 * (frqs[key] if frqs[key] % 2 == 0 else frqs[key] - 1)
                continue
            minCount = min(
                frqs[key],
                frqs[key[::-1]]
                )
            res += 4 * minCount
            frqs[key] -= minCount
            if minCount:
                frqs[key[::-1]] -= minCount
        return res + (2 if oddSeen else 0)