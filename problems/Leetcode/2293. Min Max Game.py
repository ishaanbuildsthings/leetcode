class Solution:
    def minMaxGame(self, nums: List[int]) -> int:
        if len(nums) == 1:
            return nums[0]
        narr = []
        for i in range(len(nums) // 2):
            if i % 2 == 0:
                narr.append(min(nums[2 * i], nums[2*i+1]))
            else:
                narr.append(max(nums[2 * i], nums[2*i+1]))
        return self.minMaxGame(narr)