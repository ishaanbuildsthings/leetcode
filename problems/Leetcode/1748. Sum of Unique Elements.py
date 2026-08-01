class Solution:
    def sumOfUnique(self, nums: List[int]) -> int:
        c = Counter(nums)
        return sum(
            num for num in nums if c[num] == 1
        )