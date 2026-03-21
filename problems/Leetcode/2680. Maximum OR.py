import functools

class Solution:
    def maximumOr(self, nums: List[int], k: int) -> int:        
        # 12 -> 1100
        # 9 ->  1001

        # 11000 | 01001 -> 11001 -> 25

        # double the 9 instead
        # 01100 | 10010 -> 11110 -> 30

        orLeft = [] # or from 0...i
        curr = 0
        for i in range(len(nums)):
            curr |= nums[i]
            orLeft.append(curr)
        
        orRight = [None] * len(nums)
        curr = 0
        for i in range(len(nums) -1, -1, -1):
            curr |= nums[i]
            orRight[i] = curr
        
        res = 0

        # assume this is the one we apply ops to
        for i in range(len(nums)):
            num = nums[i]
            num = num << k
            orOnLeft = orLeft[i - 1] if i else 0
            orOnRight = orRight[i + 1] if i < len(nums) - 1 else 0
            orHere = num | orOnLeft | orOnRight
            res = max(res, orHere)
        
        return res