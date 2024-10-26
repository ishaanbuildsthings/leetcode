# https://leetcode.com/problems/find-good-days-to-rob-the-bank/description/
# difficulty: medium
# tags: prefix, postfix

# Problem
# You and a gang of thieves are planning on robbing a bank. You are given a 0-indexed integer array security, where security[i] is the number of guards on duty on the ith day. The days are numbered starting from 0. You are also given an integer time.

# The ith day is a good day to rob the bank if:

# There are at least time days before and after the ith day,
# The number of guards at the bank for the time days before i are non-increasing, and
# The number of guards at the bank for the time days after i are non-decreasing.
# More formally, this means day i is a good day to rob the bank if and only if security[i - time] >= security[i - time + 1] >= ... >= security[i] <= ... <= security[i + time - 1] <= security[i + time].

# Return a list of all days (0-indexed) that are good days to rob the bank. The order that the days are returned in does not matter.

# Solution, O(n) time and space, can even do with just postfix, prefix tracked as we iterate. I think there is an O(1) space solution with two pointers.

class Solution:
    def goodDaysToRobBank(self, security: List[int], time: int) -> List[int]:
        biggerOnLeft = [0] * len(security)
        for i in range(1, len(security)):
            if security[i] <= security[i - 1]:
                biggerOnLeft[i] = biggerOnLeft[i - 1] + 1
        biggerOnRight = [0] * len(security)
        for i in range(len(security) - 2, -1, -1):
            if security[i] <= security[i + 1]:
                biggerOnRight[i] = biggerOnRight[i + 1] + 1

        return [
            i for i in range(time, len(security) - time)
            if biggerOnLeft[i] >= time and biggerOnRight[i] >= time
        ]

