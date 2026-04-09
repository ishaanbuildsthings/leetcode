class BIT:
    __slots__ = ['n', 'tree']
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (self.n + 1)
        for i, v in enumerate(arr):
            if v:
                self.update(i, v)

    # point add
    def update(self, i, delta):
        i += 1
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)

    def queryPf(self, i):
        s = 0
        i += 1
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)
        return s

    def query(self, l, r):
        if l > r:
            return 0
        if l == 0:
            return self.queryPf(r)
        return self.queryPf(r) - self.queryPf(l - 1)


MX_NUM = 7 * 10**4
# MX_NUM = 100
numToFacs = [[] for _ in range(MX_NUM + 1)]
for factor in range(1, MX_NUM + 1):
    mult = 1
    while mult * factor <= MX_NUM:
        numToFacs[mult * factor].append(factor)
        mult += 1
class Solution:
    def totalBeauty(self, nums: List[int]) -> int:
        MOD = 10**9 + 7
        mx = max(nums)
        # for a number say 20 it has factors 1 2 4 5 10 20
        # any of those could be the gcd
        # so for each factor we look up that gcd map and we get a bucket of ending numbers
        # we need to add all ending numbers < 20 to the new dp layer

        # the total bucket sizes is harmonic series based
        # so the 1 bucket has all N numbers
        # the 2 bucket has N/2 numbers

        # so for a number we do O(d) factor checks
        # for each factor check we need a range dp add which we can use a lazy tree for
        # so that's n * d * log n

        # dps[factor] -> seg tree 
        dps = {}
        for factor in range(1, mx + 1):
            validEndingNumbers = mx // factor
            segArr = [0] * validEndingNumbers
            st = BIT(segArr)
            dps[factor] = st
        
        for i, v in enumerate(nums):
            for fac in numToFacs[v]:
                st = dps[fac]
                idx = (v // fac) - 1
                prevTot = st.query(0, idx - 1) if idx else 0
                st.update(idx, (1 + prevTot) % MOD) # 1 is for a new sequence we start
        
        divisibleBy = [0] * (mx + 1)
        # divisibleBy[x] is how many subsequences are strictly increasing and divisible by x
        for fac in range(1, mx + 1):
            st = dps[fac]
            tot = st.query(0, (mx // fac) - 1) % MOD
            divisibleBy[fac] = divisibleBy[fac] + tot % MOD
                
        res = 0
        for fac in range(mx, 0, -1):
            res += (fac * divisibleBy[fac]) % MOD
            res %= MOD

            for subFac in numToFacs[fac]:
                divisibleBy[subFac] -= divisibleBy[fac]
                divisibleBy[subFac] %= MOD
        
        return res



        