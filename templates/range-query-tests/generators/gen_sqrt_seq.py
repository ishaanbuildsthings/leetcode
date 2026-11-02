"""Sequence edits (insert anywhere, cut / paste, reverse, rotate) with value-order queries (count / sum / xor / AND / OR
of the values below x, k-th smallest, ...) in O(sqrt(N) log N): a list of blocks.

    python3 gen_sqrt_seq.py

No tree can keep both orders at once (positions, for the edits, and values, for the queries) in log time, so the array
is cut into blocks of about B = sqrt(N log N) values. Each block keeps its values in array order and the same values
sorted, with prefix sums / xors and AND / OR trees over the sorted copy (each only when an op needs it), plus O(1) tags:
reversed, + add, = assign. A query walks the blocks: a whole block answers from its sorted copy with a binary search, a
partial one (at most two) is read value by value. An edit splits at most a few blocks (re-sorting them) and moves
whole blocks around in the list; when the list holds too many blocks it is rebuilt into even ones (amortized).

Templates: every subset of {sum, xor, and, or} (each adds its ops) x {no range update, rangeAdd, rangeAssign, both}
(rangeAdd only without xor / AND / OR: a pending add would change those of every value) x with or without rangeReverse.
"""
import itertools
import os
import shutil

from gen_treap import wrap
from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
DTYPE = "sqrt"
MARK = "List of sorted blocks"
CLS = "SqrtSequence"
SEQ = ["append", "appendLeft", "cut", "getAll", "insertAt", "insertCopiesAt", "merge", "paste", "rangeRotateLeft",
       "rangeRotateRight", "split", "trisect"]
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
CMPS = ["Lt", "Lte", "Gt", "Gte"]
BASE = (["countInValRange", "countOccurrences", "kthSmallest", "largestLtX", "largestLteX", "leftmostIndexOf",
         "leftmostIndexOfInRange", "rangeMax", "rangeMin", "rightmostIndexOf", "rightmostIndexOfInRange", "smallestGtX",
         "smallestGteX"] + [f"count{c}X" for c in CMPS] + [f"kth{c}X" for c in CMPS])
FAM_OPS = {"sum": ["rangeSum", "sumAbsDiffToX", "sumInValRange", "sumKthLargestRange", "sumKthSmallestRange", "sumLargestK",
                   "sumSmallestK"] + [f"sum{c}X" for c in CMPS],
           "xor": ["rangeXorQuery", "xorInValRange"] + [f"xor{c}X" for c in CMPS],
           "and": ["rangeAndQuery", "andInValRange"] + [f"and{c}X" for c in CMPS],
           "or": ["rangeOrQuery", "orInValRange"] + [f"or{c}X" for c in CMPS]}
FAMS = ["sum", "xor", "and", "or"]
STRUCT = {"append", "appendLeft", "cut", "insertAt", "insertCopiesAt", "merge", "paste", "rangeReverse", "rangeRotateLeft",
          "rangeRotateRight", "split", "trisect"}
KTH_U = {"kthSmallest", "sumSmallestK", "sumLargestK", "sumKthSmallestRange", "sumKthLargestRange"}


def variants():
    out = []
    for k in range(5):
        for fams in itertools.combinations(FAMS, k):
            bits = bool({"xor", "and", "or"} & set(fams))
            for ups in ((), ("assign",)) if bits else ((), ("add",), ("assign",), ("add", "assign")):
                for rev in (False, True):
                    out.append((fams, ups, rev))
    return out


def ops_of(fams, ups, rev):
    return sorted(set(BASE + SEQ + POINT + [o for f in fams for o in FAM_OPS[f]] + (["rangeReverse"] if rev else []) +
                      (["rangeAdd"] if "add" in ups else []) + (["rangeAssign"] if "assign" in ups else [])))


def flags(fams, ups, rev):
    return {"S": "sum" in fams, "X": "xor" in fams, "N": "and" in fams, "O": "or" in fams, "R": rev, "A": "add" in ups,
            "G": "assign" in ups, "Q": rev or bool(ups), "U": bool(ups), "W": rev and "assign" in ups,
            "V": rev and "assign" not in ups, "Y": "assign" in ups and (rev or "add" in ups)}


def pick(text, f):
    """keep the lines whose @letters@ prefix names a flag that is on (any of them; !X = X off; X&Y = both); no prefix:
    always"""
    out = []
    for ln in text.split("\n"):
        if ln.startswith("@"):
            k = ln.index("@", 1)
            keys, ln = ln[1:k], ln[k + 1:]
            if "&" in keys:  # (X&Y: both on)
                if all(f[x[1]] != (x[0] == "!") if len(x) == 2 else f[x] for x in keys.split("&")):
                    out.append(ln)
                continue
            ok, i = False, 0
            while i < len(keys):
                if keys[i] == "!":
                    ok |= not f[keys[i + 1]]
                    i += 2
                else:
                    ok |= f[keys[i]]
                    i += 1
            if not ok:
                continue
        out.append(ln)
    return "\n".join(out)


def header(cm, fams, ups, rev):
    ops = ops_of(fams, ups, rev)
    f = flags(fams, ups, rev)

    def cost(op):
        if op == "getAll":
            return "N"
        if op == "pointGet":
            return "sqrt(N)"
        if op in KTH_U:
            return "sqrt(N)*log(N)*log(U)"
        if op in STRUCT:
            return "sqrt(N)*log(N) amortized"
        return "sqrt(N)*log(N)"
    lines = [f"@operations: {' '.join(ops)}", f"@data-structure-type: {DTYPE}", "@complexities:"]
    lines += [f"  {op}: {cost(op)}" for op in ops] + ["  build: N*log(N)", "@memory:", "  layout: none"]
    node = ["vals[1*N]", "srt[1*N]"] + (["ps[1*N]"] if f["S"] else []) + (["px[1*N]"] if f["X"] else []) + (
        ["ta[2*N]"] if f["N"] else []) + (["to[2*N]"] if f["O"] else [])
    tags = (["rev[1*sqrt(N)]"] if rev else []) + (["add[1*sqrt(N)]"] if f["A"] else []) + (
        ["has[1*sqrt(N)]", "asg[1*sqrt(N)]"] if f["G"] else [])
    lines += [f"  node: {' '.join(node)}", f"  tags: {' '.join(tags) or 'none'}", "  other: none",
              "  note: blocks of about sqrt(N log N) values, each kept in array order and sorted (N here is the current length)" +
              ("; C++ also keeps ord[1*N], each sorted value's position, so edits merge instead of sorting again" if cm == "//" else "")]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def describe(fams, ups, rev):
    what = {"sum": "sums", "xor": "xors", "and": "ANDs", "or": "ORs"}
    keeps = ", ".join(what[f] for f in fams)
    up = " and ".join({"add": "rangeAdd", "assign": "rangeAssign"}[u] for u in ups)
    return (f"{MARK}: an array you can insert into anywhere, " + ("reverse, " if rev else "") + "rotate, cut pieces out of "
            "(that is how to erase) and paste them back, and ask value questions about any range a[l..r]: how many values "
            "are below x, the k-th smallest, the nearest value above / below x, where x first / last appears" +
            (f", and the {keeps} of the values in a value range" if keeps else "") + (f"; with {up}" if up else "") +
            ". Each op costs about sqrt(N log N): the array is a list of blocks, each kept both in array order and sorted. "
            "All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array.")


# ================================================================================================ Python

PY_BLOCK = '''class _Block:
    # a run of the array: vals in array order and srt, the same values sorted, both raw (the tags apply on read)
    __slots__ = ("vals", "srt"@S@, "ps"@X@, "px"@N@, "ta"@O@, "to"@R@, "rev"@A@, "add"@G@, "has", "asg")

    def __init__(self, vals):
        self.vals = vals
@R@        self.rev = False  # (vals read backwards)
@A@        self.add = 0  # (every value + add)
@G@        self.has = False  # (every value = asg, then + add)
@G@        self.asg = 0
        self.rebuild()

    def rebuild(self):  # O(B log B) -- srt and what is kept over it, from vals (no tag pending)
        srt = self.srt = sorted(self.vals)
@S@        self.ps = [0, *accumulate(srt)]  # ps[k] = sum of the k smallest
@X@        self.px = [0, *accumulate(srt, xor)]  # px[k] = xor of the k smallest
@N@        m = len(srt)  # ta / to: AND / OR trees over srt (leaves at m..2m-1)
@N@        ta = self.ta = [-1] * m + srt
@N@        for i in range(m - 1, 0, -1):
@N@            ta[i] = ta[2 * i] & ta[2 * i + 1]
@O@        m = len(srt)
@O@        to = self.to = [0] * m + srt
@O@        for i in range(m - 1, 0, -1):
@O@            to[i] = to[2 * i] | to[2 * i + 1]
@Q@
@Q@    def bake(self):  # O(B log B) -- hand the pending tags to vals and rebuild
@G@        if self.has:  # (one value: the order and the add don't matter)
@G@            self.vals = [self.asg{ADD}] * len(self.vals)
@Y@        else:
@G&R@            if self.rev:
@G&R@                self.vals.reverse()
@G&A@            if self.add:
@G&A@                self.vals = [v + self.add for v in self.vals]
@!G&R@        if self.rev:
@!G&R@            self.vals.reverse()
@!G&A@        if self.add:
@!G&A@            self.vals = [v + self.add for v in self.vals]
@G@        self.has = False
@R@        self.rev = False
@A@        self.add = 0
@Q@        self.rebuild()

    def get(self, k):  # the value at position k of this block
@G@        if self.has:
@G@            return self.asg{ADD}
@R@        return self.vals[len(self.vals) - 1 - k if self.rev else k]{ADD}
@!R@        return self.vals[k]{ADD}

    def values(self, lo, hi):  # the values at positions lo..hi, in order
@G@        if self.has:
@G@            return [self.asg{ADD}] * (hi - lo + 1)
@R@        if self.rev:
@R@            m = len(self.vals)
@R@            seg = self.vals[m - 1 - hi:m - lo][::-1]
@R@        else:
@R@            seg = self.vals[lo:hi + 1]
@!R@        seg = self.vals[lo:hi + 1]
@A@        return [v + self.add for v in seg] if self.add else seg
@!A@        return seg

    def below(self, x, strict):  # how many values are < x (strict) or <= x
@G@        if self.has:
@G@            v = self.asg{ADD}
@G@            return len(self.vals) if (v < x if strict else v <= x) else 0
@A@        return (bisect_left if strict else bisect_right)(self.srt, x - self.add)
@!A@        return (bisect_left if strict else bisect_right)(self.srt, x)

    def kth(self, k):  # the k-th smallest value, k from 0
@G@        if self.has:
@G@            return self.asg{ADD}
        return self.srt[k]{ADD}
@S@
@S@    def sumFirst(self, k):  # the sum of the k smallest values
@G&S@        if self.has:
@G&S@            return k * (self.asg{ADD})
@S@        return self.ps[k]{KADD}
@X@
@X@    def xorFirst(self, k):  # the xor of the k smallest values
@G&X@        if self.has:
@G&X@            return self.asg if k & 1 else 0
@X@        return self.px[k]
@N@
@N@    def andRange(self, i, j):  # the AND of the i-th..(j-1)-th smallest (-1, every bit, if none)
@G&N@        if self.has:
@G&N@            return self.asg if i < j else -1
@N@        ta, m, res = self.ta, len(self.srt), -1
@N@        i += m
@N@        j += m
@N@        while i < j:
@N@            if i & 1:
@N@                res &= ta[i]
@N@                i += 1
@N@            if j & 1:
@N@                j -= 1
@N@                res &= ta[j]
@N@            i >>= 1
@N@            j >>= 1
@N@        return res
@O@
@O@    def orRange(self, i, j):  # the OR of the i-th..(j-1)-th smallest (0 if none)
@G&O@        if self.has:
@G&O@            return self.asg if i < j else 0
@O@        to, m, res = self.to, len(self.srt), 0
@O@        i += m
@O@        j += m
@O@        while i < j:
@O@            if i & 1:
@O@                res |= to[i]
@O@                i += 1
@O@            if j & 1:
@O@                j -= 1
@O@                res |= to[j]
@O@            i >>= 1
@O@            j >>= 1
@O@        return res
'''

PY_CLASS = '''class SqrtSequence:
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

    # O(sqrt(N)) -- a[i]
    def pointGet(self, i):
        b, k = self._locate(i)
        return b.get(k)
{POINT}
{RANGE_UPD}
    # O(sqrt(N) log N) amortized -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        j, k = self._at(i)
        if j == len(self.blocks):  # (the end: onto the last block)
            if not j or len(self.blocks[-1].vals) >= 2 * self.B:
                self.blocks.append(_Block([v]))
                self.n += 1
                return
            j, k = j - 1, len(self.blocks[-1].vals)
        b = self.blocks[j]
@Q@        b.bake()
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

    # O(k + sqrt(N) log N) amortized -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    def insertCopiesAt(self, i, v, k):
        if k <= 0:
            return
        j = self._splitAt(i)
        self.blocks[j:j] = [_Block([v] * min(self.B, k - s)) for s in range(0, k, self.B)]
        self.n += k
        self._tidy()
@R@
@R@    # O(sqrt(N) log N) amortized -- reverse a[l..r] in place
@R@    def rangeReverse(self, l, r):
@R@        j1 = self._splitAt(l)
@R@        j2 = self._splitAt(r + 1)
@R@        seg = self.blocks[j1:j2][::-1]
@R@        for b in seg:
@R@            b.rev = not b.rev
@R@        self.blocks[j1:j2] = seg
@R@        self._tidy()

    # O(sqrt(N) log N) amortized -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    # it is taken mod the length (negative shifts right)
    def rangeRotateLeft(self, l, r, k):
        k %= r - l + 1
        if k:
            j1 = self._splitAt(l)
            j2 = self._splitAt(l + k)
            j3 = self._splitAt(r + 1)
            self.blocks[j1:j3] = self.blocks[j2:j3] + self.blocks[j1:j2]
            self._tidy()

    # O(sqrt(N) log N) amortized -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    # length (negative shifts left)
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)

    # O(sqrt(N) log N) amortized -- remove a[l..r] and return it as a SqrtSequence of its own (indices from 0)
    def cut(self, l, r):
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
    # (0 <= i <= size()); other is left empty
    def paste(self, i, other):
        j = self._splitAt(i)
        self.blocks[j:j] = other.blocks
        self.n += other.n
        other.blocks, other.n = [], 0
        self._tidy()

    # O(sqrt(N) log N) amortized -- append all of other at the end; other is left empty
    def merge(self, other):
        self.paste(self.n, other)

    # O(sqrt(N) log N) amortized -- (a[0..k-1], a[k..]) as two SqrtSequences of their own; this one is left empty
    def split(self, k):
        left = SqrtSequence()
        left.blocks, left.n, left.B = self.blocks, self.n, self.B
        self.blocks, self.n = [], 0
        right = left.cut(k, left.n - 1) if k < left.n else SqrtSequence()
        return left, right

    # O(sqrt(N) log N) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three SqrtSequences of their own; this one is
    # left empty
    def trisect(self, l, r):
        left, right = self.split(r + 1)
        left, mid = left.split(l)
        return left, mid, right

    # O(sqrt(N) log N) -- # of values < x in a[l..r]
    def countLtX(self, l, r, x):
        return self._count(l, r, None, x, False, True)

    # O(sqrt(N) log N) -- # of values <= x in a[l..r]
    def countLteX(self, l, r, x):
        return self._count(l, r, None, x, False, False)

    # O(sqrt(N) log N) -- # of values > x in a[l..r]
    def countGtX(self, l, r, x):
        return self._count(l, r, x, None, True, False)

    # O(sqrt(N) log N) -- # of values >= x in a[l..r]
    def countGteX(self, l, r, x):
        return self._count(l, r, x, None, False, False)

    # O(sqrt(N) log N) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    def countInValRange(self, l, r, lowVal, highVal):
        return self._count(l, r, lowVal, highVal, False, False) if lowVal <= highVal else 0

    # O(sqrt(N) log N) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        return self._count(l, r, x, x, False, False)

    # O(sqrt(N) log N log U) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else
    # IndexError (a binary search over the values, each step a count)
    def kthSmallest(self, l, r, k):
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

    # O(sqrt(N) log N) -- min of a[l..r]
    def rangeMin(self, l, r):
        return min(b.kth(0) if full else min(b.values(lo, hi)) for b, lo, hi, full, _ in self._span(l, r))

    # O(sqrt(N) log N) -- max of a[l..r]
    def rangeMax(self, l, r):
        return max(b.kth(hi) if full else max(b.values(lo, hi)) for b, lo, hi, full, _ in self._span(l, r))

    # O(sqrt(N) log N) -- smallest value >= x in a[l..r], or None
    def smallestGteX(self, l, r, x):
        return self._nearest(l, r, x, True, False)

    # O(sqrt(N) log N) -- smallest value > x in a[l..r], or None
    def smallestGtX(self, l, r, x):
        return self._nearest(l, r, x, True, True)

    # O(sqrt(N) log N) -- largest value <= x in a[l..r], or None
    def largestLteX(self, l, r, x):
        return self._nearest(l, r, x, False, False)

    # O(sqrt(N) log N) -- largest value < x in a[l..r], or None
    def largestLtX(self, l, r, x):
        return self._nearest(l, r, x, False, True)

    # O(sqrt(N) log N) -- the first i with a[i] == x, or -1
    def leftmostIndexOf(self, x):
        return self.leftmostIndexOfInRange(0, self.n - 1, x) if self.n else -1

    # O(sqrt(N) log N) -- the last i with a[i] == x, or -1
    def rightmostIndexOf(self, x):
        return self.rightmostIndexOfInRange(0, self.n - 1, x) if self.n else -1

    # O(sqrt(N) log N) -- the first i in [l, r] with a[i] == x, or -1
    def leftmostIndexOfInRange(self, l, r, x):
        return self._kthWhere(l, r, 1, x, x, False, False)

    # O(sqrt(N) log N) -- the last i in [l, r] with a[i] == x, or -1
    def rightmostIndexOfInRange(self, l, r, x):
        return self._kthWhere(l, r, -1, x, x, False, False)

    # O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] < x, or -1
    def kthLtX(self, l, r, k, x):
        return self._kthWhere(l, r, k, None, x, False, True) if k >= 1 else -1

    # O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] <= x, or -1
    def kthLteX(self, l, r, k, x):
        return self._kthWhere(l, r, k, None, x, False, False) if k >= 1 else -1

    # O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] > x, or -1
    def kthGtX(self, l, r, k, x):
        return self._kthWhere(l, r, k, x, None, True, False) if k >= 1 else -1

    # O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] >= x, or -1
    def kthGteX(self, l, r, k, x):
        return self._kthWhere(l, r, k, x, None, False, False) if k >= 1 else -1
{FAM_PUB}
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
@Q@                p.bake()
@Q@                b.bake()
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
@Q@            b.bake()
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
'''

PY_POINT = '''
    # O(sqrt(N) log N) -- {doc}
    def {op}(self, i, v):
        b, k = self._locate(i)
        nv = {expr}
@Q@        b.bake()
        b.vals[k] = nv
        b.rebuild()
'''

PY_RANGE = '''
    # O(sqrt(N) log N) -- {doc} for i in [l, r]
    def {op}(self, l, r, v):
        for b, lo, hi, full, _ in self._span(l, r):
            if full:
                {full}
            else:
                b.bake()
                vals = b.vals
                for k in range(lo, hi + 1):
                    vals[k] {asn} v
                b.rebuild()
'''


def py_fam(f):
    out = []
    if f["S"]:
        out.append('''
    # O(sqrt(N) log N) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._sum(l, r, None, None, False, False)

    # O(sqrt(N) log N) -- sum of the values < x in a[l..r]
    def sumLtX(self, l, r, x):
        return self._sum(l, r, None, x, False, True)

    # O(sqrt(N) log N) -- sum of the values <= x in a[l..r]
    def sumLteX(self, l, r, x):
        return self._sum(l, r, None, x, False, False)

    # O(sqrt(N) log N) -- sum of the values > x in a[l..r]
    def sumGtX(self, l, r, x):
        return self._sum(l, r, x, None, True, False)

    # O(sqrt(N) log N) -- sum of the values >= x in a[l..r]
    def sumGteX(self, l, r, x):
        return self._sum(l, r, x, None, False, False)

    # O(sqrt(N) log N) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal
    def sumInValRange(self, l, r, lowVal, highVal):
        return self._sum(l, r, lowVal, highVal, False, False) if lowVal <= highVal else 0

    # O(sqrt(N) log N log U) -- sum of the k smallest values in a[l..r]; needs 0 <= k <= r - l + 1, else IndexError
    def sumSmallestK(self, l, r, k):
        if not 0 <= k <= r - l + 1:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, k)

    # O(sqrt(N) log N log U) -- sum of the k largest values in a[l..r]; needs 0 <= k <= r - l + 1, else IndexError
    def sumLargestK(self, l, r, k):
        n = r - l + 1
        if not 0 <= k <= n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {n}")
        return self.rangeSum(l, r) - self._sumFirst(l, r, n - k)

    # O(sqrt(N) log N log U) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs
    # 1 <= kFrom <= kTo <= r - l + 1, else IndexError
    def sumKthSmallestRange(self, l, r, kFrom, kTo):
        if not 1 <= kFrom <= kTo <= r - l + 1:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, kTo) - self._sumFirst(l, r, kFrom - 1)

    # O(sqrt(N) log N log U) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) =
    # the 3 biggest); needs 1 <= kFrom <= kTo <= r - l + 1, else IndexError
    def sumKthLargestRange(self, l, r, kFrom, kTo):
        n = r - l + 1
        if not 1 <= kFrom <= kTo <= n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n - kFrom + 1) - self._sumFirst(l, r, n - kTo)

    # O(sqrt(N) log N) -- sum of |a[i] - x| over i in [l, r]
    def sumAbsDiffToX(self, l, r, x):
        c, s = self._count(l, r, None, x, False, True), self._sum(l, r, None, x, False, True)
        return c * x - s + self.rangeSum(l, r) - s - (r - l + 1 - c) * x

    def _sum(self, l, r, lo, hi, loStrict, hiStrict):
        return sum(b.sumFirst(j) - b.sumFirst(i) if b else sum(i) for b, i, j in self._sel(l, r, lo, hi, loStrict, hiStrict))

    def _sumFirst(self, l, r, k):  # the sum of the k smallest values of a[l..r]
        if k == 0:
            return 0
        v = self.kthSmallest(l, r, k)  # (the k-th smallest: the values below it, then copies of it)
        return self._sum(l, r, None, v, False, True) + (k - self._count(l, r, None, v, False, True)) * v
''')
    for fam, letter, op, ident, fn in (("xor", "X", "^", "0", "xorFirst"), ("and", "N", "&", "-1", "andRange"), ("or", "O", "|", "0", "orRange")):
        if not f[letter]:
            continue
        full = f"b.xorFirst(j) ^ b.xorFirst(i)" if fam == "xor" else f"b.{fn}(i, j)"
        what = {"xor": "xor", "and": "AND", "or": "OR"}[fam]
        none = {"xor": "0 if there are none", "and": "-1 (every bit) if there are none", "or": "0 if there are none"}[fam]
        cop = " (copies count)" if fam == "xor" else ""
        Q = {"xor": "rangeXorQuery", "and": "rangeAndQuery", "or": "rangeOrQuery"}[fam]
        out.append(f'''
    # O(sqrt(N) log N) -- a[l] {op} ... {op} a[r]
    def {Q}(self, l, r):
        return self._{fam}(l, r, None, None, False, False)

    # O(sqrt(N) log N) -- {what} of the values < x in a[l..r]{cop}; {none}
    def {fam}LtX(self, l, r, x):
        return self._{fam}(l, r, None, x, False, True)

    # O(sqrt(N) log N) -- {what} of the values <= x in a[l..r]{cop}; {none}
    def {fam}LteX(self, l, r, x):
        return self._{fam}(l, r, None, x, False, False)

    # O(sqrt(N) log N) -- {what} of the values > x in a[l..r]{cop}; {none}
    def {fam}GtX(self, l, r, x):
        return self._{fam}(l, r, x, None, True, False)

    # O(sqrt(N) log N) -- {what} of the values >= x in a[l..r]{cop}; {none}
    def {fam}GteX(self, l, r, x):
        return self._{fam}(l, r, x, None, False, False)

    # O(sqrt(N) log N) -- {what} of the a[i] in [l, r] with lowVal <= a[i] <= highVal{cop}; {none}
    def {fam}InValRange(self, l, r, lowVal, highVal):
        return self._{fam}(l, r, lowVal, highVal, False, False) if lowVal <= highVal else {ident}

    def _{fam}(self, l, r, lo, hi, loStrict, hiStrict):
        res = {ident}
        for b, i, j in self._sel(l, r, lo, hi, loStrict, hiStrict):
            if b:
                res {op}= {full}
            else:
                for v in i:
                    res {op}= v
        return res
''')
    return "".join(out)


def py(fams, ups, rev):
    f = flags(fams, ups, rev)
    add, kadd = (" + self.add", " + k * self.add") if f["A"] else ("", "")
    block = PY_BLOCK.replace("{ADD}", add).replace("{KADD}", kadd)
    # (the @letters@ marks inside the __slots__ line)
    slots = '    __slots__ = ("vals", "srt"' + "".join(f', "{n}"' for n, k in (("ps", "S"), ("px", "X"), ("ta", "N"), ("to", "O"), ("rev", "R"),
                                                                            ("add", "A")) if f[k]) + (', "has", "asg"' if f["G"] else "") + ")"
    block = "\n".join(slots if ln.startswith("    __slots__") else ln for ln in block.split("\n"))
    point = "".join(PY_POINT.replace("{op}", op).replace("{doc}", doc).replace("{expr}", expr)
                    for op, doc, expr in (("pointAssign", "a[i] = v", "v"), ("pointAdd", "a[i] += v", "b.get(k) + v"),
                                          ("pointChmax", "a[i] = max(a[i], v)", "max(b.get(k), v)"),
                                          ("pointChmin", "a[i] = min(a[i], v)", "min(b.get(k), v)")))
    rng = ""
    if f["A"]:
        rng += PY_RANGE.replace("{op}", "rangeAdd").replace("{doc}", "a[i] += v").replace("{full}", "b.add += v").replace("{asn}", "+=")
    if f["G"]:
        rng += PY_RANGE.replace("{op}", "rangeAssign").replace("{doc}", "a[i] = v").replace(
            "{full}", "b.has, b.asg" + (", b.add = True, v, 0" if f["A"] else " = True, v")).replace("{asn}", "=")
    cls = PY_CLASS.replace("{POINT}", point).replace("{RANGE_UPD}", rng).replace("{FAM_PUB}", py_fam(f))
    imports = ("from bisect import bisect_left, bisect_right\n" + ("from itertools import accumulate\n" if f["S"] or f["X"] else "") +
               "from math import isqrt\n" + ("from operator import xor\n" if f["X"] else "") + "\n\n")
    text = header("#", fams, ups, rev) + "\n" + wrap(describe(fams, ups, rev), "#") + imports + pick(block, f) + "\n\n" + pick(cls, f)
    return text


# ================================================================================================ C++

CPP_HEAD = '''template <typename T>
struct SqrtSequence {
@S@    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // a run of the array: vals in array order and srt, the same values sorted, both raw (the tags apply on read);
    // ord[i] is the position in vals of srt[i], so an edit merges instead of sorting again
    struct Block {
        vector<T> vals, srt;
        vector<int> ord;
@S@        vector<S> ps;  // ps[k] = sum of the k smallest
@X@        vector<T> px;  // px[k] = xor of the k smallest
@N@        vector<T> ta;  // AND tree over srt (leaves at m..2m-1)
@O@        vector<T> to;  // OR tree over srt
@R@        bool rev = false;  // (vals read backwards)
@G@        bool has = false;  // (every value = asg, then + add)
@A@        T add = T(0);  // (every value + add)
@G@        T asg = T(0);

        Block() = default;

        explicit Block(vector<T> v) : vals(std::move(v)) {  // O(B log B)
            ord.resize(vals.size());
            iota(ord.begin(), ord.end(), 0);
            sort(ord.begin(), ord.end(), [&](int x, int y) { return vals[x] < vals[y]; });
            srt.resize(vals.size());
            for (int i = 0; i < size(); i++) srt[i] = vals[ord[i]];
            refresh();
        }

        int size() const { return (int)vals.size(); }

        void refresh() {  // O(B) -- what is kept over srt
            int m = size();
@S@            ps.assign(m + 1, S(0));
@S@            for (int i = 0; i < m; i++) ps[i + 1] = ps[i] + S(srt[i]);
@X@            px.assign(m + 1, T(0));
@X@            for (int i = 0; i < m; i++) px[i + 1] = px[i] ^ srt[i];
@N@            ta.assign(2 * m, ~T(0));
@N@            copy(srt.begin(), srt.end(), ta.begin() + m);
@N@            for (int i = m - 1; i > 0; i--) ta[i] = ta[2 * i] & ta[2 * i + 1];
@O@            to.assign(2 * m, T(0));
@O@            copy(srt.begin(), srt.end(), to.begin() + m);
@O@            for (int i = m - 1; i > 0; i--) to[i] = to[2 * i] | to[2 * i + 1];
            (void)m;
        }

@!Q@        void bake() {}  // (no tags: nothing is ever pending)
@Q@        void bake() {  // O(B) -- hand the pending tags to vals (srt keeps its order)
@Q@            if (!({PEND})) return;
@G@            if (has) {  // (one value: the order and the add don't matter)
@G@                std::fill(vals.begin(), vals.end(), T(asg{ADD}));
@G@                std::fill(srt.begin(), srt.end(), T(asg{ADD}));
@G@                iota(ord.begin(), ord.end(), 0);
@Y@            } else {
@G&R@                if (rev) {
@G&R@                    reverse(vals.begin(), vals.end());
@G&R@                    for (int& p : ord) p = size() - 1 - p;
@G&R@                }
@G&A@                if (add != T(0)) {
@G&A@                    for (T& v : vals) v += add;
@G&A@                    for (T& v : srt) v += add;
@G&A@                }
@G@            }
@!G&R@            if (rev) {
@!G&R@                reverse(vals.begin(), vals.end());
@!G&R@                for (int& p : ord) p = size() - 1 - p;
@!G&R@            }
@!G&A@            if (add != T(0)) {
@!G&A@                for (T& v : vals) v += add;
@!G&A@                for (T& v : srt) v += add;
@!G&A@            }
@G@            has = false;
@R@            rev = false;
@A@            add = T(0);
@Q@            refresh();
@Q@        }

        // O(B) -- the values at positions lo..hi become f(value), where f keeps their order (an add, an assign, a
        // single value): the changed and the unchanged entries of srt are each still sorted, so one merge restores it
        template <class F>
        void update(int lo, int hi, F f) {
            bake();
            for (int k = lo; k <= hi; k++) vals[k] = f(vals[k]);
            vector<int> in, out;
            for (int p : ord) (lo <= p && p <= hi ? in : out).push_back(p);
            std::merge(in.begin(), in.end(), out.begin(), out.end(), ord.begin(), [&](int x, int y) { return vals[x] < vals[y]; });
            for (int i = 0; i < size(); i++) srt[i] = vals[ord[i]];
            refresh();
        }

        void insert(int k, T v) {  // O(B) -- v goes in at position k
            bake();
            vals.insert(vals.begin() + k, v);
            for (int& p : ord) p += p >= k;
            int i = int(upper_bound(srt.begin(), srt.end(), v) - srt.begin());
            srt.insert(srt.begin() + i, v), ord.insert(ord.begin() + i, k);
            refresh();
        }

        Block cutTail(int k) {  // O(B) -- positions k.. as a block of their own (this one keeps 0..k-1)
            bake();
            Block t;
            t.vals.assign(vals.begin() + k, vals.end());
            vals.resize(k);
            vector<T> s;
            vector<int> o;
            for (int i = 0; i < (int)ord.size(); i++) {
                if (ord[i] < k) s.push_back(srt[i]), o.push_back(ord[i]);
                else t.srt.push_back(srt[i]), t.ord.push_back(ord[i] - k);
            }
            srt = std::move(s), ord = std::move(o);
            refresh(), t.refresh();
            return t;
        }

        void absorb(Block& o) {  // O(B) -- o's values appended after this block's (o is left empty)
            bake(), o.bake();
            int m = size();
            vals.insert(vals.end(), o.vals.begin(), o.vals.end());
            for (int& p : o.ord) p += m;
            vector<T> s(vals.size());
            vector<int> w(vals.size());
            int i = 0, j = 0, k = 0;
            while (i < m || j < o.size()) {
                if (j == o.size() || (i < m && srt[i] <= o.srt[j])) s[k] = srt[i], w[k++] = ord[i++];
                else s[k] = o.srt[j], w[k++] = o.ord[j++];
            }
            srt = std::move(s), ord = std::move(w);
            o.vals.clear(), o.srt.clear(), o.ord.clear();
            refresh();
        }

        void sortedPart(int a, int c, vector<T>& out) const {  // O(B) -- the values at positions a..c, sorted
@G@            if (has) {
@G@                out.assign(c - a + 1, T(asg{ADD}));
@G@                return;
@G@            }
@R@            int lo = rev ? size() - 1 - c : a, hi = rev ? size() - 1 - a : c;  // (the positions in vals)
@!R@            int lo = a, hi = c;
            out.clear();
            for (int i = 0; i < size(); i++)
                if (lo <= ord[i] && ord[i] <= hi) out.push_back(T(srt[i]{ADD}));
        }

        T get(int k) const {  // the value at position k of this block
@G@            if (has) return T(asg{ADD});
@R@            return T(vals[rev ? size() - 1 - k : k]{ADD});
@!R@            return T(vals[k]{ADD});
        }

        int below(T x, bool strict) const {  // how many values are < x (strict) or <= x
@G@            if (has) return (strict ? T(asg{ADD}) < x : T(asg{ADD}) <= x) ? size() : 0;
@A@            T y = T(x - add);
@!A@            const T& y = x;
            return int((strict ? lower_bound(srt.begin(), srt.end(), y) : upper_bound(srt.begin(), srt.end(), y)) - srt.begin());
        }

        T kth(int k) const {  // the k-th smallest value, k from 0
@G@            if (has) return T(asg{ADD});
            return T(srt[k]{ADD});
        }
@S@
@S@        S sumFirst(int k) const {  // the sum of the k smallest values
@G&S@            if (has) return S(k) * S(asg{ADD});
@S@            return ps[k]{KADD};
@S@        }
@X@
@X@        T xorFirst(int k) const {  // the xor of the k smallest values
@G&X@            if (has) return k & 1 ? asg : T(0);
@X@            return px[k];
@X@        }
@N@
@N@        T andRange(int i, int j) const {  // the AND of the i-th..(j-1)-th smallest (~0, every bit, if none)
@G&N@            if (has) return i < j ? asg : ~T(0);
@N@            T res = ~T(0);
@N@            for (i += size(), j += size(); i < j; i >>= 1, j >>= 1) {
@N@                if (i & 1) res &= ta[i++];
@N@                if (j & 1) res &= ta[--j];
@N@            }
@N@            return res;
@N@        }
@O@
@O@        T orRange(int i, int j) const {  // the OR of the i-th..(j-1)-th smallest (0 if none)
@G&O@            if (has) return i < j ? asg : T(0);
@O@            T res = T(0);
@O@            for (i += size(), j += size(); i < j; i >>= 1, j >>= 1) {
@O@                if (i & 1) res |= to[i++];
@O@                if (j & 1) res |= to[--j];
@O@            }
@O@            return res;
@O@        }
    };

    // pieces (cut / split / trisect) are SqrtSequences of their own: paste / merge move their blocks over
    vector<Block> blocks;
    int n = 0, B = 16;

    // O(N log N) -- arr: the initial array (leave it out to start empty)
    explicit SqrtSequence(const vector<T>& arr = {}) { fill(arr); }

    // O(1) -- the current length of the array
    int size() const { return n; }

    // O(N) -- the whole current array
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (const Block& b : blocks)
            for (int k = 0; k < b.size(); k++) out.push_back(b.get(k));
        return out;
    }

    // O(sqrt(N)) -- a[i]
    T pointGet(int i) const {
        auto [j, k] = at(i);
        return blocks[j].get(k);
    }
{POINT}
{RANGE_UPD}
    // O(sqrt(N) log N) amortized -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        auto [j, k] = at(i);
        if (j == (int)blocks.size()) {  // (the end: onto the last block)
            if (!j || blocks.back().size() >= 2 * B) {
                blocks.emplace_back(vector<T>{v}), n++;
                return;
            }
            j--, k = blocks.back().size();
        }
        blocks[j].insert(k, v);
        if (blocks[j].size() > 2 * B) {  // (too long: two blocks)
            Block tail = blocks[j].cutTail(blocks[j].size() / 2);
            blocks.insert(blocks.begin() + j + 1, std::move(tail));
        }
        n++;
        if (idealB(n) > 2 * B) fill(getAll());  // (grown a lot: bigger blocks)
    }

    // O(sqrt(N) log N) amortized -- append v to the end
    void append(T v) { insertAt(n, v); }

    // O(sqrt(N) log N) amortized -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(k + sqrt(N) log N) amortized -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        int j = splitAt(i);
        vector<Block> add;
        for (long long s = 0; s < k; s += B) add.emplace_back(vector<T>(min<long long>(B, k - s), v));
        blocks.insert(blocks.begin() + j, make_move_iterator(add.begin()), make_move_iterator(add.end()));
        n += (int)k;
        tidy();
    }
@R@
@R@    // O(sqrt(N) log N) amortized -- reverse a[l..r] in place
@R@    void rangeReverse(int l, int r) {
@R@        int j1 = splitAt(l), j2 = splitAt(r + 1);
@R@        reverse(blocks.begin() + j1, blocks.begin() + j2);
@R@        for (int j = j1; j < j2; j++) blocks[j].rev = !blocks[j].rev;
@R@        tidy();
@R@    }

    // O(sqrt(N) log N) amortized -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    // it is taken mod the length (negative shifts right)
    void rangeRotateLeft(int l, int r, long long k) {
        long long len = r - l + 1;
        k = ((k % len) + len) % len;
        if (!k) return;
        int j1 = splitAt(l), j2 = splitAt(l + (int)k), j3 = splitAt(r + 1);
        rotate(blocks.begin() + j1, blocks.begin() + j2, blocks.begin() + j3);
        tidy();
    }

    // O(sqrt(N) log N) amortized -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left)
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(sqrt(N) log N) amortized -- remove a[l..r] and return it as a SqrtSequence of its own (indices from 0)
    SqrtSequence cut(int l, int r) {
        int j1 = splitAt(l), j2 = splitAt(r + 1);
        SqrtSequence piece;
        piece.blocks.assign(make_move_iterator(blocks.begin() + j1), make_move_iterator(blocks.begin() + j2));
        piece.n = r - l + 1, piece.B = B;
        blocks.erase(blocks.begin() + j1, blocks.begin() + j2);
        n -= r - l + 1;
        tidy(), piece.tidy();
        return piece;
    }

    // O(sqrt(N) log N) amortized -- insert all of other (any SqrtSequence, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(int i, SqrtSequence& other) {
        int j = splitAt(i);
        blocks.insert(blocks.begin() + j, make_move_iterator(other.blocks.begin()), make_move_iterator(other.blocks.end()));
        n += other.n;
        other.blocks.clear(), other.n = 0;
        tidy();
    }

    // O(sqrt(N) log N) amortized -- append all of other at the end; other is left empty
    void merge(SqrtSequence& other) { paste(n, other); }

    // O(sqrt(N) log N) amortized -- (a[0..k-1], a[k..]) as two SqrtSequences of their own; this one is left empty
    pair<SqrtSequence, SqrtSequence> split(int k) {
        SqrtSequence left;
        left.blocks = std::move(blocks), left.n = n, left.B = B;
        blocks.clear(), n = 0;
        SqrtSequence right = k < left.n ? left.cut(k, left.n - 1) : SqrtSequence();
        return {std::move(left), std::move(right)};
    }

    // O(sqrt(N) log N) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three SqrtSequences of their own; this one is
    // left empty
    tuple<SqrtSequence, SqrtSequence, SqrtSequence> trisect(int l, int r) {
        auto [left, right] = split(r + 1);
        auto [first, mid] = left.split(l);
        return {std::move(first), std::move(mid), std::move(right)};
    }

    // O(sqrt(N) log N) -- # of values < x in a[l..r]
    int countLtX(int l, int r, T x) const { return count(l, r, nullopt, x, false, true); }

    // O(sqrt(N) log N) -- # of values <= x in a[l..r]
    int countLteX(int l, int r, T x) const { return count(l, r, nullopt, x, false, false); }

    // O(sqrt(N) log N) -- # of values > x in a[l..r]
    int countGtX(int l, int r, T x) const { return count(l, r, x, nullopt, true, false); }

    // O(sqrt(N) log N) -- # of values >= x in a[l..r]
    int countGteX(int l, int r, T x) const { return count(l, r, x, nullopt, false, false); }

    // O(sqrt(N) log N) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    int countInValRange(int l, int r, T lowVal, T highVal) const {
        return lowVal <= highVal ? count(l, r, lowVal, highVal, false, false) : 0;
    }

    // O(sqrt(N) log N) -- # of i in [l, r] with a[i] == x
    int countOccurrences(int l, int r, T x) const { return count(l, r, x, x, false, false); }

    // O(sqrt(N) log N log U) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else
    // throws out_of_range (a binary search over the values, each step a count)
    T kthSmallest(int l, int r, int k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        vector<const Block*> whole;
        vector<vector<T>> parts;  // (the values of the partial blocks, sorted)
        span(l, r, [&](const Block& b, int a, int c, bool all, int) {
            if (all) whole.push_back(&b);
            else parts.emplace_back(), b.sortedPart(a, c, parts.back());
            return false;
        });
        optional<T> lo, hi;
        for (const Block* b : whole) lo = lo ? min(*lo, b->kth(0)) : b->kth(0), hi = hi ? max(*hi, b->kth(b->size() - 1)) : b->kth(b->size() - 1);
        for (auto& p : parts) lo = lo ? min(*lo, p.front()) : p.front(), hi = hi ? max(*hi, p.back()) : p.back();
        while (*lo < *hi) {
            T mid = *lo + (*hi - *lo) / 2;
            int c = 0;
            for (auto& p : parts) c += int(upper_bound(p.begin(), p.end(), mid) - p.begin());
            for (const Block* b : whole) c += b->below(mid, false);
            if (c >= k) hi = mid;
            else lo = mid + 1;
        }
        return *lo;
    }

    // O(sqrt(N) log N) -- min of a[l..r]
    T rangeMin(int l, int r) const {
        optional<T> best;
        span(l, r, [&](const Block& b, int lo, int hi, bool whole, int) {
            if (whole) best = best ? min(*best, b.kth(0)) : b.kth(0);
            else for (int k = lo; k <= hi; k++) best = best ? min(*best, b.get(k)) : b.get(k);
            return false;
        });
        return *best;
    }

    // O(sqrt(N) log N) -- max of a[l..r]
    T rangeMax(int l, int r) const {
        optional<T> best;
        span(l, r, [&](const Block& b, int lo, int hi, bool whole, int) {
            if (whole) best = best ? max(*best, b.kth(hi)) : b.kth(hi);
            else for (int k = lo; k <= hi; k++) best = best ? max(*best, b.get(k)) : b.get(k);
            return false;
        });
        return *best;
    }

    // O(sqrt(N) log N) -- smallest value >= x in a[l..r], or nullopt
    optional<T> smallestGteX(int l, int r, T x) const { return nearest(l, r, x, true, false); }

    // O(sqrt(N) log N) -- smallest value > x in a[l..r], or nullopt
    optional<T> smallestGtX(int l, int r, T x) const { return nearest(l, r, x, true, true); }

    // O(sqrt(N) log N) -- largest value <= x in a[l..r], or nullopt
    optional<T> largestLteX(int l, int r, T x) const { return nearest(l, r, x, false, false); }

    // O(sqrt(N) log N) -- largest value < x in a[l..r], or nullopt
    optional<T> largestLtX(int l, int r, T x) const { return nearest(l, r, x, false, true); }

    // O(sqrt(N) log N) -- the first i with a[i] == x, or -1
    int leftmostIndexOf(T x) const { return n ? leftmostIndexOfInRange(0, n - 1, x) : -1; }

    // O(sqrt(N) log N) -- the last i with a[i] == x, or -1
    int rightmostIndexOf(T x) const { return n ? rightmostIndexOfInRange(0, n - 1, x) : -1; }

    // O(sqrt(N) log N) -- the first i in [l, r] with a[i] == x, or -1
    int leftmostIndexOfInRange(int l, int r, T x) const { return kthWhere(l, r, 1, x, x, false, false); }

    // O(sqrt(N) log N) -- the last i in [l, r] with a[i] == x, or -1
    int rightmostIndexOfInRange(int l, int r, T x) const { return kthWhere(l, r, -1, x, x, false, false); }

    // O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] < x, or -1
    int kthLtX(int l, int r, int k, T x) const { return k >= 1 ? kthWhere(l, r, k, nullopt, x, false, true) : -1; }

    // O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] <= x, or -1
    int kthLteX(int l, int r, int k, T x) const { return k >= 1 ? kthWhere(l, r, k, nullopt, x, false, false) : -1; }

    // O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] > x, or -1
    int kthGtX(int l, int r, int k, T x) const { return k >= 1 ? kthWhere(l, r, k, x, nullopt, true, false) : -1; }

    // O(sqrt(N) log N) -- the index of the k-th i in [l, r] (k from 1, left to right) with a[i] >= x, or -1
    int kthGteX(int l, int r, int k, T x) const { return k >= 1 ? kthWhere(l, r, k, x, nullopt, false, false) : -1; }
{FAM_PUB}
    // ---- internals ----

    // sqrt(n log n): a query reads n / B blocks (a binary search each) and two partial ones
    static int idealB(int n) { return max(16, (int)sqrt((double)n * (__lg(max(n, 1)) + 1))); }

    void fill(const vector<T>& vals) {  // blocks of about idealB values holding vals
        n = (int)vals.size(), B = idealB(n);
        blocks.clear();
        for (int s = 0; s < n; s += B) blocks.emplace_back(vector<T>(vals.begin() + s, vals.begin() + min(n, s + B)));
    }

    // O(N / B + B) amortized -- merge each run of neighbours that fit in one block (each merge is paid for by the
    // split that made it), so any two neighbours hold more than B values; when the array has grown so much that B is
    // too small, rebuild into even blocks (O(N log N), after about N new values)
    void tidy() {
        if (idealB(n) > 2 * B) return fill(getAll());
        vector<Block> out;
        for (Block& b : blocks) {
            if (!b.size()) continue;
            if (!out.empty() && out.back().size() + b.size() <= B) out.back().absorb(b);
            else out.push_back(std::move(b));
        }
        blocks = std::move(out);
    }

    pair<int, int> at(int i) const {  // (block index, position in it) of a[i]; i == size() gives (number of blocks, 0)
        for (int j = 0; j < (int)blocks.size(); j++) {
            if (i < blocks[j].size()) return {j, i};
            i -= blocks[j].size();
        }
        return {(int)blocks.size(), 0};
    }

    int splitAt(int i) {  // make a block start at a[i] (0 <= i <= size()): that block's index
        auto [j, k] = at(i);
        if (!k) return j;
        Block tail = blocks[j].cutTail(k);
        blocks.insert(blocks.begin() + j + 1, std::move(tail));
        return j + 1;
    }

    // f(block, lo, hi, whole, start) for each block meeting a[l..r] (positions lo..hi of it, whether that is all of
    // it, the index of its first value), until f returns true
    template <class F>
    void span(int l, int r, F f) const {
        int i = 0;
        for (const Block& b : blocks) {
            int m = b.size();
            if (i + m > l) {
                int lo = max(l - i, 0), hi = min(r - i, m - 1);
                if (f(b, lo, hi, lo == 0 && hi == m - 1, i) || i + m > r) return;
            }
            i += m;
        }
    }

    static bool passes(T v, const optional<T>& lo, const optional<T>& hi, bool loStrict, bool hiStrict) {
        return (!lo || (loStrict ? *lo < v : *lo <= v)) && (!hi || (hiStrict ? v < *hi : v <= *hi));
    }

    // the values v of a[l..r] with lo <(=) v <(=) hi (a missing bound: none): whole(b, i, j) for a whole block (its
    // i-th..(j-1)-th smallest pass), part(v) for each passing value of a partial one
    template <class W, class P>
    void select(int l, int r, optional<T> lo, optional<T> hi, bool loStrict, bool hiStrict, W whole, P part) const {
        span(l, r, [&](const Block& b, int a, int c, bool all, int) {
            if (all) whole(b, lo ? b.below(*lo, !loStrict) : 0, hi ? b.below(*hi, hiStrict) : b.size());
            else
                for (int k = a; k <= c; k++)
                    if (T v = b.get(k); passes(v, lo, hi, loStrict, hiStrict)) part(v);
            return false;
        });
    }

    int count(int l, int r, optional<T> lo, optional<T> hi, bool loStrict, bool hiStrict) const {
        int res = 0;
        select(l, r, lo, hi, loStrict, hiStrict, [&](const Block&, int i, int j) { res += j - i; }, [&](T) { res++; });
        return res;
    }

    optional<T> nearest(int l, int r, T x, bool up, bool strict) const {  // the smallest > (>=) x (up) or largest < (<=)
        optional<T> best;
        auto take = [&](T v) {
            if (!best || (up ? v < *best : v > *best)) best = v;
        };
        span(l, r, [&](const Block& b, int lo, int hi, bool whole, int) {
            if (whole) {
                int k = up ? b.below(x, !strict) : b.below(x, strict) - 1;
                if (k >= 0 && k < b.size()) take(b.kth(k));
            } else {
                for (int k = lo; k <= hi; k++) {
                    T v = b.get(k);
                    if (up ? (strict ? v > x : v >= x) : (strict ? v < x : v <= x)) take(v);
                }
            }
            return false;
        });
        return best;
    }

    // the index of the k-th i in [l, r] (k = -1: the last one) with lo <(=) a[i] <(=) hi, or -1: whole blocks are
    // skipped by their counts, and only the block holding it is read
    int kthWhere(int l, int r, int k, optional<T> lo, optional<T> hi, bool loStrict, bool hiStrict) const {
        vector<tuple<const Block*, int, int, bool, int>> spans;
        span(l, r, [&](const Block& b, int a, int c, bool whole, int start) {
            spans.emplace_back(&b, a, c, whole, start);
            return false;
        });
        if (k < 0) reverse(spans.begin(), spans.end());
        for (auto [b, a, c, whole, start] : spans) {
            if (whole) {
                int cnt = (hi ? b->below(*hi, hiStrict) : b->size()) - (lo ? b->below(*lo, !loStrict) : 0);
                if (max(k, 1) > cnt) {
                    k -= cnt;
                    continue;
                }
            }
            for (int p = 0; p <= c - a; p++) {
                int pos = k < 0 ? c - p : a + p;
                if (passes(b->get(pos), lo, hi, loStrict, hiStrict)) {
                    if (k == 1 || k == -1) return start + pos;
                    k > 0 ? k-- : k++;
                }
            }
        }
        return -1;
    }
};
'''

CPP_POINT = '''
    // O(sqrt(N log N)) -- {doc}
    void {op}(int i, T v) {
        auto [j, k] = at(i);
        Block& b = blocks[j];
        T nv = {expr};
        b.update(k, k, [&](T) { return nv; });
    }
'''

CPP_RANGE = '''
    // O(sqrt(N log N)) -- {doc} for i in [l, r]
    void {op}(int l, int r, T v) {
        int i = 0;
        for (Block& b : blocks) {
            int m = b.size();
            if (i + m > l) {
                int lo = max(l - i, 0), hi = min(r - i, m - 1);
                if (lo == 0 && hi == m - 1) b.{full};
                else b.update(lo, hi, [&](T x) { return {asn}; });
                if (i + m > r) return;
            }
            i += m;
        }
    }
'''


def cpp_fam(f):
    out = []
    if f["S"]:
        out.append('''
    // O(sqrt(N) log N) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) const { return sum(l, r, nullopt, nullopt, false, false); }

    // O(sqrt(N) log N) -- sum of the values < x in a[l..r]
    S sumLtX(int l, int r, T x) const { return sum(l, r, nullopt, x, false, true); }

    // O(sqrt(N) log N) -- sum of the values <= x in a[l..r]
    S sumLteX(int l, int r, T x) const { return sum(l, r, nullopt, x, false, false); }

    // O(sqrt(N) log N) -- sum of the values > x in a[l..r]
    S sumGtX(int l, int r, T x) const { return sum(l, r, x, nullopt, true, false); }

    // O(sqrt(N) log N) -- sum of the values >= x in a[l..r]
    S sumGteX(int l, int r, T x) const { return sum(l, r, x, nullopt, false, false); }

    // O(sqrt(N) log N) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal
    S sumInValRange(int l, int r, T lowVal, T highVal) const {
        return lowVal <= highVal ? sum(l, r, lowVal, highVal, false, false) : S(0);
    }

    // O(sqrt(N) log N log U) -- sum of the k smallest values in a[l..r]; needs 0 <= k <= r - l + 1, else throws
    // out_of_range
    S sumSmallestK(int l, int r, int k) const {
        if (k < 0 || k > r - l + 1) throw out_of_range("sumSmallestK: needs 0 <= k <= r - l + 1");
        return sumFirst(l, r, k);
    }

    // O(sqrt(N) log N log U) -- sum of the k largest values in a[l..r]; needs 0 <= k <= r - l + 1, else throws
    // out_of_range
    S sumLargestK(int l, int r, int k) const {
        if (k < 0 || k > r - l + 1) throw out_of_range("sumLargestK: needs 0 <= k <= r - l + 1");
        return rangeSum(l, r) - sumFirst(l, r, r - l + 1 - k);
    }

    // O(sqrt(N) log N log U) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs
    // 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    S sumKthSmallestRange(int l, int r, int kFrom, int kTo) const {
        if (kFrom < 1 || kFrom > kTo || kTo > r - l + 1) throw out_of_range("sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, kTo) - sumFirst(l, r, kFrom - 1);
    }

    // O(sqrt(N) log N log U) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) =
    // the 3 biggest); needs 1 <= kFrom <= kTo <= r - l + 1, else throws out_of_range
    S sumKthLargestRange(int l, int r, int kFrom, int kTo) const {
        int n = r - l + 1;
        if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range("sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1");
        return sumFirst(l, r, n - kFrom + 1) - sumFirst(l, r, n - kTo);
    }

    // O(sqrt(N) log N) -- sum of |a[i] - x| over i in [l, r]
    S sumAbsDiffToX(int l, int r, T x) const {
        S c = count(l, r, nullopt, x, false, true), s = sum(l, r, nullopt, x, false, true);
        return c * S(x) - s + rangeSum(l, r) - s - (S(r - l + 1) - c) * S(x);
    }

    S sum(int l, int r, optional<T> lo, optional<T> hi, bool loStrict, bool hiStrict) const {
        S res = 0;
        select(l, r, lo, hi, loStrict, hiStrict, [&](const Block& b, int i, int j) { res += b.sumFirst(j) - b.sumFirst(i); },
               [&](T v) { res += S(v); });
        return res;
    }

    S sumFirst(int l, int r, int k) const {  // the sum of the k smallest values of a[l..r]
        if (k == 0) return S(0);
        T v = kthSmallest(l, r, k);  // (the k-th smallest: the values below it, then copies of it)
        return sum(l, r, nullopt, v, false, true) + S(k - count(l, r, nullopt, v, false, true)) * S(v);
    }
''')
    for fam, letter, op, ident in (("xor", "X", "^", "T(0)"), ("and", "N", "&", "~T(0)"), ("or", "O", "|", "T(0)")):
        if not f[letter]:
            continue
        full = "b.xorFirst(j) ^ b.xorFirst(i)" if fam == "xor" else f"b.{fam}Range(i, j)"
        what = {"xor": "xor", "and": "AND", "or": "OR"}[fam]
        none = {"xor": "0 if there are none", "and": "~0 (every bit) if there are none", "or": "0 if there are none"}[fam]
        cop = " (copies count)" if fam == "xor" else ""
        Q = {"xor": "rangeXorQuery", "and": "rangeAndQuery", "or": "rangeOrQuery"}[fam]
        F = fam + "Of"
        out.append(f'''
    // O(sqrt(N) log N) -- a[l] {op} ... {op} a[r]
    T {Q}(int l, int r) const {{ return {F}(l, r, nullopt, nullopt, false, false); }}

    // O(sqrt(N) log N) -- {what} of the values < x in a[l..r]{cop}; {none}
    T {fam}LtX(int l, int r, T x) const {{ return {F}(l, r, nullopt, x, false, true); }}

    // O(sqrt(N) log N) -- {what} of the values <= x in a[l..r]{cop}; {none}
    T {fam}LteX(int l, int r, T x) const {{ return {F}(l, r, nullopt, x, false, false); }}

    // O(sqrt(N) log N) -- {what} of the values > x in a[l..r]{cop}; {none}
    T {fam}GtX(int l, int r, T x) const {{ return {F}(l, r, x, nullopt, true, false); }}

    // O(sqrt(N) log N) -- {what} of the values >= x in a[l..r]{cop}; {none}
    T {fam}GteX(int l, int r, T x) const {{ return {F}(l, r, x, nullopt, false, false); }}

    // O(sqrt(N) log N) -- {what} of the a[i] in [l, r] with lowVal <= a[i] <= highVal{cop}; {none}
    T {fam}InValRange(int l, int r, T lowVal, T highVal) const {{
        return lowVal <= highVal ? {F}(l, r, lowVal, highVal, false, false) : {ident};
    }}

    T {F}(int l, int r, optional<T> lo, optional<T> hi, bool loStrict, bool hiStrict) const {{
        T res = {ident};
        select(l, r, lo, hi, loStrict, hiStrict, [&](const Block& b, int i, int j) {{ res {op}= {full}; }}, [&](T v) {{ res {op}= v; }});
        return res;
    }}
''')
    return "".join(out)


def cpp(fams, ups, rev):
    f = flags(fams, ups, rev)
    add, kadd = (" + add", " + S(k) * S(add)") if f["A"] else ("", "")
    point = "".join(CPP_POINT.replace("{op}", op).replace("{doc}", doc).replace("{expr}", expr)
                    for op, doc, expr in (("pointAssign", "a[i] = v", "v"), ("pointAdd", "a[i] += v", "T(b.get(k) + v)"),
                                          ("pointChmax", "a[i] = max(a[i], v)", "max(b.get(k), v)"),
                                          ("pointChmin", "a[i] = min(a[i], v)", "min(b.get(k), v)")))
    rng = ""
    if f["A"]:
        rng += CPP_RANGE.replace("{op}", "rangeAdd").replace("{doc}", "a[i] += v").replace("b.{full}", "b.add += v").replace("{asn}", "T(x + v)")
    if f["G"]:
        rng += CPP_RANGE.replace("{op}", "rangeAssign").replace("{doc}", "a[i] = v").replace(
            "b.{full}", "b.has = true, b.asg = v" + (", b.add = T(0)" if f["A"] else "")).replace("{asn}", "(void)x, v")
    pend = " || ".join(x for x, k in (("has", "G"), ("rev", "R"), ("add != T(0)", "A")) if f[k])
    body = CPP_HEAD.replace("{PEND}", pend).replace("{ADD}", add).replace("{KADD}", kadd).replace("{POINT}", point).replace("{RANGE_UPD}", rng).replace("{FAM_PUB}", cpp_fam(f))
    return (header("//", fams, ups, rev) + "\n" + wrap(describe(fams, ups, rev), "//") +
            "// T: int, long long, ..." + ("; sums are kept in S (long long for small T)." if f["S"] else "") + "\n" + pick(body, f))


def folder_of(fams, ups, rev):
    name = folder_name(ops_of(fams, ups, rev))
    return name if len(name) <= 180 else "sqrt-seq-" + ("-".join(fams) or "plain") + ("-" + "-".join(ups) if ups else "") + ("-rev" if rev else "")


def main():
    for d in os.listdir(DIR):
        t = os.path.join(DIR, d, "template.py")
        if os.path.exists(t) and MARK in " ".join(open(t).read().replace("#", " ").split()):
            shutil.rmtree(os.path.join(DIR, d))
    seen = set()
    for fams, ups, rev in variants():
        folder = folder_of(fams, ups, rev)
        assert folder not in seen, folder
        seen.add(folder)
        os.makedirs(os.path.join(DIR, folder), exist_ok=True)
        write_template(os.path.join(DIR, folder, "template.py"), py(fams, ups, rev))
        write_template(os.path.join(DIR, folder, "template.cpp"), cpp(fams, ups, rev))
    print("wrote", len(seen), "sqrt sequences")


if __name__ == "__main__":
    main()
