# O(n) time / space
class Prime:
    def __init__(self, n):
        self.n = n
        spf = [0] * (n + 1)
        primes = []
        spf[1] = 1
        for i in range(2, n + 1):
            if spf[i] == 0:
                spf[i] = i
                primes.append(i)
            for p in primes:
                if p * i > n or p > spf[i]:
                    break
                spf[p * i] = p
        self.spf = spf
        self.primeList = primes
        self.isPrimeArr = [False, False] + [spf[i] == i for i in range(2, n + 1)]

    # O(1)  if num ≤ n
    # O(log num) deterministic Miller–Rabin (≤ 4 294 967 295) otherwise
    def isPrime(self, num):
        if num <= self.n:
            return self.isPrimeArr[num]
        return self._isPrimeDeterministic32(num)

    # O(log num), works for nums up to n^2
    # 12 -> [2, 2, 3]
    def getPrimeFactorListWithDuplicates(self, num):
        if num <= 1:
            return []
        if num <= self.n:
            res = []
            while num > 1:
                p = self.spf[num]
                res.append(p)
                num //= p
            return res
        res = []
        for p in self.primeList:
            if p * p > num:
                break
            while num % p == 0:
                res.append(p)
                num //= p
        if num > 1:
            res.append(num)
        return res

    # O(log num), works for nums up to n^2
    # 12 -> [2, 3]
    def getPrimeFactorListDistinct(self, num):
        factors = self.getPrimeFactorListWithDuplicates(num)
        res = []
        for p in factors:
            if not res or res[-1] != p:
                res.append(p)
        return res

    # O(log num)
    def getEulerTotient(self, num):
        res = num
        for p in set(self.getPrimeFactorListWithDuplicates(num)):
            res -= res // p
        return res

    # O(n log log n) time and O(n log log n) space I think
    # [[], [], [2], [3], [2,2], [5]] # number -> factors, O(n) since we re-use lists in the result
    def getFactorListsUpToIncludingN(self):
        factors = [[] for _ in range(self.n + 1)]
        for i in range(2, self.n + 1):
            p = self.spf[i]
            factors[i] = factors[i // p] + [p]
        return factors

    # O((high-low+1) · log log high)
    # Gets a list of prime numbers in low...high
    def getPrimesInRange(self, low, high):
        if high < 2 or high < low:
            return []
        low = max(low, 2)
        seg = [True] * (high - low + 1)
        root = int(high ** 0.5)
        for p in self.primeList:
            if p > root:
                break
            start = ((low + p - 1) // p) * p
            for num in range(start, high + 1, p):
                seg[num - low] = False
        if high > self.n:
            num = self.n + 1
            while num <= root:
                if self._isPrimeDeterministic32(num):
                    start = ((low + num - 1) // num) * num
                    for y in range(start, high + 1, num):
                        seg[y - low] = False
                num += 1
        return [low + i for i, v in enumerate(seg) if v]

    # helper – deterministic for num ≤ 4 294 967 295  (2³²–1)
    # O(log num)
    def _isPrimeDeterministic32(self, num):
        if num < 2:
            return False
        for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
            if num % p == 0:
                return num == p
        d, s = num - 1, 0
        while d % 2 == 0:
            d //= 2
            s += 1
        for a in (2, 7, 61):  # proven bases for 32-bit
            if a % num == 0:
                continue
            cur = pow(a, d, num)
            if cur in (1, num - 1):
                continue
            for _ in range(s - 1):
                cur = (cur * cur) % num
                if cur == num - 1:
                    break
            else:
                return False
        return True


# O(n log n) time / space (matches total output size)
# factors[i] -> list of all divisors of i, in ascending order
# uses harmonic series to compute this
def getDivisorListsUpToIncludingN(n):
    factors = [[] for _ in range(n + 1)]
    for d in range(1, n + 1):
        for m in range(d, n + 1, d):
            factors[m].append(d)
    return factors


# O(rootN) time
# Gets a list of all factors for a number, like 4 -> [1, 2, 4]
def getDivisors(num):
    if num <= 0:
        return []
    small, large = [], []
    i = 1
    while i * i <= num:
        if num % i == 0:
            small.append(i)
            if i != num // i:
                large.append(num // i)
        i += 1
    return small + large[::-1]


P = Prime(10**5 + 1)

class Solution:
    def maxScore(self, nums: List[int], maxVal: int) -> int:
        BIG = max(maxVal, max(nums))
        c = Counter(nums)

        facToCount = defaultdict(int) # maps number -> how many numbers are divisible by it
        for num in range(1, BIG + 1):
            for mult in range(num, BIG + 1, num):
                facToCount[num] += c[mult]
                
        primeFacsToCount = defaultdict(int)
        numToPrimeFacs = defaultdict(list)
        for v in range(2, BIG + 1):
            facs = P.getPrimeFactorListDistinct(v)
            numToPrimeFacs[v] = facs
            for fac in facs:
                primeFacsToCount[fac] += c[v]

        # try setting to 1 manually
        if 1 not in nums:
            res = 0
        else:
            res = 1

        allNums = list(range(2, maxVal + 1))
        numsAbove = [x for x in nums if x > maxVal]
        allNums += numsAbove
        allNums = list(set(allNums))
        
        
        # consider this number as the coprime one
        for num in allNums:
            factors = numToPrimeFacs[num]
            sharingAFactor = 0
            fmask = (1 << len(factors)) - 1
            for mask in range(1, fmask + 1):
                count = mask.bit_count()
                product = 1
                for b in range(len(factors)):
                    if (1 << b) & mask:
                        product *= factors[b]
                divisBy = facToCount[product]
                if count % 2 == 1:
                    sharingAFactor += divisBy
                else:
                    sharingAFactor -= divisBy

            if not c[num]:
                # if this number doesnt exist at least try to use one sharing a factor
                if sharingAFactor:
                    score = num - sharingAFactor
                else:
                    score = num - 1
            else:
                score = num - (sharingAFactor - 1)
            res = max(res, score)
            
        return res