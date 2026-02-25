class Solution:
    def countQuadruplets(self, nums: List[int]) -> int:
        n = len(nums)
        res = 0
        mp = Counter()
        # iterate backwards on c/d pairs

        # a + b = d - c
        for c in range(n - 1, 1, -1):
            for d in range(c + 1, n):
                # d - c
                mp[nums[d] - nums[c]] += 1
            # solve all pairs for a fixed b
            b = c - 1
            for a in range(b - 1, -1, -1):
                res += mp[nums[a] + nums[b]]
        return res


            
