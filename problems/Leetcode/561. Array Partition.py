class Solution:
    def arrayPairSum(self, nums: List[int]) -> int:
        # could use bucket sort since nums[i] is low
        nums.sort()
        return sum(min(nums[i], nums[i + 1]) for i in range(0, len(nums), 2))