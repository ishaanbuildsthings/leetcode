def nextLetter(letter):
    return chr(ord(letter) + 1) if 'a' <= letter < 'z' else None

class Solution:
    def makeStringGood(self, s: str) -> int:
        count = [0] * 26
        for v in s:
            pos = ord(v) - ord('a')
            count[pos] += 1    
        
        res = inf

        # min # of operations to set everything to target (or make it disappear)
        def fn(target):

            @cache
            def dp(letterI, prevDeletedOrCarried):
                if letterI == 26:
                    return 0
                if count[letterI] < target:
                    deleteAll = count[letterI] + dp(letterI + 1, count[letterI])
                    ifFillVal = min(target, count[letterI] + prevDeletedOrCarried)
                    adding = (target - ifFillVal) + dp(letterI + 1, 0)
                    return min(deleteAll, adding)
                return (count[letterI] - target) + dp(letterI + 1, count[letterI] - target)
            return dp(0,0)
                
        for target in range(1, len(s) + 1):
            res = min(res, fn(target))
        
        return res