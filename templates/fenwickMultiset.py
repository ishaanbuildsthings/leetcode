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