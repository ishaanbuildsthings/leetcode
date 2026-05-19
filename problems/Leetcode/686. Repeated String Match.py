class Solution:
    def repeatedStringMatch(self, a: str, b: str) -> int:
        MOD = 10**9 + 7
        BASE = 26

        @cache
        def modPow(base, exponent, mod):
            if exponent == 0:
                return 1
            if exponent == 1:
                return base % mod
            half = modPow(base, exponent // 2, mod)
            if exponent % 2 == 0:
                return (half * half) % mod
            else:
                return (half * half * base) % mod

        def val(letter):
            return ord(letter) - ord('a') + 1

        def isSubstring(haystack, needle):
            if len(haystack) < len(needle):
                return False

            # compute target hash
            targetHash = 0
            haystackHash = 0
            for i in range(len(needle)):
                haystackHash *= BASE
                haystackHash += val(haystack[i])
                haystackHash %= MOD

                targetHash *= BASE
                targetHash += val(needle[i])
                targetHash %= MOD

            if haystackHash == targetHash:
                return True
            
            # slide haystack
            for r in range(len(needle), len(haystack)):
                leftpow = len(needle) - 1
                leftIndex = r - len(needle)
                leftVal = haystack[leftIndex]
                leftValue = val(leftVal)
                leftPowContribution = modPow(BASE, leftpow, MOD)
                leftModContribution = (leftValue * leftPowContribution) % MOD
                haystackHash -= leftModContribution
                haystackHash %= MOD

                haystackHash *= BASE
                newChar = haystack[r]
                haystackHash += val(newChar)
                haystackHash %= MOD

                if haystackHash == targetHash:
                    return True
            
            return False

    
        l = math.ceil(len(b) / len(a))
        r = 2 * math.ceil(len(b) / len(a))
        res = None
        while l <= r:
            m = (r + l) // 2
            if isSubstring(a * m, b):
                res = m
                r = m - 1
            else:
                l = m + 1
        return res if res != None else -1



