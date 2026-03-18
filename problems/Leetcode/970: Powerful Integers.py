# https://leetcode.com/problems/powerful-integers/
# difficulty: medium

# Problem
# Given three integers x, y, and bound, return a list of all the powerful integers that have a value less than or equal to bound.

# An integer is powerful if it can be represented as xi + yj for some integers i >= 0 and j >= 0.

# You may return the answer in any order. In your answer, each value should occur at most once.

# Solution
# I just brute forced checked all possible combos, log^2 time and O(1) space

class Solution:
    def powerfulIntegers(self, x: int, y: int, bound: int) -> List[int]:
        # edge case
        if not bound:
            return []

        # note, could handle duplicate answers better probably
        res = set()
        maxXExponent = math.floor(math.log(bound, x)) if x > 1 else 0
        maxYExponent = math.floor(math.log(bound, y)) if y > 1 else 0
        for xNum in range(maxXExponent + 1):
            for yNum in range(maxYExponent + 1):
                if x**xNum + y**yNum <= bound:
                    res.add(x**xNum + y**yNum)
                else:
                    break

        return list(res)