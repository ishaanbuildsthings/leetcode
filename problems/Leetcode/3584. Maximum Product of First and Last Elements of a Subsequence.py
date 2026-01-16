class Solution:
    def maximumProduct(self, nums: List[int], m: int) -> int:
        bigLeft = {}
        smallLeft = {}
        big = -inf
        small = inf
        for i in range(len(nums)):
            big = max(big, nums[i])
            small = min(small, nums[i])
            bigLeft[i] = big
            smallLeft[i] = small

        bigRight = {}
        smallRight = {}
        big = -inf
        small = inf
        for i in range(len(nums) - 1, -1, -1):
            big = max(big, nums[i])
            small = min(small, nums[i])
            bigRight[i] = big
            smallRight[i] = small

        res = -inf

        for i in range(len(nums)):
            right = i + m - 1
            if right >= len(nums):
                break
            curr = nums[i]
            opt1 = curr * bigRight[right]
            opt2 = curr * smallRight[right]
            res = max(res, opt1, opt2)
        return res
            