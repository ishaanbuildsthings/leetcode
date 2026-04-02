class Solution:
    def numDecodings(self, s: str) -> int:
        MOD = 10**9 + 7
        n = len(s)
        @cache
        def dp(l):
            if l == n:
                return 1
            if s[l] == '0':
                return 0
            
            # if this digit were a 1
            ones = 0
            ones += dp(l + 1) # we just use the single 1 and move on
            if l < n - 1:
                nxt = s[l + 1]
                # 15 sort of thing, we use a double
                if nxt.isdigit():
                    ones += dp(l + 2)
                else:
                    # 1* works
                    ones += 9 * dp(l + 2)
            ones %= MOD

            twos = 0
            twos += dp(l + 1) # use a single 2
            if l < n - 1:
                nxt = s[l + 1]
                # 25 sort of thing, we use a double
                if nxt.isdigit():
                    if int(nxt) <= 6:
                        twos += dp(l + 2)
                else:
                    twos += 6 * dp(l + 2)
                    # otherwise nxt is *, we add all 6 digits
            twos %= MOD

            star = 0
            star += 7 * dp(l + 1) # we pick any starting digit 3-9
            star += ones
            star += twos
            star %= MOD

            if s[l] == '1':
                return ones
            if s[l] == '2':
                return twos
            if s[l] == '*':
                return star
            return dp(l + 1)
        return dp(0)