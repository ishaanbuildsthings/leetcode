class Solution:
    def minImpossibleOR(self, nums: List[int]) -> int:
        numSet = set(nums)
        for b in range(32):
            if (1 << b) not in numSet:
                return (1 << b)