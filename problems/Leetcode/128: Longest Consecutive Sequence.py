class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        
        5, 7, 6, 4, 0, 1, 2
        
        max_length = 0
        nums = set(nums)
        
        for num in nums:
            if num - 1 in nums:
                continue
            else:
                right = num
                while right+1 in nums:
                    right+= 1
                max_length = max(max_length, right-num+1)
        
        return max_length
            
                    
            