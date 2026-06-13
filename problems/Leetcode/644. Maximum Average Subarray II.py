class Solution:
    def findMaxAverage(self, nums: List[int], k: int) -> float:
        l = min(nums)
        r = max(nums)
        res = min(nums)

        def attain(v):
            arr = [x - v for x in nums]

            pfArr = []
            curr = 0
            for val in arr:
                curr += val
                pfArr.append(curr)

            # we need a subarray of total sum >= 0
            pf = 0
            minCut = inf
            for i, v in enumerate(arr):
                pf += v
                if i == k - 1:
                    minCut = 0
                elif i > k - 1:
                    cutPoint = i - k
                    minCut = min(minCut, pfArr[cutPoint])
                if pf - minCut >= 0:
                    return True
            return False



        EPSILON = 1 / (10**5)
        while l + EPSILON <= r:
            m = (r + l) / 2
            if attain(m):
                res = m
                l = m
            else:
                r = m
        
        return res