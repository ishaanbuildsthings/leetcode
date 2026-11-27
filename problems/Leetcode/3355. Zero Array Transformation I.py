class Solution:
    def isZeroArray(self, nums: List[int], queries: List[List[int]]) -> bool:
        decs = [0] * (len(nums) + 1) # sweepline decs
        
        for l, r in queries:
            decs[l] += 1
            decs[r + 1] -= 1
        
        finalDecs = []
        
        curr = 0
        for d in decs:
            curr += d
            finalDecs.append(curr)
        
        return all(
        finalDecs[i] >= nums[i] for i in range(len(nums)))
        
        