class Solution:
    def canBeIncreasing(self, nums: List[int]) -> bool:
        validLeft = 0
        for i in range(1, len(nums)):
            if nums[i]>nums[i-1]:
                validLeft = i
            else:
                break
        validRight = len(nums) - 1
        for i in range(len(nums) - 2, -1, -1):
            if nums[i] < nums[i + 1]:
                validRight = i
            else:
                break
        if validRight <= 1:
            return True
        if validLeft >= len(nums) - 2:
            return True
        for i in range(1, len(nums) - 1):
            if validLeft >= i - 1 and validRight <= i + 1 and nums[i + 1] > nums[i - 1]:
                return True
        return False
