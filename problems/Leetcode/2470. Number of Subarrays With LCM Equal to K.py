class Solution:
    def subarrayLCM(self, nums: list[int], k: int) -> int:
        l = r = res = 0
        currLcm = 1
        n = len(nums)

        MAX_V = max(nums)
        spf = [0] * (MAX_V + 1)
        spf[0] = spf[1] = 0
        for num in range(2, MAX_V + 1):
            if spf[num] != 0:
                continue
            for mult in range(num, MAX_V + 1, num):
                if spf[mult] == 0:
                    spf[mult] = num
        
        @cache
        def primeFactorize(num):
            primes = Counter() # prime -> count
            curr = num
            while curr > 1:
                p = spf[curr]
                e = 0
                while curr % p == 0:
                    e += 1
                    curr //= p
                primes[p] = e
            return primes
        
        def withLcmLteX(x):
            if x == 0:
                return 0
            l = r = res = 0
            currLcm = 1
            primeFactorToSortedListOfPowers = defaultdict(SortedList)

            while r < n:
                gain = nums[r]
                primeCounts = primeFactorize(gain)
                for p, e in primeCounts.items():
                    oldE = primeFactorToSortedListOfPowers[p][-1] if primeFactorToSortedListOfPowers[p] else 0
                    if e > oldE:
                        diff = e - oldE
                        currLcm *= (p ** diff)
                    primeFactorToSortedListOfPowers[p].add(e)
                
                while currLcm > x:
                    lost = nums[l]
                    primeCounts = primeFactorize(lost)
                    for p, e in primeCounts.items():
                        oldMax = primeFactorToSortedListOfPowers[p][-1]
                        primeFactorToSortedListOfPowers[p].remove(e)
                        nmax = primeFactorToSortedListOfPowers[p][-1] if primeFactorToSortedListOfPowers[p] else 0
                        currLcm //= (p ** (oldMax - nmax))
                    l += 1
                
                res += r - l + 1
                r += 1
            
            return res
        
        return withLcmLteX(k) - withLcmLteX(k - 1)


