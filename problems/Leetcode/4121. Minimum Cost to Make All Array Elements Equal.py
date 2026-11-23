class Solution:
    def minCost(self, nums: list[int]) -> int:
        n = len(nums)
        @cache
        def onRight(i):
            if i == n - 1:
                return i
            v = nums[i]
            nxt = nums[i+1]
            if nxt != v:
                return i
            return onRight(i + 1)

        res = inf

        @cache
        def onLeft(i):
            if i == 0:
                return i
            v = nums[i]
            prev = nums[i-1]
            if v != prev:
                return i
            return onLeft(i - 1)

        for i in range(1, n - 1):
            v = nums[i]
            # print('----')
            needLeft = onLeft(i) != 0
            costLeft = (i * v) if needLeft else 0
            goRight = onRight(i)
            needRight = goRight != n - 1
            costRight = ((n - goRight - 1) * v) if needRight else 0
            # print(f'{costLeft=} {costRight=} {goRight=}')
            res = min(res, costLeft + costRight)
            # print(f'{res=} for i={i}')

        if len(set(nums)) == 1:
            return 0

        return res