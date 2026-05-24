class Solution:
    def minimumSwaps(self, nums: list[int]) -> int:
        n = len(nums)
        zeroes = sum(x == 0 for x in nums)
        nonZInSuff = 0
        for i in range(n - 1, n - 1 - zeroes, -1):
            nonZInSuff += nums[i] != 0

        return nonZInSuff

        