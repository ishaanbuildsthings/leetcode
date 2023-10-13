# https://leetcode.com/problems/maximum-number-of-words-found-in-sentences/
# difficulty: easy

# Problem
# A sentence is a list of words that are separated by a single space with no leading or trailing spaces.

# You are given an array of strings sentences, where each sentences[i] represents a single sentence.

# Return the maximum number of words that appear in a single sentence.

# Solution, O(chars) time, O(1) space

def countSpaces(s):
    spaces = 0
    for char in s:
        if char == ' ':
            spaces += 1
    return spaces

class Solution:
    def mostWordsFound(self, sentences: List[str]) -> int:
        return max([countSpaces(sentence) for sentence in sentences]) + 1