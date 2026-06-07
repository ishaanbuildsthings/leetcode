class Solution:
    def maxSum(self, nums: List[int]) -> int:
        res = 0
        c = Counter(nums)
        for key in c:
            if key > 0:
                res += key
        if res == 0:
            return max(nums)
        return res