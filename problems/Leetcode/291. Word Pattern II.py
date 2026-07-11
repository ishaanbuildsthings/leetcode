class Solution:
    def wordPatternMatch(self, pattern: str, s: str) -> bool:
        
        def bt(mp1, mp2, i, j):
            if i == len(pattern):
                return j == len(s)
            if j == len(s):
                return False
            for k in range(j, len(s)):
                substring = s[j:k+1]

                # if this substring was used it must be for that letter
                if substring in mp2:
                    if mp2[substring] != pattern[i]:
                        continue
                # if this pattern char was used it must be this substring
                if pattern[i] in mp1:
                    if mp1[pattern[i]] != substring:
                        continue
                
                old1 = mp1.get(pattern[i], None)
                old2 = mp2.get(substring, None)

                mp1[pattern[i]] = substring
                mp2[substring] = pattern[i]
                if bt(mp1, mp2, i + 1, k + 1):
                    return True
                
                if old1 is None:
                    del mp1[pattern[i]]
                else:
                    mp1[pattern[i]] = old1
                
                if old2 is None:
                    del mp2[substring]
                else:
                    mp2[substring] = old2
            
            return False
        
        return bt({}, {}, 0, 0)