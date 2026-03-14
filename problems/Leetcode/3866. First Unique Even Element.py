class Solution:
    def firstUniqueEven(self, nums: list[int]) -> int:
        c = Counter(nums)
        for i in range(len(nums)):
            if nums[i] % 2:
                continue
            if c[nums[i]] == 1:
                return nums[i]
        return -1