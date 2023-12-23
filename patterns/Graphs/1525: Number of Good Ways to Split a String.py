# https://leetcode.com/problems/number-of-good-ways-to-split-a-string/description/
# difficulty: medium

# Problem
# You are given a string s.

# A split is called good if you can split s into two non-empty strings sleft and sright where their concatenation is equal to s (i.e., sleft + sright = s) and the number of distinct letters in sleft and sright is the same.

# Return the number of good splits you can make in s.

# Solution, O(n) time and O(1) space, just count the left and right

class Solution:
    def numSplits(self, s: str) -> int:
        counts = collections.Counter(s)
        res = 0
        left = set()
        rightSize = len(counts.keys())
        for allLeft in range(len(s) - 1):
            char = s[allLeft]
            counts[char] -= 1
            if counts[char] == 0:
                del counts[char]
                rightSize -= 1
            left.add(char)
            res += len(left) == rightSize
        return res