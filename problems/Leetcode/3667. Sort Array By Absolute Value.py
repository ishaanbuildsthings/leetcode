class Solution:
    def sortByAbsoluteValue(self, nums: List[int]) -> List[int]:
        nums.sort(key=lambda x: abs(x))
        return nums