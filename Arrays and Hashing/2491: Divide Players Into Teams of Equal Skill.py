# https://leetcode.com/problems/divide-players-into-teams-of-equal-skill/description/
# difficulty: medium
# tags: two pointers

# Problem
# You are given a positive integer array skill of even length n where skill[i] denotes the skill of the ith player. Divide the players into n / 2 teams of size 2 such that the total skill of each team is equal.

# The chemistry of a team is equal to the product of the skills of the players on that team.

# Return the sum of the chemistry of all the teams, or return -1 if there is no way to divide the players into teams such that the total skill of each team is equal.

# Solution, O(n log n) time, O(sort) space, just sort and use two pointers. Can do this in linear time with linear memory by getting max and min and determining what the match should be, then using a hashmap.

class Solution:
    def dividePlayers(self, skills: List[int]) -> int:
        skills.sort()
        res = 0
        l = 0
        r = len(skills) - 1
        requiredSum = skills[l] + skills[r]
        while l < r:
            teamSum = skills[l] + skills[r]
            if teamSum != requiredSum:
                return -1
            res += skills[l] * skills[r]
            l += 1
            r -= 1
        return res
