class Solution:
    def countValidSubarrays(self, nums: list[int], x: int) -> int:
        n = len(nums)
        pf = list(accumulate(nums))
        res = 0
        curr = 0

        # dCount[d][i] = how many of pf[0...i-1] end in digit d
        dCount = [[0] * (n + 2) for _ in range(10)]

        for i in range(n):
            for d in range(10):
                dCount[d][i + 1] = dCount[d][i]
            dCount[pf[i] % 10][i + 1] += 1

        def query(l, r, d):
            if l > r:
                return 0
            return dCount[d][r + 1] - dCount[d][l]

        for i, v in enumerate(nums):
            curr += v
            lastDigit = curr % 10

            reqLastCut = (lastDigit - x) % 10
            mult = 1 # 1 10 100 ...
            for sz in range(1, 17):

                low = x * mult
                if low > curr:
                    break
                high = low + mult - 1

                # find the leftmost L such that L...r is in the range low...high
                l = 0
                r = i - 1
                resI = None
                while l <= r:
                    m = (l + r) // 2
                    if pf[m] >= curr - high:
                        resI = m
                        r = m - 1
                    else:
                        l = m + 1
                L = resI

                # find the rightmost L' such that L'...r is in the range low...high
                l = 0
                r = i - 1
                resI = None
                while l <= r:
                    m = (l + r) // 2
                    if pf[m] <= curr - low:
                        resI = m
                        l = m + 1
                    else:
                        r = m - 1
                LP = resI

                # now in that range, we need a target last digit to cut off

                # how many things in the range L...L' have a prefix sum where the last digit is reqLastCut?
                if L is not None and LP is not None:
                    res += query(L, LP, reqLastCut)

                if reqLastCut == 0 and curr <= high:
                    res += 1

                mult *= 10

        return res