# https://leetcode.com/problems/determine-if-two-strings-are-close/?envType=daily-question&envId=2024-01-14
# difficulty: medium

# Problem
# Two strings are considered close if you can attain one from the other using the following operations:

# Operation 1: Swap any two existing characters.
# For example, abcde -> aecdb
# Operation 2: Transform every occurrence of one existing character into another existing character, and do the same with the other character.
# For example, aacabb -> bbcbaa (all a's turn into b's, and all b's turn into a's)
# You can use the operations on either string as many times as necessary.

# Given two strings, word1 and word2, return true if word1 and word2 are close, and false otherwise.

# Solution
# Standard counter solution

class Solution:
    def closeStrings(self, word1: str, word2: str) -> bool:
        c1 = Counter(word1)
        frqs = sorted(list(c1[key] for key in c1))
        c2 = Counter(word2)
        frqs2 = sorted(list(c2[key] for key in c2))
        for key in c2:
            if not key in c1:
                return False
        return frqs == frqs2