# template by: https://github.com/agrawalishaan/leetcode

# n in the constructor is basically the biggest number we will operate on. So for instance finding n! % MOD. But also things like interleaving two sequences of length 500 and length 700 would require n=1200. To be safe, can always just put a big number like 1e5.
class ModCalc:
    def __init__(self, n, primeMod):
        self.n = n
        self.mod = primeMod # If this is not prime, anything using modInv may break (fermat's little theorem)
        # O(n) time to build a factorial mod array
        self.factorialsWithMod = self._buildFactorialsWithMod()
        # O(n) time to build an inverse factorial mod array
        self.inverseFactorialsWithMod = self._buildInverseFactorialsWithMod()

    # ********** STUFF WITH FACTORIALS **********

    # O(n) time to build a factorial mod array
    def _buildFactorialsWithMod(self):
        factorialsWithMod = [1] # 0 factorial is 1
        for factorial in range(1, self.n + 1):
            factorialsWithMod.append(factorialsWithMod[-1] * factorial % self.mod)
        return factorialsWithMod

    # O(n) time to build an inverse factorial mod array
    def _buildInverseFactorialsWithMod(self):
        inverseFactorialsWithMod = [1] * (self.n + 1)
        inverseFactorialsWithMod[self.n] = self.modInv(self.factorialsWithMod[self.n])
        for i in range(self.n - 1, 0, -1):
            inverseFactorialsWithMod[i] = inverseFactorialsWithMod[i + 1] * (i + 1) % self.mod
        return inverseFactorialsWithMod

    # Gets (x! % MOD)
    # O(1) time
    def getFactorialWithMod(self, factorial):
        return self.factorialsWithMod[factorial]

    # Gets (1/x! % MOD)
    # O(1) time
    def getInverseFactorialWithMod(self, inverseFactorial):
        return self.inverseFactorialsWithMod[inverseFactorial]

    # Given two sequences of length X and Y, such as "123" and "4567", find the # of ways to interleave them.  Note we don't care about the actual items in each sequence, we just care about the # of ways we can interleave the two. We don't even get the actual sequences themselves, just their lengths.
    # O(1) time
    def interleaveTwoSequencesWithMod(self, length1, length2):
        # Interleaving a sequence of length 3 and 4 would be like 7!/(3!4!), which is 7! * (1/3!) * (1/4!)
        combinedLength = length1 + length2
        if combinedLength >= len(self.factorialsWithMod):
            raise ValueError(f"To interleave {length1} and {length2} items, we need at least {combinedLength + 1} items in the factorial array.")
        numerator = self.getFactorialWithMod(combinedLength)
        denominator1 = self.getInverseFactorialWithMod(length1)
        denominator2 = self.getInverseFactorialWithMod(length2)
        return self.modMultiply(numerator, denominator1, denominator2)


    # Calculates the # of ways to select k items from n unique items. Order does not matter.
    # Formula for C(n, k) = n! / (k!(n-k)!)
    # Denominator is 1/k! * 1/(n-k)!
    # O(1) time
    def nChooseKWithMod(self, n, k):
        if k > n:
            return 0
        numerator = self.getFactorialWithMod(n)
        denominator1 = self.getInverseFactorialWithMod(k)
        denominator2 = self.getInverseFactorialWithMod(n - k)
        return self.modMultiply(numerator, denominator1, denominator2)

    # Calculates the # of ways to select k items from n unique items. Order matters.
    # Formula for P(n, k) = n! / (n-k)!
    # Denominator is 1/(n-k)!
    # O(1) time
    def nPermuteKWithMod(self, n, k):
        if k > n:
            return 0
        numerator = self.getFactorialWithMod(n)
        denominator = self.getInverseFactorialWithMod(n - k)
        return self.modMultiply(numerator, denominator)

    # Calculate the # of ways to distribute n identical items into k distinct buckets (relates to stars and bars)
    # Formula for allowing empty buckets is C(n+k-1, k-1), which is: (n+k-1)! * 1/(n-1)! * 1/k!
    # Formula for NOT allowing empty buckets is C(n-1, k-1), which is: (n-1)! * 1/(n-k)! * 1/k!
    # O(1) time
    def waysToPutIdenticalItemsIntoDistinctBucketsWithMod(self, items, buckets, allowEmptyBuckets=True):
        if allowEmptyBuckets:
            return self.nChooseKWithMod(items + buckets - 1, buckets - 1)
        return self.nChooseKWithMod(items - 1, buckets - 1)

    # Putting n distinct items into k distinct buckets is just k options for the first item, k for the second, etc, so k^n. This is if we allow empty buckets. If we don't allow empty buckets, we need Stirling numbers of the second kind.
    # O(log items) time due to modPow, but modPow can be cached
    def waysToPutDistinctItemsIntoDistinctBucketsAllowingEmptyWithMod(self, items, buckets):
        return self.modPow(buckets, items)

    def waysToPutDistinctItemsIntoDistinctNonemptyBucketsWithMod(self, items, buckets):
        # need to figure out how to do this in O(1) if it is possible lol
        pass

    # ********** NO FACTORIALS NEEDED **********

    # Multiples k numbers together
    # O(k) time
    def modMultiply(self, *args):
        result = 1
        for num in args:
            result = (result * num) % self.mod
        return result

    # Calculates base^exponent % MOD
    # Can add caching if we are using the same base a lot. But if we are using one instance of the ModCalc class across all test cases, maybe that would MLE? I think no cache by default is better, since it is very fast already.
    # O(log exponent) time (even without caching)
    # @cache # uncomment to cache
    def modPow(self, base, exponent):
        return pow(base, exponent, self.mod)

    # Gets 1/x % MOD
    # Could cache this, if we are calling the same range of numbers a lot. If this class is created once across all test cases, could maybe MLE? Also num needs to be coprime to MOD.
    # O(log MOD) time
    # @cache # uncomment to cache
    def modInv(self, num):
        return self.modPow(num, self.mod - 2)


MOD = 998244353
calc = ModCalc(10**6 + 5, MOD)
import math
T = int(input())

for _ in range(T):
    n = int(input())
    A = list(map(int, input().split()))
    # n = 4
    # A = [5, 2, 2, 3, 3]

    extras = A[0]
    big = max(A[1:])

    # we need to distrubte the extra balls first, to fill every spot up to big-1 (or big if already big)
    for i in range(1, len(A)):
        if A[i] < big - 1:
            diff = (big - 1) - A[i]
            extras -= diff
            A[i] += diff
    
    if extras < 0:
        # print(f'couldnt fill out people with extra balls, ret 0')
        print(0)
        continue
    
    A = A[1:]


    lowSlots = 0
    for i in range(n):
        if A[i] != big:
            lowSlots += 1

    # how many of these low slots we can fill
    # if we can fill them all, we could basically force any permutation
    if extras >= lowSlots:
        # print(f'we can fill all, can force any permutation')
        ans = calc.getFactorialWithMod(len(A))
        print(ans)
        continue

    assignmentsForLow = calc.nChooseKWithMod(lowSlots, extras)
    newLow = lowSlots - extras
    newHigh = len(A) - newLow
    ans = (assignmentsForLow * calc.getFactorialWithMod(newLow) * calc.getFactorialWithMod(newHigh)) % MOD
    print(ans)