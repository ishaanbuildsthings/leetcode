# https://leetcode.com/problems/split-strings-by-separator/
# difficulty: easy

# problem
# Given an array of strings words and a character separator, split each string in words by separator.

# Return an array of strings containing the new strings formed after the splits, excluding empty strings.

# Notes

# separator is used to determine where the split should occur, but it is not included as part of the resulting strings.
# A split may result in more than two strings.
# The resulting strings must maintain the same order as they were initially given.

# Solution, O(words * word length + total words) time, O(max(max(wordstr), total words)) space or something like that lol
# Separate each wordstr which takes O(wordstr) time and space. For each word, add it to the res. I did use linear memory at the end with a list comprehension which could be avoided.

class Solution:
    def splitWordsBySeparator(self, words: List[str], separator: str) -> List[str]:
        res = []
        for wordstr in words:
            res.extend(wordstr.split(separator))
        return [item for item in res if item] # filter empty if the separators were on the ends
