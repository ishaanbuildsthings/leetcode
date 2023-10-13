# https://leetcode.com/problems/rings-and-rods/
# difficulty: easy

# Problem
# There are n rings and each ring is either red, green, or blue. The rings are distributed across ten rods labeled from 0 to 9.

# You are given a string rings of length 2n that describes the n rings that are placed onto the rods. Every two characters in rings forms a color-position pair that is used to describe each ring where:

# The first character of the ith pair denotes the ith ring's color ('R', 'G', 'B').
# The second character of the ith pair denotes the rod that the ith ring is placed on ('0' to '9').
# For example, "R3G2B1" describes n == 3 rings: a red ring placed onto the rod labeled 3, a green ring placed onto the rod labeled 2, and a blue ring placed onto the rod labeled 1.

# Return the number of rods that have all three colors of rings on them.

# Solution, O(n) time, O(1) space (only ten rods and 3 rings for each)

class Solution:
    def countPoints(self, rings: str) -> int:
        ringMap = defaultdict(set) # map a rod to its rings

        for i in range(0, len(rings), 2):
            rod = rings[i + 1]
            color = rings[i]
            ringMap[rod].add(color)

        res = 0
        for rod in ringMap.keys():
            if len(ringMap[rod]) == 3:
                res += 1

        return res
