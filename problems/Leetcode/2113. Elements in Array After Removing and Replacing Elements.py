class Solution:
    def elementInNums(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        res = []
        n = len(nums)
        for time, i in queries:
            bucket = (time) % (2*n)
            if bucket == n:
                sz = 0
            elif bucket < n:
                sz = n - bucket
                l = bucket
                r = l + sz - 1
            else:
                sz = bucket - n
                l = 0
                r = l + sz - 1
            if i >= sz:
                res.append(-1)
                continue
            res.append(nums[(l+i)% n])
        return res
        
            
        