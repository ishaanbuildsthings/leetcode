class Solution:
    def getMinDistance(self, nums: List[int], target: int, start: int) -> int:
        for dist in range(len(nums)):
            if start - dist >= 0 and nums[start - dist] == target:
                return dist
            if start + dist < len(nums) and nums[start + dist] == target:
                return dist