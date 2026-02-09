class Solution:
    def minMoves(self, nums: List[int]) -> int:
        mx = max(nums)
        return sum(mx - v for v in nums)