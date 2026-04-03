class Solution:
    def recoverArray(self, n: int, sums: List[int]) -> List[int]:
        sums.sort()
        c = Counter(sums)
        mn = min(sums)
        ways = c[mn]
        zeroes = int(math.log2(ways))
        mult = 2**zeroes

        @cache
        def nck(n, k):
            return math.comb(n, k)

        dp = defaultdict(int)
        dp[0] = mult # number of ways to form sum X using only numbers 0...R that we have processed

        frq = Counter()
        frq[0] = zeroes
        # use abs here because again our code doesn't solve for positive factors, we don't know the sign
        for number in range(1, max(abs(x) for x in sums) + 1):
            tot = mn + number
            count = c[tot] # in theory we could have `number` up to this many times            
            alreadyFormed = dp[number]
            # not required to avoid tle but MASSIVE improvement
            # normally we copy our dp, of size up to 2^n, U times
            # but now we only copy it when we encounter a number in the actual array, which is like N times
            if count == alreadyFormed:
                continue

            actualNumber = (count - alreadyFormed) // mult
            # assume arr = [0, 3]
            # subset sums are [0, 0, 3, 3]
            # now we are at number=3
            # we claim there's at most 2 possible 3s in the array, by looking at mn+3
            # we haven't formed a total of 3 in dp yet, so we imply there are two 3s?
            # but there's only 1! because the zeroes inflate it

            ndp = dp.copy()
            for frqUsed in range(1, actualNumber + 1):
                # select = math.comb(actualNumber, frqUsed)
                select = nck(actualNumber, frqUsed)
                for prevDp in dp:
                    nsum = prevDp + (frqUsed * number)
                    ndp[nsum] += dp[prevDp] * select
            
            frq[number] = actualNumber
            
            dp = ndp
                
        absVals = []
        for number, cnt in frq.items():
            absVals.extend([number] * cnt)

        target = -mn
        m = len(absVals)
        for mask in range(1 << m):
            if sum(absVals[i] for i in range(m) if mask >> i & 1) == target:
                return [(-absVals[i] if mask >> i & 1 else absVals[i]) for i in range(m)]
