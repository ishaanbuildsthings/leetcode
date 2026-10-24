class Solution:
    def sortPermutation(self, nums: List[int]) -> int:
        mask = (1 << 64) - 1
        res = mask
        for i, v in enumerate(nums):
            if v != i:
                res &= v
        return res if res != mask else 0