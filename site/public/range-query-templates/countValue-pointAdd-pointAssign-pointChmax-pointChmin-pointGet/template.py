# @operations: countValue pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: seg-tree
# @complexities:
#   countValue: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: tree[2*N]
#   tags: none
#   other: vals[1*N]
#   note: tree[n + i] is 1 when a[i] equals the value fixed at build, internal nodes sum their children
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/CountAndKthIndexSegmentTree.py

# Count occurrences of one value (fixed at build time) in a range, with point updates.
# All indices 0-based, ranges inclusive [l, r]. Iterative 2N tree of 0/1 counts.
class CountValueTree:
    __slots__ = ("n", "number", "vals", "tree")

    # O(N)
    def __init__(self, arr, number):
        n = self.n = len(arr)
        self.number = number
        self.vals = list(arr)
        tree = self.tree = [0] * n + [1 if v == number else 0 for v in arr]
        for i in range(n - 1, 0, -1):
            tree[i] = tree[2 * i] + tree[2 * i + 1]

    # O(logN) -- how many i in [l, r] have a[i] == number
    def countValue(self, l, r):
        tree = self.tree
        res = 0
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                res += tree[l]
                l += 1
            if r & 1:
                r -= 1
                res += tree[r]
            l >>= 1
            r >>= 1
        return res

    # O(logN) -- a[i] = val; only walks up when the 0/1 at the leaf actually flips
    def pointAssign(self, i, val):
        self.vals[i] = val
        tree = self.tree
        p = i + self.n
        bit = 1 if val == self.number else 0
        delta = bit - tree[p]
        if delta:
            while p:
                tree[p] += delta
                p >>= 1

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.vals[i]

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.vals[i]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.vals[i]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.vals[i] + delta)
