# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-treap-hash-xor-and-or-gcd-run-alt-updates-assign/template.py
# @operations: append appendLeft copy cut getAll insertAt insertCopiesAt isPalindrome longestEqualRun maxAltSubseqSum merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeAssign rangeGcd rangeHash rangeHashReversed rangeOrQuery rangeRotateLeft rangeRotateRight rangeXorQuery rangesEqual split trisect
# @data-structure-type: persistent-treap
# @complexities:
#   append: log(N)*log(U) expected ?
#   appendLeft: log(N)*log(U) expected ?
#   copy: log(N)*log(U) expected ?
#   cut: log(N)*log(U) expected ?
#   getAll: N
#   insertAt: log(N)*log(U) expected ?
#   insertCopiesAt: log(N)*log(U) expected ?
#   isPalindrome: log(N)*log(U) expected ?
#   longestEqualRun: log(N)*log(U) expected ?
#   maxAltSubseqSum: log(N)*log(U) expected ?
#   merge: log(N)*log(U) expected ?
#   paste: log(N)*log(U) expected ?
#   pointAdd: log(N)*log(U) expected ?
#   pointAssign: log(N)*log(U) expected ?
#   pointChmax: log(N)*log(U) expected ?
#   pointChmin: log(N)*log(U) expected ?
#   pointGet: log(N) expected
#   rangeAndQuery: log(N)*log(U) expected ?
#   rangeAssign: log(N)*log(U) expected ?
#   rangeGcd: log(N)*log(U) expected ?
#   rangeHash: log(N)*log(U) expected ?
#   rangeHashReversed: log(N)*log(U) expected ?
#   rangeOrQuery: log(N)*log(U) expected ?
#   rangeRotateLeft: log(N)*log(U) expected ?
#   rangeRotateRight: log(N)*log(U) expected ?
#   rangeXorQuery: log(N)*log(U) expected ?
#   rangesEqual: log(N)*log(U) expected ?
#   split: log(N)*log(U) expected ?
#   trisect: log(N)*log(U) expected ?
#   build: N*log(U) ?
# @memory:
#   layout: none
#   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] fh[1*N*log(N)] bh[1*N*log(N)] pw[1*N*log(N)] gs[1*N*log(N)] xr[1*N*log(N)] an[1*N*log(N)] orr[1*N*log(N)] g[1*N*log(N)] fv[1*N*log(N)] lv[1*N*log(N)] pr[1*N*log(N)] sr[1*N*log(N)] br[1*N*log(N)] a00[1*N*log(N)] a01[1*N*log(N)] a10[1*N*log(N)] a11[1*N*log(N)]
#   tags: asg[1*N*log(N)] hasAsg[1*N*log(N)]
#   other: none
#   note: nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and copies share every node they don't change; log(N) is of the length, which can be huge (long long)

# Persistent implicit treap with composable aggregates: an array you can insert into anywhere, rotate, cut pieces out
# of (that is how to erase), paste them back and copy (copy(l, r): a[l..r] as a treap of its own in O(logN) however
# long, since the copy shares the same nodes; this one is unchanged), with rangeAssign; each node keeps its forward /
# backward hash (and B^size), its xor, its AND, its OR, its gcd, its first / last value and the equal runs at its ends
# and inside, its best alternating (+ - + ...) subsequence sum for each start / end sign over its subtree. No node
# changes once another tree can see it: an op copies the nodes on its paths, so a copy and its original never affect
# each other. Lengths and indices are long long. All indices 0-based, ranges inclusive [l, r], an index always the
# position in the CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this
# node, not yet to its children".
import random
from math import gcd


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


INF, NEG = float("inf"), float("-inf")


def _altJoin(A, B):  # A's part, then B's: (++, +-, -+, --) = best by (start sign, end sign)
    a0, a1, a2, a3 = A
    b0, b1, b2, b3 = B
    return (max(a0, b0, a0 + b2, a1 + b0), max(a1, b1, a0 + b3, a1 + b1),
            max(a2, b2, a2 + b2, a3 + b0), max(a3, b3, a2 + b3, a3 + b1))


class PersistentTreap:
    # one node pool shared by every PersistentTreap: cut / paste move nodes between them, so a piece from one can go
    # into any other (node 0 = the empty tree). Nodes are never freed (memory = O(log N) per op, over the whole run),
    # so there is nothing to reset between test cases
    val = [0]
    L = [0]
    R = [0]
    sz = [0]
    fh = [0]
    bh = [0]
    pw = [1]
    gs = [0]
    xr = [0]
    an = [-1]
    orr = [0]
    g = [0]
    fv = [0]
    lv = [0]
    pr = [0]
    sr = [0]
    br = [0]
    a00 = [0]
    a01 = [0]
    a10 = [0]
    a11 = [0]
    asg = [0]
    hasAsg = [0]
    __slots__ = ("root",)

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self.root = self._build(list(arr))

    def _empty(self):  # a new, empty PersistentTreap (on the same pool, like every one)
        return PersistentTreap()

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(logN * logU) expected -- append v to the end
    def append(self, v):
        self.root = self._merge(self.root, self._newNode(v))

    # O(logN * logU) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN * logU) expected -- a[l..r] (leave out l and r: the whole array, O(1)) as a PersistentTreap of its own;
    # this one is unchanged. The copy shares this one's nodes, so it costs O(logN) however long it is; needs 0 <= l <=
    # r < size(), else IndexError
    def copy(self, l=0, r=None):
        n = self.size()
        if r is None:
            r = n - 1
        whole = l == 0 and r == n - 1  # (an empty treap's whole copy too)
        if not whole and not 0 <= l <= r < n:
            raise IndexError(f"copy: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {n}")
        piece = self._empty()
        piece.root = self.root if whole else self._cut(l, r)[1]
        return piece

    # O(logN * logU) expected -- remove a[l..r] and return it as a treap of its own (indices from 0); needs
    # 0 <= l <= r < size(), else IndexError
    def cut(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"cut: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        self.root = self._merge(a, c)
        piece = self._empty()
        piece.root = b
        return piece

    # O(N) -- the whole current array, every pending tag applied on the way
    def getAll(self):
        L, R, val = self.L, self.R, self.val
        out, stack, t = [], [], self.root
        while stack or t:
            while t:
                self._push(t)
                stack.append(t)
                t = L[t]
            t = stack.pop()
            out.append(val[t])
            t = R[t]
        return out

    # O(logN * logU) expected -- insert v so it becomes a[i]; needs 0 <= i <= size(), else IndexError (i = size()
    # appends)
    def insertAt(self, i, v):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, self._newNode(v)), c)

    # O(k + logN * logU) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    # 0 <= i <= size(), else IndexError
    def insertCopiesAt(self, i, v, k):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertCopiesAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        if k > 0:
            a, c = self._split(self.root, i)
            self.root = self._merge(self._merge(a, self._build([v] * k)), c)

    # O(logN * logU) expected -- is a[l..r] a palindrome (its two hashes agree); needs 0 <= l <= r < size(), else
    # IndexError
    def isPalindrome(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"isPalindrome: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.fh[b] == self.bh[b]
        return res

    # O(logN * logU) expected -- the longest run of equal adjacent values in a[l..r]; needs 0 <= l <= r < size(), else
    # IndexError
    def longestEqualRun(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"longestEqualRun: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.br[b]
        return res

    # O(logN * logU) expected -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]; needs
    # 0 <= l <= r < size(), else IndexError
    def maxAltSubseqSum(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"maxAltSubseqSum: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = max(self.a00[b], self.a01[b])
        return res

    # O(logN * logU) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(logN * logU) expected -- insert all of other (any PersistentTreap, e.g. a cut piece) so it starts at a[i]
    # (needs 0 <= i <= size(), else IndexError); other is left empty
    def paste(self, i, other):
        if not 0 <= i <= self.size():
            raise IndexError(f"paste: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), c)
        other.root = 0

    # O(logN * logU) expected -- a[i] += v; needs 0 <= i < size(), else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAdd: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        a, b, c = self._cut(i, i)  # (b: a fresh copy of a[i]'s node, alone)
        self.val[b] = self.val[b] + v
        self._pull(b)
        self._join(a, b, c)

    # O(logN * logU) expected -- a[i] = v; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        a, b, c = self._cut(i, i)  # (b: a fresh copy of a[i]'s node, alone)
        self.val[b] = v
        self._pull(b)
        self._join(a, b, c)

    # O(logN * logU) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmax: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        a, b, c = self._cut(i, i)  # (b: a fresh copy of a[i]'s node, alone)
        self.val[b] = max(self.val[b], v)
        self._pull(b)
        self._join(a, b, c)

    # O(logN * logU) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmin: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        a, b, c = self._cut(i, i)  # (b: a fresh copy of a[i]'s node, alone)
        self.val[b] = min(self.val[b], v)
        self._pull(b)
        self._join(a, b, c)

    # O(logN) expected -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        return self.val[self._find(i)[0]]

    # O(logN * logU) expected -- a[l] & ... & a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeAndQuery(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAndQuery: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.an[b]
        return res

    # O(logN * logU) expected -- a[i] = v for i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        self._applyAssign(b, v)
        self._join(a, b, c)

    # O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < size(), else IndexError
    def rangeGcd(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeGcd: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.g[b]
        return res

    # O(logN * logU) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal;
    # needs 0 <= l <= r < size(), else IndexError
    def rangeHash(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeHash: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.fh[b]
        return res

    # O(logN * logU) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs
    # 0 <= l <= r < size(), else IndexError
    def rangeHashReversed(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeHashReversed: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.bh[b]
        return res

    # O(logN * logU) expected -- a[l] | ... | a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeOrQuery(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeOrQuery: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.orr[b]
        return res

    # O(logN * logU) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it
    # is taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateLeft(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateLeft: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = self._split(b, k)
            b = self._merge(b2, b1)
        self._join(a, b, c)

    # O(logN * logU) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    # length (negative shifts left); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateRight(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateRight: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        self.rangeRotateLeft(l, r, -k)

    # O(logN * logU) expected -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeXorQuery(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeXorQuery: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        a, b, c = self._cut(l, r)
        res = self.xr[b]
        return res

    # O(logN * logU) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    # 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), else IndexError
    def rangesEqual(self, l1, r1, l2, r2):
        if not (0 <= l1 <= r1 < self.size() and 0 <= l2 <= r2 < self.size()):
            raise IndexError(f"rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), got "
                             f"l1 = {l1}, r1 = {r1}, l2 = {l2}, r2 = {r2}, n = {self.size()}")
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # O(logN * logU) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty; needs
    # 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.size():
            raise IndexError(f"split: needs 0 <= k <= size(), got k = {k}, n = {self.size()}")
        left, right = self._empty(), self._empty()
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right

    # O(logN * logU) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty;
    # needs 0 <= l <= r < size(), else IndexError
    def trisect(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"trisect: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        left, mid, right = self._empty(), self._empty(), self._empty()
        left.root, mid.root, right.root = self._cut(l, r)
        self.root = 0
        return left, mid, right

    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
        self.fh.append((v + _HO) % _HP)
        self.bh.append((v + _HO) % _HP)
        self.pw.append(_HB)
        self.gs.append(1)
        self.xr.append(v)
        self.an.append(v)
        self.orr.append(v)
        self.g.append(abs(v))
        self.fv.append(v)
        self.lv.append(v)
        self.pr.append(1)
        self.sr.append(1)
        self.br.append(1)
        self.a00.append(v)
        self.a01.append(NEG)
        self.a10.append(NEG)
        self.a11.append(-v)
        self.asg.append(0)
        self.hasAsg.append(0)
        return x

    # a balanced tree of new nodes holding vals in order, O(len)
    def _build(self, vals, lo=0, hi=None):
        if hi is None:
            hi = len(vals)
        if lo >= hi:
            return 0
        mid = (lo + hi) // 2
        x = self._newNode(vals[mid])
        self.L[x] = self._build(vals, lo, mid)
        self.R[x] = self._build(vals, mid + 1, hi)
        self._pull(x)
        return x

    def _clone(self, x):  # a new copy of node x (sharing its children)
        y = len(self.val)
        for arr in (self.val, self.L, self.R, self.sz, self.fh, self.bh, self.pw, self.gs, self.xr, self.an,
                    self.orr, self.g, self.fv, self.lv, self.pr, self.sr, self.br, self.a00, self.a01, self.a10,
                    self.a11, self.asg, self.hasAsg):
            arr.append(arr[x])
        return y

    def _pull(self, x):  # recompute x from its children
        l, r = self.L[x], self.R[x]
        self.sz[x] = self.sz[l] + self.sz[r] + 1
        v = self.val[x]
        B, P, pw, fh, bh = _HB, _HP, self.pw, self.fh, self.bh
        hv = (v + _HO) % P
        pw[x] = pw[l] * B % P * pw[r] % P
        gs = self.gs
        gs[x] = ((gs[l] * B + 1) * pw[r] + gs[r]) % P
        fh[x] = ((fh[l] * B + hv) * pw[r] + fh[r]) % P
        bh[x] = ((bh[r] * B + hv) * pw[l] + bh[l]) % P
        self.xr[x] = self.xr[l] ^ v ^ self.xr[r]
        self.an[x] = self.an[l] & v & self.an[r]  # (node 0: the AND of nothing, -1)
        self.orr[x] = self.orr[l] | v | self.orr[r]
        self.g[x] = gcd(gcd(self.g[l], v), self.g[r])
        pr = sr = br = 1
        if l:
            j = self.lv[l] == v
            pr = self.pr[l] + (1 if j and self.pr[l] == self.sz[l] else 0)
            sr = self.sr[l] + 1 if j else 1
            br = max(self.br[l], sr)
        if r:
            j = v == self.fv[r]
            rp, rs = self.pr[r], self.sr[r]
            br = max(br, self.br[r], sr + rp if j else 0)
            if j and pr == self.sz[l] + 1:
                pr += rp
            sr = rs + sr if j and rs == self.sz[r] else rs
        self.pr[x], self.sr[x], self.br[x] = pr, sr, br
        self.fv[x] = self.fv[l] if l else v
        self.lv[x] = self.lv[r] if r else v
        c = (v, NEG, NEG, -v)
        if l:
            c = _altJoin((self.a00[l], self.a01[l], self.a10[l], self.a11[l]), c)
        if r:
            c = _altJoin(c, (self.a00[r], self.a01[r], self.a10[r], self.a11[r]))
        self.a00[x], self.a01[x], self.a10[x], self.a11[x] = c

    def _applyAssign(self, x, v):  # every value of x's subtree becomes v
        if x:
            n = self.sz[x]
            self.val[x] = v
            self.an[x] = v
            self.orr[x] = v
            self.fh[x] = self.bh[x] = (v + _HO) % _HP * self.gs[x] % _HP
            self.xr[x] = v if n & 1 else 0
            self.g[x] = abs(v)
            self.fv[x] = self.lv[x] = v
            self.pr[x] = self.sr[x] = self.br[x] = n
            self.a00[x], self.a11[x] = v, -v
            self.a01[x] = self.a10[x] = 0 if n > 1 else NEG
            self.asg[x], self.hasAsg[x] = v, 1

    def _push(self, x):  # hand x's pending tags to its children
        if not (self.hasAsg[x]):
            return
        L, R = self.L, self.R  # (the children get tags: fresh copies of them, since other trees may share them)
        if L[x]:
            L[x] = self._clone(L[x])
        if R[x]:
            R[x] = self._clone(R[x])
        if self.hasAsg[x]:
            self._applyAssign(self.L[x], self.asg[x])
            self._applyAssign(self.R[x], self.asg[x])
            self.hasAsg[x] = 0

    def _split(self, t, k):  # (first k of t, the rest), as new nodes (t's are left as they were)
        if not t:
            return 0, 0
        t = self._clone(t)
        self._push(t)
        L, R = self.L, self.R
        if self.sz[L[t]] >= k:
            a, L[t] = self._split(L[t], k)
            self._pull(t)
            return a, t
        R[t], b = self._split(R[t], k - self.sz[L[t]] - 1)
        self._pull(t)
        return t, b

    def _merge(self, a, b):  # a's elements, then b's, as new nodes; the root is a with probability |a| / (|a| + |b|)
        if not a or not b:
            return a or b
        if random.randrange(self.sz[a] + self.sz[b]) < self.sz[a]:
            a = self._clone(a)
            self._push(a)
            self.R[a] = self._merge(self.R[a], b)
            self._pull(a)
            return a
        b = self._clone(b)
        self._push(b)
        self.L[b] = self._merge(a, self.L[b])
        self._pull(b)
        return b

    def _cut(self, l, r):  # (a[0..l-1], a[l..r], a[r+1..])
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    def _join(self, a, b, c):
        self.root = self._merge(self._merge(a, b), c)

    def _find(self, i):  # (node holding a[i], the nodes above it), every tag on the way pushed
        L, sz, t, path = self.L, self.sz, self.root, []
        while True:
            self._push(t)
            ls = sz[L[t]]
            if i == ls:
                return t, path
            path.append(t)
            if i < ls:
                t = L[t]
            else:
                i -= ls + 1
                t = self.R[t]


# Example (pieces move between treaps; merge appends and leaves its argument empty):
#     t = PersistentTreap([1, 2, 3, 4, 5])
#     left, mid, right = t.trisect(1, 3)  # left = [1], mid = [2, 3, 4], right = [5]; t is empty now
#     t.merge(right)                      # t = [5]
#     t.merge(mid)                        # t = [5, 2, 3, 4]
#     t.merge(left)                       # t = [5, 2, 3, 4, 1]
