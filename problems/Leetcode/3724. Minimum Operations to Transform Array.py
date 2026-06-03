class Solution:
    def minOperations(self, nums1: List[int], nums2: List[int]) -> int:
        n1 = len(nums1)
        n2 = len(nums2)

        res = 1 # a single append

        for i, v in enumerate(nums1):
            diff = abs(nums2[i] - nums1[i])
            res += diff

        # print(f'res after append and diff: {res}')

        last = nums2[-1]

        def in2(low, high, num):
            return num >= low and num <= high

        # was that last number inside any range
        for i in range(n1):
            low = min(nums1[i], nums2[i])
            high = max(nums1[i], nums2[i])
            if in2(low, high, last):
                # print(f'in range, ret')
                return res

        # find closest to any low or any high
        closest = inf
        for i in range(n1):
            low = min(nums1[i], nums2[i])
            high = max(nums1[i], nums2[i])
            d1 = abs(last - low)
            d2 = abs(last - high)
            closest = min(closest, d1, d2)

        return res + closest
            
            