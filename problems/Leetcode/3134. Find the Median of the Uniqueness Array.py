class Solution:
    def medianOfUniquenessArray(self, nums: List[int]) -> int:
        n = len(nums)
        uniq = len(set(nums))
        subarrays = n * (n + 1) // 2
        req = subarrays // 2 if not subarrays % 2 else ceil(subarrays / 2)

        def countSubarraysWithDistinctLteX(x):
            l = r = resHere = 0
            frq = Counter()
            while r < n:
                gain = nums[r]
                frq[gain] += 1
                # shrink while invalid
                while len(frq) > x:
                    lost = nums[l]
                    frq[lost] -= 1
                    if not frq[lost]: del frq[lost]
                    l += 1
                resHere += r - l + 1
                r += 1
            return resHere

        l = 1
        r = uniq
        res = None
        # find the smallest distinct count where we have at least req subarrays with <= that distinct count
        while l <= r:
            m = (l + r) // 2
            if countSubarraysWithDistinctLteX(m) >= req:
                res = m
                r = m - 1
            else:
                l = m + 1
        
        return res

