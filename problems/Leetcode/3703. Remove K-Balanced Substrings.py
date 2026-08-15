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
