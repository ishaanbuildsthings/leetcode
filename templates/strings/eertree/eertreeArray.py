from bisect import bisect_left

# Palindromic tree (eertree) over an array a of any comparable, hashable values
# (ints of any size, negatives, floats, strings, tuples -- values are compared
# only for equality, never used as indices, so anything sortable works).
# Internally each distinct palindromic subarray of a is one node, but no method
# below exposes nodes -- everything is stated in terms of indices into a.
# An array of length n has at most n distinct palindromic subarrays, so every
# list returned below has size <= n.
# numUniqueValsInArray below = how many DISTINCT values actually appear in a
# (derived from a): 2 for a binary array, 4 for DNA, up to n in general.

class Eertree:
    # O(n log numUniqueValsInArray) time, O(n) memory
    # (the transition table is dense when small enough to afford, else hashed,
    # and is discarded when the build ends -- it is not kept on the object)
    def __init__(self, a):
        self.a = a
        n = self.n = len(a)
        vals = sorted(set(a))
        k = self.numUniqueValsInArray = max(1, len(vals))
        code = [bisect_left(vals, x) for x in a]
        self.palLen = [-1, 0]
        self.palLink = [0, 0]
        self.depth = [0, 0]
        self.firstEnd = [-1, -1]
        self.diff = [0, 0]
        self.sLink = [0, 0]
        self.sufNode = [0] * n
        self.newAt = [0] * n
        self._occ = None
        self._revLen = None
        self._prefCnt = None

        if (n + 2) * k <= 2_000_000:
            table = [0] * ((n + 2) * k)
            def getT(v, c):
                return table[v * k + c]
        else:
            table = {}
            def getT(v, c):
                return table.get(v * k + c, 0)
        def setT(v, c, u):
            table[v * k + c] = u

        last = 1
        for i in range(n):
            c = code[i]
            cur = last
            while True:
                j = i - self.palLen[cur] - 1
                if j >= 0 and code[j] == c:
                    break
                cur = self.palLink[cur]
            ex = getT(cur, c)
            if ex:
                last = ex
                self.sufNode[i] = last
                continue
            v = len(self.palLen)
            self.palLen.append(self.palLen[cur] + 2)
            self.firstEnd.append(i)
            if self.palLen[v] == 1:
                link = 1
            else:
                t = self.palLink[cur]
                while True:
                    j = i - self.palLen[t] - 1
                    if j >= 0 and code[j] == c:
                        break
                    t = self.palLink[t]
                link = getT(t, c)
            self.palLink.append(link)
            self.depth.append(self.depth[link] + 1)
            d = self.palLen[v] - self.palLen[link]
            self.diff.append(d)
            self.sLink.append(link if d != self.diff[link] else self.sLink[link])
            setT(cur, c, v)
            self.newAt[i] = 1
            last = v
            self.sufNode[i] = last

    # O(1) -- the smallest l such that a[l..r] is a palindrome
    def leftmostLForPalEndingAt(self, r):
        return r - self.palLen[self.sufNode[r]] + 1

    # O(n) -- list of size n, res[r] = leftmostLForPalEndingAt(r)
    def leftmostLForPalEndingAtEach(self):
        return [self.leftmostLForPalEndingAt(r) for r in range(self.n)]

    # O(n log numUniqueValsInArray) on first call (builds the eertree of reversed
    # a), O(1) after -- the largest r such that a[l..r] is a palindrome
    def rightmostRForPalStartingAt(self, l):
        if self._revLen is None:
            rev = Eertree(self.a[::-1])
            self._revLen = [rev.palLen[v] for v in rev.sufNode]
        return l + self._revLen[self.n - 1 - l] - 1

    # O(n log numUniqueValsInArray) on first call, O(n) after
    # list of size n, res[l] = rightmostRForPalStartingAt(l)
    def rightmostRForPalStartingAtEach(self):
        self.rightmostRForPalStartingAt(0)
        n = self.n
        return [l + self._revLen[n - 1 - l] - 1 for l in range(n)]

    # O(1) -- how many distinct palindromic subarrays a[0..r] has
    def numDistinctPalsInPrefix(self, r):
        if self._prefCnt is None:
            self._prefCnt = []
            run = 0
            for i in range(self.n):
                run += self.newAt[i]
                self._prefCnt.append(run)
        return self._prefCnt[r]

    # O(n) -- list of size n, res[r] = numDistinctPalsInPrefix(r)
    def numDistinctPalsInPrefixEach(self):
        self.numDistinctPalsInPrefix(0)
        return list(self._prefCnt)

    # O(1) -- how many distinct palindromic subarrays a has, at most n
    def numDistinctPals(self):
        return len(self.palLen) - 2

    # O(1) -- how many palindromic subarrays end exactly at r, counting every
    # distinct palindrome that ends there (they are all suffixes of a[0..r])
    def numPalsEndingAt(self, r):
        return self.depth[self.sufNode[r]]

    # O(n) -- list of size n, res[r] = numPalsEndingAt(r)
    def numPalsEndingAtEach(self):
        return [self.depth[self.sufNode[r]] for r in range(self.n)]

    # O(n) -- total number of palindromic subarrays of a with multiplicity
    # (so [5, 5] counts 3: two single 5's and one [5, 5]), up to n * (n + 1) / 2
    def numPalsTotal(self):
        return sum(self._occCounts()[2:])

    # O(n) -- list of (l, r, count), one entry per DISTINCT palindromic subarray
    # of a, so at most n entries. a[l..r] is that palindrome (using its first
    # occurrence) and count is how many times it occurs in a.
    def distinctPalsWithCounts(self):
        occ = self._occCounts()
        res = []
        for v in range(2, len(self.palLen)):
            e = self.firstEnd[v]
            res.append((e - self.palLen[v] + 1, e, occ[v]))
        return res

    # O(n log n) -- fewest palindromes a can be cut into
    def minPalPartition(self):
        n = self.n
        INF = float("inf")
        dp = [INF] * (n + 1)
        dp[0] = 0
        seriesAns = [0] * len(self.palLen)
        for i in range(1, n + 1):
            v = self.sufNode[i - 1]
            while self.palLen[v] > 0:
                seriesAns[v] = dp[i - self.palLen[self.sLink[v]] - self.diff[v]]
                if self.diff[v] == self.diff[self.palLink[v]]:
                    seriesAns[v] = min(seriesAns[v], seriesAns[self.palLink[v]])
                if seriesAns[v] + 1 < dp[i]:
                    dp[i] = seriesAns[v] + 1
                v = self.sLink[v]
        return dp[n]

    def _occCounts(self):
        if self._occ is None:
            occ = [0] * len(self.palLen)
            for v in self.sufNode:
                occ[v] += 1
            for v in range(len(self.palLen) - 1, 1, -1):
                occ[self.palLink[v]] += occ[v]
            occ[0] = occ[1] = 0
            self._occ = occ
        return self._occ