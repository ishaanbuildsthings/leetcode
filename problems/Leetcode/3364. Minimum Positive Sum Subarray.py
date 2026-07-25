class Solution:
    def minimumSumSubarray(self, nums: List[int], l: int, r: int) -> int:
        resMin = inf
        for size in range(l, r + 1):
            for left in range(len(nums)):
                right = left + size - 1
                if right >= len(nums):
                    break
                tot = sum(nums[left:right+1])
                if tot > 0:
                    resMin = min(resMin, tot)
        if resMin == inf:
            return -1
        return resMin