MAX_V = 10**5
spf = [None] * (MAX_V + 1)
spf[0] = spf[1] = 0
for v in range(2, MAX_V + 1):
    if spf[v] is not None:
        continue
    for mult in range(v, MAX_V + 1, v):
        if spf[mult] is None:
            spf[mult] = v

class Solution:
    def minDifference(self, n: int, k: int) -> List[int]:
        def primeFactorize(v):
            facs = []
            curr = v
            while curr > 1:
                fac = spf[curr]
                facs.append(fac)
                curr //= fac
            return facs
        
        primeFactors = primeFactorize(n)

        @cache
        def dp(i, tup):
            if i == len(primeFactors):
                diff = max(tup) - min(tup)
                return tup, diff
                return diff
            resTup = None
            resDiff = inf
            v = primeFactors[i]
            for pos in range(k):
                ntup = tuple(sorted(tup[:pos] + tuple([tup[pos] * v]) + tup[pos+1:]))
                finalTup, ndiff = dp(i + 1, ntup)
                if ndiff < resDiff:
                    resDiff = ndiff
                    resTup = finalTup
            return resTup, resDiff
        
        return list(dp(0, tuple([1] * k))[0])