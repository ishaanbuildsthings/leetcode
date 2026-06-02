gpows = [1] # 2^x % MOD
MOD = 10**9 + 7
for _ in range(10**5 + 1):
    nextP = (pows[-1] * 2) % MOD
    pows.append(nextP)

class Solution:
    def sumSubseqWidths(self, nums: List[int]) -> int:
        nums.sort()
        res = 0
        for i in range(len(nums)):
            # nums[i] is the minimum
            onRight = len(nums) - i - 1
            res -= nums[i] * pows[onRight]
            # nums[i] is maximum
            onLeft = i
            res += nums[i] * pows[onLeft]
        return res % MOD
