class Solution:
    def minimumDeviation(self, nums: List[int]) -> int:
        n = len(nums)
        globalMaxHeap = SortedList() # holds (value, i) where i corresponds to which number index it came from
        ranges = []
        maxes = set()
        for i, v in enumerate(nums):
            rangeHere = []
            rangeHere.append(v)
            if v % 2:
                rangeHere.append(2 * v)
            else:
                while v % 2 == 0:
                    v //= 2
                    rangeHere.append(v)
            for val in rangeHere:
                globalMaxHeap.add((val, i))
                maxes.add(val)
            ranges.append(sorted(rangeHere))
        maxes = sorted(maxes,reverse=True)

        smallestHead = min(bucket[-1] for bucket in ranges)

        res = inf

        for mx in maxes:
            while globalMaxHeap and globalMaxHeap[-1][0] > mx:
                poppedV, poppedI = globalMaxHeap.pop()
                bucket = ranges[poppedI]
                bucket.pop()
                if not bucket:
                    return res
                smallestHead = min(smallestHead, bucket[-1])
            res = min(res, mx - smallestHead)
        
        return res
                

        