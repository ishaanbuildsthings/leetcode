class Solution:
    def goodIntegers(self, l: int, r: int, k: int) -> int:

        r = str(r)
        l = str(l)
        diff = len(r) - len(l)
        l = ('0' * diff) + l

        print(f'{l=}')
        print(f'{r=}')

        @cache
        def dp(lt, ht, i, prev, nonZTaken):
            if i == len(r):
                return 1
            res = 0
            low = 0 if not lt else int(l[i])
            hi = 9 if not ht else int(r[i])
            for d in range(low, hi + 1):
                nlt = lt and d == low
                nht = ht and d == hi
                nn = nonZTaken or d != 0
                diff = abs(d - prev) if nonZTaken else 0
                if diff > k:
                    continue
                res += dp(nlt,nht,i+1,d, nn)
            return res

        ans = dp(True,True,0,None,False)
        return ans