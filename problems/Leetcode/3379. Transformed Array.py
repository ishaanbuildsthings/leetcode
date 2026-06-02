class Solution:
    def constructTransformedArray(self, nums: List[int]) -> List[int]:
        res = []
        for i in range(len(nums)):
            num = nums[i]
            if num > 0:
                curr = i
                for _ in range(num):
                    curr += 1
                    if curr >= len(nums):
                        curr -= len(nums)
                res.append(nums[curr])
            elif num == 0:
                res.append(nums[i])
            else:
                curr = i
                for _ in range(abs(num)):
                    curr -= 1
                    if curr < 0:
                        curr = len(nums) - 1
                res.append(nums[curr])
        
        return res