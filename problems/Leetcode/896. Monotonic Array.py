class Solution:
    def isMonotonic(self, nums: List[int]) -> bool:
        dir = 'neutral'
        for i, num in enumerate(nums):
            if i == 0:
                continue
            if nums[i] == nums[i - 1]:
                continue
            if nums[i] > nums[i - 1]:
                if dir == 'down':
                    return False
                if dir == 'neutral':
                    dir = 'up'
            elif nums[i] < nums[i - 1]:
                if dir == 'up':
                    return False
                if dir == 'neutral':
                    dir = 'down'
                
        return True