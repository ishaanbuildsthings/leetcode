class Solution:
    def numDecodings(self, s: str) -> int:
        dp1 = 0 if s[-1] == '0' else 1
        dp2 = 1

        def isValid(twoDigit):
            if twoDigit[0] == '0' or twoDigit[0] > '2':
                return False
            if twoDigit[0] == '1':
                return True
            return twoDigit[1] <= '6'

        for i in range(len(s) - 2, -1, -1):
            if s[i] == '0':
                dp2 = dp1
                dp1 = 0
                continue

            newWays = dp1
            if isValid(s[i:i+2]):
                newWays += dp2

            dp2 = dp1
            dp1 = newWays

        return dp1