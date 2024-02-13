# https://leetcode.com/problems/find-first-palindromic-string-in-the-array/
# Difficulty: easy
# tags: palindrome

# Problem
# Given an array of strings words, return the first palindromic string in the array. If there is no such string, return an empty string "".

# A string is palindromic if it reads the same forward and backward.

# Solution
# O(chars) time, O(1) space

class Solution:
    def firstPalindrome(self, words: List[str]) -> str:
        for word in words:
            l = 0
            r = len(word) - 1
            isPal = True
            while l < r:
                if word[l] == word[r]:
                    l += 1
                    r -= 1
                else:
                    isPal = False
                    break
            if isPal:
                return word


        return ''
