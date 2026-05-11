class Solution:
    def beautifulArray(self, n: int) -> List[int]:
        def rec(nums):
            if len(nums) <= 2:
                return nums
            
            odds = [nums[i] for i in range(len(nums)) if i % 2 == 0]
            evens = [nums[i] for i in range(len(nums)) if i % 2]
            return rec(odds) + rec(evens)
        
        return rec(list(range(1, n + 1)))



        # 1 2 3 4 5 6 7 8

        # 1 3 5 7 | 2 4 6 8
