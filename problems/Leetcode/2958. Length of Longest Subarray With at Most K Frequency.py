class Solution:
    def maxSubarrayLength(self, nums: List[int], k: int) -> int:
        res = 0
        l = 0
        r = 0
        frq = defaultdict(int)
        
        while r < len(nums):
            newNum = nums[r]
            frq[newNum] += 1
            while frq[newNum] > k:
                lostNum = nums[l]
                frq[lostNum] -= 1
                l += 1
            res = max(res, r - l + 1)
            r += 1
        return res
            