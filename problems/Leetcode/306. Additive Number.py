class Solution:
    def isAdditiveNumber(self, num: str) -> bool:
        @cache
        def dp(i, p1, p2, usedThird):
            if i == len(num):
                return usedThird
            for j in range(i, len(num)):
                v = int(num[i:j+1])
                if (j - i + 1) >= 2 and num[i] == '0':
                    break
                if p1 is not None and p2 is not None and v == p1 + p2:
                    opt = dp(j + 1, p2, v, True)
                    if opt:
                        return True
                if p1 is not None and p2 is not None and v != (p1 + p2):
                    continue
                opt = dp(j + 1, p2, v, False)
                if opt:
                    return True
            return False
        
        return dp(0,None,None,False)
        
