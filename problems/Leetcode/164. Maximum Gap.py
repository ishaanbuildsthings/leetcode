class Solution:
    def maximumGap(self, nums: List[int]) -> int:
        # 0 10 20 ... 1000 # 100 elements from 0-1000, smallest max gap is 10

        # if we make our bucket size 5
        # [0, 5] [6, 10] [11, 15] [16, 20] ...

        # then the answer can never be two elements in the same bucket, since the smallest max gap is at minimum 10

        if len(nums) == 1:
            return 0

        mn = min(nums)
        mx = max(nums)
        n = len(nums)
        gaps = n - 1
        bigGap = mx - mn
        smallestPossibleMaxGap = math.ceil(bigGap / gaps)

        buckets = []
        lo = mn
        while lo <= mx:
            buckets.append([lo, lo + smallestPossibleMaxGap])
            lo += smallestPossibleMaxGap + 1

        # # [MN, MN + smallestGap] [MN + smallestGap + 1, MN + 2*smallestGap + 1], ...
        def numToBucket(num):
            # each bucket has smallestGap+1 values
            return (num-mn) // (smallestPossibleMaxGap+1)

        bucketMn = defaultdict(lambda: inf)
        bucketMx = defaultdict(lambda: -inf)
        for i, v in enumerate(nums):
            bucketI = numToBucket(v)
            bucketMn[bucketI] = min(bucketMn[bucketI], v)
            bucketMx[bucketI] = max(bucketMx[bucketI], v)
        
        res = 0
        prevMx = None
        for i in range(len(buckets)):
            # within this bucket
            if bucketMx[i] != inf and bucketMn[i] != -inf:
                res = max(res, bucketMx[i] - bucketMn[i])
            if prevMx is not None:
                if bucketMn[i] != inf:
                    diff = bucketMn[i] - prevMx
                    res = max(res, diff)
            if bucketMx[i] != -inf:
                prevMx = bucketMx[i] 
        
        return res