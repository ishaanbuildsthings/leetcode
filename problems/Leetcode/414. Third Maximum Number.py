class Solution:
    def thirdMax(self, nums: List[int]) -> int:
        f = list(set(nums))
        if len(f) < 3:
            return max(f)
        # can use qs or variables
        return heapq.nlargest(3, f)[-1]