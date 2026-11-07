class Solution:
    def countValidSubstrings(self, s: str) -> int:
        n = len(s)
        @cache
        def dp(i, matches):
            if i == n:
                return 0
            resHere = 0
            nmatches = matches
            v = s[i]
            if v == 'a' and matches == 0 or v == 'b' and matches == 1 or v == 'c' and matches == 2:
                nmatches += 1
            if nmatches < 3:
                resHere += 1
                resHere += dp(i + 1, nmatches)
            return resHere
        return sum(dp(i, 0) for i in range(n))  