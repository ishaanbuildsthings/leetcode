class Solution:
    def minStartValue(self, nums: List[int]) -> int:
        desc = inf
        curr = 0
        for num in nums:
            curr += num
            desc = min(desc, curr)
        res = (-1 * desc) + 1
        if res <= 0:
            return 1
