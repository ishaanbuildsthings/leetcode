class Solution:
    def smallestIndex(self, nums: List[int]) -> int:
        res = inf
        for i in range(len(nums)):
            if sum(int(digit) for digit in str(nums[i])) == i:
                return i
        return -1