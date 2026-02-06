class Solution:
    def longestAlternating(self, nums: List[int]) -> int:
        n = len(nums)
        maxDown = [-1] * n # max subarray length ending at i where prev sign was down
        maxUp = [-1] * n

        maxDown[0] = 1
        maxUp[0] = 1

        for i in range(1, len(nums)):
            v = nums[i]
            if v > nums[i - 1]:
                maxUp[i] = 1 + maxDown[i - 1]
                maxDown[i] = 1
            elif v == nums[i - 1]:
                maxUp[i] = 1
                maxDown[i] = 1
            elif v < nums[i - 1]:
                maxDown[i] = 1 + maxUp[i - 1]
                maxUp[i] = 1


        maxUp2 = [-1] * n # max subarray length for i... where we need to use this sign next
        maxDown2 = [-1] * n
        maxUp2[-1] = 1
        maxDown2[-1] = 1

        for i in range(len(nums) - 2, -1, -1):
            v = nums[i]
            if v == nums[i + 1]:
                maxUp2[i] = 1
                maxDown2[i] = 1
            elif v < nums[i + 1]:
                maxUp2[i] = maxDown2[i + 1] + 1
                maxDown2[i] = 1
            elif v > nums[i + 1]:
                maxDown2[i] = maxUp2[i + 1] + 1
                maxUp2[i] = 1

        res = max(max(maxDown), max(maxUp))

        for i in range(1, len(nums) - 1):
            prev = nums[i-1]
            nxt = nums[i+1]
            if prev == nxt:
                continue
            elif prev > nxt:
                here = maxUp[i - 1] + maxUp2[i + 1]
                res = max(res, here)
            elif prev  < nxt:
                here = maxDown[i - 1] + maxDown2[i + 1]
                res = max(res, here)

        return res
            