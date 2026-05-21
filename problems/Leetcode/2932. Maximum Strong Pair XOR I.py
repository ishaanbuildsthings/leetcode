class Solution:
    def maximumStrongPairXor(self, nums: List[int]) -> int:
        res = float('-inf')
        for i in range(len(nums)):
            for j in range(len(nums)):
                if abs(nums[i] - nums[j]) <= min(nums[i], nums[j]):
                    bitOr = nums[i] ^ nums[j]
                    res = max(res, bitOr)
        return res
                    