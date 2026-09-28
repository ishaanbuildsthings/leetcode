class Solution:
    def longestSubarray(self, nums: list[int], k: int) -> int:
        n = len(nums)
        leftmost = { 0 : -1 } # for prefixes, maps the earliest occurrence of every prefix
        rightmost = { 0 : n }
        curr = 0
        for i, v in enumerate(nums):
            curr = (curr + v) % k
            if curr not in leftmost:
                leftmost[curr] = i
        curr = 0
        for i in range(n - 1, -1, -1):
            v = nums[i]
            curr = (curr + v) % k
            if curr not in rightmost:
                rightmost[curr] = i
        
        res = 0
        # no negate
        curr = 0
        for i, v in enumerate(nums):
            curr = (curr + v) % k
            if curr in leftmost and leftmost[curr] < i:
                width = i - leftmost[curr]
                res = max(res, width)
        
        tot = sum(nums) % k

        vtoI = defaultdict(list)
        for i, v in enumerate(nums):
            vtoI[v % k].append(i)
                        
        # negate
        S = set([x % k for x in nums])
        for v in S:
            remainder = (tot - v - v) % k
            for cutLeft in range(k + 1):
                cutRight = (remainder - cutLeft) % k
                if cutLeft not in leftmost or cutRight not in rightmost:
                    continue
                L = leftmost[cutLeft]
                R = rightmost[cutRight]

                # subarray is L+1...R-1
                

                # check if any are in between, can prob remove this log
                bucket = vtoI[v]
                # binary search for smallest occurrence 
                l = 0
                r = len(bucket) - 1
                resI = None
                while l <= r:
                    m = (l + r) // 2
                    if bucket[m] >= L + 1:
                        resI = m
                        r = m - 1
                    else:
                        l = m + 1
                
                if resI is None:
                    continue

                idx = bucket[resI]
                
                if idx >= L + 1 and idx <= R - 1:
                    width = (R - 1) - (L + 1) + 1
                    res = max(res, width)
        
        return res


