# https://leetcode.com/problems/check-whether-two-strings-are-almost-equivalent/description/
# difficulty: easy

# Solution, O(n+m) time O(26) space

class Solution:
    def checkAlmostEquivalent(self, word1: str, word2: str) -> bool:
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        c1 = Counter(word1)
        c2 = Counter(word2)
        return all(
            abs((c1[char]) - (c2[char])) <= 3
            for char in ABC
        )