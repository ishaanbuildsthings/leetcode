class Solution:
    def longestArithmetic(self, nums: List[int]) -> int:
        # longest chain going backwards, increasing by diff each time
        @cache
        def pref(i, diff):
            if i == -1:
                return 0
            if i == 0:
                return 1
            if nums[i-1] - nums[i] == diff:
                return 1 + pref(i-1,diff)
            return 1

        # longest chain going forwards, increasing by diff each time
        @cache
        def suff(i, diff):
            if i == len(nums):
                return 0
            if i == len(nums) - 1:
                return 1
            if nums[i+1] - nums[i] == diff:
                return 1 + suff(i+1,diff)
            return 1

        res = 2

        for i in range(len(nums)):
            if i >= 2:
                # connect to the previous elements only
                pp = nums[i-2]
                p = nums[i-1]
                pdiff = pp - p
                leftRes = pref(i-1,pdiff) + 1
                res = max(res, leftRes)

            # connect to the right elements only
            if i <= len(nums) - 3:
                ff = nums[i+2]
                f = nums[i+1]
                fdiff = ff - f
                rightRes = suff(i+1,fdiff) + 1
                res = max(res, rightRes)

            # chain both sides together
            if i > 0 and i < len(nums) - 1:
                prev = nums[i-1]
                post = nums[i+1]
                gap = post - prev
                if gap % 2:
                    continue
                between = (prev+post) // 2
                # change nums[i] to between
                previous = pref(i - 1, prev - between)
                after = suff(i + 1, post - between)
                lengthHere = 1 + previous + after
                res = max(res, lengthHere)
                
        pref.cache_clear()
        suff.cache_clear()

        return res