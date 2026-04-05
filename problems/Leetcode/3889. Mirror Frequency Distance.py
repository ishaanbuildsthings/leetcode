class Solution:
    def mirrorFrequency(self, s: str) -> int:
        abc = 'abcdefghijklmnopqrstuvwxyz'

        ctoi = {
            c : i for i, c in enumerate(abc)
        }

        def mir(v):
            if v.isdigit():
                xx = int(v)
                opp = 9 - xx
                return str(opp)
            i = ctoi[v]
            opp = abc[~i]
            return opp

        c = Counter(s)

        allChar = set([v for v in s])
        pairs = set()
        res = 0
        for k in allChar:
            opp = mir(k)
            pair = tuple(sorted([k, opp]))
            if pair in pairs:
                continue
            pairs.add(pair)
            score = abs(c[k] - c[opp])
            res += score

        return res
            
            
                