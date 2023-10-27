# https://leetcode.com/problems/check-if-the-sentence-is-pangram/
# difficulty: easy

# Problem
# A pangram is a sentence where every letter of the English alphabet appears at least once.

# Given a string sentence containing only lowercase English letters, return true if sentence is a pangram, or false otherwise.

# Solution, O(n) time and O(1) space, early terminate

class Solution:
    def checkIfPangram(self, sentence: str) -> bool:
        has = 0
        chars = defaultdict(int)
        for char in sentence:
            if not chars[char]:
                chars[char] += 1
                has += 1
            if has == 26:
                return True
        return False