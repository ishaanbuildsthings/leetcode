# https://leetcode.com/problems/find-the-shortest-superstring/
# difficulty: hard
# tags: dynamic programming 2d, bit mask

# Problem
# Given an array of strings words, return the smallest string that contains each string in words as a substring. If there are multiple valid strings of the smallest length, return any of them.

# You may assume that no string in words is a substring of another string in words.

# Solution
# Did bitmask dp. also kept parent pointers to reconstruct the path.

class Solution:
    def shortestSuperstring(self, words: List[str]) -> str:
        fullMask = (1 << (len(words))) - 1
        nextWord = {} # maps a dp state to the optimal next word
        nextState = {} # maps a dp state to the next dp state, not strictly needed

        @cache
        def dp(mask, prev):
            # base case
            if mask == fullMask:
                return 0
            resThis = float('inf')
            for i in range(len(words)):
                if mask & (1 << i):
                    continue
                dupeCount = squish(prev, words[i])
                nextDp = len(words[i]) - dupeCount + dp(mask | (1 << i), words[i])
                if nextDp < resThis:
                    resThis = nextDp
                    nextWord[(mask, prev)] = words[i]
                    nextState[(mask, prev)] = (mask | (1 << i), words[i])
            return resThis

        @cache
        def squish(w1, w2):
            dupeCount = 0
            for suffixLength in range(1, len(w1) + 1):
                suffix = w1[len(w1) - suffixLength:]
                prefix = w2[:suffixLength]
                if suffix == prefix:
                    dupeCount = suffixLength
            return dupeCount

        dp(0, '')

        resArr = []

        prevState = (0, '')
        while len(resArr) != len(words):
            newWord = nextWord[prevState]
            resArr.append(newWord)
            prevState = nextState[prevState]
        resArrFinal = []
        for i in range(len(resArr) - 1):
            squishCount = squish(resArr[i], resArr[i + 1])
            word = resArr[i]
            resArrFinal.append(word[:len(word) - squishCount])
        resArrFinal.append(resArr[-1])

        return ''.join(resArrFinal)

