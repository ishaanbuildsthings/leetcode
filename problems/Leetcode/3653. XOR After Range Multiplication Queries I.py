class Solution:
    def xorAfterQueries(self, nums: List[int], queries: List[List[int]]) -> int:
        arr = nums[:]
        M = 10**9 + 7
        for l, r, k, v in queries:
            L = l
            while L <= r:
                nums[L] *= v
                nums[L] %= M
                L += k
        v = nums[0]
        for i in range(1, len(nums)):
            v ^= nums[i]
        return v
                