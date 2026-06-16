class Solution:
    def largestSumAfterKNegations(self, nums: List[int], k: int) -> int:
        # can use quickselect, bucket sort, etc
        nums.sort()
        opsLeft = k
        for i in range(len(nums)):
            if nums[i] >= 0:
                break
            opsLeft -= 1
            nums[i] *= -1
            if not opsLeft:
                break
        
        if opsLeft % 2 == 0:
            return sum(nums)
        
        closestToZero = inf
        for i, v in enumerate(nums):
            dist = abs(v)
            closestToZero = min(closestToZero, dist)
        
        
        return sum(nums) - (2 * closestToZero)