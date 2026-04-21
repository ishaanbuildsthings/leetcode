class Solution:
    def isScramble(self, s1: str, s2: str) -> bool:
        # can l1...r1 become l2...r2
        @cache
        def dp(l1, r1, l2, r2):
            if l1 == r1:
                return s1[l1] == s2[l2]
            
            for allLeft in range(l1, r1):
                width = allLeft - l1 + 1

                # split and swap
                if dp(l1, allLeft, l2, l2 + width - 1) and dp(allLeft + 1, r1, l2 + width, r2):
                    return True
                
                # split but swap
                if (dp(l1, allLeft, r2 - width + 1, r2) and dp(allLeft + 1, r1, l2, r2 - width)):
                    return True
            

            return False
        
        return dp(0, len(s1) - 1, 0, len(s2) - 1)


            