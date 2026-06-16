# https://leetcode.com/problems/sort-characters-by-frequency/
# difficulty: medium

# Problem
# Given a string s, sort it in decreasing order based on the frequency of the characters. The frequency of a character is the number of times it appears in the string.

# Return the sorted string. If there are multiple answers, return any of them.

# Solution
# O(n) time O(n) space, standard counter stuff, can do O(1) space in C

class Solution:
    def frequencySort(self, s: str) -> str:
        counts = Counter(s)
        sortedKeys = sorted(counts, key=counts.get, reverse=True)
        resArr = []
        for char in sortedKeys:
            resArr.extend(char for i in range(counts[char]))
        return ''.join(resArr)
