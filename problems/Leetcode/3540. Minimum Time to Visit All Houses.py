class Solution:
    def minTotalTime(self, forward: List[int], backward: List[int], queries: List[int]) -> int:
        n = len(forward)

        pfF = []
        curr = 0
        for i in range(n):
            curr += forward[i]
            pfF.append(curr)

        pfB = []
        curr = 0
        for i in range(n):
            curr += backward[i]
            pfB.append(curr)

        def query(pf, l, r):
            if l > r:
                return 0
            return pf[r] - (pf[l - 1] if l > 0 else 0)

        res = 0
        cur = 0
        for q in queries:
            if cur == q:
                continue
            if cur < q:
                cw = query(pfF, cur, q - 1)
                ccw = query(pfB, 0, cur) + query(pfB, q + 1, n - 1)
            else:
                cw = query(pfF, cur, n - 1) + query(pfF, 0, q - 1)
                ccw = query(pfB, q + 1, cur)
            res += min(cw, ccw)
            cur = q
        return res