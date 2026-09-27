class Solution:
    def rearrangeArray(self, nums: list[int]) -> list[int]:
        res = []
        while nums:
            c = Counter(nums)
            vals = sorted(c.keys())
            for v in vals:
                res.append(v)
                c[v] -= 1
            nums2 = []
            for k, v in c.items():
                if v:
                    for _ in range(v):
                        nums2.append(k)
            nums = nums2

        return res