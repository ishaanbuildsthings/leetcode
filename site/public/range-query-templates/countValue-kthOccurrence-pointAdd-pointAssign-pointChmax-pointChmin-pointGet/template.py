# @operations: countValue kthOccurrence pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: BIT
# @complexities:
#   countValue: log(N)
#   kthOccurrence: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   build: N
# @memory:
#   layout: none
#   node: tree[1*N]
#   tags: none
#   other: vals[1*N]
#   note: a Fenwick tree over the 0/1 array [a[i] == number]; kthOccurrence binary-lifts over it
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/CountAndKthIndexSegmentTree.py

# Count / find the k-th occurrence of one value (fixed at build time) in a range, with point updates.
# All indices 0-based, ranges inclusive [l, r]. A Fenwick tree over ind[i] = (a[i] == number).
# kthOccurrence(l, r, k) = smallest i with ind[0] + ... + ind[i] >= (occurrences before l) + k, found by binary
# lifting down the tree in O(log N).


class CountValueBIT:
    __slots__ = ("n", "number", "vals", "tree", "top")

    # O(N)
    def __init__(self, arr, number):
        n = self.n = len(arr)
        self.number = number
        self.vals = list(arr)
        tree = self.tree = [0] * (n + 1)
        for i, v in enumerate(arr):
            if v == number:
                tree[i + 1] = 1
        for i in range(1, n + 1):
            j = i + (i & -i)
            if j <= n:
                tree[j] += tree[i]
        self.top = 1 << (n.bit_length() - 1) if n else 0

    # O(logN) -- # of i in [0, i] with a[i] == number (0 for i = -1)
    def _prefix(self, i):
        tree = self.tree
        s = 0
        i += 1
        while i > 0:
            s += tree[i]
            i &= i - 1
        return s

    # O(logN) -- how many i in [l, r] have a[i] == number
    def countValue(self, l, r):
        return self._prefix(r) - self._prefix(l - 1) if l <= r else 0

    # O(logN) -- index of the k-th (1-indexed) i in [l, r] with a[i] == number, or -1
    def kthOccurrence(self, l, r, k):
        if k <= 0 or l > r:
            return -1
        target = self._prefix(l - 1) + k
        tree, n = self.tree, self.n
        pos, acc, step = 0, 0, self.top
        while step:
            nxt = pos + step
            if nxt <= n and acc + tree[nxt] < target:
                pos = nxt
                acc += tree[nxt]
            step >>= 1
        return pos if pos <= r else -1  # pos is the 0-based index of the target-th occurrence (n if none)

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        d = (val == self.number) - (self.vals[i] == self.number)
        self.vals[i] = val
        if d:
            tree, n = self.tree, self.n
            i += 1
            while i <= n:
                tree[i] += d
                i += i & -i

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.vals[i]

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.vals[i] + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.vals[i]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.vals[i]:
            self.pointAssign(i, val)
