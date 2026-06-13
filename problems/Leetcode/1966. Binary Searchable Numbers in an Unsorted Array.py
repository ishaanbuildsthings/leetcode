class Solution:
    def binarySearchableNumbers(self, nums: List[int]) -> int:
        biggerThanAllOnLeft = [False] * len(nums)
        mx = -inf
        for i, v in enumerate(nums):
            if v > mx:
                mx = v
                biggerThanAllOnLeft[i] = True
        
        smallerThanAllOnRight = [False] * len(nums)
        mn = inf
        for i in range(len(nums) - 1, -1, -1):
            v = nums[i]
            if v < mn:
                mn = v
                smallerThanAllOnRight[i] = True
        
        return sum(biggerThanAllOnLeft[i] and smallerThanAllOnRight[i] for i in range(len(nums)))