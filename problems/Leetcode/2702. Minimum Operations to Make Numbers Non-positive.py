class Solution:
    def minOperations(self, nums: List[int], x: int, y: int) -> int:
        nums.sort(reverse=True) # more speedup optimization
        mx = max(nums)

        maxOps = [math.ceil(v / x) for v in nums]

        fmax = lambda x, y : x if x > y else y
        fmin = lambda x, y : x if x < y else y

        def canDo(ops):
            # basic pruning
            # if even using only x ops we cannot zero-out everything we fail
            if mx / x > ops:
                return False

            totalXOps = 0
            # how many x operations does each number need
            for i, v in enumerate(nums):

                mxXOps = maxOps[i]

                # can use math, I use another binary search :-)

                l = 0
                r = fmin(ops, mxXOps)
                resHere = None
                while l <= r:
                    m = (l + r) // 2
                    xGain = m * x
                    yOps = ops - m
                    yGain = yOps * y
                    gain = xGain + yGain
                    if gain >= v:
                        resHere = m
                        r = m - 1
                    else:
                        l = m + 1
                
                totalXOps += resHere
                if totalXOps > ops:
                    return False
            
            return True


        l = 1
        mostOps = 0
        for v in nums:
            mostOps = max(mostOps, math.ceil(v / y))
        r = mostOps
        res = None
        while l <= r:
            m = (l + r) // 2
            if canDo(m):
                res = m
                r = m - 1
            else:
                l = m + 1
        return res