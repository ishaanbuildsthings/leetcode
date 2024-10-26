# https://leetcode.com/problems/longest-ideal-subsequence/description/?envType=daily-question&envId=2024-04-25
# difficulty: medium
# tags: dynamic programming 1d, bottom up recursion

# Solution, O(26n) time O(26) space, could make cache have unique(s) chars instead

class Solution:
    def longestIdealString(self, s: str, k: int) -> int:
        def alphaDifference(char1, char2):
            return abs(ord(char1) - ord(char2))

        ABC = 'abcdefghijklmnopqrstuvwxyz'
        cache = {
            char : 0 for char in ABC
        }

        for i in range(len(s)):
            currChar = s[i]
            cache[currChar] += 1
            for prevChar in cache:
                if prevChar == currChar:
                    continue
                if alphaDifference(prevChar, currChar) <= k or cache[prevChar] == 0:
                    cache[currChar] = max(cache[currChar], cache[prevChar] + 1)

        return max(cache.values())
