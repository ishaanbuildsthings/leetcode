class Solution:
    def movesToMakeZigzag(self, nums: List[int]) -> int:
        n = len(nums)

        # case 1, 0th index is bigger
        res1 = 0
        for i in range(1, n, 2):
            prev = nums[i-1]
            nxt = nums[i+1] if i != n - 1 else inf
            mn = min(prev, nxt)
            req = mn - 1
            if nums[i] <= req:
                continue
            diff = nums[i] - req
            res1 += diff
        
        # case 1, 1st index is bigger
        res2 = 0
        for i in range(0, n, 2):
            prev = nums[i-1] if i else inf
            nxt = nums[i+1] if i != n - 1 else inf
            mn = min(prev, nxt)
            req = mn - 1
            if nums[i] <= req:
                continue
            diff = nums[i] - req
            res2 += diff
        
        return min(res1, res2)