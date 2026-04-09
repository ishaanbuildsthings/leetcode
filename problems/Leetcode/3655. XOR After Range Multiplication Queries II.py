# SOLUTION 1
# same complexity but I use a flat array of size N+1 per smallJumpSize
# sweeps[smallJump] = [1, 1, 1, ..., 1] of size n + 1
# when we apply a heavy query, we mark directly at position l and cancel at the first position past r in the same residue class
# then at the end we walk each residue class with a running multiplier and apply to nums
class Solution:
    def xorAfterQueries(self, nums: List[int], queries: List[List[int]]) -> int:
        MOD = 10**9 + 7

        n = len(nums)
        B = math.ceil(math.sqrt(n))

        # sweeps[smallJump] = flat sweep line across all residue classes, size n + 1
        # this is n root n because among a jump size we get N total values and there are B jump sizes
        sweeps = [[1] * (n + 1) for _ in range(B)]

        usedHeavyJumps = set() # trying to prune for python to pass

        @cache
        def minv(v):
            return pow(v, MOD - 2, MOD)

        for l, r, k, v in queries:
            # light query, do it manually
            if k >= B:
                L = l
                while L <= r:
                    nums[L] = nums[L] * v % MOD
                    L += k
            else:
                # heavy query
                # k < B
                usedHeavyJumps.add(k)
                sweeps[k][l] = sweeps[k][l] * v % MOD

                # find the first position past r in the same residue class
                # its the first number greater than r, which is lastHit + k
                lastHit = l + ((r - l) // k) * k
                cancelPos = lastHit + k
                if cancelPos <= n:
                    sweeps[k][cancelPos] = sweeps[k][cancelPos] * minv(v) % MOD

        # aggregate: for every small jump size, walk each residue class with a running multiplier
        for smallJump in range(1, B):
            if smallJump not in usedHeavyJumps:
                continue
            bucket = sweeps[smallJump]
            for startI in range(smallJump):
                currMult = 1
                posI = startI
                while posI < n:
                    currMult = currMult * bucket[posI] % MOD
                    nums[posI] = nums[posI] * currMult % MOD
                    posI += smallJump

        res = 0
        for v in nums:
            res ^= v
        return res

        
# # SOLUTION 2
# # same complexity but I use a dictionary of (smallJumpSize, startIndex) -> [1, 1, 1, 1, 1, ...] (sweep line)
# # the amount of 1s is based on how many indices fit with that set of parameters
# # now when we apply a heavy query, I manually iterate on all of those 1s and update within that residue class
# # then at the end we aggregate everything
# class Solution:
#     def xorAfterQueries(self, nums: List[int], queries: List[List[int]]) -> int:
#         MOD = 10**9 + 7

#         n = len(nums)
#         B = math.ceil(math.sqrt(n))

#         # sweeps[(smallJump, startI)] is a sweep line for all positions, so if the small jump is 3 we have 3 residue classes, like 0, 3, 6,    1, 4, 7,    etc
#         # this is n root n beccause among a jump size we get N total values and there are B jump sizes
#         # sweeps = defaultdict(lambda: defaultdict(lambda : 1))
#         sweeps = {}
#         for smallJump in range(B):
#             for startI in range(smallJump):
#                 jumps = ((n - 1) - startI) // smallJump
#                 sweeps[(smallJump, startI)] = [1] * (jumps + 2) # +2 because a sweep line naturally adds +1, and if we have 1 jump we have two indices so thats the second +1

#         @cache
#         def minv(v):
#             return pow(v, MOD - 2, MOD)

#         # so sweeps[(smallJump, startI)][idx] is for the idx-th position in that bucket [1, 4, 7, 10, ...]

#         for l, r, k, v in queries:
#             # light query, do it manually
#             if k >= B:
#                 L = l
#                 while L <= r:
#                     nums[L] = nums[L] * v % MOD
#                     L += k
#             else:
#                 # heavy query
#                 # k < B
#                 residue = l % k
#                 # find where exactly l occurs in that bucket
#                 bucket = sweeps[(k, residue)]
#                 diff = l - residue
#                 jumps = diff // k # how many jumps to reach l, starting from residue, basically the index in our bucket
#                 bucket[jumps] = bucket[jumps] * v % MOD

#                 # find the right index we lose at, which is not necessarily r
#                 # its the first number greater than r
#                 lastHit = l + ((r - l) // k) * k
#                 endIdx = (lastHit - residue) // k + 1
#                 bucket[endIdx] = bucket[endIdx] * minv(v) % MOD


#         for (smallJump, startI), bucket in sweeps.items():
#             currMult = 1
#             for i in range(len(bucket) - 1):
#                 posI = startI + (i * smallJump) # our index against the n positions in the full aray
#                 currMult *= bucket[i]
#                 currMult %= MOD
#                 nums[posI] *= currMult
#                 nums[posI] %= MOD
        
#         res = 0
#         for v in nums:
#             res ^= v
#         return res
