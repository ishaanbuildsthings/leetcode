class Solution:
    def shortestBeautifulSubstring(self, s: str, k: int) -> str:
        
        pf = []
        BASE = 911
        MOD = 10**9 + 7
        basePow = []
        currH = 1
        for p in range(len(s) + 1):
            basePow.append(currH)
            currH *= BASE
            currH %= MOD
        currHash = 0
        for c in s:
            currHash *= BASE
            coeff = int(c) + 1
            currHash += coeff
            currHash %= MOD
            pf.append(currHash)
        
        def getHash(l, r):
            full = pf[r]
            width = r - l + 1
            leftHash = pf[l - 1] if l else 0
            leftHash *= basePow[width]
            leftHash %= MOD
            return (full - leftHash) % MOD

        
        def lcp(L, R, A, B):
            width = R - L + 1

            l = 1
            r = width
            res = 0
            while l <= r:
                m = (l + r) // 2
                h1 = getHash(L, L + m - 1)
                h2 = getHash(A, A + m - 1)
                if h1 == h2:
                    res = m
                    l = m + 1
                else:
                    r = m - 1
            return res
        
        resL = -1
        resR = -1
        l = r = 0
        ks = 0
        while r < len(s):
            gain = s[r]
            if gain == '1':
                ks += 1
            while ks > k:
                lost = s[l]
                if lost == '1':
                    ks -= 1
                l += 1
            

            # second condition, shrink while invalid e.g. leading 0s
            while l <= r and s[l] == '0':
                l += 1

            if ks < k:
                r += 1
                continue
            
            width = r - l + 1
            
            # if we previously had a better width, just keep going
            if resL != -1 and (resR - resL + 1) < width:
                r += 1
                continue
            
            # if we have a new best width, override
            if resL == -1 or (width < (resR - resL + 1)):
                resL = l
                resR = r
                r += 1
                continue
            
            # for a tie, compare lcp
            lcpVal = lcp(resL, resR, l, r)

            if lcpVal == width:
               r += 1
               continue
            
            next1 = s[resL + lcpVal]
            next2 = s[l + lcpVal]
            if int(next2) < int(next1):
                resL = l
                resR = r
            
            r += 1
        if resL == -1:
            return ''
        return s[resL:resR+1]


            
                
