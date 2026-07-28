class Solution:
    def sumOfBeauties(self, nums: List[int]) -> int:
        pfMax = []
        curr = 0
        for v in nums:
            curr = max(curr, v)
            pfMax.append(curr)
        
        suffMin = [inf] * len(nums)
        currMin = inf
        for i in range(len(nums) - 1, -1, -1):
            v = nums[i]
            currMin = min(currMin, v)
            suffMin[i] = currMin
        
        res = 0

        for i in range(1, len(nums) - 1):
            if suffMin[i + 1] > nums[i] > pfMax[i - 1]:
                res += 2
            elif nums[i + 1] > nums[i] > nums[i - 1]:
                res += 1
        
        return res