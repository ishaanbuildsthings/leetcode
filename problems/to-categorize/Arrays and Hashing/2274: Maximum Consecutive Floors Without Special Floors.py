# https://leetcode.com/problems/maximum-consecutive-floors-without-special-floors/
# difficulty: medium

# Problem
# Alice manages a company and has rented some floors of a building as office space. Alice has decided some of these floors should be special floors, used for relaxation only.

# You are given two integers bottom and top, which denote that Alice has rented all the floors from bottom to top (inclusive). You are also given the integer array special, where special[i] denotes a special floor that Alice has designated for relaxation.

# Return the maximum number of consecutive floors without a special floor.

# Solution, O(special log special time), O(sort(special)) space
# Check between any two specials, and also between the specials and the ends.

class Solution:
    def maxConsecutive(self, bottom: int, top: int, special: List[int]) -> int:
        res = float('-inf')
        special.sort()
        for i in range(1, len(special)):
            res = max(res, special[i] - special[i - 1] - 1)
        res = max(res, special[0] - bottom, top - special[-1])
        return res