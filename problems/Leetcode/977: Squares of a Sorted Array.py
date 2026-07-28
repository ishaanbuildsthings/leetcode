class Solution:
    def sortedSquares(self, nums: List[int]) -> List[int]:
        res = [None] * len(nums)
        i = len(res) - 1
        l = 0
        r = len(nums) - 1
        while l <= r:
            if abs(nums[l]) >= abs(nums[r]):
                res[i] = nums[l] ** 2
                l += 1
                i -= 1
            else:
                res[i] = nums[r] ** 2
                r -= 1
                i -= 1
        return res

