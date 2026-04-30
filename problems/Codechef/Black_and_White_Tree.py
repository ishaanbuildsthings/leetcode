class HLD:
    def __init__(self, n, edges, vals, base, combine, reverse):
        self.n = n
        self.base = base
        self.combine = combine
        self.reverse = reverse
        self.adj = [[] for _ in range(n)]
        for u, v in edges:
            self.adj[u].append(v)
            self.adj[v].append(u)
        self.par = [-1] * n
        self.depth = [0] * n
        self.sz = [1] * n
        self.heavy = [-1] * n
        self.head = [0] * n
        self.pos = [0] * n
        self._dfsInit()
        self._dfsDecompose()
        self.segN = 1
        while self.segN < n:
            self.segN <<= 1
        self.seg = [None] * (2 * self.segN)
        for i in range(n):
            self.seg[self.segN + self.pos[i]] = base(vals[i])
        for i in range(self.segN - 1, 0, -1):
            self.seg[i] = self._combineOpt(self.seg[2*i], self.seg[2*i+1])
    
    def _combineOpt(self, a, b):
        if a is None: return b
        if b is None: return a
        return self.combine(a, b)
    
    def _dfsInit(self):
        order = []
        stack = [(0, -1, 0)]
        while stack:
            node, parent, d = stack.pop()
            self.par[node] = parent
            self.depth[node] = d
            order.append(node)
            for nxt in self.adj[node]:
                if nxt != parent:
                    stack.append((nxt, node, d + 1))
        for node in reversed(order):
            best = 0
            for nxt in self.adj[node]:
                if nxt == self.par[node]: continue
                self.sz[node] += self.sz[nxt]
                if self.sz[nxt] > best:
                    best = self.sz[nxt]
                    self.heavy[node] = nxt
    
    def _dfsDecompose(self):
        timer = 0
        stack = [(0, 0)]
        while stack:
            node, h = stack.pop()
            self.head[node] = h
            self.pos[node] = timer
            timer += 1
            for nxt in self.adj[node]:
                if nxt == self.par[node] or nxt == self.heavy[node]:
                    continue
                stack.append((nxt, nxt))
            if self.heavy[node] != -1:
                stack.append((self.heavy[node], h))
    
    def _rangeQuery(self, ql, qr):
        resL = None
        resR = None
        ql += self.segN
        qr += self.segN + 1
        while ql < qr:
            if ql & 1:
                resL = self._combineOpt(resL, self.seg[ql])
                ql += 1
            if qr & 1:
                qr -= 1
                resR = self._combineOpt(self.seg[qr], resR)
            ql >>= 1
            qr >>= 1
        return self._combineOpt(resL, resR)
    
    def pathQuery(self, a, b):
        leftPieces = []
        rightPieces = []
        while self.head[a] != self.head[b]:
            if self.depth[self.head[a]] >= self.depth[self.head[b]]:
                chunk = self._rangeQuery(self.pos[self.head[a]], self.pos[a])
                leftPieces.append(self.reverse(chunk))
                a = self.par[self.head[a]]
            else:
                chunk = self._rangeQuery(self.pos[self.head[b]], self.pos[b])
                rightPieces.append(self.reverse(chunk))
                b = self.par[self.head[b]]
        if self.depth[a] >= self.depth[b]:
            chunk = self._rangeQuery(self.pos[b], self.pos[a])
            leftPieces.append(self.reverse(chunk))
        else:
            chunk = self._rangeQuery(self.pos[a], self.pos[b])
            rightPieces.append(self.reverse(chunk))
        leftAcc = None
        for p in leftPieces:
            leftAcc = p if leftAcc is None else self.combine(leftAcc, p)
        rightAcc = None
        for p in reversed(rightPieces):
            rev = self.reverse(p)
            rightAcc = rev if rightAcc is None else self.combine(rightAcc, rev)
        if leftAcc is None: return rightAcc
        if rightAcc is None: return leftAcc
        return self.combine(leftAcc, rightAcc)


def cTwo(w): return w * (w - 1) // 2
def cThree(w): return w * (w - 1) * (w - 2) // 6

# stores segment length
# # of B nodes
# the length of a white-only prefix
# length of a white-only suffix
# how many white-white chains there are, meaning two white nodes only connected via a white path, making a bad triplet with any value in the other node
# # of bad triplets in this segment, we will subtract from total triplets later
def base(v):
    if v == 1: return (1, 1, 0, 0, 0, 0)
    else: return (1, 0, 1, 1, 0, 0)

def agg(a, b):
    aLen, aB, aPref, aSuf, aWW, aBadT = a
    bLen, bB, bPref, bSuf, bWW, bBadT = b
    aAllW = (aB == 0)
    bAllW = (bB == 0)
    nLen = aLen + bLen
    nB = aB + bB
    nPref = aLen + bPref if aAllW else aPref
    nSuf = bLen + aSuf if bAllW else bSuf
    # new white-white chains is fully left, fully right, and cross counts
    nWW = aWW + bWW + aSuf * bPref

    middleWhite = aSuf + bPref
    
    # new bad triplets includes fully contained bad triplets
    newBadT = aBadT + bBadT
    # or the # of white-white pairs on the left with any node on the right
    newBadT += aWW * bLen
    # or vice versa
    newBadT += bWW * aLen
    
    # but ALSO we could pair a white from left, white from right, to form a new white-white chain, and add any other third node
    # but make sure that third node isn't part of a ww chain from either side using those suffixes/prefixes, or we double count
    newBadT += (aSuf * bPref) * (bLen - bPref)
    newBadT += (aSuf * bPref) * (aLen - aSuf)
    
    return (nLen, nB, nPref, nSuf, nWW, newBadT)

def reverseData(d):
    length, B, prefW, sufW, ww, badT = d
    return (length, B, sufW, prefW, ww, badT)


def solve():
    n = int(input())
    vals = list(map(int, input().split()))
    edges = []
    for _ in range(n - 1):
        a, b = list(map(int, input().split()))
        edges.append((a - 1, b - 1))
    hld = HLD(n, edges, vals, base, agg, reverseData)
    q = int(input())
    out = []
    for _ in range(q):
        a, b = list(map(int, input().split()))
        a -= 1; b -= 1
        result = hld.pathQuery(a, b)
        length = result[0]
        badT = result[5]
        ans = cThree(length) - badT
        out.append(str(ans))
    print('\n'.join(out))

t = int(input())
for _ in range(t):
    solve()