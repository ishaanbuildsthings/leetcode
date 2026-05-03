# used in https://leetcode.com/problems/sum-of-beautiful-subsequences/submissions/1973972991/
class BIT:
    __slots__ = ['n', 'tree']
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (self.n + 1)
        for i, v in enumerate(arr):
            if v:
                self.update(i, v)

    # point add, logN
    def update(self, i, delta):
        i += 1
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)

    # gets prefix sum 0...i
    def queryPf(self, i):
        s = 0
        i += 1
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)
        return s

    # gets sum l...r
    def query(self, l, r):
        if l > r:
            return 0
        if l == 0:
            return self.queryPf(r)
        return self.queryPf(r) - self.queryPf(l - 1)