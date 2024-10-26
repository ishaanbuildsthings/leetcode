# https://leetcode.com/problems/jewels-and-stones/
# difficulty: easy

# problem
# You're given strings jewels representing the types of stones that are jewels, and stones representing the stones you have. Each character in stones is a type of stone you have. You want to know how many of the stones you have are also jewels.

# Letters are case sensitive, so "a" is considered a different type of stone from "A".

# Solution, O(jewels + stones) time, O(jewels) space

class Solution:
    def numJewelsInStones(self, jewels: str, stones: str) -> int:
        jewelSet = set()
        for char in jewels:
            jewelSet.add(char)
        res = 0
        for stone in stones:
            if stone in jewelSet:
                res += 1
        return res