class Solution:
    def countValidSubarrays(self, nums: list[int], x: int) -> int:
        res = 0
        for l in range(len(nums)):
            tot = 0
            for r in range(l, len(nums)):
                tot += nums[r]
                if tot % 10 == x and int(str(tot)[0]) == x:
                    res += 1
        return res