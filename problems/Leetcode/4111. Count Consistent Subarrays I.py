class Solution:
    def countConsistent(self, nums: list[int]) -> int:
        res = 0
        n = len(nums)
        for l in range(n):
            AND = nums[l]
            mn = inf
            for r in range(l, n):
                AND &= nums[r]
                mn = min(mn, nums[r])
                if AND == mn:
                    res += 1

        return res