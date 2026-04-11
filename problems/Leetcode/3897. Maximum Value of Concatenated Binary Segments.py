@cache
def modPow(base, exponent, mod):
    if exponent == 0:
        return 1
    if exponent == 1:
        return base % mod
    half = modPow(base, exponent // 2, mod)
    if exponent % 2 == 0:
        return (half * half) % mod
    else:
        return (half * half * base) % mod

class Solution:
    def maxValue(self, nums1: list[int], nums0: list[int]) -> int:
        MOD = 10**9 + 7

        def cmp(a, b):
            # option 1, if A+B < B+A put A before B, but this takes A+B time so the sort becomes (n+L) log n where n is the # of terms and L is the total length of all terms
            # if a[0] + b[0] < b[0] + a[0]:
            #     return 1
            # return -1
            # option 2, we don't spend A+B time, we spend O(1) time, so sort is n log n
            # put the one with more leading ones on the left, if tied, fewer 0s, but edge case of all 1s should always go left

            if not a[2]:
                return -1
            if not b[2]:
                return 1
                
            # more 1s goes on the left
            if a[1] > b[1]:
                return -1
            elif a[1] < b[1]:
                return 1
            # fewer 0s on the left
            if a[2] < b[2]:
                return -1
            return 1

        segs = []
        for i in range(len(nums1)):
            segment = ([1] * nums1[i]) + ([0] * nums0[i])
            segs.append([segment, nums1[i], nums0[i]])

        segs.sort(key=cmp_to_key(cmp))

        segs = [x[0] for x in segs]

        arr = []
        for seg in segs:
            for v in seg:
                arr.append(str(v))
        
        res = 0
        for i in range(len(arr)):
            v = int(arr[~i])
            if v:
                mpowed = modPow(2, i, MOD)
                res += mpowed
            res %= MOD

        return res