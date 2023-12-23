# https://leetcode.com/problems/number-of-distinct-binary-strings-after-applying-operations/description/
# difficulty: medium
# tags: math

# problem
# You are given a binary string s and a positive integer k.

# You can apply the following operation on the string any number of times:

# Choose any substring of size k from s and flip all its characters, that is, turn all 1's into 0's, and all 0's into 1's.
# Return the number of distinct strings you can obtain. Since the answer may be too large, return it modulo 109 + 7.

# Note that:

# A binary string is a string that consists only of the characters 0 and 1.
# A substring is a contiguous part of a string.

# Solution, O(k) time and O(1) space
# We can always control the leftmost char by starting the flips from there, except for the ending chars.

class Solution:
    def countDistinctStrings(self, s: str, k: int) -> int:
        return (2 ** (len(s) - k + 1)) % (10**9 + 7)