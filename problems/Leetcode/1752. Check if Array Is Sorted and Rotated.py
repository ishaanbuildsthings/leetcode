class Solution:
    def check(self, nums: List[int]) -> bool:
        increments = 1
        for i in range(1, len(nums)):
            if nums[i] < nums[i - 1]:
                increments += 1
                
        if increments > 2:
            return False
        if increments == 1:
            return True
        return nums[-1] <= nums[0]
