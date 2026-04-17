class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        nums.sort()
        res = []

        for i in range(len(nums)):
            l = i + 1
            r = len(nums) - 1
            if i and nums[i] == nums[i - 1]:
                continue
            while l < r:
                if l != i + 1 and nums[l] == nums[l - 1]:
                    l += 1
                    continue
                tot = nums[i] + nums[l] + nums[r]
                if tot == 0:
                    res.append([nums[i], nums[l], nums[r]])
                    l += 1                
                elif tot < 0:
                    l += 1                
                else:
                    r -= 1
        
        return res