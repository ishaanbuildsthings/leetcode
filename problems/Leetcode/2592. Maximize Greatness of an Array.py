class Solution:
    def maximizeGreatness(self, nums: List[int]) -> int:
        nums.sort()
        res = i = 0
        for j in range(len(nums)):
            if i >= len(nums):
                break
            while i < len(nums) and nums[i] <= nums[j]:
                i += 1
            if i != len(nums):
                i += 1 # consume that number
                res += 1

        return res