class Solution:
    def longestSubarray(self, nums: list[int], k: int) -> int:
        res = 0
        n = len(nums)
        for l in range(n):
            drops = {0}
            tot = 0
            for r in range(l, n):
                v = nums[r] % k
                tot += v
                extra = tot % k
                drops.add((2 * v) % k)

                if extra in drops:
                    res = max(res, r - l + 1)

                
        return res