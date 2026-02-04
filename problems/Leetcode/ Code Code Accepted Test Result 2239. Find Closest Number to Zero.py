class Solution:
    def findClosestNumber(self, nums: List[int]) -> int:
        res = float('inf')
        for num in nums:
            if abs(num) < abs(res):
                res = num
            elif abs(num) == abs(res):
                res = max(num, res)
        return res 