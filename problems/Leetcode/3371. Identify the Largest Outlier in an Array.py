class Solution:
    def getLargestOutlier(self, nums: List[int]) -> int:
        c = Counter(nums)
        res = -inf
        tot = sum(nums)
        for i in range(len(nums)):
            num = nums[i] # check if this is an outlier
            remainTot = tot - num
            if remainTot % 2:
                continue
            
            c[num] -= 1
            cPotentialHalf = c[remainTot // 2]
            if cPotentialHalf:
                res = max(res, num)
            
            c[num] += 1
        
        return res
            