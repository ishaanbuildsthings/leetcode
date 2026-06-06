class Solution:
    def canJump(self, nums: List[int]) -> bool:
        furthestRight = nums[0]
        for i in range(len(nums)):
            if i > furthestRight:
                return False
            furthestRight = max(furthestRight, i + nums[i])
        return True