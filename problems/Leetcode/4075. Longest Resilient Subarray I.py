class Solution:
    def resilientSubarray(self, nums: list[int], k: int) -> int:
        @cache
        def matchParity(i):
            if i == 0:
                return 1
            v = nums[i]
            prev = nums[i - 1]
            if v % k != prev % k:
                return 1
            return 1 + matchParity(i - 1)
            
        res = 0
        for i, v in enumerate(nums):
            matched = matchParity(i)
            rem = v % k
            # every step contributes "rem" to my parity
            # I want to contribute "rem" total so when I cut 1 off I am divisible by K
            # need to determine the cycle size
            g = gcd(k, rem)
            hit = k // g # cycle size
            # so we can take 1, 1 + hit, 1 + hit + hit, ...
            # what is the most we can take that is <= matched?
            groups = (matched - 1) // hit
            res = max(res, (groups * hit) + 1)


        return res
            