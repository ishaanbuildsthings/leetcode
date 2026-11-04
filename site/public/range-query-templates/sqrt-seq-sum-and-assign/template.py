# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sqrt-seq-sum-and-assign/template.py
# @operations: andGtX andGteX andInValRange andLtX andLteX append appendLeft countGtX countGteX countInValRange countLtX countLteX countOccurrences cut getAll insertAt insertCopiesAt kthGtX kthGteX kthLtX kthLteX kthSmallest largestLtX largestLteX leftmostIndexOf leftmostIndexOfInRange merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeAssign rangeMax rangeMin rangeRotateLeft rangeRotateRight rangeSum rightmostIndexOf rightmostIndexOfInRange size smallestGtX smallestGteX split sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK trisect
# @data-structure-type: sqrt
# @complexities:
#   andGtX: sqrt(N)*log(N)
#   andGteX: sqrt(N)*log(N)
#   andInValRange: sqrt(N)*log(N)
#   andLtX: sqrt(N)*log(N)
#   andLteX: sqrt(N)*log(N)
#   append: sqrt(N)*log(N) amortized
#   appendLeft: sqrt(N)*log(N) amortized
#   countGtX: sqrt(N)*log(N)
#   countGteX: sqrt(N)*log(N)
#   countInValRange: sqrt(N)*log(N)
#   countLtX: sqrt(N)*log(N)
#   countLteX: sqrt(N)*log(N)
#   countOccurrences: sqrt(N)*log(N)
#   cut: sqrt(N)*log(N) amortized
#   getAll: N
#   insertAt: sqrt(N)*log(N) amortized
#   insertCopiesAt: sqrt(N)*log(N) amortized
#   kthGtX: sqrt(N)*log(N)
#   kthGteX: sqrt(N)*log(N)
#   kthLtX: sqrt(N)*log(N)
#   kthLteX: sqrt(N)*log(N)
#   kthSmallest: sqrt(N)*log(N)*log(U)
#   largestLtX: sqrt(N)*log(N)
#   largestLteX: sqrt(N)*log(N)
#   leftmostIndexOf: sqrt(N)*log(N)
#   leftmostIndexOfInRange: sqrt(N)*log(N)
#   merge: sqrt(N)*log(N) amortized
#   paste: sqrt(N)*log(N) amortized
#   pointAdd: sqrt(N)*log(N)
#   pointAssign: sqrt(N)*log(N)
#   pointChmax: sqrt(N)*log(N)
#   pointChmin: sqrt(N)*log(N)
#   pointGet: sqrt(N)
#   rangeAndQuery: sqrt(N)*log(N)
#   rangeAssign: sqrt(N)*log(N)
#   rangeMax: sqrt(N)*log(N)
#   rangeMin: sqrt(N)*log(N)
#   rangeRotateLeft: sqrt(N)*log(N) amortized
#   rangeRotateRight: sqrt(N)*log(N) amortized
#   rangeSum: sqrt(N)*log(N)
#   rightmostIndexOf: sqrt(N)*log(N)
#   rightmostIndexOfInRange: sqrt(N)*log(N)
#   smallestGtX: sqrt(N)*log(N)
#   smallestGteX: sqrt(N)*log(N)
#   split: sqrt(N)*log(N) amortized
#   sumAbsDiffToX: sqrt(N)*log(N)
#   sumGtX: sqrt(N)*log(N)
#   sumGteX: sqrt(N)*log(N)
#   sumInValRange: sqrt(N)*log(N)
#   sumKthLargestRange: sqrt(N)*log(N)*log(U)
#   sumKthSmallestRange: sqrt(N)*log(N)*log(U)
#   sumLargestK: sqrt(N)*log(N)*log(U)
#   sumLtX: sqrt(N)*log(N)
#   sumLteX: sqrt(N)*log(N)
#   sumSmallestK: sqrt(N)*log(N)*log(U)
#   trisect: sqrt(N)*log(N) amortized
#   size: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: vals[1*N] srt[1*N] ps[1*N] ta[2*N]
#   tags: has[1*sqrt(N)] asg[1*sqrt(N)]
#   other: none
#   note: blocks of about sqrt(N log N) values, each kept in array order and sorted (N here is the current length)

# List of sorted blocks: an array you can insert into anywhere, rotate, cut pieces out of (that is how to erase) and
# paste them back, and ask value questions about any range a[l..r]: how many values are below x, the k-th smallest,
# the nearest value above / below x, where x first / last appears, and the sums, ANDs of the values in a value range;
# with rangeAssign. Each op costs about sqrt(N log N): the array is a list of blocks, each kept both in array order
# and sorted. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array.
from bisect import bisect_left, bisect_right
from itertools import accumulate
from math import isqrt


class _Block:
    # a run of the array: vals in array order and srt, the same values sorted, both raw (the tags apply on read)
    __slots__ = ("vals", "srt", "ps", "ta", "has", "asg")

    def __init__(self, vals):
        self.vals = vals
        self.has = False  # (every value = asg, then + add)
        self.asg = 0
        self.rebuild()

    def rebuild(self):  # O(B log B) -- srt and what is kept over it, from vals (no tag pending)
        srt = self.srt = sorted(self.vals)
        self.ps = [0, *accumulate(srt)]  # ps[k] = sum of the k smallest
        m = len(srt)  # ta / to: AND / OR trees over srt (leaves at m..2m-1)
        ta = self.ta = [-1] * m + srt
        for i in range(m - 1, 0, -1):
            ta[i] = ta[2 * i] & ta[2 * i + 1]

    def bake(self):  # O(B log B) -- hand the pending tags to vals and rebuild
        if self.has:  # (one value: the order and the add don't matter)
            self.vals = [self.asg] * len(self.vals)
        self.has = False
        self.rebuild()

    def get(self, k):  # the value at position k of this block
        if self.has:
            return self.asg
        return self.vals[k]

    def values(self, lo, hi):  # the values at positions lo..hi, in order
        if self.has:
            return [self.asg] * (hi - lo + 1)
        seg = self.vals[lo:hi + 1]
        return seg

    def below(self, x, strict):  # how many values are < x (strict) or <= x
        if self.has:
            v = self.asg
            return len(self.vals) if (v < x if strict else v <= x) else 0
        return (bisect_left if strict else bisect_right)(self.srt, x)

    def kth(self, k):  # the k-th smallest value, k from 0
        if self.has:
            return self.asg
        return self.srt[k]

    def sumFirst(self, k):  # the sum of the k smallest values
        if self.has:
            return k * (self.asg)
        return self.ps[k]

    def andRange(self, i, j):  # the AND of the i-th..(j-1)-th smallest (-1, every bit, if none)
        if self.has:
            return self.asg if i < j else -1
        ta, m, res = self.ta, len(self.srt), -1
        i += m
        j += m
        while i < j:
            if i & 1:
                res &= ta[i]
                i += 1
            if j & 1:
                j -= 1
                res &= ta[j]
            i >>= 1
            j >>= 1
        return res


class SqrtSequence:
    # pieces (cut / split / trisect) are SqrtSequences of their own: paste / merge move their blocks over
    __slots__ = ("blocks", "n", "B")

    # O(N log N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self._fill(list(arr))

    # O(1) -- the current length of the array
    def size(self):
        return self.n

    # O(N) -- the whole current array
    def getAll(self):
        out = []
        for b in self.blocks:
            out += b.values(0, len(b.vals) - 1)
        return out

    # O(sqrt(N)) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        b, k = self._locate(i)
        return b.get(k)

    # O(sqrt(N) log N) -- a[i] = v; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        b, k = self._locate(i)
        nv = v
        b.bake()
        b.vals[k] = nv
        b.rebuild()

    # O(sqrt(N) log N) -- a[i] += v; needs 0 <= i < size(), else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAdd: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        b, k = self._locate(i)
        nv = b.get(k) + v
        b.bake()
        b.vals[k] = nv
        b.rebuild()

    # O(sqrt(N) log N) -- a[i] = max(a[i], v); needs 0 <= i < size(), else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmax: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        b, k = self._locate(i)
        nv = max(b.get(k), v)
        b.bake()
        b.vals[k] = nv
        b.rebuild()

    # O(sqrt(N) log N) -- a[i] = min(a[i], v); needs 0 <= i < size(), else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmin: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        b, k = self._locate(i)
        nv = min(b.get(k), v)
        b.bake()
        b.vals[k] = nv
        b.rebuild()


    # O(sqrt(N) log N) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        for b, lo, hi, full, _ in self._span(l, r):
            if full:
                b.has, b.asg = True, v
            else:
                b.bake()
                vals = b.vals
                for k in range(lo, hi + 1):
                    vals[k] = v
                b.rebuild()

    # O(sqrt(N) log N) amortized -- insert v so it becomes a[i]; needs 0 <= i <= size(), else IndexError (i = size()
    # appends)
    def insertAt(self, i, v):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        j, k = self._at(i)
        if j == len(self.blocks):  # (the end: onto the last block)
            if not j or len(self.blocks[-1].vals) >= 2 * self.B:
                self.blocks.append(_Block([v]))
                self.n += 1
                return
            j, k = j - 1, len(self.blocks[-1].vals)
        b = self.blocks[j]
        b.bake()
        b.vals.insert(k, v)
        if len(b.vals) > 2 * self.B:  # (too long: two blocks)
            h = len(b.vals) // 2
            self.blocks[j:j + 1] = [_Block(b.vals[:h]), _Block(b.vals[h:])]
        else:
            b.rebuild()
        self.n += 1
        if self._idealB(self.n) > 2 * self.B:  # (grown a lot: bigger blocks)
            self._fill(self.getAll())

    # O(sqrt(N) log N) amortized -- append v to the end
    def append(self, v):
        self.insertAt(self.n, v)

    # O(sqrt(N) log N) amortized -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(k + sqrt(N) log N) amortized -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    # 0 <= i <= size(), else IndexError
    def insertCopiesAt(self, i, v, k):
        if not 0 <= i <= self.size():
            raise IndexError(f"insertCopiesAt: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        if k <= 0:
            return
        j = self._splitAt(i)
        self.blocks[j:j] = [_Block([v] * min(self.B, k - s)) for s in range(0, k, self.B)]
        self.n += k
        self._tidy()

    # O(sqrt(N) log N) amortized -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    # it is taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateLeft(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateLeft: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        k %= r - l + 1
        if k:
            j1 = self._splitAt(l)
            j2 = self._splitAt(l + k)
            j3 = self._splitAt(r + 1)
            self.blocks[j1:j3] = self.blocks[j2:j3] + self.blocks[j1:j2]
            self._tidy()

    # O(sqrt(N) log N) amortized -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    # length (negative shifts left); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateRight(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeRotateRight: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        self.rangeRotateLeft(l, r, -k)

    # O(sqrt(N) log N) amortized -- remove a[l..r] and return it as a SqrtSequence of its own (indices from 0); needs
    # 0 <= l <= r < size(), else IndexError
    def cut(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"cut: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        j1 = self._splitAt(l)
        j2 = self._splitAt(r + 1)
        piece = SqrtSequence()
        piece.blocks, piece.n, piece.B = self.blocks[j1:j2], r - l + 1, self.B
        del self.blocks[j1:j2]
        self.n -= r - l + 1
        self._tidy()
        piece._tidy()
        return piece

    # O(sqrt(N) log N) amortized -- insert all of other (any SqrtSequence, e.g. a cut piece) so it starts at a[i]
    # (needs 0 <= i <= size(), else IndexError); other is left empty
    def paste(self, i, other):
        if not 0 <= i <= self.size():
            raise IndexError(f"paste: needs 0 <= i <= size(), got i = {i}, n = {self.size()}")
        j = self._splitAt(i)
        self.blocks[j:j] = other.blocks
        self.n += other.n
        other.blocks, other.n = [], 0
        self._tidy()

    # O(sqrt(N) log N) amortized -- append all of other at the end; other is left empty
    def merge(self, other):
        self.paste(self.n, other)

    # O(sqrt(N) log N) amortized -- (a[0..k-1], a[k..]) as two SqrtSequences of their own; this one is left empty;
    # needs 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.size():
            raise IndexError(f"split: needs 0 <= k <= size(), got k = {k}, n = {self.size()}")
        left = SqrtSequence()
        left.blocks, left.n, left.B = self.blocks, self.n, self.B
        self.blocks, self.n = [], 0
        right = left.cut(k, left.n - 1) if k < left.n else SqrtSequence()
        return left, right

    # O(sqrt(N) log N) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three SqrtSequences of their own; this one is
    # left empty; needs 0 <= l <= r < size(), else IndexError
    def trisect(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"trisect: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        left, right = self.split(r + 1)
        left, mid = left.split(l)
        return left, mid, right

    # O(sqrt(N) log N) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._count(l, r, None, x, False, True)

    # O(sqrt(N) log N) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._count(l, r, None, x, False, False)

    # O(sqrt(N) log N) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._count(l, r, x, None, True, False)

    # O(sqrt(N) log N) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._count(l, r, x, None, False, False)

    # O(sqrt(N) log N) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < size(), else IndexError
    def countInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countInValRange: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._count(l, r, lowVal, highVal, False, False) if lowVal <= highVal else 0

    # O(sqrt(N) log N) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._count(l, r, x, x, False, False)

    # O(sqrt(N) log N log U) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and 1 <= k
    # <= r - l + 1, else IndexError (a binary search over the values, each step a count)
    def kthSmallest(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"kthSmallest: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        whole, part = [], []  # (the values of the partial blocks, sorted once)
        for b, a, c, full, _ in self._span(l, r):
            if full:
                whole.append(b)
            else:
                part += b.values(a, c)
        part.sort()
        lo = min([b.kth(0) for b in whole] + part[:1])
        hi = max([b.kth(len(b.vals) - 1) for b in whole] + part[-1:])
        while lo < hi:
            mid = (lo + hi) // 2
            if bisect_right(part, mid) + sum(b.below(mid, False) for b in whole) >= k:
                hi = mid
            else:
                lo = mid + 1
        return lo

    # O(sqrt(N) log N) -- min of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMin: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return min(b.kth(0) if full else min(b.values(lo, hi)) for b, lo, hi, full, _ in self._span(l, r))

    # O(sqrt(N) log N) -- max of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeMax: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return max(b.kth(hi) if full else max(b.values(lo, hi)) for b, lo, hi, full, _ in self._span(l, r))

    # O(sqrt(N) log N) -- smallest value >= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"smallestGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._nearest(l, r, x, True, False)

    # O(sqrt(N) log N) -- smallest value > x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"smallestGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._nearest(l, r, x, True, True)

    # O(sqrt(N) log N) -- largest value <= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"largestLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._nearest(l, r, x, False, False)

    # O(sqrt(N) log N) -- largest value < x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"largestLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._nearest(l, r, x, False, True)

    # O(sqrt(N) log N) -- the first i with a[i] == x, or -1
    def leftmostIndexOf(self, x):
        return self.leftmostIndexOfInRange(0, self.n - 1, x) if self.n else -1

    # O(sqrt(N) log N) -- the last i with a[i] == x, or -1
    def rightmostIndexOf(self, x):
        return self.rightmostIndexOfInRange(0, self.n - 1, x) if self.n else -1

    # O(sqrt(N) log N) -- the first i in [l, r] with a[i] == x, or -1; needs 0 <= l <= r < size(), else IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._kthWhere(l, r, 1, x, x, False, False)

    # O(sqrt(N) log N) -- the last i in [l, r] with a[i] == x, or -1; needs 0 <= l <= r < size(), else IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._kthWhere(l, r, -1, x, x, False, False)

    # O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] < x, or -1; needs
    # 0 <= l <= r < size(), else IndexError
    def kthLtX(self, l, r, k, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"kthLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._kthWhere(l, r, k, None, x, False, True) if k >= 1 else -1

    # O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] <= x, or -1; needs
    # 0 <= l <= r < size(), else IndexError
    def kthLteX(self, l, r, k, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"kthLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._kthWhere(l, r, k, None, x, False, False) if k >= 1 else -1

    # O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] > x, or -1; needs
    # 0 <= l <= r < size(), else IndexError
    def kthGtX(self, l, r, k, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"kthGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._kthWhere(l, r, k, x, None, True, False) if k >= 1 else -1

    # O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] >= x, or -1; needs
    # 0 <= l <= r < size(), else IndexError
    def kthGteX(self, l, r, k, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"kthGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._kthWhere(l, r, k, x, None, False, False) if k >= 1 else -1

    # O(sqrt(N) log N) -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeSum: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._sum(l, r, None, None, False, False)

    # O(sqrt(N) log N) -- sum of the values < x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def sumLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"sumLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._sum(l, r, None, x, False, True)

    # O(sqrt(N) log N) -- sum of the values <= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def sumLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"sumLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._sum(l, r, None, x, False, False)

    # O(sqrt(N) log N) -- sum of the values > x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def sumGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"sumGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._sum(l, r, x, None, True, False)

    # O(sqrt(N) log N) -- sum of the values >= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def sumGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"sumGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._sum(l, r, x, None, False, False)

    # O(sqrt(N) log N) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < size(), else
    # IndexError
    def sumInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"sumInValRange: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._sum(l, r, lowVal, highVal, False, False) if lowVal <= highVal else 0

    # O(sqrt(N) log N log U) -- sum of the k smallest values in a[l..r]; needs 0 <= l <= r < size() and 0 <= k <= r -
    # l + 1, else IndexError
    def sumSmallestK(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"sumSmallestK: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        if not 0 <= k <= r - l + 1:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, k)

    # O(sqrt(N) log N log U) -- sum of the k largest values in a[l..r]; needs 0 <= k <= r - l + 1, else IndexError;
    # needs 0 <= l <= r < size(), else IndexError
    def sumLargestK(self, l, r, k):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"sumLargestK: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        n = r - l + 1
        if not 0 <= k <= n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {n}")
        return self.rangeSum(l, r) - self._sumFirst(l, r, n - k)

    # O(sqrt(N) log N log U) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs
    # 0 <= l <= r < size() and 1 <= kFrom <= kTo <= r - l + 1, else IndexError
    def sumKthSmallestRange(self, l, r, kFrom, kTo):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"sumKthSmallestRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        if not 1 <= kFrom <= kTo <= r - l + 1:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got "
                             f"kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, kTo) - self._sumFirst(l, r, kFrom - 1)

    # O(sqrt(N) log N log U) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) =
    # the 3 biggest); needs 1 <= kFrom <= kTo <= r - l + 1, else IndexError; needs 0 <= l <= r < size(), else
    # IndexError
    def sumKthLargestRange(self, l, r, kFrom, kTo):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"sumKthLargestRange: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        n = r - l + 1
        if not 1 <= kFrom <= kTo <= n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got "
                             f"kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n - kFrom + 1) - self._sumFirst(l, r, n - kTo)

    # O(sqrt(N) log N) -- sum of |a[i] - x| over i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def sumAbsDiffToX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"sumAbsDiffToX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        c, s = self._count(l, r, None, x, False, True), self._sum(l, r, None, x, False, True)
        return c * x - s + self.rangeSum(l, r) - s - (r - l + 1 - c) * x

    def _sum(self, l, r, lo, hi, loStrict, hiStrict):
        return sum(b.sumFirst(j) - b.sumFirst(i) if b else sum(i) for b, i, j in self._sel(l, r, lo, hi, loStrict, hiStrict))

    def _sumFirst(self, l, r, k):  # the sum of the k smallest values of a[l..r]
        if k == 0:
            return 0
        v = self.kthSmallest(l, r, k)  # (the k-th smallest: the values below it, then copies of it)
        return self._sum(l, r, None, v, False, True) + (k - self._count(l, r, None, v, False, True)) * v

    # O(sqrt(N) log N) -- a[l] & ... & a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeAndQuery(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAndQuery: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._and(l, r, None, None, False, False)

    # O(sqrt(N) log N) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none; needs
    # 0 <= l <= r < size(), else IndexError
    def andLtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"andLtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._and(l, r, None, x, False, True)

    # O(sqrt(N) log N) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none; needs
    # 0 <= l <= r < size(), else IndexError
    def andLteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"andLteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._and(l, r, None, x, False, False)

    # O(sqrt(N) log N) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none; needs
    # 0 <= l <= r < size(), else IndexError
    def andGtX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"andGtX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._and(l, r, x, None, True, False)

    # O(sqrt(N) log N) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none; needs
    # 0 <= l <= r < size(), else IndexError
    def andGteX(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"andGteX: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._and(l, r, x, None, False, False)

    # O(sqrt(N) log N) -- AND of the a[i] in [l, r] with lowVal <= a[i] <= highVal; -1 (every bit) if there are none;
    # needs 0 <= l <= r < size(), else IndexError
    def andInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"andInValRange: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._and(l, r, lowVal, highVal, False, False) if lowVal <= highVal else -1

    def _and(self, l, r, lo, hi, loStrict, hiStrict):
        res = -1
        for b, i, j in self._sel(l, r, lo, hi, loStrict, hiStrict):
            if b:
                res &= b.andRange(i, j)
            else:
                for v in i:
                    res &= v
        return res

    # ---- internals ----

    @staticmethod
    def _idealB(n):  # sqrt(n log n): a query reads n / B blocks (a binary search each) and two partial ones
        return max(16, isqrt(n * max(1, n.bit_length())))

    def _fill(self, vals):  # blocks of about _idealB values holding vals
        n = self.n = len(vals)
        B = self.B = self._idealB(n)
        self.blocks = [_Block(vals[s:s + B]) for s in range(0, n, B)]

    # O(N / B + B log B) amortized -- merge each run of neighbours that fit in one block (each merge is paid for by
    # the split that made it), so any two neighbours hold more than B values; when the array has grown so much that B
    # is too small, rebuild into even blocks (O(N log N), after about N new values)
    def _tidy(self):
        if self._idealB(self.n) > 2 * self.B:
            return self._fill(self.getAll())
        out, B = [], self.B
        for b in self.blocks:
            if not b.vals:
                continue
            if out and len(out[-1].vals) + len(b.vals) <= B:
                p = out.pop()
                p.bake()
                b.bake()
                b = _Block(p.vals + b.vals)
            out.append(b)
        self.blocks = out

    def _at(self, i):  # (block index, position in it) of a[i]; i == size() gives (number of blocks, 0)
        for j, b in enumerate(self.blocks):
            m = len(b.vals)
            if i < m:
                return j, i
            i -= m
        return len(self.blocks), 0

    def _locate(self, i):  # (block, position in it) of a[i]
        j, k = self._at(i)
        return self.blocks[j], k

    def _splitAt(self, i):  # make a block start at a[i] (0 <= i <= size()): that block's index
        j, k = self._at(i)
        if k:
            b = self.blocks[j]
            b.bake()
            self.blocks[j:j + 1] = [_Block(b.vals[:k]), _Block(b.vals[k:])]
            return j + 1
        return j

    def _span(self, l, r):  # (block, lo, hi, whole, start) for each block meeting a[l..r]: positions lo..hi of it,
        i = 0  # whether that is all of it, and the index of its first value
        for b in self.blocks:
            m = len(b.vals)
            if i + m > l:
                lo, hi = max(l - i, 0), min(r - i, m - 1)
                yield b, lo, hi, lo == 0 and hi == m - 1, i
                if i + m > r:
                    return
            i += m

    # the values v of a[l..r] with lo <(=) v <(=) hi (a None bound: none), as (block, i, j) for a whole block (its
    # i-th..(j-1)-th smallest pass) and (None, values, 0) for a partial one
    def _sel(self, l, r, lo, hi, loStrict, hiStrict):
        for b, a, c, full, _ in self._span(l, r):
            if full:
                yield (b, 0 if lo is None else b.below(lo, not loStrict),
                       len(b.vals) if hi is None else b.below(hi, hiStrict))
            else:
                yield None, [v for v in b.values(a, c) if (lo is None or (lo < v if loStrict else lo <= v)) and
                             (hi is None or (v < hi if hiStrict else v <= hi))], 0

    def _count(self, l, r, lo, hi, loStrict, hiStrict):
        return sum(j - i if b else len(i) for b, i, j in self._sel(l, r, lo, hi, loStrict, hiStrict))

    def _nearest(self, l, r, x, up, strict):  # the smallest value > (>=) x (up) or the largest < (<=) x, or None
        best = None
        for b, lo, hi, full, _ in self._span(l, r):
            if full:
                k = b.below(x, not strict) if up else b.below(x, strict) - 1
                if 0 <= k < len(b.vals):
                    v = b.kth(k)
                    best = v if best is None or (v < best if up else v > best) else best
            else:
                for v in b.values(lo, hi):
                    if (v > x if strict else v >= x) if up else (v < x if strict else v <= x):
                        best = v if best is None or (v < best if up else v > best) else best
        return best

    # the index of the k-th i in [l, r] (k = -1: the last one) with lo <(=) a[i] <(=) hi, or -1: whole blocks are
    # skipped by their counts, and only the block holding it is read
    def _kthWhere(self, l, r, k, lo, hi, loStrict, hiStrict):
        ok = lambda v: (lo is None or (lo < v if loStrict else lo <= v)) and (hi is None or (v < hi if hiStrict else v <= hi))  # noqa: E731
        spans = list(self._span(l, r))
        if k < 0:
            spans.reverse()
        for b, a, c, full, start in spans:
            if full:
                cnt = (len(b.vals) if hi is None else b.below(hi, hiStrict)) - (0 if lo is None else b.below(lo, not loStrict))
                if max(k, 1) > cnt:
                    k -= cnt
                    continue
            vals = b.values(a, c)
            order = range(len(vals) - 1, -1, -1) if k < 0 else range(len(vals))
            for p in order:
                if ok(vals[p]):
                    if k in (1, -1):
                        return start + a + p
                    k -= 1
        return -1
