class Solution:
    def minimizeStringValue(self, s: str) -> str:
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        
        c = Counter(s)

        gain = Counter()

        for _ in range(c['?']):
            minFrq = inf
            mn = None
            for v in ABC:
                if c[v] < minFrq:
                    minFrq = c[v]
                    mn = v
            gain[mn] += 1
            c[mn] += 1
        
        res = []
        for v in s:
            if v != '?':
                res.append(v)
                continue
            for v in ABC:
                if gain[v]:
                    gain[v] -= 1
                    res.append(v)
                    break
        
        return ''.join(res)