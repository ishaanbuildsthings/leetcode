class Solution:
    def sumOfFlooredPairs(self, nums: List[int]) -> int:
        mx = max(nums)
        c = Counter(nums)
        pf = []
        curr = 0
        for num in range(mx + 1):
            curr += c[num]
            pf.append(curr)
        
        def query(l, r):
            if l <= 0:
                return pf[r]
            if r > mx:
                r = mx
            return pf[r] - pf[l-1]
        
        res = 0
        M = 10**9 + 7

        uniq = list(set(nums))

        for num in uniq:
            curr = num
            while curr <= mx:
                # find from curr...curr + num - 1
                gainPer = curr // num
                inside = query(curr, curr + num - 1)
                res += gainPer * inside *c[num]
                res %= M
                curr +=num
        
        return res% M