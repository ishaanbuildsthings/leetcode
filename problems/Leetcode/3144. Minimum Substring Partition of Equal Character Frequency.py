from copy import copy

class Solution:
    def minimumSubstringsInPartition(self, s: str) -> int:
        uniqueChars = len(set(s))

        @cache
        def dp(i):
            if i == len(s):
                return 0
            c = Counter() # count of each letter
            cc = Counter() # count of counts
            uniqueSizes = 0
            res = 1001
            for r in range(i, len(s)):
                oldCount = c[s[r]]
                cc[oldCount] -= 1
                if not cc[oldCount]:
                    uniqueSizes -= 1
                c[s[r]] += 1
                newCount = c[s[r]]
                cc[newCount] += 1
                if cc[newCount] == 1:
                    uniqueSizes += 1
                if uniqueSizes == 1:
                    splitHere = 1 + dp(r+1)
                    if splitHere < res:
                        res = splitHere
            return res
        
        a = dp(0)
        dp.cache_clear()
        return a

                
