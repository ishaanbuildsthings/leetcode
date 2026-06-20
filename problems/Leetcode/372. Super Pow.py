class Solution:
    def superPow(self, a: int, b: List[int]) -> int:
        MOD = 1337
        @cache
        def modPow(base, power):
            if power == 0:
                return 1
            if power % 2:
                return (base * modPow(base, power - 1)) % MOD
            return (modPow(base, power // 2) ** 2) % MOD
        
        big = int(''.join(map(str, b)))
        return modPow(a, big)

