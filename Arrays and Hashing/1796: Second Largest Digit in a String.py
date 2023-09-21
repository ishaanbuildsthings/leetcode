# https://leetcode.com/problems/second-largest-digit-in-a-string/description/
# Difficulty: Easy

# Problem
# Given an alphanumeric string s, return the second largest numerical digit that appears in s, or -1 if it does not exist.

# An alphanumeric string is a string consisting of lowercase English letters and digits.

# Solution, O(n) time, O(1) space, store seen digits
# Oops, isDigit is a thing, no need for weird try except
class Solution:
    def secondHighest(self, s: str) -> int:
        seenDigits = set()
        for char in s:
            try:
                int(char)
                seenDigits.add(int(char))
            except:
                continue
        if len(seenDigits) <= 1:
            return -1
        return sorted(list(seenDigits))[-2]