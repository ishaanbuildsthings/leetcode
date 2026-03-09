class Solution:
    def reverseSubarrays(self, nums: list[int], k: int) -> list[int]:
        n = len(nums)
        per = n // k
        i = 0
        while i < n:
            ending = i + per
            nums[i:ending] = nums[i:ending][::-1]
            i = ending
        return nums