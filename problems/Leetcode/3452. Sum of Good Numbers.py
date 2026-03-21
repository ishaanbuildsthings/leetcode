class Solution:
    def sumOfGoodNumbers(self, nums: List[int], k: int) -> int:
        res = 0
        for i in range(len(nums)):
            left = i - k
            right = i + k
            leftPass = False
            if left < 0:
                leftPass = True
            else:
                if nums[i] > nums[left]:
                    leftPass = True
            
            rightPass = False
            if right >= len(nums):
                rightPass = True
            else:
                if nums[i] > nums[right]:
                    rightPass = True
            
            if leftPass and rightPass:
                res += nums[i]
        
        return res
            