class Solution:
    def countTime(self, time: str) -> int:
        def isValid(t):
            a, b = map(int, t.split(':'))
            return a < 24 and b < 60
        
        res = set()
        a, b, c, d = time[:2] + time[3:]

        for v1 in range(3):
            v1Real = int(a) if a != '?' else v1
            for v2 in range(10):
                v2Real = int(b) if b != '?' else v2
                for v3 in range(6):
                    v3Real = int(c) if c != '?' else v3
                    for v4 in range(10):
                        v4Real = int(d) if d != '?' else v4
                        s = f'{v1Real}{v2Real}:{v3Real}{v4Real}'
                        if isValid(s):
                            res.add(s)
        
        return len(res)
