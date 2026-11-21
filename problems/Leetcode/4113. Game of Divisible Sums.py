class Solution:
    def maxDifference(self, nums: list[int]) -> int:
        n = len(nums)
        tot = sum(nums)

        # max score this player can get in surplus
        @cache
        def dp(i):
            if i == n:
                return 0

            if i == n - 1:
                return nums[i]


            options = []
            
            tot = nums[i] + nums[i + 1]
            if tot % 3 == 0:
                opt1 = tot - dp(i + 2)
                options.append(opt1)
            else:
                opt1 = tot + dp(i + 2)
                options.append(opt1)

            if nums[i] % 3 == 0:
                opt2 = nums[i] - dp(i + 1)
                options.append(opt2)
            else:
                opt2 = nums[i] + dp(i + 1)
                options.append(opt2)
                

            return max(options)

        surplus = dp(0)
        dp.cache_clear()

        return surplus