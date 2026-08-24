class Solution:
    def divideArray(self, nums: List[int], k: int) -> List[List[int]]:
        def diff(a, b):
            return abs(a-b)
        
        res = []
        
        nums.sort()
        for i in range(0, len(nums) - 2, 3):
            if diff(nums[i], nums[i + 2]) <= k:
                res.append(nums[i:i+3])
            else:
                return []
        return res
                
            
            
                
                