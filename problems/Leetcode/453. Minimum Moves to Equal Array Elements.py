class Solution:
    def minMoves(self, nums: List[int]) -> int:
        small = min(nums)
        return sum(abs(num - small) for num in nums)