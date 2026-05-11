class Solution:
    def concatWithReverse(self, nums: list[int]) -> list[int]:
        return nums + nums[::-1]