class Solution:
    def smallestRangeI(self, nums: List[int], k: int) -> int:
        small = min(nums)
        big = max(nums)
        if small + k < big - k:
            return big - small - 2*k
        return 0
