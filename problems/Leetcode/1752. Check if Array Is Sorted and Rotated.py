class Solution:
    def check(self, nums: List[int]) -> bool:
        drops = 0
        for i in range(len(nums) - 1):
            if nums[i] > nums[i + 1]:
                drops += 1
        if drops > 1:
            return False
        if drops == 0:
            return True
        return nums[0] >= nums[-1]