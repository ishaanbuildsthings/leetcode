# https://leetcode.com/problems/check-if-two-string-arrays-are-equivalent/?envType=daily-question&envId=2023-12-01
# difficulty: easy
# tags: two pointers

# Problem
# Given two string arrays word1 and word2, return true if the two arrays represent the same string, and false otherwise.

# A string is represented by an array if the array elements concatenated in order forms the string.

# Solution
# Standard two pointers, O(total chars) time, O(1) space. I think we could technically say the time is chars + words because we do an extra pointer iteration for each word. Like each character triggers a character pointer increase (or a reset to 0), but each word triggers a word pointer increase.

class Solution:
    def arrayStringsAreEqual(self, word1: List[str], word2: List[str]) -> bool:
        wordI = 0
        wordJ = 0
        charI = 0
        charJ = 0
        while wordI < len(word1) and wordJ < len(word2):
            if word1[wordI][charI] != word2[wordJ][charJ]:
                return False
            charI += 1
            charJ += 1
            if charI == len(word1[wordI]):
                charI = 0
                wordI += 1
            if charJ == len(word2[wordJ]):
                charJ = 0
                wordJ += 1
        # validate no chars left
        return wordI == len(word1) and wordJ == len(word2)
