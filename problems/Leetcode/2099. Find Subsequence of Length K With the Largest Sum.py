class Solution:
    def maxSubsequence(self, nums: List[int], k: int) -> List[int]:
        # can use quickselect
        c = Counter(sorted(nums, reverse=True)[:k])
        res = []
        for n in nums:
            if c[n]:
                res.append(n)
                c[n] -= 1
        return res

        