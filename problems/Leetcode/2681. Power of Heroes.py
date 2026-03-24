class Solution:
    def sumOfPower(self, nums: List[int]) -> int:
        # for a given value A that is the max, it is like this

        # A*B*2^width + A*C*2^width + ...

        # which is A * (B*2^width + C*2^width + ...)
        # so I think we can track this rolling prefix value and update it, multiply the prior value by 2
        # then add the new one

        nums.sort()
        res = 0
        MOD = 10**9 + 7
        pfValue = 0

        for r in range(len(nums)):
            v = nums[r]
            res += (v**2 * pfValue) % MOD
            res += v**3 # solo group
            res %= MOD
            pfValue *= 2
            pfValue += v
            pfValue %= MOD

        return res