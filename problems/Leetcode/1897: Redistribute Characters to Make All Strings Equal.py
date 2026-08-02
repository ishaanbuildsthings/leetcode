# https://leetcode.com/problems/redistribute-characters-to-make-all-strings-equal/description/?envType=daily-question&envId=2023-12-30
# difficulty: easy
# tags: functional

# Problem
# You are given an array of strings words (0-indexed).

# In one operation, pick two distinct indices i and j, where words[i] is a non-empty string, and move any character from words[i] to any position in words[j].

# Return true if you can make every string in words equal using any number of operations, and false otherwise.

# Solution, O(chars) time and O(26) space, check they can all be divided
class Solution:
    def makeEqual(self, words: List[str]) -> bool:
        accumulatedCounts = Counter(char for word in words for char in word)
        return all(
            math.floor(amount := accumulatedCounts[key] / len(words)) == amount
            for key in accumulatedCounts
        )