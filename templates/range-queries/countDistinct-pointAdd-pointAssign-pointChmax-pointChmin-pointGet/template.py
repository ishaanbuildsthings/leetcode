# @operations: countDistinct pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: sqrt
# @complexities:
#   countDistinct: sqrt(N)*log(N)
#   pointAdd: sqrt(N)
#   pointAssign: sqrt(N)
#   pointChmax: sqrt(N)
#   pointChmin: sqrt(N)
#   pointGet: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: blocks[1*N]
#   tags: none
#   other: a[1*N] nxt[1*N] chains[1*N]
#   note: blocks are sqrt(N) sorted lists of next-occurrence indices (a query binary-searches each whole block); chains maps each value to its sorted positions (C++: std::set; Python: plain lists, so an assign is a memmove over that value's occurrences)
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/other-range-queries/rangeDistinctWithPointUpdateSqrtDecomp.py

from bisect import bisect_left, bisect_right, insort


class DynamicDistinct:
    # Point assign + range count distinct.
    # nxt[i] = next index j > i with a[j] == a[i], else n.
    # A value is counted once per window, at its LAST occurrence: nxt[i] > r.
    # blocks[b] is the sorted multiset of nxt values whose index lies in block b.
    # chains[v] is the sorted list of indices holding value v (pred/succ lookup).
    # O(n log n) build, O(sqrt n) update, O(sqrt n log n) query.
    def __init__(self, arr):
        self.n = n = len(arr)
        self.a = list(arr)
        self.nxt = [n] * n
        self.chains = {}
        last = {}
        for i in range(n - 1, -1, -1):
            v = arr[i]
            self.nxt[i] = last.get(v, n)
            last[v] = i
        for i in range(n):
            v = arr[i]
            if v in self.chains:
                self.chains[v].append(i)
            else:
                self.chains[v] = [i]
        self.blockSize = max(1, int(n ** 0.5))
        self.blocks = [sorted(self.nxt[b:b + self.blockSize])
                       for b in range(0, n, self.blockSize)]

    # O(sqrt n) — overwrite nxt[i] with v, repairing i's block
    def _setNxt(self, i, v):
        blk = self.blocks[i // self.blockSize]
        blk.pop(bisect_right(blk, self.nxt[i]) - 1)
        insort(blk, v)
        self.nxt[i] = v

    # O(sqrt n) — assign a[i] = val (overwrite, not add)
    # Touches at most 3 nxt entries: i's old predecessor, i's new predecessor, i.
    def pointAssign(self, i, val):
        old = self.a[i]
        if old == val:
            return
        S = self.chains[old]
        k = bisect_left(S, i)
        if k > 0:
            self._setNxt(S[k - 1], S[k + 1] if k + 1 < len(S) else self.n)
        S.pop(k)
        T = self.chains.setdefault(val, [])
        k = bisect_left(T, i)
        T.insert(k, i)
        succ = T[k + 1] if k + 1 < len(T) else self.n
        if k > 0:
            self._setNxt(T[k - 1], i)
        self._setNxt(i, succ)
        self.a[i] = val

    # O(sqrt n log n) — # of distinct values in a[l..r], inclusive
    def countDistinct(self, l, r):
        lb, rb = l // self.blockSize, r // self.blockSize
        nxt = self.nxt
        if lb == rb:
            return sum(1 for i in range(l, r + 1) if nxt[i] > r)
        total = sum(1 for i in range(l, (lb + 1) * self.blockSize) if nxt[i] > r)
        for b in range(lb + 1, rb):
            blk = self.blocks[b]
            total += len(blk) - bisect_right(blk, r)
        total += sum(1 for i in range(rb * self.blockSize, r + 1) if nxt[i] > r)
        return total

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.a[i]

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.a[i]:
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.a[i]:
            self.pointAssign(i, val)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.a[i] + delta)