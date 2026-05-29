class Solution:
    def minimumOperations(self, nums: List[int]) -> int:
        ops = 0
        while True:
            if len(set(nums)) == len(nums):
                return ops
            if nums:
                nums.pop(0)
            if nums:
                nums.pop(0)
            if nums:
                nums.pop(0)
            ops += 1