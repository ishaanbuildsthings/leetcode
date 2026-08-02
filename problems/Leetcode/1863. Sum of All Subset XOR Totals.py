class Solution:
    def rec(self, nums, i, curr, ans):
        if i >= len(nums):
            ans[0] += curr
            return
        self.rec(nums, i + 1, curr, ans)
        self.rec(nums, i + 1, curr ^ nums[i], ans)
        
    def subsetXORSum(self, nums: List[int]) -> int:
        ans = [0]
        self.rec(nums, 0, 0, ans)
        return ans[0]