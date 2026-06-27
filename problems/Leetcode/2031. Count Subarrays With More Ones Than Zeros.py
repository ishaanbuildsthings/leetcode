class Solution:
    def subarraysWithMoreOnesThanZeroes(self, nums: List[int]) -> int:
        arr = [-1 if x == 0 else 1 for x in nums]
        sl = SortedList()
        MOD = 10**9 + 7
        res = 0
        sl.add(0)
        curr = 0
        for v in arr:
            curr += v
            # we can cut off at most curr - 1
            countGte = sl.bisect_left(curr)
            res += countGte
            sl.add(curr)
        return res % MOD
            