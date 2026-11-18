class Solution:
    def maxSizeSlices(self, slices: list[int]) -> int:
        pick = len(slices) // 3

        @cache
        def dp(i, picked, pickedFirst):
            if picked == pick:
                return 0
            if i >= len(slices):
                return 0
            if i == len(slices) - 1 and pickedFirst:
                return 0
            ifSkip = dp(i + 1, picked, pickedFirst)
            ifTake = slices[i] + dp(i + 2, picked + 1, pickedFirst or i == 0)
            return max(ifSkip, ifTake)
        
        return dp(0, 0, False)