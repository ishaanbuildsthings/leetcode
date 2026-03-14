class Solution:
    def gcdSum(self, nums: list[int]) -> int:
        mx = []
        curr = 0
        for v in nums:
            curr = max(curr, v)
            mx.append(curr)

        prefixGcd = []
        for i in range(len(nums)):
            prefixGcd.append(gcd(nums[i], mx[i]))

        prefixGcd.sort()

        res = 0
        l = 0
        r = len(prefixGcd) - 1
        while l < r:
            res += gcd(prefixGcd[l], prefixGcd[r])
            l += 1
            r -= 1

        return res