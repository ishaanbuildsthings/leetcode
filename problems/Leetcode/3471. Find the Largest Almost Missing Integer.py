class Solution:
    def largestInteger(self, nums: List[int], k: int) -> int:
        res = -1
        for num in nums:
            seen = 0
            for left in range(len(nums)):
                right = left + k - 1
                if right >= len(nums):
                    break
                if num in nums[left:right+1]:
                    seen += 1
            if seen == 1:
                res = max(res, num)
        return res
                