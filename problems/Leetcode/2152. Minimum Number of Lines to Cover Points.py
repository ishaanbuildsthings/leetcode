class Solution:
    def minimumLines(self, points: List[List[int]]) -> int:
        n = len(points)
        fmask = (1 << n) - 1
        
        def slope(p1, p2):
            rise = p1[1] - p2[1]
            run = p1[0] - p2[0]
            if not run:
                return (inf, 0)
            if run < 0:
                rise = -rise
                run = -run
            g = gcd(rise, run)
            return (rise // g, run // g)

        @cache
        def maskOfPointsCoveredBy(i1, i2):
            slopeHere = slope(points[i1], points[i2])

            mask = 1 << i1
            for i in range(n):
                if i == i1: continue
                if slope(points[i1], points[i]) == slopeHere:
                    mask |= (1 << i)
            return mask

        @cache
        def dp(mask):
            if mask == fmask:
                return 0
            if mask.bit_count() + 1 == fmask.bit_count():
                return 1
            resHere = inf
            p1 = (fmask ^ mask).bit_length() - 1 # max uncovered big, kind of like CF fish where we strip the top bit
            for p2 in range(p1):
                if mask & (1 << p2): continue
                fillMask = maskOfPointsCoveredBy(p1, p2)
                nmask = mask | fillMask
                ndp = 1 + dp(nmask)
                resHere = min(resHere, ndp)
            return resHere
        
        return dp(0)


