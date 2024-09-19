from functools import cache
# template by: https://github.com/agrawalishaan/leetcode
# pow, factorial, inverse factorial, combination, permutation, interleave, all preprocessed with `mod`
class ModCalc:
    def __init__(self, n, mod):
        self.n = n
        self.mod = mod
        self.modFacts = self._buildModFacts()
        self.invModFacts = self._buildInvModFacts()

    def _buildModFacts(self):
        modFacts = [1]  # 0!
        for i in range(1, self.n + 1):
            modFacts.append(self.modMul(modFacts[i - 1], i))
        return modFacts

    def _buildInvModFacts(self):
        invModFacts = [1] * self.n
        invModFacts[self.n - 1] = self.modInv(self.modFacts[self.n - 1])
        for i in range(self.n - 2, -1, -1):
            invModFacts[i] = self.modMul(i + 1, invModFacts[i + 1])
        return invModFacts

    # @cache # uncomment to cache
    def modInv(self, num):
        return self.modPow(num, self.mod - 2)

    def modMul(self, *args):
        result = 1
        for num in args:
            result = (result * num) % self.mod
        return result

    # @cache # uncomment to cache
    def modPow(self, base, exponent):
        return pow(base, exponent, self.mod)

    def modFact(self, n):
        return self.modFacts[n]

    # interleaving groups of 4 and 3 is (7!/(3!4!)), use mod inverse
    def modInterleaveTwoSubseq(self, a, b):
        facA = self.modFacts[a]
        facB = self.modFacts[b]
        facSum = self.modFacts[a + b]
        return self.modMul(self.modMul(facSum, self.modInv(facA)), self.modInv(facB))

    def starsBars(self, balls, buckets):
        return self.modComb(balls + buckets - 1, buckets - 1)

    def modCombi(self, n, k):
        return self.modMul(self.modFact(n), self.modInv(self.modMul(self.modFact(k), self.modFact(n - k))))

    def modPermu(self, n, k):
        return self.modMul(self.modFact(n), self.modInv(self.modFact(n - k)))
