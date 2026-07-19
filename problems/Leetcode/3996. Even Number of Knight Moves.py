class Solution:
    def canReach(self, start: list[int], target: list[int]) -> bool:
        return sum(start) % 2 == sum(target) % 2©leetcode