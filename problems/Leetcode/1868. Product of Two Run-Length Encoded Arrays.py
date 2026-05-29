class Solution:
    def findRLEArray(self, enc1: List[List[int]], enc2: List[List[int]]) -> List[List[int]]:
        prod = []
        i = j = 0
        n = len(enc1)
        m = len(enc2)
        while i < n and j < m:
            b1 = enc1[i][1]
            b2 = enc2[j][1]
            mn = min(b1, b2)
            val = enc1[i][0] * enc2[j][0]
            prod.append([val, mn])
            enc1[i][1] -= mn
            enc2[j][1] -= mn
            if enc1[i][1] == 0:
                i += 1
            if enc2[j][1] == 0:
                j += 1
        while i < n:
            prod.append(enc1[i])
            i += 1
        while j < m:
            prod.append(enc2[j])
            j += 1
        
        res = [prod[0]]
        for i in range(1, len(prod)):
            v, frq = prod[i]
            pv, pfrq = res[-1]
            if pv == v:
                res[-1][-1] += frq
            else:
                res.append([v, frq])
        
        return res