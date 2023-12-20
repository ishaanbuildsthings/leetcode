
# https://leetcode.com/problems/get-equal-substrings-within-budget/
# difficulty: medium
# tags: sliding window variable

# Problem
# You are given two strings s and t of the same length and an integer maxCost.

# You want to change s to t. Changing the ith character of s to ith character of t costs |s[i] - t[i]| (i.e., the absolute difference between the ASCII values of the characters).

# Return the maximum length of a substring of s that can be changed to be the same as the corresponding substring of t with a cost less than or equal to maxCost. If there is no substring from s that can be changed to its corresponding substring from t, return 0.

# Solution
# O(n) time O(1) space, standard sliding window

class Solution:
    def equalSubstring(self, s: str, t: str, maxCost: int) -> int:
        l = 0
        r = 0
        currCost = 0
        res = 0
        while r < len(s):
            newCost = abs(ord(s[r]) - ord(t[r]))
            currCost += newCost
            while currCost > maxCost:
                lostCost = abs(
                    ord(s[l]) - ord(t[l])
                    )
                currCost -= lostCost
                l += 1
            res = max(res, r - l + 1)
            r += 1
        return res
