class Solution:
    def goodIndices(self, nums: List[int], k: int) -> List[int]:

        @cache
        def streakIncLeft(i):
            if i == 0:
                return 1
            if nums[i - 1] >= nums[i]:
                return 1 + streakIncLeft(i - 1)
            return 1
        
        @cache
        def streakIncRight(i):
            if i == len(nums) - 1:
                return 1
            if nums[i + 1] >= nums[i]:
                return 1 + streakIncRight(i + 1)
            return 1
        
        res = []
        for i in range(1, len(nums) - 1):
            leftstreak = streakIncLeft(i - 1)
            rightstreak = streakIncRight(i + 1)
            if leftstreak >= k and rightstreak >= k:
                res.append(i)
        
        return res