class Solution:
    def subsetXORSum(self, nums: List[int]) -> int:
        seenBits = 0
        for v in nums:
            seenBits |= v
        res = 0
        ss = 2**len(nums) // 2
        for offset in range(32):
            if (1 << offset) & seenBits:
                res += (1 << offset) * ss
        return res