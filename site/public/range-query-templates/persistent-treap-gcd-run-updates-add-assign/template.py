# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-treap-gcd-run-updates-add-assign/template.py
# @operations: append appendLeft copy cut getAll insertAt insertCopiesAt longestEqualRun merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeGcd rangeRotateLeft rangeRotateRight size split trisect
# @data-structure-type: persistent-treap
# @complexities:
#   append: log(N)*log(U) expected ?
#   appendLeft: log(N)*log(U) expected ?
#   copy: log(N)*log(U) expected ?
#   cut: log(N)*log(U) expected ?
#   getAll: N
#   insertAt: log(N)*log(U) expected ?
#   insertCopiesAt: log(N)*log(U) expected ?
#   longestEqualRun: log(N)*log(U) expected ?
#   merge: log(N)*log(U) expected ?
#   paste: log(N)*log(U) expected ?
#   pointAdd: log(N)*log(U) expected ?
#   pointAssign: log(N)*log(U) expected ?
#   pointChmax: log(N)*log(U) expected ?
#   pointChmin: log(N)*log(U) expected ?
#   pointGet: log(N) expected
#   rangeAdd: log(N)*log(U) expected ?
#   rangeAssign: log(N)*log(U) expected ?
#   rangeGcd: log(N)*log(U) expected ?
#   rangeRotateLeft: log(N)*log(U) expected ?
#   rangeRotateRight: log(N)*log(U) expected ?
#   split: log(N)*log(U) expected ?
#   trisect: log(N)*log(U) expected ?
#   size: 1
#   build: N*log(U) ?
# @memory:
#   layout: none
#   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] g[1*N*log(N)] fv[1*N*log(N)] lv[1*N*log(N)] pr[1*N*log(N)] sr[1*N*log(N)] br[1*N*log(N)]
#   tags: asg[1*N*log(N)] hasAsg[1*N*log(N)] add[1*N*log(N)]
#   other: none
#   note: nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and copies share every node they don't change; log(N) is of the length, which can be huge (long long)

# Persistent implicit treap with composable aggregates: an array you can insert into anywhere, rotate, cut pieces out
# of (that is how to erase), paste them back and copy (copy(l, r): a[l..r] as a treap of its own in O(logN) however
# long, since the copy shares the same nodes; this one is unchanged), with rangeAdd, rangeAssign; each node keeps its
# gcd, its first / last value and the equal runs at its ends and inside over its subtree. No node changes once another
# tree can see it: an op copies the nodes on its paths, so a copy and its original never affect each other. Lengths
# and indices are long long. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT
# array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this node, not yet to its
# children"; a pending assign comes before a pending add.
import random
from math import gcd


class PersistentTreap:
    # one node pool shared by every PersistentTreap: cut / paste move nodes between them, so a piece from one can go
    # into any other (node 0 = the empty tree). Nodes are never freed (memory = O(log N) per op, over the whole run),
    # so there is nothing to reset between test cases
    val = [0]
    L = [0]
    R = [0]
    sz = [0]
    g = [0]
    fv = [0]
    lv = [0]
    pr = [0]
    sr = [0]
    br = [0]
    asg = [0]
    hasAsg = [0]
    add = [0]
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

    # O(logN * logU) expected -- the longest run of equal adjacent values in a[l..r]; needs 0 <= l <= r < size(), else
    # IndexError
    def longestEqualRun(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"longestEqualRun: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = self.br[b]
        self._release(mark)
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

    # O(logN * logU) expected -- a[i] += v (copies the one path down to a[i]); needs 0 <= i < size(), else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAdd: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        self.root = self._setAt(self.root, i, lambda w: w + v)

    # O(logN * logU) expected -- a[i] = v (copies the one path down to a[i]); needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        self.root = self._setAt(self.root, i, lambda w: v)

    # O(logN * logU) expected -- a[i] = max(a[i], v) (copies the one path down to a[i]); needs 0 <= i < size(), else
    # IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmax: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        self.root = self._setAt(self.root, i, lambda w: max(w, v))

    # O(logN * logU) expected -- a[i] = min(a[i], v) (copies the one path down to a[i]); needs 0 <= i < size(), else
    # IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmin: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        self.root = self._setAt(self.root, i, lambda w: min(w, v))

    # O(logN) expected -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        return self.val[self._find(i)[0]]

    # O(logN * logU) expected -- a[i] += v for i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def rangeAdd(self, l, r, v):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        self.root = self._upd(self.root, l, r, lambda x, off: self._applyAdd(x, v))

    # O(logN * logU) expected -- a[i] = v for i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        self.root = self._upd(self.root, l, r, lambda x, off: self._applyAssign(x, v))

    # O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < size(), else IndexError
    def rangeGcd(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeGcd: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        b, mark = self._rangeNode(l, r)
        res = gcd(self.fv[b], self.g[b])
        self._release(mark)
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
        self.g.append(0)
        self.fv.append(v)
        self.lv.append(v)
        self.pr.append(1)
        self.sr.append(1)
        self.br.append(1)
        self.asg.append(0)
        self.hasAsg.append(0)
        self.add.append(0)
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
        for arr in (self.val, self.L, self.R, self.sz, self.g, self.fv, self.lv, self.pr, self.sr, self.br, self.asg,
                    self.hasAsg, self.add):
            arr.append(arr[x])
        return y

    def _pull(self, x):  # recompute x from its children
        l, r = self.L[x], self.R[x]
        self.sz[x] = self.sz[l] + self.sz[r] + 1
        v = self.val[x]
        g = gcd(self.g[l], self.g[r])
        if l:
            g = gcd(g, v - self.lv[l])
        if r:
            g = gcd(g, self.fv[r] - v)
        self.g[x] = g
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

    def _applyAssign(self, x, v):  # every value of x's subtree becomes v
        if x:
            n = self.sz[x]
            self.val[x] = v
            self.g[x] = 0
            self.fv[x] = self.lv[x] = v
            self.pr[x] = self.sr[x] = self.br[x] = n
            self.asg[x], self.hasAsg[x] = v, 1
            self.add[x] = 0  # (an add pending below the assign is gone)

    def _applyAdd(self, x, v):  # every value of x's subtree gains v
        if x:
            self.val[x] += v
            self.fv[x] += v
            self.lv[x] += v
            self.add[x] += v

    def _push(self, x):  # hand x's pending tags to its children
        if not (self.hasAsg[x] or self.add[x]):
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
        if self.add[x]:
            self._applyAdd(self.L[x], self.add[x])
            self._applyAdd(self.R[x], self.add[x])
            self.add[x] = 0

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

    def _pieces(self, t, l, r, out):  # a[l..r] of t's subtree as (node, whole subtree?) in order; tags on the way pushed
        if not t or r < 0 or l >= self.sz[t]:
            return
        if l <= 0 and self.sz[t] - 1 <= r:
            out.append((t, True))
            return
        self._push(t)
        ls = self.sz[self.L[t]]
        self._pieces(self.L[t], l, r, out)
        if l <= ls <= r:
            out.append((t, False))
        self._pieces(self.R[t], l - ls - 1, r - ls - 1, out)

    def _rangeNode(self, l, r):  # (a temporary node holding a[l..r]'s aggregates, the pool size _release goes back to)
        self._pieces(self.root, l, r, [])  # (every pending tag on the two boundary paths pushed down first)
        mark = len(self.val)
        return self._rq(self.root, l, r), mark

    def _rq(self, t, l, r):  # a node over a[l..r] of t's subtree: t itself when it is all of it, else temporaries
        sz = self.sz
        if not t or r < 0 or l >= sz[t]:
            return 0
        if l <= 0 and sz[t] - 1 <= r:
            return t
        ls = sz[self.L[t]]
        if r < ls:
            return self._rq(self.L[t], l, r)
        if l > ls:
            return self._rq(self.R[t], l - ls - 1, r - ls - 1)
        a, b = self._rq(self.L[t], l, r), self._rq(self.R[t], l - ls - 1, r - ls - 1)
        y = self._clone(t)
        self.L[y], self.R[y] = a, b
        self._pull(y)
        return y

    def _release(self, mark):  # drop every node made after mark (temporaries: no tree points to them)
        for arr in (self.val, self.L, self.R, self.sz, self.g, self.fv, self.lv, self.pr, self.sr, self.br, self.asg,
                    self.hasAsg, self.add):
            del arr[mark:]

    def _setAt(self, t, i, f):  # t with a[i] = f(a[i]): new copies of the nodes on the path to it
        t = self._clone(t)
        self._push(t)
        L, R = self.L, self.R
        ls = self.sz[L[t]]
        if i < ls:
            L[t] = self._setAt(L[t], i, f)
        elif i > ls:
            R[t] = self._setAt(R[t], i - ls - 1, f)
        else:
            self.val[t] = f(self.val[t])
        self._pull(t)
        return t

    # t with the update f(x, off) on a[l..r] of its subtree (x: a node covered whole, off: its first value's distance
    # from l), copying only the nodes on the range's two boundary paths
    def _upd(self, t, l, r, f):
        sz = self.sz
        if not t or r < 0 or l >= sz[t]:
            return t
        t = self._clone(t)
        if l <= 0 and sz[t] - 1 <= r:
            f(t, -l)
            return t
        self._push(t)
        L, R = self.L, self.R
        ls = sz[L[t]]
        L[t] = self._upd(L[t], l, r, f)
        R[t] = self._upd(R[t], l - ls - 1, r - ls - 1, f)
        if l <= ls <= r:  # (t's own value: the update on a lone temporary copy of it)
            y = self._clone(t)
            L[y] = R[y] = 0
            self._pull(y)
            f(y, ls - l)
            self.val[t] = self.val[y]
            self._release(y)
        self._pull(t)
        return t


# Example (pieces move between treaps; merge appends and leaves its argument empty):
#     t = PersistentTreap([1, 2, 3, 4, 5])
#     left, mid, right = t.trisect(1, 3)  # left = [1], mid = [2, 3, 4], right = [5]; t is empty now
#     t.merge(right)                      # t = [5]
#     t.merge(mid)                        # t = [5, 2, 3, 4]
#     t.merge(left)                       # t = [5, 2, 3, 4, 1]
