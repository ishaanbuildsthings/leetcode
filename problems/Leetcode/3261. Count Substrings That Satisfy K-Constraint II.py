# O(21)
# Maps [L, R] -> some ordering
# 2^pow must be > max(R)
# 21: 2e6, 22: 4e6, etc.
# Use like:
# queries.sort(key=lambda q: hilbertOrder(q[0], q[1])), safe as the hilbert is computed once and cached, not re-ran per sort comparison
# Using mo's on hilbert order gives O(N * root Q) which is always better than O(N + Q) root N from normal Mo's. O(N * root Q) is also doable with normal Mo's using some other techniques.
# ⚠️ Not optimized
def hilbertOrder(l: int, r: int, pow: int = 21, rot: int = 0) -> int:
    if pow == 0:
        return 0
    hpow = 1 << (pow - 1)

    if l < hpow:
        seg = 0 if r < hpow else 3
    else:
        seg = 1 if r < hpow else 2

    seg = (seg + rot) & 3
    rotateDelta = (3, 0, 0, 1)

    nx = l & (hpow - 1)
    ny = r & (hpow - 1)
    nrot = (rot + rotateDelta[seg]) & 3

    subSize = 1 << (2 * pow - 2)
    ordv = seg * subSize

    add = hilbertOrder(nx, ny, pow - 1, nrot)
    ordv += add if (seg == 1 or seg == 2) else (subSize - add - 1)
    return ordv

class Solution:
    def countKConstraintSubstrings(self, s: str, k: int, queries: List[List[int]]) -> List[int]:
        origQueries = queries[:]

        n = len(s)
        left = [None] * n # how far left we can go from left[i] safely, where i is the rightmost edge

        l = r = ones = zeroes = 0
        while r < n:
            v = s[r]
            zeroes += v == '0'
            ones += v == '1'
            while ones > k and zeroes > k:
                lost = s[l]
                ones -= lost == '1'
                zeroes -= lost == '0'
                l += 1
            left[r] = l
            r += 1
        
        right = [None] * n
        l = r = n - 1
        ones = zeroes = 0
        while l >= 0:
            v = s[l]
            zeroes += v == '0'
            ones += v == '1'
            while ones > k and zeroes > k:
                lost = s[r]
                ones -= lost == '1'
                zeroes -= lost == '0'
                r -= 1
            right[l] = r
            l -= 1

        queries.sort(key=lambda q: hilbertOrder(q[0], q[1]))

        L = 0
        R = -1
        valid = 0

        def addL(l):
            nonlocal valid
            goRight = min(right[l], R)
            gained = goRight - l + 1
            valid += gained
        
        def addR(r):
            nonlocal valid
            goLeft = max(left[r], L)
            gained = r - goLeft + 1
            valid += gained
        
        def removeL(l):
            nonlocal valid
            goRight = min(right[l], R)
            lost = goRight - l + 1
            valid -= lost

        def removeR(r):
            nonlocal valid
            goLeft = max(left[r], L)
            lost = r - goLeft + 1
            valid -= lost
        
        lrToRes = {}
        for l, r in queries:
            while L > l:
                addL(L - 1)
                L -= 1
            while R < r:
                addR(R + 1)
                R += 1
            while L < l:
                removeL(L)
                L += 1
            while R > r:
                removeR(R)
                R -= 1
            lrToRes[l, r] = valid
        
        return [lrToRes[l, r] for l, r in origQueries]
                
        





