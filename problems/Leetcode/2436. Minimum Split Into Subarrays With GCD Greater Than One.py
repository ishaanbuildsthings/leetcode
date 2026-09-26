class Solution:
    def minimumSplits(self, nums: List[int]) -> int:
        res = 0
        currGcd = None
        for i in range(len(nums)):
            num = nums[i]
            gcdIfTakeNum = num if currGcd is None else math.gcd(currGcd, num)
            if gcdIfTakeNum == 1:
                res += 1
                currGcd = nums[i]
            else:
                currGcd = gcdIfTakeNum
        return res + 1