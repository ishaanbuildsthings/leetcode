# template by: https://github.com/agrawalishaan/leetcode

# ⚠️ Complexities could be wrong or not maximally optimized, prime stuff is confusing
# ⚠️ Probbly missing some useful methods
# ⚠️ Might not be constant factor optimized

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
p = Prime(10**5 + 1)
class Solution:
    def splitArray(self, nums: List[int]) -> int:
        aS = 0
        bS = 0
        for i in range(len(nums)):
            if p.isPrime(i):
                aS += nums[i]
            else:
                bS += nums[i]
        return abs(aS-bS)
        





# nums =
# [42]
# maxVal =
# 312
# Use Testcase
# Output
# 310
# Expected
# 311



# Wrong Answer
# 958 / 1001 testcases passed
# Input
# nums =
# [1000]
# maxVal =
# 1000
# Use Testcase
# Output
# 1001
# Expected
# 1000


# Wrong Answer
# 614 / 1001 testcases passed
# Input
# nums =
# [1]
# maxVal =
# 1
# Use Testcase
# Output
# 0
# Expected
# 1


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
        
        primeFacsToNums = [[] for _ in range(BIG + 1)]
        numToPrimeFacs = [[] for _ in range(BIG + 1)]
        for v in range(2, BIG + 1):
            facs = P.getPrimeFactorListDistinct(v)
            numToPrimeFacs[v] = facs
            for fac in facs:
                primeFacsToNums[fac].append(v)

        
        c = Counter(nums)

        res = -inf

        # try setting to 1 manually
        if 1 not in nums:
            res = 0
        else:
            res = 1

        primeFacToNumDupeCount = defaultdict(int) # maps a prime factor to the amount of numbers that are actually inside nums
        
        for primeKey in range(len(primeFacsToNums)):
            if primeKey > BIG:
                break
            if not primeFacsToNums[primeKey]:
                continue
            multiples = 0
            for v in primeFacsToNums[primeKey]:
                if c[v]:
                    multiples += c[v]
            primeFacToNumDupeCount[primeKey] = multiples

        # print(f'{primeFacToNumDupeCount=}')
            



        

        # consider this number as the coprime one
        # for num in range(maxVal, maxVal + 1):
        for num in range(2, maxVal + 1):
            print('=======')
            print(f'testing num: {num}')
            factors = numToPrimeFacs[num]
            # find how many numbers need to be modified
            # modded = set()

            moddedCount2 = 0
            for fac in factors:
                dupeMultiples = primeFacToNumDupeCount[fac]
                moddedCount2 += dupeMultiples

            print(f'modded count 2: {moddedCount2=}')
                
            # for fac in factors:
            #     for numberWithFac in primeFacsToNums[fac]:
            #         # skip unpresent
            #         if c[numberWithFac] == 0:
            #             continue
            #         modded.add(numberWithFac)
            # print(f'{modded=}')

            # modded is all unique numbers that share a factor with the target num
            # we might be worried about these
            
            # moddedCount = 0
            # for modified in modded:
            #     moddedCount += c[modified]

            # we can always change one of those
            # if num in modded:
            if c[num]:
                actualChange = moddedCount2 - 1
            else:
                # if not modded:
                if not moddedCount2:
                    actualChange = 1
                else:
                    actualChange = moddedCount2

            # print(f'actual change: {actualChange=}')
                
            scoreHere = num - actualChange
            res = max(res, scoreHere)
            # print(f'res now: {res}')

            # print(f'if {num} is the unique candidate then we have to modify: {moddedCount} numbers')

        # print('===============================')
        # print(f'first pass res: {res}')
        # print('===============================')

        numsAbove = [x for x in nums if x > maxVal]
        numsAbove = list(set(numsAbove))
        # print(f'{numsAbove=}')
        # or pick a number above max val as the coprime one, but only if it exists
        for num in numsAbove:
            # print(f'now testing num above: {num}')
            factors = numToPrimeFacs[num]
            modded = set()
            for fac in factors:
                for numberWithFac in primeFacsToNums[fac]:
                    if c[numberWithFac] == 0:
                        continue
                    modded.add(numberWithFac)
            moddedCount = 0
            for modified in modded:
                if modified != num:
                    moddedCount += c[modified]
                else:
                    moddedCount += c[modified] - 1
            # print(f'modded count: {moddedCount}')
            scoreHere = num - moddedCount
            res = max(res, scoreHere)
                    


        return res©leetcode