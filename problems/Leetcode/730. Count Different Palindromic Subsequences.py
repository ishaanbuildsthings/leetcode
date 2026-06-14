class Solution:
    def countPalindromicSubsequences(self, s: str) -> int:
        ABC = sorted(list(set(s)))
        curr = {
            c : inf for c in ABC
        }
        iToRightmostClosests = {}
        for i in range(len(s) - 1, -1, -1):
            iToRightmostClosests[i] = curr.copy()
            curr[s[i]] = i
        
        curr = {
            c : -inf for c in ABC
        }
        iToLeftmostClosests = {}
        for i in range(len(s)):
            iToLeftmostClosests[i] = curr.copy()
            curr[s[i]] = i
        
        MOD = 10**9 + 7

        @cache
        def dp(l, r):
            if l > r:
                return 0
            # I manually handle single letter palindromes outside
            if l == r:
                return 0
            
            resHere = 1 # do nothing

            rights = iToRightmostClosests[l]
            lefts = iToLeftmostClosests[r]

            # add single letter centers
            for c in ABC:
                newL = rights[c]
                if newL < r:
                    resHere += 1

            for c in ABC:
                newL = rights[c]
                newR = lefts[c]
                resHere += dp(newL, newR)
            
            return resHere % MOD
        
        ans = 0
        for c in ABC:
            firstOcc = inf
            lastOcc = -inf
            for i in range(len(s)):
                if s[i] == c:
                    firstOcc = min(firstOcc, i)
                    lastOcc = i
            if firstOcc != lastOcc:
                ans += dp(firstOcc, lastOcc)
        
        # add the normal single letters
        ans += len(ABC)
        
        return ans % MOD


                

            