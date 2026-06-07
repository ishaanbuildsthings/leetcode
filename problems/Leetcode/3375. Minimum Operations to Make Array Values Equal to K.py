class Solution:
    def minOperations(self, nums: List[int], k: int) -> int:
        seen = set()
        for num in nums:
            if num > k:
                seen.add(num)
            if num < k:
                return -1
        
        return len(seen)
        
        