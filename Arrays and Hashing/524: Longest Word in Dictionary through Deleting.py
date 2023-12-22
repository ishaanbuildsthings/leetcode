# https://leetcode.com/problems/longest-word-in-dictionary-through-deleting/description/
# difficulty: medium

# Problem
# Given a string s and a string array dictionary, return the longest string in the dictionary that can be formed by deleting some of the given string characters. If there is more than one possible result, return the longest word with the smallest lexicographical order. If there is no possible result, return the empty string.

# Solution
# Two pointers on each word, O(n*m) time and O(1) space or max(len(word)) if you want to be specific, can optimize most likely by sorting long length to short length words

class Solution:
    def findLongestWord(self, s: str, dictionary: List[str]) -> str:
        def isSubseq(big, small):
            i = 0
            j = 0
            while i < len(big):
                if big[i] == small[j]:
                    j += 1
                if j == len(small):
                    return True
                i += 1
            return False

        res = ''
        for sub in dictionary:
            if isSubseq(s, sub):
                if len(sub) > len(res) or (len(sub) == len(res) and sub < res):
                    res = sub
        return res
