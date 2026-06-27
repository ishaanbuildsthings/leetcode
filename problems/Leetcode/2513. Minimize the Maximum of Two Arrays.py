class Solution:
    def minimizeSet(self, divisor1: int, divisor2: int, uniqueCnt1: int, uniqueCnt2: int):
        L = lcm(divisor1, divisor2)

        def canDo(x):
            divisA = x // divisor1
            divisB = x // divisor2
            divisBoth = x // L

            onlyA = divisB - divisBoth
            onlyB = divisA - divisBoth
            useForEither = x - divisA - divisB + divisBoth

            needA = uniqueCnt1
            needB = uniqueCnt2

            takeA = min(needA, onlyA)
            needA -= takeA

            takeB = min(needB, onlyB)
            needB -= takeB

            remaining = needA + needB
            return remaining <= useForEither

        l = 0
        r = 10**18
        res = None

        while l <= r:
            m = (l + r) // 2
            if canDo(m):
                res = m
                r = m - 1
            else:
                l = m + 1

        return res