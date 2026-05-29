class Solution:
    def hasMatch(self, s: str, p: str) -> bool:
        @cache
        def canBeDone(sI, pI):
            if pI == len(p):
                return True
            if pI == len(p) - 1 and p[-1] == '*':
                return True
            if sI == len(s):
                return False
            if p[pI] == '*':
                if canBeDone(sI + 1, pI + 1):
                    return True
                for newSi in range(sI + 1, len(s) + 1):
                    if canBeDone(newSi, pI + 1):
                        return True
                if canBeDone(sI, pI + 1):
                    return True
                return False
            if s[sI] == p[pI]:
                return canBeDone(sI + 1, pI + 1)
            return False
            
            
        
        for startPos in range(len(s)):
            if canBeDone(startPos, 0):
                return True
        
        return False
        
            