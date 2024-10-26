# https://leetcode.com/problems/a-number-after-a-double-reversal/description/
# Difficulty: easy

# Problem
# Reversing an integer means to reverse all its digits.

# For example, reversing 2021 gives 1202. Reversing 12300 gives 321 as the leading zeros are not retained.
# Given an integer num, reverse num to get reversed1, then reverse reversed1 to get reversed2. Return true if reversed2 equals num. Otherwise return false.

# Solution, O(1) time and space
class Solution:
    def isSameAfterReversals(self, num: int) -> bool:
        # edge case
        if num == 0:
            return True
        return num % 10 != 0