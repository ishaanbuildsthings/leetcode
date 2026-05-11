class FenwickMultiset:
    def __init__(self, maxVal):
        self.n = maxVal
        self.tree = [0] * (self.n + 2)
        self.total = 0
        self.cnt = [0] * (self.n + 1)

    def _update(self, i, delta):
        i += 1
        while i <= self.n + 1:
            self.tree[i] += delta
            i += i & (-i)

    def _query(self, i):
        i += 1
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)
        return s

    def add(self, val):
        isDuplicate = self.cnt[val] > 0
        self.cnt[val] += 1
        self._update(val, 1)
        self.total += 1
        return isDuplicate

    def remove(self, val):
        if self.cnt[val] == 0:
            return False
        self.cnt[val] -= 1
        self._update(val, -1)
        self.total -= 1
        return True

    def countLessOrEqual(self, x):
        if x < 0:
            return 0
        return self._query(min(x, self.n))

    def countGreaterOrEqual(self, x):
        if x > self.n:
            return 0
        return self.total - self._query(x - 1) if x > 0 else self.total
# SOLUTION 1, try every value as a potential min
class Solution:
    def maximumBeauty(self, flowers: List[int], newFlowers: int, target: int, full: int, partial: int) -> int:
        fen = FenwickMultiset(10**5 + 1)
        n = len(flowers)
        flowers.sort()
        res = 0
        completionCost = [None] * n
        cost = 0
        for i in range(n - 1, -1, -1):
            v = flowers[i]
            costToCompleteThisFlower = max(0, target - v)
            cost += costToCompleteThisFlower
            completionCost[i] = cost

        pf = []
        curr = 0
        for v in flowers:
            curr += v
            pf.append(curr)

        # 0...i will be incomplete
        # i + 1... will be complete
        for i in range(n - 1):
            fen.add(flowers[i])
            if flowers[i] >= target:
                break
            completeSuffix = completionCost[i + 1]
            if completeSuffix > newFlowers:
                continue
            remainOps = newFlowers - completeSuffix

            # find the max we can lift the prefix to
            l = 0
            r = target - 1
            mxFound = 0
            while l <= r:
                m = (l + r) // 2
                # can we lift the prefix all to m
                countLte = fen.countLessOrEqual(m)
                desireSum = countLte * m
                actualSum = pf[countLte - 1] if countLte else 0
                prefixOps = max(0, desireSum - actualSum)
                if prefixOps <= remainOps:
                    mxFound = m
                    l = m + 1
                else:
                    r = m - 1
            
            suffixScore = (n - i - 1) * full
            prefixScore = mxFound * partial
            score = prefixScore + suffixScore
            res = max(res, score)
        
        # edge case one, all are complete
        if completionCost[0] <= newFlowers:
            res = max(res, n * full)
        
        tot = sum(flowers)

        fen.add(flowers[-1])
        
        # edge case two, none are complete
        if max(flowers) < target:
            # find max we can lift to
            l = 0
            r = target - 1
            mxFound = 0
            while l <= r:
                m = (l + r) // 2
                countLte = fen.countLessOrEqual(m)
                desireSum = countLte * m
                actualSum = pf[countLte - 1] if countLte else 0
                prefixOps = max(0, desireSum - actualSum)
                if prefixOps <= newFlowers:
                    mxFound = m
                    l = m + 1
                else:
                    r = m - 1
            noneComplete = mxFound * partial
            res = max(res, noneComplete)
        
        return res
