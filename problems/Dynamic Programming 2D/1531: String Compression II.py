# https://leetcode.com/problems/string-compression-ii/description/?envType=daily-question&envId=2023-12-28
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# Run-length encoding is a string compression method that works by replacing consecutive identical characters (repeated 2 or more times) with the concatenation of the character and the number marking the count of the characters (length of the run). For example, to compress the string "aabccc" we replace "aa" by "a2" and replace "ccc" by "c3". Thus the compressed string becomes "a2bc3".

# Notice that in this problem, we are not adding '1' after single characters.

# Given a string s and an integer k. You need to delete at most k characters from s such that the run-length encoded version of s has minimum length.

# Find the minimum length of the run-length encoded version of s after deleting at most k characters.

# Solution
# At first I tried dp where I jump / scan, but I think it might not work. Instead do dp on each character if we delete it or not, maintain the previous streak and type. O(n*k*n*26) time and space

class Solution:
    def getLengthOfOptimalCompression(self, s: str, k: int) -> int:
        @cache
        def dp(i, delRemain, prevStreak, prevType):
            # base
            if i == len(s):
                if prevStreak <= 1:
                    return prevStreak
                return 1 + len(str(prevStreak))

            ifDelete = (
                dp(i + 1, delRemain - 1, prevStreak, prevType) if
                delRemain > 0 else
                float('inf'))

            # if we don't delete
            newPrevStreak = prevStreak + 1 if s[i] == prevType else 1
            ifNoDelete = dp(i + 1, delRemain, newPrevStreak, s[i])
            if prevType != s[i]:
                prevLength = prevStreak if prevStreak <= 1 else 1 + len(str(prevStreak))
                ifNoDelete += prevLength

            return min(ifDelete, ifNoDelete)

        return dp(0, k, 0, '')


