# https://leetcode.com/problems/number-of-distinct-roll-sequences/description/
# Difficulty: Hard
# Tags: Dynamic Programming 2d

# Problem
# You are given an integer n. You roll a fair 6-sided dice n times. Determine the total number of distinct sequences of rolls possible such that the following conditions are satisfied:

# The greatest common divisor of any adjacent values in the sequence is equal to 1.
# There is at least a gap of 2 rolls between equal valued rolls. More formally, if the value of the ith roll is equal to the value of the jth roll, then abs(i - j) > 2.
# Return the total number of distinct sequences possible. Since the answer may be very large, return it modulo 109 + 7.

# Two sequences are considered distinct if at least one element is different.

# Solution, O(n) time and space
# For a given amount of rolls remaining, we can roll any number 1-6, then sum up the answer to the subproblems. Those subproblem allowed rolls depend on the prior two rolls though, so we use a 3d dp array.

