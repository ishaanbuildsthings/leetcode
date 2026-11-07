# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeFloorDiv/template.py
# @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv
# @data-structure-type: seg-tree
# @complexities:
#   getAll: N
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeFloorDiv: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: tree[1*N]
#   tags: tree[1*N]
#   other: none
#   note: tree[n:] holds the values, tree[1:n] holds each node's pending divisor (product of divisions, capped); leaves count as node data, internal nodes as tags

# Range floor-divide + point ops. All indices 0-based, ranges inclusive [l, r].
# floor(floor(x / a) / b) == floor(x / (a * b)) for positive integers a, b and any integer x, so pending
# divisions are just a product. Products are capped at CAP: once a divisor exceeds every |value|, any larger
# divisor gives the same floor. Requires every divisor >= 1 and |a[i]| < CAP at all times.
CAP = 1 << 62


class RangeFloorDivTree:
    __slots__ = ("n", "tree")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.tree = [1] * n + list(arr)

    # O(logN) -- a[i] = a[i] // d for i in [l, r], d >= 1; needs 0 <= l <= r < n, else IndexError
    def rangeFloorDiv(self, l, r, d):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeFloorDiv: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if d == 1:
            return
        tree, n = self.tree, self.n
        l += n
        r += n + 1
        while l < r:
            if l & 1:
                if l >= n:
                    tree[l] //= d
                else:
                    t = tree[l] * d
                    tree[l] = t if t < CAP else CAP
                l += 1
            if r & 1:
                r -= 1
                if r >= n:
                    tree[r] //= d
                else:
                    t = tree[r] * d
                    tree[r] = t if t < CAP else CAP
            l >>= 1
            r >>= 1

    # O(logN) -- apply the divisors on i's path to the leaf, so nothing above i is pending
    def _push(self, p):
        tree, n = self.tree, self.n
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            t = tree[x]
            if t != 1:
                y = x << 1
                for c in (y, y | 1):
                    if c >= n:
                        tree[c] //= t
                    else:
                        u = tree[c] * t
                        tree[c] = u if u < CAP else CAP
                tree[x] = 1

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        tree = self.tree
        p = i + self.n
        v = tree[p]
        d = 1
        p >>= 1
        while p:
            d *= tree[p]
            if d >= CAP:
                d = CAP
            p >>= 1
        return v // d

    # O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    # each node's tag is complete when it is pushed), then read the leaves
    def getAll(self):
        tree, n = self.tree, self.n
        for x in range(1, self.n):
            t = tree[x]
            if t != 1:
                y = x << 1
                for c in (y, y | 1):
                    if c >= n:
                        tree[c] //= t
                    else:
                        u = tree[c] * t
                        tree[c] = u if u < CAP else CAP
                tree[x] = 1
        return self.tree[self.n:]

    # O(logN) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        self.tree[p] = val

    # O(logN) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        self.tree[p] += delta

    # O(logN) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        if val > self.tree[p]:
            self.tree[p] = val

    # O(logN) -- a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        if val < self.tree[p]:
            self.tree[p] = val
