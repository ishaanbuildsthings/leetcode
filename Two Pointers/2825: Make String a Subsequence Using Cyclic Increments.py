# https://leetcode.com/problems/make-string-a-subsequence-using-cyclic-increments/description/
# difficulty: medium
# tags: two pointers

# Problem
# You are given two 0-indexed strings str1 and str2.

# In an operation, you select a set of indices in str1, and for each index i in the set, increment str1[i] to the next character cyclically. That is 'a' becomes 'b', 'b' becomes 'c', and so on, and 'z' becomes 'a'.

# Return true if it is possible to make str2 a subsequence of str1 by performing the operation at most once, and false otherwise.

# Note: A subsequence of a string is a new string that is formed from the original string by deleting some (possibly none) of the characters without disturbing the relative positions of the remaining characters.

# Solutionm O(str1) time, O(1) space, standard two pointers, can prune if we don't have enough of str1 left to finish str2

class Solution:
    def canMakeSubsequence(self, str1: str, str2: str) -> bool:
        def isValid(char1, char2):
            if char1 == char2:
                return True
            if ord(char2) == ord(char1) + 1:
                return True
            return (char2 == 'a' and char1 == 'z')

        j = 0
        for i in range(len(str1)):
            if j == len(str2):
                return True
            char1 = str1[i]
            char2 = str2[j]
            if isValid(char1, char2):
                j += 1

        return j == len(str2)