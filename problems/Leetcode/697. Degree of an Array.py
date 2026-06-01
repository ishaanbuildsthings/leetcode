class Solution:
    def findShortestSubArray(self, nums: List[int]) -> int:
        big = max(Counter(nums).values())
        l = r = 0
        res = inf
        curr = Counter()
        while r < len(nums):
            curr[nums[r]] += 1
            if curr[nums[r]] < big:
                r += 1
                continue
            while curr[nums[r]] == big:
                curr[nums[l]] -= 1
                l += 1
            res = min(res, r - l + 1)
            r += 1
        return res + 1
    