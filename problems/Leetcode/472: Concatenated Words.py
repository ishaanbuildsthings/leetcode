# https://leetcode.com/problems/concatenated-words/description/
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# Given an array of strings words (without duplicates), return all the concatenated words in the given list of words.

# A concatenated word is defined as a string that is comprised entirely of at least two shorter words (not necessarily distinct) in the given array.

# Solution
# Run the dp on each word, we can clear cache as needed
class Solution:
    def findAllConcatenatedWordsInADict(self, words: List[str]) -> List[str]:
        wordSet = set(words)

        @cache
        def isWordDoable(word, i):
            # base
            if i == len(word):
                return True

            for allLeft in range(i, len(word)):
                # don't use the entire word
                if i == 0 and allLeft == len(word) - 1:
                    break
                leftRegion = word[i:allLeft + 1]
                if leftRegion in wordSet and isWordDoable(word, allLeft + 1):
                    return True

            return False

        return [word for word in words if isWordDoable(word, 0,)]

