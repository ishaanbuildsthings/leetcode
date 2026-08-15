class Solution:
    def removeSubstring(self, s: str, k: int) -> str:
        s2 = '(' * k + ')' * k
        stack = [] # holds (char, prefixMatchCount)
        for v in s:
            if not stack:
                if v == '(':
                    stack.append(('(', 1))
                else:
                    stack.append((')', 0))
                continue
            prevC, prevStreak = stack[-1]

            if v == '(':
                if prevC == '(':
                    nstreak = min(k, prevStreak + 1)
                else:
                    nstreak = 1
            else:
                if prevStreak >= k:
                    nstreak = prevStreak + 1
                else:
                    nstreak = 0
            
            stack.append((v, nstreak))
            
            if nstreak == 2 * k:
                for _ in range(2 * k):
                    stack.pop()

        res = []
        for a, b in stack:
            res.append(a)
        return ''.join(res)

class Solution:
    def removeSubstring(self, s: str, k: int) -> str:
        BASE = 911
        MOD = 10**9 + 7
        s2 = '(' * k + ')' * k

        hash2 = 0
        for v in s2:
            coeff = ord(v)
            hash2 *= BASE
            hash2 += coeff
            hash2 %= MOD

        basePow = []
        curr = 1
        for power in range(len(s) + 1):
            basePow.append(curr)
            curr *= BASE
            curr %= MOD


        stack = []
        pf = [] # holds pf hashes
        for v in s:
            coeff = ord(v)
            prevHash = pf[-1] if pf else 0
            nhash = ((prevHash * BASE) + coeff) % MOD
            pf.append(nhash)
            stack.append(v)
            if len(pf) < len(s2):
                continue
            R = len(pf) - 1
            L = R - len(s2) + 1
            full = pf[R]
            left = pf[L - 1] if L else 0
            left *= basePow[R - L + 1]
            left %= MOD
            final = (full - left) % MOD
            if final == hash2:
                for _ in range(2 * k):
                    pf.pop()
                    stack.pop()
        
        return ''.join(stack)            
        

