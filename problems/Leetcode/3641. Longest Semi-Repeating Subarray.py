class Solution:
    def longestSubarray(self, nums: List[int], k: int) -> int:
        c = Counter()
        rep = 0
        l = r = res = 0
        n = len(nums)
        while r < n:
            gained = nums[r]
            c[gained] += 1
            if c[gained] == 2:
                rep += 1
            while rep > k:
                lost = nums[l]
                c[lost] -= 1
                if c[lost] == 1:
                    rep -= 1
                l += 1
            res = max(res, r - l + 1)
            r += 1
        return res