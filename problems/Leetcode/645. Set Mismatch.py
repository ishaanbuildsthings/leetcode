class Solution:
    def findErrorNums(self, nums):
        return [sum(nums) - sum(set(nums)), sum(range(1, len(nums)+1)) - sum(set(nums))]