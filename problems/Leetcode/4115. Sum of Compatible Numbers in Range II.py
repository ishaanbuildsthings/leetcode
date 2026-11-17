class Solution:
    def sumOfGoodIntegers(self, n: int, k: int) -> int:
        high = n + k
        highS = bin(high)[2:]
        low = max(0, n - k)
        lowS = bin(low)[2:]
        ns = bin(n)[2:]
        diff2 = len(highS) - len(ns)
        ns = ('0' * diff2) + ns
        diff = len(highS) - len(lowS)
        lowS = ('0' * diff) + lowS
        MOD = 10**9 + 7

        # returns sum, count
        @cache
        def dp(i, lt, ht):
            if i == len(highS):
                return 0, 1
            u = int(highS[i]) if ht else 1
            d = int(lowS[i]) if lt else 0
            totHere = countHere = 0

            for digit in range(d, u + 1):
                if digit == 1 and ns[i] == '1':
                    continue
                nht = ht and digit == u
                nlt = lt and digit == d
                tots, counts = dp(i + 1, nlt, nht)
                totHere += tots
                countHere += counts
                if digit == 1:
                    totHere += (2 ** (len(highS) - i - 1)) * counts
            
            return totHere, countHere
        
        return dp(0, True, True)[0] % MOD
