class Solution:
    def sumOfDigits(self, nums: List[int]) -> int:
        def digitSum(num):
            res = 0
            while num:
                last = num % 10
                res += last
                num //= 10
            return res
        
        return 1 - digitSum(min(nums)) % 2