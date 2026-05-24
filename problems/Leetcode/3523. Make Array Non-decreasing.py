class Solution:
    def maximumPossibleSize(self, nums: List[int]) -> int:
       # any number with a bigger number on the left is gonna get lost
        bigLeft = -inf
        lost = 0
        for i in range(len(nums)):
            if nums[i] < bigLeft:
                lost += 1
            bigLeft = max(bigLeft, nums[i])
        return len(nums) - lost
            
    