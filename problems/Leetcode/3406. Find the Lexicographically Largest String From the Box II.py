MOD = 10**9 + 7
BASE = 911
class Solution:
    def answerString(self, word: str, numFriends: int) -> str:
        if numFriends == 1:
            return word
            
        pf = []
        h = 0
        for v in word:
            coeff = ord(v) - ord('a') + 1
            h *= BASE
            h += coeff
            h %= MOD
            pf.append(h)
        
        basePow = [1]
        for sz in range(len(word) + 1):
            npow = (basePow[-1] * BASE) % MOD
            basePow.append(npow)
        
        def hash(l, r):
            full = pf[r]
            left = pf[l - 1] if l else 0
            left *= basePow[r - l + 1]
            return (full - left) % MOD
        
        maxSize = len(word) - numFriends + 1
        
        resL = 0
        resR = maxSize - 1

        # true if s1 is >= s2
        def bigger(L1, R1, L2, R2):
            w1 = R1 - L1 + 1
            w2 = R2 - L2 + 1

            # binary search for the size of the longest common prefix
            l = 1
            r = min(w1, w2)
            resSize = -1
            while l <= r:
                m = (l + r) // 2
                h1 = hash(L1, L1 + m - 1)
                h2 = hash(L2, L2 + m - 1)
                if h1 == h2:
                    resSize = m
                    l = m + 1
                else:
                    r = m - 1
            
            if resSize == -1:
                return word[L1] > word[L2]
            
            if w1 == w2 == resSize:
                return True
            
            if L1 + resSize >= len(word):
                return False
            if L2 + resSize >= len(word):
                return True
            next1 = word[L1 + resSize]
            next2 = word[L2 + resSize]
            return next1 >= next2

        for l in range(len(word)):
            r = l + maxSize - 1
            if r >= len(word):
                break
            
            # find LCP between resL...resR and l...r
            if bigger(l, r, resL, resR):
                resL = l
                resR = r
        
        for i in range(len(word) - 1, -1, -1):
            L = i
            R = len(word) - 1
            width = R - L + 1
            if width >= maxSize:
                break
            if bigger(L, R, resL, resR):
                resL = L
                resR = R
        
        return word[resL:resR+1]

            
        