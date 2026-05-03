class Solution:
    def countOppositeParity(self, nums: list[int]) -> list[int]:
        n = len(nums)
        res = [0] * n
        for i in range(n):
            for j in range(i + 1, n):
                if nums[i] % 2 != nums[j] % 2:
                    res[i] += 1
        return res