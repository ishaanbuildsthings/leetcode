class Solution:
    def maxGcdSum(self, nums: List[int], k: int) -> int:
        n = len(nums)
        _gcd = gcd # speed optimization lol

        LOG = n.bit_length()
        sparse = [[0] * n for _ in range(LOG)]
        sparse[0] = list(nums)
        for power in range(1, LOG):
            prev = sparse[power - 1]
            cur = sparse[power]
            halfWidth = 1 << (power - 1)
            limit = n - halfWidth
            for left in range(limit):
                cur[left] = _gcd(prev[left], prev[left + halfWidth])
            for left in range(limit, n):
                cur[left] = prev[left]

        pf = [0] * n
        pf[0] = nums[0]
        for i in range(1, n):
            pf[i] = pf[i - 1] + nums[i]

        res = 0
        nMinus1 = n - 1

        for l in range(n - k + 1):
            currentLeftBoundary = l + k - 1
            
            w = currentLeftBoundary - l + 1
            maxPow = w.bit_length() - 1
            desiredGcd = _gcd(sparse[maxPow][l], sparse[maxPow][l + w - (1 << maxPow)])

            while True:
                lo = currentLeftBoundary
                hi = nMinus1
                resRightmost = -1
                while lo <= hi:
                    m = (lo + hi) >> 1
                    w = m - l + 1
                    maxPow = w.bit_length() - 1
                    pw = 1 << maxPow
                    g = _gcd(sparse[maxPow][l], sparse[maxPow][l + w - pw])
                    if g >= desiredGcd:
                        resRightmost = m
                        lo = m + 1
                    else:
                        hi = m - 1

                if resRightmost == -1:
                    break

                totSum = pf[resRightmost] - pf[l - 1] if l else pf[resRightmost]
                score = totSum * desiredGcd
                if score > res:
                    res = score

                if desiredGcd == 1 or resRightmost == nMinus1:
                    break

                w = resRightmost - l + 2
                maxPow = w.bit_length() - 1
                pw = 1 << maxPow
                desiredGcd = _gcd(sparse[maxPow][l], sparse[maxPow][l + w - pw])
                currentLeftBoundary = resRightmost + 1

        return res