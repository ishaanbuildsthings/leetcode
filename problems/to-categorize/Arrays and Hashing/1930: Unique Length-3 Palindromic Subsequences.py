# https://leetcode.com/problems/unique-length-3-palindromic-subsequences/description/
# difficulty: medium

# problem
# Given a string s, return the number of unique palindromes of length three that are a subsequence of s.

# Note that even if there are multiple ways to obtain the same subsequence, it is still only counted once.

# A palindrome is a string that reads the same forwards and backwards.

# A subsequence of a string is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.

# For example, "ace" is a subsequence of "abcde".

# Maintain a rolling count of letters on the left and on the right. For each index, remove from the left/add to the right. Check each letter. For instance for b, check all letters on left and right, if there is a match add it to the seen set.

class Solution:
    def countPalindromicSubsequence(self, s: str) -> int:
        onRight = collections.Counter(s)
        onRight[s[0]] -= 1
        onLeft = defaultdict(int)
        seen = set()
        for i in range(1, len(s)):
            # once we take a number, we gain the on left of the prior number, but we lose that in the on right
            prior = s[i - 1]
            onLeft[prior] += 1
            onRight[s[i]] -= 1
            for char in onLeft.keys():
                if char in onRight:
                    if onRight[char] > 0:
                        seen.add(char + s[i] + char)
        return len(seen)