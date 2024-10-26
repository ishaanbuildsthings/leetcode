# https://leetcode.com/problems/longest-string-chain/
# difficulty: medium
# tags: dynamic programming 1d

# Problem
# You are given an array of words where each word consists of lowercase English letters.

# wordA is a predecessor of wordB if and only if we can insert exactly one letter anywhere in wordA without changing the order of the other characters to make it equal to wordB.

# For example, "abc" is a predecessor of "abac", while "cba" is not a predecessor of "bcad".
# A word chain is a sequence of words [word1, word2, ..., wordk] with k >= 1, where word1 is a predecessor of word2, word2 is a predecessor of word3, and so on. A single word is trivially a word chain with k == 1.

# Return the length of the longest possible word chain with words chosen from the given list of words.

# Solution, I don't remember solving this, looks a bit like a graph or tree problem with some DP also

class Solution:
    def longestStrChain(self, words: List[str]) -> int:
        # if a is a pred of b
        def isPred(a, b):
            p1 = 0
            p2 = 0
            while p2 < len(b):
                if p1 == len(a):
                    return True
                if a[p1] == b[p2]:
                    p1 += 1
                    p2 += 1
                else:
                    p2 += 1
            if p1 == len(a):
                return True
            return False

        groupBySize = defaultdict(list) # maps a specific length to a list of words that are that length
        for word in words:
            groupBySize[len(word)].append(word)

        preds = defaultdict(list) # maps a word to a list of its predecessors

        for wordLength in range(2, 17):
            biggerBucket = groupBySize[wordLength]
            smallerBucket = groupBySize[wordLength - 1]
            for biggerWord in biggerBucket:
                for smallerWord in smallerBucket:
                    if isPred(smallerWord, biggerWord):
                        preds[biggerWord].append(smallerWord)

        # gets the longest chain starting from that word, we cache because multiple words can have the same predecessor
        @cache
        def dfs(word):
            resForThis = 1
            for pred in preds[word]:
                ifTakeThisChain = 1 + dfs(pred)
                resForThis = max(resForThis, ifTakeThisChain)
            return resForThis
        res = 1
        for word in words:
            res = max(res, dfs(word))
        return res


    #     abc  agc
    #   /     \/
    # ab      ac