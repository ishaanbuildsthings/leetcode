class Solution:
    def countDominantElements(self, nums: list[int]) -> int:
        if len(nums) == 1:
            return 1

        n = len(nums)
        res = 0
        for i in range(1, n - 1):
            v = nums[i]
            prev = nums[i-1]
            nxt = nums[i+1]
            if v >= (prev+nxt)/2:
                res += 1
        if nums[0] >= nums[1]:
            res += 1
        if nums[-1] >= nums[-2]:
            res += 1

        return res