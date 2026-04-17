# https://leetcode.com/problems/reverse-words-in-a-string/
# difficulty: medium

# Problem
# Given an input string s, reverse the order of the words.

# A word is defined as a sequence of non-space characters. The words in s will be separated by at least one space.

# Return a string of the words in reverse order concatenated by a single space.

# Note that s may contain leading or trailing spaces or multiple spaces between two words. The returned string should only have a single space separating the words. Do not include any extra spaces.

# Solution, O(n) time and space, O(1) space is doable in C where we can mutate strings. Note that myString.split() with no args to split will just parse out whitespace.

class Solution:
    def reverseWords(self, s: str) -> str:
        return ' '.join(reversed(s.split()))
