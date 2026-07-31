class Solution:
    def maximumTop(self, nums: List[int], k: int) -> int:
        n = len(nums)
        if k % 2 and n == 1:
            return -1
        res = -inf
        # only do removes
        if k < n:
            res = nums[k]
        for i, v in enumerate(nums):
            # how many to remove to put this at the top
            removesBefore = i

            if removesBefore > k:
                break
            
            extraRemoves = k - removesBefore
            # even parity, just put back a previous one and remove it over and over
            if extraRemoves % 2 == 0 and i != 0:
                res = max(res, v)
            # or if this is the first element, remove it and put it back over and over
            if extraRemoves % 2 == 0:
                res = max(res, v)
            # or if on the wrong parity, remove this, remove one more, put this one back
            if extraRemoves % 2 == 1 and i + 1 < n and extraRemoves >= 3:
                res = max(res, v)
            # or if the wrong parity, remove this, place one down from before, put this one back
            if extraRemoves % 2 == 1 and i > 0 and extraRemoves >= 3:
                res = max(res, v)
        
        return res
        