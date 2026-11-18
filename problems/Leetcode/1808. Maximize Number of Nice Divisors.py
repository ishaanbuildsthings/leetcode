class Solution:
    def maxNiceDivisors(self, primeFactors: int) -> int:
        # 2,2,2 5,5 -> 6 options in total

        # we want as even splits as possible that sum to <= primeFactors

        # we want to triple as much as we can then use a double

        doubles = 0
        triples = 0
        if primeFactors % 3 == 0:
            triples = primeFactors // 3
        elif primeFactors % 3 == 1:
            triples = (primeFactors - 4) // 3
            doubles = (primeFactors - (3 * triples)) // 2
        elif primeFactors % 3 == 2:
            triples = primeFactors // 3
            doubles = 1
        
        if primeFactors == 1:
            doubles = triples = 0
        
        MOD = 10**9 + 7

        @cache
        def modPow(base, e):
            if e == 0:
                return 1
            if e % 2:
                return (base * modPow(base, e - 1)) % MOD
            half = modPow(base, e // 2)
            return (half * half) % MOD

        return ((modPow(3, triples) if triples else 1) * (modPow(2, doubles) if doubles else 1)) % MOD