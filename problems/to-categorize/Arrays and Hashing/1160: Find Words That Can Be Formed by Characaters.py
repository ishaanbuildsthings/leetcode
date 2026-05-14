# https://leetcode.com/problems/find-words-that-can-be-formed-by-characters/
# difficulty: easy

# Problem
# You are given an array of strings words and a string chars.

# A string is good if it can be formed by characters from chars (each character can only be used once).

# Return the sum of lengths of all good strings in words.

# Solution, O(all chars) time, O(1) space, count # chars in chars, then for each word in words, count chars, compare up to 26 chars

class Solution:
    def countCharacters(self, words: List[str], chars: str) -> int:
        res = 0
        charCount = collections.Counter(chars)
        for word in words:
            wordCount = collections.Counter(word)
            errorFound = False
            for char in word:
                if wordCount[char] > charCount[char]:
                    errorFound = True
                    break
            if not errorFound:
                res += len(word)
        return res