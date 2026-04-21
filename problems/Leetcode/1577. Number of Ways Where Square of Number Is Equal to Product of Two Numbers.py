MAX = 10**5

# Smallest prime factor sieve, O(N log log N)
# spf[1] = 0, spf[prime] = prime, spf[composite] = smallest prime dividing it
spf = [0] * (MAX + 1)
for div in range(2, MAX + 1):
    if spf[div]:
        continue
    spf[div] = div
    mult = div * div
    while mult <= MAX:
        if spf[mult] == 0:
            spf[mult] = div
        mult += div

# Prime factorization using SPF sieve, O(logX) per call
# output shape: [(p1, e1), (p2, e2), ...] where x = Π (pi ** ei)
def primeFactorize(x):
    pfs = []
    cur = x
    while cur > 1:
        p = spf[cur]
        e = 0
        while cur % p == 0:
            e += 1
            cur //= p
        pfs.append((p, e))
    return pfs

# Generate all divisors from a prime factorization, O(D) where D = number of divisors
# Output shape: [d1, d2, ...] unsorted
def pfsToFacs(pfs):
    facs = [1]
    for p, e in pfs:
        primePow = 1
        cSize = len(facs)
        for usedE in range(1, e + 1):
            primePow *= p
            for i in range(cSize):
                facs.append(primePow * facs[i])
    return facs

# All divisors of x^2, given x
# We factor x (small), then double all exponents to get x^2's factorization
# Much faster than factoring x^2 directly
def divisorsOfSquare(x):
    pfs = primeFactorize(x)
    pfsDoubled = [(p, 2 * e) for p, e in pfs]
    return pfsToFacs(pfsDoubled)

class Solution:
    def numTriplets(self, nums1: List[int], nums2: List[int]) -> int:
        # a will have squared terms
        def process(a, b):
            c1 = Counter(a)
            c2 = Counter(b)
            res = 0
            for v in a:
                divOfSquare = sorted(divisorsOfSquare(v))
                for div in divOfSquare:
                    # dedupe pairs
                    if div > v:
                        break
                    if div != v:
                        res += c2[div] * c2[v**2 // div]
                    else:
                        res += c2[div] * (c2[div] - 1) // 2
            return res

        return process(nums1, nums2) + process(nums2, nums1)