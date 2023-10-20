# https://leetcode.com/problems/number-of-distinct-binary-strings-after-applying-operations/description/
# Difficulty: Medium
# tags: math

# Problem
# You are given a binary string s and a positive integer k.

# You can apply the following operation on the string any number of times:

# Choose any substring of size k from s and flip all its characters, that is, turn all 1's into 0's, and all 0's into 1's.
# Return the number of distinct strings you can obtain. Since the answer may be too large, return it modulo 109 + 7.

# Note that:

# A binary string is a string that consists only of the characters 0 and 1.
# A substring is a contiguous part of a string.

# Solution O(n) time, O(1) space
# We can control every bit except the last k-1. Technically my solution isn't good, because we let the number grow really big first, so the number becomes uncapped and not really O(1), we should keep modding it first but I was trying to get through problems quickly to hit 1000.

class Solution:
    def countDistinctStrings(self, s: str, k: int) -> int:
        return 2**(len(s) - k + 1) % (10**9 + 7)