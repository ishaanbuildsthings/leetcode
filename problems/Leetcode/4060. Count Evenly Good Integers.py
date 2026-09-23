class Solution:
    def countEvenlyGoodIntegers(self, l: int, r: int) -> int:
        B = str(r)
        A = str(l)
        diff = len(B) - len(A)
        A = ('0' * diff) + A

        @cache
        def dp(i, lt, ht, started, evenParity):
            if i == len(B):
                return evenParity ^ 1
            low = 0 if not lt else int(A[i])
            high = 9 if not ht else int(B[i])
            res = 0
            for d in range(low, high + 1):
                nlt = lt and d == low
                nht = ht and d == high
                nstarted = started or d != 0
                neven = evenParity
                if nstarted and d % 2 == 0:
                    neven ^= 1
                print(f'{neven=}')
                res += dp(i + 1, nlt, nht, nstarted, neven)
            return res
        
        return dp(0, True, True, False, 0)
            