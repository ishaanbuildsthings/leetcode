class Solution:
    def maxSum(self, nums: List[int], threshold: List[int]) -> int:
        res = 0
        z = sorted(zip(threshold, nums))

        for i in range(len(z)):
            if z[i][0] > i + 1:
                break
            res += z[i][1]
        
        return res
            
