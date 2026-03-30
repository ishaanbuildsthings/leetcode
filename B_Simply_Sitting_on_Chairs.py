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

def solve():
    # print('------')
    n = int(input())
    p = list(map(int,input().split()))
    p = [x-1 for x in p]
    # print(f'{p=}')
    fw = FenwickMultiset(n + 1)
    for v in p:
        fw.add(v)

    pf = []
    curr = 0
    for i, v in enumerate(p):
        if v <= i:
            curr += 1
        pf.append(curr)

    res = 0
    # this is the last chair we sit on
    # so how many on left have markings >i
    for i in range(len(p)-1,-1,-1):
        # print(f'{i=}')
        fw.remove(p[i])
        cnt = fw.countGreaterOrEqual(i+1)
        # print(f'before count that mark here or onwards: {cnt}')
        here = 1 + cnt + (pf[i-1] if i else 0)
        res = max(res,here)
        # print(f'res now: {res}')
    
    print(res)



t = int(input())
for _ in range(t):
    solve()