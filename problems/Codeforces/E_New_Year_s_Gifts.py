if True:
    from io import BytesIO, IOBase
    import sys
    import os
    BUFSIZE = 4096

    class FastIO(IOBase):
        newlines = 0

        def __init__(self, file):
            self._fd = file.fileno()
            self.buffer = BytesIO()
            self.writable = "x" in file.mode or "r" not in file.mode
            self.write = self.buffer.write if self.writable else None

        def read(self):
            while True:
                b = os.read(self._fd, max(os.fstat(self._fd).st_size, BUFSIZE))
                if not b:
                    break
                ptr = self.buffer.tell()
                self.buffer.seek(0, 2)
                self.buffer.write(b)
                self.buffer.seek(ptr)
            self.newlines = 0
            return self.buffer.read()

        def readline(self):
            while self.newlines == 0:
                b = os.read(self._fd, max(os.fstat(self._fd).st_size, BUFSIZE))
                self.newlines = b.count(b"\n") + (not b)
                ptr = self.buffer.tell()
                self.buffer.seek(0, 2)
                self.buffer.write(b)
                self.buffer.seek(ptr)
            self.newlines -= 1
            return self.buffer.readline()

        def flush(self):
            if self.writable:
                os.write(self._fd, self.buffer.getvalue())
                self.buffer.truncate(0)
                self.buffer.seek(0)

    class IOWrapper(IOBase):
        def __init__(self, file):
            self.buffer = FastIO(file)
            self.flush = self.buffer.flush
            self.writable = self.buffer.writable
            self.write = lambda s: self.buffer.write(s.encode("ascii"))
            self.read = lambda: self.buffer.read().decode("ascii")
            self.readline = lambda: self.buffer.readline().decode("ascii")

    sys.stdin = IOWrapper(sys.stdin)
    sys.stdout = IOWrapper(sys.stdout)
    input = lambda: sys.stdin.readline().rstrip("\r\n")

data = sys.stdin.buffer.read()
it = iter(data.split())

def nextInt():
    return int(next(it))

from bisect import bisect_right

def rightmostLTE(arr, x):
    i = bisect_right(arr, x) - 1
    return i # returns -1 if nothing is <= X

class SegTree:
    def __init__(self, arr):
        self.n = len(arr)
        n = self.n
        negInf = -10**30
        self.val = [negInf] * (2 * n)
        self.idx = [-1] * (2 * n)

        for i, v in enumerate(arr):
            p = n + i
            self.val[p] = v
            self.idx[p] = i

        for p in range(n - 1, 0, -1):
            l = p << 1
            r = l | 1
            lv, rv = self.val[l], self.val[r]
            if lv > rv:
                self.val[p] = lv
                self.idx[p] = self.idx[l]
            elif rv > lv:
                self.val[p] = rv
                self.idx[p] = self.idx[r]
            else:
                li, ri = self.idx[l], self.idx[r]
                self.val[p] = lv
                self.idx[p] = li if li < ri else ri

    def pointUpdate(self, i, v):
        n = self.n
        val = self.val
        idx = self.idx

        p = n + i
        val[p] = v
        idx[p] = i
        p >>= 1
        while p:
            l = p << 1
            r = l | 1
            lv, rv = val[l], val[r]
            if lv > rv:
                val[p] = lv
                idx[p] = idx[l]
            elif rv > lv:
                val[p] = rv
                idx[p] = idx[r]
            else:
                li, ri = idx[l], idx[r]
                val[p] = lv
                idx[p] = li if li < ri else ri
            p >>= 1

    def rangeMax(self, l, r):
        n = self.n
        val = self.val
        idx = self.idx

        l += n
        r += n

        bestV = -10**30
        bestI = -1

        while l < r:
            if l & 1:
                v = val[l]
                if v > bestV:
                    bestV = v
                    bestI = idx[l]
                elif v == bestV and idx[l] < bestI:
                    bestI = idx[l]
                l += 1
            if r & 1:
                r -= 1
                v = val[r]
                if v > bestV:
                    bestV = v
                    bestI = idx[r]
                elif v == bestV and idx[r] < bestI:
                    bestI = idx[r]
            l >>= 1
            r >>= 1

        return (bestI, bestV)

T = nextInt()
for _ in range(T):
    n = nextInt()
    m = nextInt()
    k = nextInt()
    beauty = []
    for _ in range(m):
        beauty.append(nextInt())
    beauty.sort()
    friends = [] # holds (beautyPoint, coinsPoint)
    for j in range(n):
        a = nextInt()
        b = nextInt()
        c = nextInt()
        friends.append((a, c - b))
        k -= b
    friends.sort()


    friendB = [x[0] for x in friends]
    friendCoins = [x[1] for x in friends]
    st = SegTree(friendCoins)

    givenGift = [False] * n

    # for each gift in ascending order, give it to the biggest coins we can find for that gift
    res = 0
    for i, b in enumerate(beauty):
        # find the rightmost index in friends that is <= b
        # then we have a range 0...r for which we need to select the largest coin amount, and we choose to give our gift to them instead
        # then set their coin amount to -1 to make this person not chosen again
        rightmostI = rightmostLTE(friendB, b)

        # we cannot give this gift to anyone else, so we are done
        if rightmostI == -1:
            continue
        
        # now the range is 0...rightmostI for who we could give a gift to, find the largest coin in that range
        largestCoinI, largestCoinValue = st.rangeMax(0, rightmostI + 1)
        # everyone has a gift in that range
        if largestCoinValue == -1:
            continue
        st.pointUpdate(largestCoinI, -1)
        givenGift[largestCoinI] = True
        res += 1
    
    coins = [] # coins of friends who didn't get gifts
    for i in range(n):
        if givenGift[i] == False:
            coins.append(friendCoins[i])
    coins.sort()

    for i, v in enumerate(coins):
        if k >= v:
            k -= v
            res += 1
    
    print(res)