class Solution:
    def maxTotalValue(self, nums: List[int], k: int) -> int:
        b = max(nums)
        s = min(nums)
        return (b-s) * k