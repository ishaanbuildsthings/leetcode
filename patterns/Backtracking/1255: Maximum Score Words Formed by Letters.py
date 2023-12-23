# https://leetcode.com/problems/maximum-score-words-formed-by-letters/description/
# difficulty: hard
# tags: backtracking

# problem
# Given a list of words, list of  single letters (might be repeating) and score of every character.

# Return the maximum score of any valid set of words formed by using the given letters (words[i] cannot be used two or more times).

# It is not necessary to use all characters in letters and each letter can only be used once. Score of letters 'a', 'b', 'c', ... ,'z' is given by score[0], score[1], ... , score[25] respectively.

# Solution, backtrack, try making a word or not. 2^words time and words space for the callstack. 26 is a constant factor.

abc = 'abcdefghijklmnopqrstuvwxyz'

class Solution:
    def maxScoreWords(self, words: List[str], letters: List[str], score: List[int]) -> int:
        scoreMap = {} # maps a letter to its score
        for i in range(26):
            scoreMap[abc[i]] = score[i]

        res = 0
        charCounts = collections.Counter(letters) # we will track how many letters we have left

        # i is the position of the word we might make
        def backtrack(i, accScore):
            nonlocal res

            if i == len(words):
                res = max(res, accScore)
                return

            # if we take the word, if we can
            wordCounts = collections.Counter(words[i])
            insufficientFound = False
            for char in wordCounts.keys():
                if charCounts[char] < wordCounts[char]:
                    insufficientFound = True
                    break
            # we can take the word
            if not insufficientFound:
                addedScore = 0
                for char in wordCounts.keys():
                    amount = wordCounts[char]
                    charCounts[char] -= amount
                    addedScore += wordCounts[char] * scoreMap[char]
                backtrack(i + 1, accScore + addedScore)
                # remove the chars
                for char in wordCounts.keys():
                    amount = wordCounts[char]
                    charCounts[char] += amount

            # if we skip the word
            backtrack(i + 1, accScore)

        backtrack(0, 0)
        return res




