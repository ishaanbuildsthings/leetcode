class Solution:
    def makeAntiPalindrome(self, s: str) -> str:
        c = Counter(s)
        n = len(s)
        mxFrq = max(c.values())
        if mxFrq > n / 2:
            return '-1'

        ABC = 'abcdefghijklmnopqrstuvwxyz'
        # a b b c
        # we cannot just put a sorted list due to this above case
        res = [None] * n
        for i in range(n):
            opp = res[~i]
            for alpha in ABC:
                if alpha == opp:
                    continue
                if not c[alpha]:
                    continue
                c[alpha] -= 1
                res[i] = alpha
                break
        
        return ''.join(res)
                
