class Solution:
    def solve(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        n = len(nums)
        B = max(1, math.isqrt(n))
        MOD = 10**9 + 7

        strideMaps = {} # maps (smallStride, startI) -> map
        for smallStride in range(1, B):
            for startI in range(smallStride):
                pf = []
                curr = 0
                for i in range(startI, n, smallStride):
                    v = nums[i]
                    curr += v
                    curr %= MOD
                    pf.append(curr)
                strideMaps[(smallStride, startI)] = pf

        # for every small stride, for each starting index up to that small stride, we can create a sum array
        
        res = [None] * len(queries)
        for i in range(len(queries)):
            qi, stride = queries[i]
            if stride >= B:
                tot = 0
                for j in range(qi, n, stride):
                    tot += nums[j]
                res[i] = tot % MOD
            else:
                strideMap = strideMaps[(stride, qi % stride)]
                total = strideMap[-1] # say our range is 7, 9, 11

                # stride map is starting at i=1, stride=2

                # the total would be 1, 3, 5, 7, 9, 11

                # now we want to cut off 1, 3, 5

                pos = qi // stride

                cutSum = strideMap[pos - 1] if pos else 0

                newTot = total - cutSum

                res[i] = newTot % MOD

        
        return res