class Solution:
    def countSubarrays(self, nums: List[int], k: int) -> int:
        l = r = res = count = 0
        n = len(nums)
        mx = max(nums)
        lateL = None
        while r < n:
            gained = nums[r]
            count += gained == mx
            while count >= k:
                lost = nums[l]
                lateL = l
                count -= lost == mx
                l += 1
            if lateL is not None:
                res += lateL + 1
            r += 1
        return res

