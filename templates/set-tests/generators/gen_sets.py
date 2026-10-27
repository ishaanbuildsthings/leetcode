"""Generate the ordered-multiset templates: templates/sets/<folder>/template.{py,cpp}.

    python3 gen_sets.py

A multiset of integers with add / remove and order queries (k-th, rank counts, neighbors, sums by value or by
rank, median, mex, ...). Every structure implements the same small core:
    _insert(x, c)     add c copies of x (c < 0 removes; the caller never removes more copies than exist)
    _lt(x), _le(x)    how many values are < x / <= x
    _kth(k)           the k-th smallest value, 1 <= k <= size
    _kthInfo(k)       (k-th smallest, copies before it, its copies, sum before it in sum versions), one search
    _countOf(x)       copies of x
    _slt, _sle        (sum versions) sums of the values < x / <= x
    _findMex()        (where supported) the mex, searched from scratch
and the public operations are written once on top of that core (shared by every structure), so they behave the
same everywhere and the brute-force tester checks them all the same way. _add / addRaw keep min and max current,
and both medians (as tracked ranks) and mex once they're first asked for, so those queries are O(1) (amortized for
the tracked ones).

Structures (each in a count-only version and a count + sum version, unless noted):
    fenwick      offline: Fenwick trees over the compressed values you pass in up front   log N
    avl          online: AVL tree on a node pool (subtree counts / sums), freed nodes reused   log N worst case
    blocks       online: sorted blocks of distinct keys with per-block counts / sums + Fenwick over blocks   sqrt N
    blocks-fenwick   online: the same blocks with a Fenwick tree inside each block: queries log N, updates sqrt N
    value-tree   online, values in [lo, hi]: a dynamic value tree (C++: shared node pool; Python: dict)   log U
    treap        online: treap on a node pool, freed nodes reused   log N expected
    splay        online: splay tree on a node pool, freed nodes reused   log N amortized
    pbds         online, C++ only, count-only: GCC order-statistics tree, one node per copy   log N
(value-tree, treap, splay and pbds lose to AVL on paper; they stay as options: check_sets.py reports them as kept.)
"""
import os
import re

ROOT = os.environ.get("SETS_DIR") or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sets")
GITHUB_USER = "https://github.com/ishaanbuildsthings"
GITHUB_FILES = GITHUB_USER + "/leetcode/blob/main/templates/sets/"

# op -> (argument kind, result kind, description). Result kinds: none / int / opt (None in Python, nullopt in C++).
OPS = {
    "add": ("x", "none", "add one copy of x"),
    "addCount": ("vc", "none", "add cnt copies of val (nothing if cnt <= 0)"),
    "remove": ("x", "int", "remove one copy of x if present; returns how many were removed (0 or 1)"),
    "removeCount": ("vc", "int", "remove min(cnt, count(val)) copies of val; returns how many were removed"),
    "removeAll": ("v", "int", "remove every copy of val; returns how many were removed"),
    "removeInValRange": ("lohi", "int", "remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)"),
    "clear": ("", "none", "remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one"),
    "popMin": ("", "opt", "remove and return the smallest value; {none} if empty"),
    "popMax": ("", "opt", "remove and return the largest value; {none} if empty"),
    "pop": ("i", "int", "remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); {err} unless 0 <= i < size"),
    "size": ("", "int", "how many values (copies count)"),
    "count": ("x", "int", "how many copies of x"),
    "sumAll": ("", "int", "sum of all values"),
    "countDistinct": ("", "int", "how many distinct values"),
    "minAdjacentDiff": ("", "opt", "smallest difference between two values in the set (0 if some value has 2+ copies); {none} if fewer than 2 values"),
    "maxGap": ("", "opt", "largest difference between two neighbouring distinct values; {none} if fewer than 2 distinct values"),
    "maxXorAgainstX": ("xv", "opt", "largest v ^ x over the values v in the set; {none} if the set is empty (needs 0 <= x < 2^bits)"),
    "minXorAgainstX": ("xv", "opt", "smallest v ^ x over the values v in the set; {none} if the set is empty (needs 0 <= x < 2^bits)"),
    "kthXor": ("xi", "int", "the i-th smallest v ^ x over the values v (0-indexed, copies count); {err} unless 0 <= i < size"),
    "countXorLtK": ("xk", "int", "how many values v have v ^ x < k"),
    "countXorLteK": ("xk", "int", "how many values v have v ^ x <= k"),
    "countXorGtK": ("xk", "int", "how many values v have v ^ x > k"),
    "countXorGteK": ("xk", "int", "how many values v have v ^ x >= k"),
    "largestXorLtK": ("xk", "opt", "largest v ^ x that is < k; {none} if there is none"),
    "largestXorLteK": ("xk", "opt", "largest v ^ x that is <= k; {none} if there is none"),
    "smallestXorGtK": ("xk", "opt", "smallest v ^ x that is > k; {none} if there is none"),
    "smallestXorGteK": ("xk", "opt", "smallest v ^ x that is >= k; {none} if there is none"),
    "mexXor": ("xv", "int", "smallest non-negative integer that is not v ^ x for any value v"),
    "sumXor": ("xv", "int", "sum of v ^ x over every value v (copies count)"),
    "maxXorWithVLtM": ("xm", "opt", "largest v ^ x over the values v < m; {none} if there is none"),
    "maxXorWithVLteM": ("xm", "opt", "largest v ^ x over the values v <= m; {none} if there is none"),
    "maxXorWithVGtM": ("xm", "opt", "largest v ^ x over the values v > m; {none} if there is none"),
    "maxXorWithVGteM": ("xm", "opt", "largest v ^ x over the values v >= m; {none} if there is none"),
    "minXorWithVLtM": ("xm", "opt", "smallest v ^ x over the values v < m; {none} if there is none"),
    "minXorWithVLteM": ("xm", "opt", "smallest v ^ x over the values v <= m; {none} if there is none"),
    "minXorWithVGtM": ("xm", "opt", "smallest v ^ x over the values v > m; {none} if there is none"),
    "minXorWithVGteM": ("xm", "opt", "smallest v ^ x over the values v >= m; {none} if there is none"),
    "maxXorWithVInValRange": ("xlohi", "opt", "largest v ^ x over the values v with lo <= v <= hi; {none} if there is none"),
    "minXorWithVInValRange": ("xlohi", "opt", "smallest v ^ x over the values v with lo <= v <= hi; {none} if there is none"),
    "xorAll": ("y", "none", "replace every value v by v ^ y (needs 0 <= y < 2^bits)"),
    "shiftAll": ("d", "none", "add d to every value (d may be negative)"),
    "mode": ("", "pair", "(a most frequent value, its count); {none} if empty. C++ returns the smallest of the most frequent values"),
    "min": ("", "opt", "smallest value; {none} if empty"),
    "max": ("", "opt", "largest value; {none} if empty"),
    "medianLow": ("", "opt", "lower median: the ceil(size/2)-th smallest value; {none} if empty"),
    "medianHigh": ("", "opt", "upper median: the (floor(size/2) + 1)-th smallest value; {none} if empty"),
    "mex": ("", "int", "smallest non-negative integer not in the set"),
    "sumAbsDiffToMedian": ("", "int", "sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty"),
    "kth": ("i", "int", "the value at sorted position i (0-indexed: kth(0) is the min); {err} unless 0 <= i < size"),
    "sumSmallestK": ("k", "int", "sum of the k smallest values; {err} unless 0 <= k <= size"),
    "sumLargestK": ("k", "int", "sum of the k largest values; {err} unless 0 <= k <= size"),
    "sumKthSmallestRange": ("kk", "int", "sum of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); {err} unless 1 <= kFrom <= kTo <= size"),
    "sumKthLargestRange": ("kk", "int", "sum of the kFrom-th..kTo-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); {err} unless 1 <= kFrom <= kTo <= size"),
    "largestLtX": ("x", "opt", "largest value < x; {none} if there is none"),
    "largestLteX": ("x", "opt", "largest value <= x; {none} if there is none"),
    "smallestGtX": ("x", "opt", "smallest value > x; {none} if there is none"),
    "smallestGteX": ("x", "opt", "smallest value >= x; {none} if there is none"),
    "countLtX": ("x", "int", "how many values < x"),
    "firstIndex": ("x", "int", "0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set"),
    "lastIndex": ("x", "int", "0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set"),
    "countLteX": ("x", "int", "how many values <= x"),
    "countGtX": ("x", "int", "how many values > x"),
    "countGteX": ("x", "int", "how many values >= x"),
    "countInValRange": ("lohi", "int", "how many values v with lo <= v <= hi (0 if lo > hi)"),
    "countDistinctInValRange": ("lohi", "int", "how many distinct values v with lo <= v <= hi (0 if lo > hi)"),
    "sumLtX": ("x", "int", "sum of the values < x"),
    "sumLteX": ("x", "int", "sum of the values <= x"),
    "sumGtX": ("x", "int", "sum of the values > x"),
    "sumGteX": ("x", "int", "sum of the values >= x"),
    "sumInValRange": ("lohi", "int", "sum of the values v with lo <= v <= hi (0 if lo > hi)"),
    "sumAbsDiffToX": ("x", "int", "sum of |v - x| over all values"),
    "xorOfAll": ("", "int", "xor of all values (copies count: a value with an even count cancels out); 0 if empty"),
    "xorOfLtX": ("x", "int", "xor of the values < x (copies count)"),
    "xorOfLteX": ("x", "int", "xor of the values <= x (copies count)"),
    "xorOfGtX": ("x", "int", "xor of the values > x (copies count)"),
    "xorOfGteX": ("x", "int", "xor of the values >= x (copies count)"),
    "xorOfInValRange": ("lohi", "int", "xor of the values v with lo <= v <= hi (copies count; 0 if lo > hi)"),
    "xorOfSmallestK": ("k", "int", "xor of the k smallest values (copies count); {err} unless 0 <= k <= size"),
    "xorOfLargestK": ("k", "int", "xor of the k largest values (copies count); {err} unless 0 <= k <= size"),
    "xorOfKthSmallestRange": ("kk", "int", "xor of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); {err} unless 1 <= kFrom <= kTo <= size"),
    "xorOfKthLargestRange": ("kk", "int", "xor of the kFrom-th..kTo-th largest values (1-indexed, inclusive); {err} unless 1 <= kFrom <= kTo <= size"),
    "orOfAll": ("", "int", "bitwise OR of all values; 0 if empty"),
    "orOfLtX": ("x", "int", "bitwise OR of the values < x; 0 if there are none"),
    "orOfLteX": ("x", "int", "bitwise OR of the values <= x; 0 if there are none"),
    "orOfGtX": ("x", "int", "bitwise OR of the values > x; 0 if there are none"),
    "orOfGteX": ("x", "int", "bitwise OR of the values >= x; 0 if there are none"),
    "orOfInValRange": ("lohi", "int", "bitwise OR of the values v with lo <= v <= hi; 0 if there are none"),
    "orOfSmallestK": ("k", "int", "bitwise OR of the k smallest values (0 for k = 0); {err} unless 0 <= k <= size"),
    "orOfLargestK": ("k", "int", "bitwise OR of the k largest values (0 for k = 0); {err} unless 0 <= k <= size"),
    "orOfKthSmallestRange": ("kk", "int", "bitwise OR of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); {err} unless 1 <= kFrom <= kTo <= size"),
    "orOfKthLargestRange": ("kk", "int", "bitwise OR of the kFrom-th..kTo-th largest values (1-indexed, inclusive); {err} unless 1 <= kFrom <= kTo <= size"),
    "andOfAll": ("", "int", "bitwise AND of all values; -1 (every bit set) if empty"),
    "andOfLtX": ("x", "int", "bitwise AND of the values < x; -1 (every bit set) if there are none"),
    "andOfLteX": ("x", "int", "bitwise AND of the values <= x; -1 (every bit set) if there are none"),
    "andOfGtX": ("x", "int", "bitwise AND of the values > x; -1 (every bit set) if there are none"),
    "andOfGteX": ("x", "int", "bitwise AND of the values >= x; -1 (every bit set) if there are none"),
    "andOfInValRange": ("lohi", "int", "bitwise AND of the values v with lo <= v <= hi; -1 (every bit set) if there are none"),
    "andOfSmallestK": ("k", "int", "bitwise AND of the k smallest values (-1 (every bit set) for k = 0); {err} unless 0 <= k <= size"),
    "andOfLargestK": ("k", "int", "bitwise AND of the k largest values (-1 (every bit set) for k = 0); {err} unless 0 <= k <= size"),
    "andOfKthSmallestRange": ("kk", "int", "bitwise AND of the kFrom-th..kTo-th smallest values (1-indexed, inclusive); {err} unless 1 <= kFrom <= kTo <= size"),
    "andOfKthLargestRange": ("kk", "int", "bitwise AND of the kFrom-th..kTo-th largest values (1-indexed, inclusive); {err} unless 1 <= kFrom <= kTo <= size"),
}
SUM_OPS = {"sumAll", "sumAbsDiffToMedian", "sumSmallestK", "sumLargestK", "sumKthSmallestRange", "sumKthLargestRange",
           "sumLtX", "sumLteX", "sumGtX", "sumGteX", "sumInValRange", "sumAbsDiffToX"}
COUNT_OPS = [op for op in OPS if op not in SUM_OPS]
# the bitwise aggregates: xor (a group, so prefix differences work like sums) and OR / AND (no inverse: range walks)
AGG_SUFFIXES = ["All", "LtX", "LteX", "GtX", "GteX", "InValRange", "SmallestK", "LargestK", "KthSmallestRange", "KthLargestRange"]
AGG_OPS = {kind: [kind + "Of" + suf for suf in AGG_SUFFIXES] for kind in ("xor", "or", "and")}
TRIE_GROUP2 = ["maxXorWithVLtM", "maxXorWithVLteM", "maxXorWithVGtM", "maxXorWithVGteM", "minXorWithVLtM", "minXorWithVLteM",
               "minXorWithVGtM", "minXorWithVGteM", "maxXorWithVInValRange", "minXorWithVInValRange"]
TRIE_OPS = {"maxXorAgainstX", "minXorAgainstX", "kthXor", "countXorLtK", "countXorLteK", "countXorGtK", "countXorGteK", "largestXorLtK",
            "largestXorLteK", "smallestXorGtK", "smallestXorGteK", "mexXor", "sumXor", "xorAll", *TRIE_GROUP2}
ARGS = {"d": ["d"], "xv": ["x"], "xi": ["x", "i"], "xk": ["x", "k"], "xm": ["x", "m"], "xlohi": ["x", "lo", "hi"], "y": ["y"], "i": ["i"], "x": ["x"], "xc": ["x", "c"], "v": ["val"], "vc": ["val", "cnt"], "k": ["k"], "kk": ["kFrom", "kTo"], "lohi": ["lo", "hi"], "": []}

# ================================================================================================ shared ops

# Python bodies of the public ops, on top of the core (self.n = size, self.total = sum).
PY_OPS = {
    "add": "self._add(x, 1)",
    "addCount": "if cnt > 0:\n    self._add(val, cnt)",
    "remove": "if not self.count(x):\n    return 0\nself._add(x, -1)\nreturn 1",
    "removeCount": "k = min(cnt, self.count(val))\nif k <= 0:\n    return 0\nself._add(val, -k)\nreturn k",
    "removeAll": "k = self.count(val)\nif k:\n    self._add(val, -k)\nreturn k",
    "countDistinctInValRange": "if lo > hi:\n    return 0\nreturn self._distinctLt(hi) - self._distinctLt(lo) + (1 if self._countOf(hi) else 0)",
    "removeInValRange": "if lo > hi:\n    return 0\nremoved = 0\nwhile self.n:  # the smallest value >= lo, while it is <= hi: drop all its copies\n    c = self._lt(lo)\n    if c == self.n:\n        break\n    v = self._kth(c + 1)\n    if v > hi:\n        break\n    k = self._countOf(v)\n    self._add(v, -k)\n    removed += k\nreturn removed",
    "clear": "self._clearData()\nself._resetCached()",
    "popMin": "if not self.n:\n    return None\nv = self.mn if self.mm else self._kth(1)\nself._add(v, -1)\nreturn v",
    "popMax": "if not self.n:\n    return None\nv = self.mx if self.mm else self._kth(self.n)\nself._add(v, -1)\nreturn v",
    "size": "return self.n",
    "count": "return self._countOf(x)",
    "sumAll": "return self.total",
    "countDistinct": "return self.d",
    "min": "if not self.n:\n    return None\nif not self.mm:\n    self._startMinMax()\nreturn self.mn",
    "max": "if not self.n:\n    return None\nif not self.mm:\n    self._startMinMax()\nreturn self.mx",
    "medianLow": "if not self.n:\n    return None\nif not self.med:\n    self._startMedians()\nreturn self.lowV",
    "medianHigh": "if not self.n:\n    return None\nif not self.med:\n    self._startMedians()\nreturn self.highV",
    "mex": "if self.mexV < 0:  # the first call: from now on _add keeps it current\n    self.mexV = self._findMex()\nreturn self.mexV",
    "sumAbsDiffToMedian": "if not self.n:\n    return 0\nif not self.med:\n    self._startMedians()\nv, b, c, s = self.lowV, self.lowB, self.lowC, self.lowS\nreturn v * b - s + (self.total - s - c * v) - v * (self.n - b - c)",
    "pop": "if not 0 <= i < self.n:\n    raise IndexError(f\"pop: needs 0 <= i < size, got i = {i}, size = {self.n}\")\nv = self._kth(i + 1)\nself._add(v, -1)\nreturn v",
    "kth": "if not 0 <= i < self.n:\n    raise IndexError(f\"kth: needs 0 <= i < size, got i = {i}, size = {self.n}\")\nreturn self._kth(i + 1)",
    "sumSmallestK": "if not 0 <= k <= self.n:\n    raise IndexError(f\"sumSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}\")\nreturn self._sumFirst(k)",
    "sumLargestK": "if not 0 <= k <= self.n:\n    raise IndexError(f\"sumLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}\")\nreturn self.total - self._sumFirst(self.n - k)",
    "sumKthSmallestRange": "if not 1 <= kFrom <= kTo <= self.n:\n    raise IndexError(f\"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}\")\nreturn self._sumFirst(kTo) - self._sumFirst(kFrom - 1)",
    "sumKthLargestRange": "if not 1 <= kFrom <= kTo <= self.n:\n    raise IndexError(f\"sumKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}\")\nreturn self._sumFirst(self.n - kFrom + 1) - self._sumFirst(self.n - kTo)",
    "largestLtX": "c = self._lt(x)\nreturn self._kth(c) if c else None",
    "largestLteX": "c = self._le(x)\nreturn self._kth(c) if c else None",
    "smallestGtX": "c = self._le(x)\nreturn self._kth(c + 1) if c < self.n else None",
    "smallestGteX": "c = self._lt(x)\nreturn self._kth(c + 1) if c < self.n else None",
    "countLtX": "return self._lt(x)",
    "firstIndex": "return self._lt(x) if self._countOf(x) else -1",
    "lastIndex": "return self._le(x) - 1 if self._countOf(x) else -1",
    "countLteX": "return self._le(x)",
    "countGtX": "return self.n - self._le(x)",
    "countGteX": "return self.n - self._lt(x)",
    "countInValRange": "return self._le(hi) - self._lt(lo) if lo <= hi else 0",
    "sumLtX": "return self._slt(x)",
    "sumLteX": "return self._sle(x)",
    "sumGtX": "return self.total - self._sle(x)",
    "sumGteX": "return self.total - self._slt(x)",
    "sumInValRange": "return self._sle(hi) - self._slt(lo) if lo <= hi else 0",
    "sumAbsDiffToX": "c, s = self._lt(x), self._slt(x)\nreturn x * c - s + (self.total - s) - x * (self.n - c)",
}

# C++ bodies (members n, total; T values, S sums).
CPP_OPS = {
    "add": ("void", "addRaw(x, 1);"),
    "addCount": ("void", "if (cnt > 0) addRaw(val, cnt);"),
    "remove": ("long long", "if (!count(x)) return 0;\naddRaw(x, -1);\nreturn 1;"),
    "removeCount": ("long long", "long long k = std::min(cnt, count(val));\nif (k <= 0) return 0;\naddRaw(val, -k);\nreturn k;"),
    "removeAll": ("long long", "long long k = count(val);\nif (k) addRaw(val, -k);\nreturn k;"),
    "countDistinctInValRange": ("long long", "if (hi < lo) return 0;\nreturn distinctLt(hi) - distinctLt(lo) + (countOf(hi) ? 1 : 0);"),
    "removeInValRange": ("long long", "if (hi < lo) return 0;\nlong long removed = 0;\nwhile (n) {  // the smallest value >= lo, while it is <= hi: drop all its copies\n    long long c = lt(lo);\n    if (c == n) break;\n    T v = kthAt(c + 1);\n    if (hi < v) break;\n    long long k = countOf(v);\n    addRaw(v, -k), removed += k;\n}\nreturn removed;"),
    "clear": ("void", "clearData();\nresetCached();"),
    "popMin": ("optional<T>", "if (!n) return nullopt;\nT v = mm ? mn : kthAt(1);\naddRaw(v, -1);\nreturn v;"),
    "popMax": ("optional<T>", "if (!n) return nullopt;\nT v = mm ? mx : kthAt(n);\naddRaw(v, -1);\nreturn v;"),
    "size": ("long long", "return n;"),
    "count": ("long long", "return countOf(x);"),
    "sumAll": ("S", "return total;"),
    "countDistinct": ("long long", "return d;"),
    "min": ("optional<T>", "if (!n) return nullopt;\nif (!mm) startMinMax();\nreturn mn;"),
    "max": ("optional<T>", "if (!n) return nullopt;\nif (!mm) startMinMax();\nreturn mx;"),
    "medianLow": ("optional<T>", "if (!n) return nullopt;\nif (!med) startMedians();\nreturn low.v;"),
    "medianHigh": ("optional<T>", "if (!n) return nullopt;\nif (!med) startMedians();\nreturn high.v;"),
    "mex": ("long long", "if (mexV < 0) mexV = findMex();  // the first call: from now on addRaw keeps it current\nreturn mexV;"),
    "sumAbsDiffToMedian": ("S", "if (!n) return 0;\nif (!med) startMedians();\nconst Info& m = low;\nreturn S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);"),
    "pop": ("T", "if (i < 0 || i >= n) throw out_of_range(\"pop: needs 0 <= i < size\");\nT v = kthAt(i + 1);\naddRaw(v, -1);\nreturn v;"),
    "kth": ("T", "if (i < 0 || i >= n) throw out_of_range(\"kth: needs 0 <= i < size\");\nreturn kthAt(i + 1);"),
    "sumSmallestK": ("S", "if (k < 0 || k > n) throw out_of_range(\"sumSmallestK: needs 0 <= k <= size\");\nreturn sumFirst(k);"),
    "sumLargestK": ("S", "if (k < 0 || k > n) throw out_of_range(\"sumLargestK: needs 0 <= k <= size\");\nreturn total - sumFirst(n - k);"),
    "sumKthSmallestRange": ("S", "if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range(\"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= size\");\nreturn sumFirst(kTo) - sumFirst(kFrom - 1);"),
    "sumKthLargestRange": ("S", "if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range(\"sumKthLargestRange: needs 1 <= kFrom <= kTo <= size\");\nreturn sumFirst(n - kFrom + 1) - sumFirst(n - kTo);"),
    "largestLtX": ("optional<T>", "long long c = lt(x);\nif (!c) return nullopt;\nreturn kthAt(c);"),
    "largestLteX": ("optional<T>", "long long c = le(x);\nif (!c) return nullopt;\nreturn kthAt(c);"),
    "smallestGtX": ("optional<T>", "long long c = le(x);\nif (c == n) return nullopt;\nreturn kthAt(c + 1);"),
    "smallestGteX": ("optional<T>", "long long c = lt(x);\nif (c == n) return nullopt;\nreturn kthAt(c + 1);"),
    "countLtX": ("long long", "return lt(x);"),
    "firstIndex": ("long long", "return countOf(x) ? lt(x) : -1;"),
    "lastIndex": ("long long", "return countOf(x) ? le(x) - 1 : -1;"),
    "countLteX": ("long long", "return le(x);"),
    "countGtX": ("long long", "return n - le(x);"),
    "countGteX": ("long long", "return n - lt(x);"),
    "countInValRange": ("long long", "return lo <= hi ? le(hi) - lt(lo) : 0;"),
    "sumLtX": ("S", "return slt(x);"),
    "sumLteX": ("S", "return sle(x);"),
    "sumGtX": ("S", "return total - sle(x);"),
    "sumGteX": ("S", "return total - slt(x);"),
    "sumInValRange": ("S", "return lo <= hi ? sle(hi) - slt(lo) : S(0);"),
    "sumAbsDiffToX": ("S", "long long c = lt(x);\nS s = slt(x);\nreturn S(x) * c - s + (total - s) - S(x) * (n - c);"),
}
CPP_PARAMS = {"d": "T d", "xv": "T x", "xi": "T x, long long i", "xk": "T x, long long k", "xm": "T x, long long m",
              "xlohi": "T x, long long lo, long long hi", "y": "T y", "i": "long long i", "x": "T x", "xc": "T x, long long c", "v": "T val", "vc": "T val, long long cnt", "k": "long long k", "kk": "long long kFrom, long long kTo", "lohi": "T lo, T hi", "": ""}


def cost_text(c):
    """'log(N)' -> 'logN', 'log^2(N) expected' -> 'log^2 N expected', for code comments."""
    c = c.replace("log^2(N)", "log^2 N").replace("log(N)", "logN").replace("log(U)", "logU").replace("sqrt(N)", "sqrtN")
    return c.replace("*", " ")


def py_ops(ops, comps, own=None):
    out = []
    for op in ops:
        args = ARGS[OPS[op][0]]
        doc = OPS[op][2].format(none="None", err="raises IndexError")
        body = "\n".join("        " + line for line in ((own or {}).get(op) or PY_OPS[op]).split("\n"))
        out.append(f"    # O({cost_text(comps[op])}) -- {doc}\n    def {op}(self{''.join(', ' + a for a in args)}):\n{body}\n")
        if op == "size":  # so len(ms) works too, like a SortedList
            out.append("    # O(1) -- same as size()\n    def __len__(self):\n        return self.n\n")
    return "\n".join(out)


def cpp_ops(ops, comps, own=None):
    out = []
    for op in ops:
        ret, body = (own or {}).get(op) or CPP_OPS[op]
        doc = OPS[op][2].format(none="nullopt", err="throws out_of_range")
        body = "\n".join("        " + line for line in body.split("\n"))
        out.append(f"    // O({cost_text(comps[op])}) -- {doc}\n    {ret} {op}({CPP_PARAMS[OPS[op][0]]}) {{\n{body}\n    }}\n")
    return "\n".join(out)


def needs_count(mexc, minmax, mode, gaps):
    """Whether _add / addRaw needs x's new count (which every insert returns): the mex, min / max, mode and gaps
    caches react to x appearing or disappearing; nothing else does."""
    return mexc or minmax or mode or gaps


def py_add(sums, mexc, minmax, medians, mode=False, gaps=False, xor=False, shift=False):
    """_add: every update goes through here. It keeps current exactly what this variant caches (min / max, both
    medians, the mex) and nothing else: no flags, no lazy starts. A variant without a cache answers that query with a
    walk instead, and its updates do none of this work."""
    S = sums
    kept = (["min / max"] if minmax else []) + (["both medians"] if medians else []) + (["the mex"] if mexc else [])
    out = ["", "    def _add(self, x, c):  # c copies of x (c < 0 removes)" + ("; keeps " + ", ".join(kept) + " current" if kept else ""),
           "        self.n += c"] + (["        self.total += c * x"] if S else []) + (
           ["        if c & 1:  # an odd number of copies flips x in or out of the xor of everything", "            self.xtotal ^= x"] if xor else []) + [
           "        f = self._insert(x, c)  # x's new count" if needs_count(mexc, minmax, mode, gaps) else "        self._insert(x, c)"]
    if mode or gaps:
        out += ["        g = f - c  # x's old count"]
    if mode:  # move x from the bucket of its old count to its new one
        out += ["        # mode: x moves from the bucket of its old count to its new one",
                "        bk = self.bk", "        if g:", "            vs = bk[g]", "            vs.discard(x)", "            if not vs:",
                "                del bk[g]", "        if f:", "            if f in bk:", "                bk[f].add(x)", "            else:",
                "                bk[f] = {x}", "            if f > self.maxF:", "                self.maxF = f",
                "        while self.maxF and self.maxF not in bk:  # (it only drops as far as copies were removed: amortized O(1))",
                "            self.maxF -= 1"]
    if gaps:  # x's count went g -> f: duplicates, and the gaps around x when it appears or disappears
        out += [
            "        if (g >= 2) != (f >= 2):  # values with 2+ copies (then the smallest difference is 0)",
            "            self.dups += 1 if f >= 2 else -1",
            "        if not g or not f:  # x appeared or disappeared: the gap between its neighbours splits or comes back",
            *(["            p, q = self.largestLtX(x), self.smallestGtX(x)"] if not shift else [
                "            i, j = self._lt(x), self._le(x)  # (stored values: the public ops would shift x again)",
                "            p, q = self._kth(i) if i else None, self._kth(j + 1) if j < self.n else None"]),
            "            if f:",
            "                if p is not None and q is not None:", "                    self._gap(q - p, -1)",
            "                if p is not None:", "                    self._gap(x - p, 1)",
            "                if q is not None:", "                    self._gap(q - x, 1)",
            "            else:",
            "                if p is not None:", "                    self._gap(x - p, -1)",
            "                if q is not None:", "                    self._gap(q - x, -1)",
            "                if p is not None and q is not None:", "                    self._gap(q - p, 1)"]
    if kept:
        out.append("        n = self.n")
        up = (["            if x == self.mexV:  # x filled the mex", "                self.mexV = self._findMex()"] if mexc else [])
        if minmax or medians:
            up += ["            if n == c:  # the set was empty"]
            up += ["                self.mn = self.mx = x"] if minmax else []
            up += ["                self.lowV = self.highV = x", "                self.lowB = self.highB = " + ("self.lowS = " if S else "") + "0",
                   "                self.lowC = self.highC = c"] if medians else []
            up += ["                return"]
            up += ["            if x < self.mn:", "                self.mn = x", "            if x > self.mx:", "                self.mx = x"] if minmax else []
        down = ([f"            if {'-self.off' if shift else '0'} <= x < self.mexV and not f:  # the last copy of a value below the mex",
                 "                self.mexV = x"] if mexc else [])
        if minmax or medians:
            down += ["            if not n:", "                return"]
            down += ["            if not f:  # x is gone: it may have been the min / max", "                if x == self.mn:", "                    self.mn = self._kth(1)",
                     "                if x == self.mx:", "                    self.mx = self._kth(n)"] if minmax else []
        out += ["        if c > 0:"] + (up or ["            pass"]) + ["        else:"] + (down or ["            pass"])
        if medians:
            out += ["        # each median is a tracked rank: shift its (value, copies before, copies" + (", sum before" if S else "") +
                    "), and search again only", "        # when the rank leaves the tracked value",
                    "        if x < self.lowV:", "            self.lowB += c"] + (["            self.lowS += c * x"] if S else []) + [
                    "        elif x == self.lowV:", "            self.lowC += c", "        r = (n + 1) >> 1",
                    "        if not self.lowB < r <= self.lowB + self.lowC:",
                    "            self.lowV, self.lowB, self.lowC" + (", self.lowS" if S else "") + " = self._kthInfo(r)",
                    "        if x < self.highV:", "            self.highB += c", "        elif x == self.highV:", "            self.highC += c",
                    "        r = (n >> 1) + 1", "        if not self.highB < r <= self.highB + self.highC:",
                    "            self.highV, self.highB, self.highC = self._kthInfo(r)" + ("[:3]" if S else "")]
    if gaps:
        out += ["", "    def _gap(self, g, c):  # one more (c = 1) / fewer (c = -1) gap of size g",
                "        gc = self.gc", "        k = gc.get(g, 0) + c", "        if k:", "            gc[g] = k",
                "            if k == 1 and c > 0:  # (a size already present has an entry in both heaps)",
                "                if len(self.gmin) > 2 * len(gc) + 8:  # mostly sizes no longer present: rebuild from the live ones",
                "                    self.gmin = sorted(gc)", "                    self.gmax = [-v for v in reversed(self.gmin)]",
                "                else:", "                    heappush(self.gmin, g)", "                    heappush(self.gmax, -g)",
                "        else:", "            del gc[g]", "",
                "    def _minGap(self):  # heap tops of sizes no longer present are dropped as they surface",
                "        h, gc = self.gmin, self.gc", "        while h[0] not in gc:", "            heappop(h)", "        return h[0]", "",
                "    def _maxGap(self):", "        h, gc = self.gmax, self.gc", "        while -h[0] not in gc:", "            heappop(h)",
                "        return -h[0]"]
    if S:
        out += ["", "    def _sumFirst(self, k):  # sum of the k smallest values", "        if k <= 0:", "            return 0",
                "        v, b, _, s = self._kthInfo(k)", "        return s + (k - b) * v"]
    return "\n".join(out) + "\n"


def cpp_add(sums, mexc, minmax, medians, mode=False, gaps=False, xor=False, shift=False):
    S = sums
    kept = (["min / max"] if minmax else []) + (["both medians"] if medians else []) + (["the mex"] if mexc else [])
    out = ["", "    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes)" + ("; keeps " + ", ".join(kept) + " current" if kept else ""),
           "        n += c;"] + (["        total += S(c) * x;"] if S else []) + (
           ["        if (c & 1) xtotal ^= x;  // an odd number of copies flips x in or out of the xor of everything"] if xor else []) + [
           "        long long f = insert(x, c);  // x's new count" if needs_count(mexc, minmax, mode, gaps) else "        insert(x, c);"]
    if mode or gaps:
        out += ["        long long g = f - c;  // x's old count"]
    if mode:
        out += ["        {  // mode: x moves from the bucket of its old count to its new one",
                "            if (g) {", "                auto it = bk.find(g);", "                it->second.erase(x);",
                "                if (it->second.empty()) bk.erase(it);", "            }", "            if (f) bk[f].insert(x);", "        }"]
    if gaps:  # x's count went g -> f: duplicates, and the gaps around x when it appears or disappears
        out += ["        {  // gaps",
                "            if ((g >= 2) != (f >= 2)) dups += f >= 2 ? 1 : -1;  // values with 2+ copies (then the smallest difference is 0)",
                "            if (!g || !f) {  // x appeared or disappeared: the gap between its neighbours splits or comes back",
                *(["                optional<T> p = largestLtX(x), q = smallestGtX(x);"] if not shift else [
                    "                long long cl = lt(x), ce = le(x);  // (stored values: the public ops would shift x again)",
                    "                optional<T> p, q;",
                    "                if (cl) p = kthAt(cl);",
                    "                if (ce < n) q = kthAt(ce + 1);"]),
                "                auto drop = [&](long long v) { gaps.erase(gaps.find(v)); };",
                "                if (f) {",
                "                    if (p && q) drop((long long)*q - (long long)*p);",
                "                    if (p) gaps.insert((long long)x - (long long)*p);",
                "                    if (q) gaps.insert((long long)*q - (long long)x);",
                "                } else {",
                "                    if (p) drop((long long)x - (long long)*p);",
                "                    if (q) drop((long long)*q - (long long)x);",
                "                    if (p && q) gaps.insert((long long)*q - (long long)*p);",
                "                }",
                "            }",
                "        }"]
    if kept:
        up = (["            if constexpr (is_integral_v<T>) if (x == T(mexV)) mexV = findMex();  // x filled the mex"] if mexc else [])
        if minmax or medians:
            up += ["            if (n == c) {  // the set was empty"]
            up += ["                mn = mx = x;"] if minmax else []
            up += ["                low = high = Info{x, 0, c" + (", 0" if S else "") + "};"] if medians else []
            up += ["                return;", "            }"]
            up += ["            if (x < mn) mn = x;", "            if (x > mx) mx = x;"] if minmax else []
        down = ([f"            if constexpr (is_integral_v<T>) if (x >= {'-off' if shift else '0'} && x < T(mexV) && !f) mexV = x;  // the last copy of a value below the mex"]
                if mexc else [])
        if minmax or medians:
            down += ["            if (!n) return;"]
            down += ["            if (!f) {  // x is gone: it may have been the min / max", "                if (x == mn) mn = kthAt(1);",
                     "                if (x == mx) mx = kthAt(n);", "            }"] if minmax else []
        out += ["        if (c > 0) {"] + up + ["        } else {"] + down + ["        }"]
        if medians:
            out += ["        // each median is a tracked rank: shift its (value, copies before, copies" + (", sum before" if S else "") +
                    "), and search again only", "        // when the rank leaves the tracked value",
                    "        if (x < low.v) low.before += c" + (", low.sb += S(c) * x" if S else "") + ";",
                    "        else if (x == low.v) low.c += c;", "        long long r = (n + 1) / 2;",
                    "        if (r <= low.before || r > low.before + low.c) low = kthInfo(r);",
                    "        if (x < high.v) high.before += c" + (", high.sb += S(c) * x" if S else "") + ";",
                    "        else if (x == high.v) high.c += c;", "        r = n / 2 + 1;",
                    "        if (r <= high.before || r > high.before + high.c) high = kthInfo(r);"]
    out += ["    }"]
    if S:
        out += ["", "    S sumFirst(long long k) {  // sum of the k smallest values", "        if (k <= 0) return 0;",
                "        Info f = kthInfo(k);", "        return f.sb + S(k - f.before) * f.v;", "    }"]
    return "\n".join(out) + "\n"


def cached_ops(minmax, medians, mexc):
    """The bodies of the queries a cache answers in O(1) (with it) or by a walk (without it), per language."""
    py = {
        "min": "return self.mn if self.n else None" if minmax else "return self._kth(1) if self.n else None",
        "max": "return self.mx if self.n else None" if minmax else "return self._kth(self.n) if self.n else None",
        "popMin": f"if not self.n:\n    return None\nv = {'self.mn' if minmax else 'self._kth(1)'}\nself._add(v, -1)\nreturn v",
        "popMax": f"if not self.n:\n    return None\nv = {'self.mx' if minmax else 'self._kth(self.n)'}\nself._add(v, -1)\nreturn v",
        "medianLow": "return self.lowV if self.n else None" if medians else "return self._kth((self.n + 1) >> 1) if self.n else None",
        "medianHigh": "return self.highV if self.n else None" if medians else "return self._kth((self.n >> 1) + 1) if self.n else None",
        "sumAbsDiffToMedian": "if not self.n:\n    return 0\nv, b, c, s = " + ("self.lowV, self.lowB, self.lowC, self.lowS" if medians
                                                                            else "self._kthInfo((self.n + 1) >> 1)") +
                              "\nreturn v * b - s + (self.total - s - c * v) - v * (self.n - b - c)",
        "mex": "return self.mexV" if mexc else "return self._findMex()",
    }
    cpp = {
        "min": ("optional<T>", "if (!n) return nullopt;\nreturn " + ("mn" if minmax else "kthAt(1)") + ";"),
        "max": ("optional<T>", "if (!n) return nullopt;\nreturn " + ("mx" if minmax else "kthAt(n)") + ";"),
        "popMin": ("optional<T>", "if (!n) return nullopt;\nT v = " + ("mn" if minmax else "kthAt(1)") + ";\naddRaw(v, -1);\nreturn v;"),
        "popMax": ("optional<T>", "if (!n) return nullopt;\nT v = " + ("mx" if minmax else "kthAt(n)") + ";\naddRaw(v, -1);\nreturn v;"),
        "medianLow": ("optional<T>", "if (!n) return nullopt;\nreturn " + ("low.v" if medians else "kthAt((n + 1) / 2)") + ";"),
        "medianHigh": ("optional<T>", "if (!n) return nullopt;\nreturn " + ("high.v" if medians else "kthAt(n / 2 + 1)") + ";"),
        "sumAbsDiffToMedian": ("S", "if (!n) return 0;\n" + ("const Info& m = low;" if medians else "Info m = kthInfo((n + 1) / 2);") +
                               "\nreturn S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);"),
        "mex": ("long long", "return mexV;" if mexc else "return findMex();"),
    }
    return py, cpp


# ================================================================================================ structures

def keep_mex(text, mex):
    """Lines ending in '  @mex' and blocks between '@mex{' / '@mex}' lines exist only in the version with mex."""
    out, skip = [], False
    for line in text.split("\n"):
        if line.strip() == "@mex{":
            skip = not mex
            continue
        if line.strip() == "@mex}":
            skip = False
            continue
        if skip:
            continue
        if line.endswith("  @mex"):
            if not mex:
                continue
            line = line[:-len("  @mex")]
        out.append(line)
    return "\n".join(out)



def fenwick(sums, mex, bits=(False, False, False)):
    s, M = sums, mex
    X = bits[0]  # (xor only: OR / AND have no inverse, and a Fenwick needs one)
    py = f'''from bisect import bisect_left, bisect_right


# Ordered multiset over values known ahead of time (offline): Fenwick trees over the sorted distinct values you pass
# to the constructor, one counting copies{", one summing them" if s else ""}{", one marking which values are present (for mex)" if M else ""}{", one xor-ing the values with an odd count" if X else ""}.
# k-th / sum of the k smallest walk down by binary lifting. The constructor only learns which values can appear (it
# compresses them); the multiset starts EMPTY. Every value you add must be one of them; query arguments (x, lo, hi)
# can be anything.


class FenwickMultiset:
    __slots__ = ("vals", "m", "top", "cnt", "fc",{' "fs",' if s else ""}{' "fx",' if X else ""}{' "fp", "z", "run",' if M else ""} "n",{' "total",' if s else ""} "d")

    # O(N log N) -- allValuesThatWillEverBeInsertedForOfflineCompression: every value you will EVER add (any order, duplicates fine), only to compress values; this does NOT add them, the multiset starts empty; N = distinct values
    def __init__(self, allValuesThatWillEverBeInsertedForOfflineCompression):
        vals = self.vals = sorted(set(allValuesThatWillEverBeInsertedForOfflineCompression))
        m = self.m = len(vals)
        self.top = 1 << (m.bit_length() - 1) if m else 0  # highest power of two <= m, for binary lifting
        self.cnt = [0] * m  # copies of vals[i]
        self.fc = [0] * (m + 1)  # Fenwick: copies
{"        self.fs = [0] * (m + 1)  # Fenwick: copies * value" + chr(10) if s else ""}        self.fx = [0] * (m + 1)  # Fenwick: xor of the values with an odd count  @xor
@mex{{
        self.fp = [0] * (m + 1)  # Fenwick: 1 where the value is present
        z = self.z = bisect_left(vals, 0)
        run = 0
        while z + run < m and vals[z + run] == run:  # vals[z .. z + run - 1] = 0, 1, ..., run - 1
            run += 1
        self.run = run
@mex}}
        self.n = {"self.total = " if s else ""}self.d = 0

    def _fen(self, f, i, v):
        m = self.m
        i += 1
        while i <= m:
            f[i] += v
            i += i & -i

    def _pre(self, f, i):  # f's total over positions 0..i-1
        s = 0
        while i > 0:
            s += f[i]
            i &= i - 1
        return s

    def _insert(self, x, c):
        i = bisect_left(self.vals, x)  # x must be one of the given values
        old = self.cnt[i]
        self.cnt[i] = old + c
        self._fen(self.fc, i, c)
{"        self._fen(self.fs, i, c * x)" + chr(10) if s else ""}        if c & 1:  # x's parity flips  @xor
            fx, j = self.fx, i + 1  @xor
            while j <= self.m:  @xor
                fx[j] ^= x  @xor
                j += j & -j  @xor
        if not old:
            self._fen(self.fp, i, 1)  @mex
            self.d += 1
        elif not old + c:
            self._fen(self.fp, i, -1)  @mex
            self.d -= 1
        return old + c  # (x's new count)

    def _lt(self, x):
        return self._pre(self.fc, bisect_left(self.vals, x))

    def _le(self, x):
        return self._pre(self.fc, bisect_right(self.vals, x))

    def _countOf(self, x):
        i = bisect_left(self.vals, x)
        return self.cnt[i] if i < self.m and self.vals[i] == x else 0
{f"""
    def _slt(self, x):
        return self._pre(self.fs, bisect_left(self.vals, x))

    def _sle(self, x):
        return self._pre(self.fs, bisect_right(self.vals, x))
""" if s else ""}
    def _kth(self, k):  # binary lifting: the largest prefix with fewer than k copies ends right before the answer
        fc, m = self.fc, self.m
        pos, step = 0, self.top
        while step:
            nxt = pos + step
            if nxt <= m and fc[nxt] < k:
                pos = nxt
                k -= fc[nxt]
            step >>= 1
        return self.vals[pos]

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies{", sum before it" if s else ""})
        fc,{" fs," if s else ""} m = self.fc,{" self.fs," if s else ""} self.m
        pos, step, before{", acc" if s else ""} = 0, self.top, 0{", 0" if s else ""}
        while step:
            nxt = pos + step
            if nxt <= m and before + fc[nxt] < k:
                pos = nxt
                before += fc[nxt]
{"                acc += fs[nxt]" + chr(10) if s else ""}            step >>= 1
        return self.vals[pos], before, self.cnt[pos]{", acc" if s else ""}

@mex{{
    def _findMex(self):  # smallest non-negative integer not in the set
        if not self.run:
            return 0  # 0 is not even a possible value
        # first absent position p >= z: lift while the number of absent positions so far stays at the count before z
        fp, m, z = self.fp, self.m, self.z
        a0 = z - self._pre(fp, z)
        pos, step, acc = 0, self.top, 0
        while step:
            nxt = pos + step
            if nxt <= m and nxt - (acc + fp[nxt]) <= a0:
                pos = nxt
                acc += fp[nxt]
            step >>= 1
        return min(pos - z, self.run)
@mex}}
'''
    cpp = f'''
// Ordered multiset over values known ahead of time (offline): Fenwick trees over the sorted distinct values you pass
// to the constructor, one counting copies{", one summing them" if s else ""}{", one marking which values are present (for mex)" if M else ""}{", one xor-ing the values with an odd count" if X else ""}.
// k-th / sum of the k smallest walk down by binary lifting. The constructor only learns which values can appear (it
// compresses them); the multiset starts EMPTY. Every value you add must be one of them; query arguments (x, lo, hi)
// can be anything. T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct FenwickMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    vector<T> vals;  // the sorted distinct values
    int m, top{", z, run" if M else ""};
    vector<long long> cnt, fc{", fp" if M else ""};  // copies per value; Fenwick of copies{"; Fenwick of present values" if M else ""}
{"    vector<S> fs;  // Fenwick of copies * value" + chr(10) if s else ""}    vector<T> fx;  // Fenwick of xor over the values with an odd count  @xor
    long long n = 0, d = 0;
{"    S total = 0;" + chr(10) if s else ""}
    // O(N log N) -- allValuesThatWillEverBeInsertedForOfflineCompression: every value you will EVER add (any order, duplicates fine), only to compress values; this does NOT add them, the multiset starts empty; N = distinct values
    explicit FenwickMultiset(vector<T> allValuesThatWillEverBeInsertedForOfflineCompression) : vals(move(allValuesThatWillEverBeInsertedForOfflineCompression)) {{
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        m = (int)vals.size();
        top = m ? 1 << (31 - __builtin_clz(m)) : 0;  // highest power of two <= m, for binary lifting
        cnt.assign(m, 0), fc.assign(m + 1, 0);
        fp.assign(m + 1, 0);  @mex
{"        fs.assign(m + 1, 0);" + chr(10) if s else ""}        fx.assign(m + 1, 0);  @xor
@mex{{
        z = int(lower_bound(vals.begin(), vals.end(), T(0)) - vals.begin());
        run = 0;
        while (z + run < m && vals[z + run] == T(run)) run++;  // vals[z .. z + run - 1] = 0, 1, ..., run - 1
@mex}}
    }}

    template <class V>
    void fen(vector<V>& f, int i, V v) {{
        for (i++; i <= m; i += i & -i) f[i] += v;
    }}

    template <class V>
    V pre(const vector<V>& f, int i) const {{  // f's total over positions 0..i-1
        V s = 0;
        for (; i > 0; i &= i - 1) s += f[i];
        return s;
    }}

    int lowerIdx(T x) const {{ return int(lower_bound(vals.begin(), vals.end(), x) - vals.begin()); }}
    int upperIdx(T x) const {{ return int(upper_bound(vals.begin(), vals.end(), x) - vals.begin()); }}

    long long insert(T x, long long c) {{  // returns x's new count
        int i = lowerIdx(x);  // x must be one of the given values
        long long old = cnt[i];
        cnt[i] += c;
        fen(fc, i, c);
{"        fen(fs, i, S(c) * x);" + chr(10) if s else ""}        if (c & 1)  @xor
            for (int j = i + 1; j <= m; j += j & -j) fx[j] ^= x;  // x's parity flips  @xor
        if (!old) {"fen(fp, i, 1LL), " if M else ""}d++;
        else if (!cnt[i]) {"fen(fp, i, -1LL), " if M else ""}d--;
        return cnt[i];
    }}

    long long lt(T x) {{ return pre(fc, lowerIdx(x)); }}
    long long le(T x) {{ return pre(fc, upperIdx(x)); }}

    long long countOf(T x) const {{
        int i = lowerIdx(x);
        return i < m && vals[i] == x ? cnt[i] : 0;
    }}
{"    S slt(T x) { return pre(fs, lowerIdx(x)); }" + chr(10) + "    S sle(T x) { return pre(fs, upperIdx(x)); }" + chr(10) if s else ""}
    T kthAt(long long k) {{  // binary lifting: the largest prefix with fewer than k copies ends right before the answer
        int pos = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= m && fc[pos + step] < k) pos += step, k -= fc[pos];
        return vals[pos];
    }}
    Info kthInfo(long long k) {{  // the k-th smallest, copies before it, its copies{", sum before it" if s else ""}
        int pos = 0;
        long long before = 0;
{"        S acc = 0;" + chr(10) if s else ""}        for (int step = top; step; step >>= 1)
            if (pos + step <= m && before + fc[pos + step] < k) pos += step, before += fc[pos]{", acc += fs[pos]" if s else ""};
        return {{vals[pos], before, cnt[pos]{", acc" if s else ""}}};
    }}
@mex{{
    long long findMex() {{  // smallest non-negative integer not in the set
        if (!run) return 0;  // 0 is not even a possible value
        // first absent position p >= z: lift while the number of absent positions so far stays at the count before z
        long long a0 = z - pre(fp, z), acc = 0;
        int pos = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= m && (pos + step) - (acc + fp[pos + step]) <= a0) pos += step, acc += fp[pos];
        return std::min<long long>(pos - z, run);
    }}
@mex}}
'''
    comps = {op: "log(N)" for op in OPS}
    comps.update({"size": "1", "sumAll": "1", "countDistinct": "1", "min": "1", "max": "1", "build": "N*log(N)"})
    node = "cnt[1*N] fc[1*N]" + (" fp[1*N]" if M else "") + (" fs[1*N]" if s else "") + (" fx[1*N]" if X else "")
    comps["xorOfAll"] = "1"
    return dict(name="FenwickMultiset", dtype="fenwick", values="offline", py=keep_aggs(keep_mex(py, M), X), cpp=keep_aggs(keep_mex(cpp, M), X),
                comps=comps, mex=M, bits=(X, False, False), mem=("none", node, "none", "vals[1*N]"),
                note="N = how many distinct values were given to the constructor; the arrays are allocated once")


# ------------------------------------------------------------------------------------------------ value tree

def value_tree(sums, mex, bits=(False, False, False)):
    s, M = sums, mex
    X, O, A = bits
    agg = "".join(f", their {w}" for w, on in (("xor", X), ("OR", O), ("AND", A)) if on)
    py = f'''
# Ordered multiset of integers in a known range [lo, hi] (values not known ahead): a dynamic tree over the value range,
# each node keeping how many copies{", their sum," if s else ""}{agg}{" and how many distinct values (for mex)" if M else ""} are below it. Sparse: dicts keyed by heap
# index over a power-of-two cover of [lo, hi]; a missing key is an empty block. k-th / sums of the k smallest descend
# by counts{"; mex descends to the first value >= 0 whose block isn" + chr(39) + "t full" if M else ""}.


class ValueTreeMultiset:
    __slots__ = ("lo", "hi", "cap", "c",{' "s",' if s else ""}{' "x",' if X else ""}{' "o",' if O else ""}{' "a",' if A else ""}{' "p",' if M else ""} "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset for values in [lo, hi] (any integers, negative is fine)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.cap = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of value v is cap + (v - lo)
        self.c = {{}}  # node -> copies below it
{"        self.s = {}  # node -> sum of the copies below it" + chr(10) if s else ""}        self.p = {{}}  # node -> distinct values below it  @mex
        self.x = {{}}  # node -> xor of the values below it with an odd count  @xor
        self.o = {{}}  # node -> OR of the values below it  @or
        self.a = {{}}  # node -> AND of the values below it  @and
        self.n = {"self.total = " if s else ""}self.d = 0

    def _insert(self, x, c):
        cc{", ss" if s else ""} = self.c{", self.s" if s else ""}
        pp = self.p  @mex
        xx = self.x  @xor
        oo = self.o  @or
        aa = self.a  @and
        i = self.cap + x - self.lo
        old = cc.get(i, 0)
        pres = (old + c > 0) - (old > 0)
        self.d += pres
        ov = x if old + c > 0 else 0  # the OR below the current node  @or
        av = x if old + c > 0 else -1  # the AND below the current node  @and
        while i:
            cc[i] = cc.get(i, 0) + c
{"            ss[i] = ss.get(i, 0) + c * x" + chr(10) if s else ""}            if c & 1:  # x's parity flips  @xor
                xx[i] = xx.get(i, 0) ^ x  @xor
            if pres:  @mex
                pp[i] = pp.get(i, 0) + pres  @mex
            if pres:  # x appeared or disappeared: the OR / AND up its path, each node with its sibling's  @or|and
                oo[i] = ov  @or
                ov |= oo.get(i ^ 1, 0)  @or
                aa[i] = av  @and
                av &= aa.get(i ^ 1, -1)  @and
            i >>= 1
        return old + c  # (x's new count)

    def _prefix(self, f, x):  # f's total over the values < x
        if x <= self.lo:
            return 0
        if x > self.hi:
            return f.get(1, 0)
        i = self.cap + x - self.lo
        res = 0
        while i > 1:
            if i & 1:
                res += f.get(i - 1, 0)
            i >>= 1
        return res

    def _lt(self, x):
        return self._prefix(self.c, x)

    def _le(self, x):
        return self._prefix(self.c, x + 1)

    def _countOf(self, x):  # the leaf of x
        return self.c.get(self.cap + x - self.lo, 0) if self.lo <= x <= self.hi else 0
{f"""
    def _slt(self, x):
        return self._prefix(self.s, x)

    def _sle(self, x):
        return self._prefix(self.s, x + 1)
""" if s else ""}
    def _kth(self, k):
        c, i, size = self.c, 1, self.cap
        while i < size:
            i <<= 1
            cl = c.get(i, 0)
            if k > cl:
                k -= cl
                i += 1
        return i - size + self.lo

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies{", sum before it" if s else ""})
        c,{" s," if s else ""} i, size, before{", acc" if s else ""} = self.c,{" self.s," if s else ""} 1, self.cap, 0{", 0" if s else ""}
        while i < size:
            i <<= 1
            cl = c.get(i, 0)
            if before + cl < k:
                before += cl
{"                acc += s.get(i, 0)" + chr(10) if s else ""}                i += 1
        return i - size + self.lo, before, c[i]{", acc" if s else ""}

@mex{{
    # smallest non-negative integer not in the set (hi + 1 if all of [0, hi] are present)
    def _findMex(self):
        if self.lo > 0:
            return 0
        p, size = self.p, self.cap

        def full(i):  # every value below node i is present
            return p.get(i, 0) == size >> (i.bit_length() - 1)

        i = size - self.lo  # the leaf of value 0
        while True:
            while i > 1 and not i & 1:  # climb while i is a left child: its parent starts at the same value
                i >>= 1
            if not full(i):  # the first missing value is inside i: descend, preferring the left child
                while i < size:
                    i <<= 1
                    if full(i):
                        i += 1
                return min(i - size + self.lo, self.hi + 1)
            i += 1
            if not i & (i - 1):  # walked off the right edge
                return self.hi + 1
@mex}}
'''
    sfield = "S s; " if s else ""
    cpp = f'''
// Ordered multiset of integers in a known range [lo, hi] (values not known ahead): a dynamic tree over the value range,
// each node keeping how many copies{", their sum," if s else ""}{agg}{" and how many distinct values (for mex)" if M else ""} are below it. Nodes live in one pool
// shared by every ValueTreeMultiset<T> (call resetPool() between test cases); node 0 is the shared empty block.
// k-th / sums of the k smallest descend by counts{"; mex descends to the first value >= 0 whose block isn" + chr(39) + "t full" if M else ""}.
// T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct ValueTreeMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node {{ long long c; {sfield}{"long long p; " if M else ""}{"T xr; " if X else ""}{"T orv; " if O else ""}{"T andv = ~T(0); " if A else ""}int l, r; }};  // copies{", sum" if s else ""}{", distinct values" if M else ""}{agg.replace(", their", ",")} below
    static inline vector<Node> pool{{Node{{}}}};  // node 0: empty, its children are itself
    long long lo, hi, n = 0, d = 0;
{"    S total = 0;" + chr(10) if s else ""}    int root = 0;

    // O(1) -- an empty multiset for values in [lo, hi] (any long long range, negative is fine)
    ValueTreeMultiset(long long lo, long long hi) : lo(lo), hi(hi) {{}}

    // O(1) -- forget every node of every ValueTreeMultiset<T>; call between test cases, then build new ones
    static void resetPool() {{ pool.resize(1); }}

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) {{ pool.reserve(nodes); }}

    static int make() {{
        pool.push_back(Node{{}});
        return (int)pool.size() - 1;
    }}

    long long insert(T x, long long c) {{  // returns x's new count
        if (!root) root = make();
        int path[130], dep = 0, y = root;
        long long a = lo, b = hi;
        while (true) {{
            path[dep++] = y;
            if (a == b) break;
            long long m = a + (b - a) / 2;
            bool right = x > m;
            int ch = right ? pool[y].r : pool[y].l;
            if (!ch) {{
                ch = make();
                (right ? pool[y].r : pool[y].l) = ch;
            }}
            y = ch;
            if (right) a = m + 1;
            else b = m;
        }}
        long long old = pool[y].c;
        long long pres = (old + c > 0) - (old > 0);
        d += pres;
        for (int k = 0; k < dep; k++) {{
            Node& v = pool[path[k]];
            v.c += c;
            v.p += pres;  @mex
{"            v.s += S(c) * x;" + chr(10) if s else ""}            if (c & 1) v.xr ^= x;  // x's parity flips  @xor
        }}
        if (pres) {{  // x appeared or disappeared: the OR / AND up its path  @or|and
            pool[y].orv = pres > 0 ? x : T(0);  @or
            pool[y].andv = pres > 0 ? x : ~T(0);  @and
            for (int k = dep - 2; k >= 0; k--) {{  @or|and
                Node& v = pool[path[k]];  @or|and
                v.orv = pool[v.l].orv | pool[v.r].orv;  @or
                v.andv = pool[v.l].andv & pool[v.r].andv;  @and
            }}  @or|and
        }}  @or|and
        return old + c;
    }}

    // (copies, sum) of the values < x
    pair<long long, S> prefix(T x) const {{
        if (x <= lo) return {{0, 0}};
        if (x > hi) return {{pool[root].c, {"pool[root].s" if s else "0"}}};
        long long cnt = 0;
        S sum = 0;
        int y = root;
        long long a = lo, b = hi;
        while (y && a < b) {{
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else {{
                const Node& L = pool[pool[y].l];
                cnt += L.c{", sum += L.s" if s else ""};
                y = pool[y].r, a = m + 1;
            }}
        }}
        return {{cnt, sum}};  // y is now the leaf of x (or empty): values < x only
    }}

    long long lt(T x) {{ return prefix(x).first; }}
    long long le(T x) {{ return prefix(x + 1).first; }}

    long long countOf(T x) const {{  // walk to the leaf of x
        if (x < lo || x > hi) return 0;
        int y = root;
        long long a = lo, b = hi;
        while (y && a < b) {{
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else y = pool[y].r, a = m + 1;
        }}
        return pool[y].c;
    }}
{"    S slt(T x) { return prefix(x).second; }" + chr(10) + "    S sle(T x) { return prefix(x + 1).second; }" + chr(10) if s else ""}
    T kthAt(long long k) {{
        int y = root;
        long long a = lo, b = hi;
        while (a < b) {{
            long long m = a + (b - a) / 2;
            long long cl = pool[pool[y].l].c;
            if (k <= cl) y = pool[y].l, b = m;
            else k -= cl, y = pool[y].r, a = m + 1;
        }}
        return T(a);
    }}

    Info kthInfo(long long k) {{  // the k-th smallest, copies before it, its copies{", sum before it" if s else ""}
        int y = root;
        long long a = lo, b = hi, before = 0;
{"        S acc = 0;" + chr(10) if s else ""}        while (a < b) {{
            long long m = a + (b - a) / 2;
            const Node& L = pool[pool[y].l];
            if (k <= before + L.c) y = pool[y].l, b = m;
            else before += L.c{", acc += L.s" if s else ""}, y = pool[y].r, a = m + 1;
        }}
        return {{T(a), before, pool[y].c{", acc" if s else ""}}};
    }}
@mex{{
    // the first value >= from in [a, b] (node y) that is not present, or LLONG_MAX
    long long firstMissing(int y, long long a, long long b, long long from) const {{
        if (b < from) return LLONG_MAX;
        if (!y) return std::max(a, from);
        if (pool[y].p == b - a + 1) return LLONG_MAX;
        if (a == b) return a;
        long long m = a + (b - a) / 2;
        long long res = firstMissing(pool[y].l, a, m, from);
        return res != LLONG_MAX ? res : firstMissing(pool[y].r, m + 1, b, from);
    }}

    // smallest non-negative integer not in the set (hi + 1 if all of [0, hi] are present)
    long long findMex() {{
        if (lo > 0) return 0;
        long long res = firstMissing(root, lo, hi, 0);
        return res == LLONG_MAX ? hi + 1 : res;
    }}
@mex}}
'''
    comps = {op: "log(U)" for op in OPS}
    comps.update({"size": "1", "sumAll": "1", "countDistinct": "1", "min": "1", "max": "1", "build": "1"})
    node = "c[1*log(U)]" + (" p[1*log(U)]" if M else "") + (" s[1*log(U)]" if s else "") + "".join(
        f" {f}[1*log(U)]" for f, on in (("x", X), ("o", O), ("a", A)) if on)
    comps.update({"xorOfAll": "1", "orOfAll": "1", "andOfAll": "1"})
    return dict(name="ValueTreeMultiset", dtype="value-tree", values="online-range", py=keep_aggs(keep_mex(py, M), X, O, A),
                cpp=keep_aggs(keep_mex(cpp, M), X, O, A), comps=comps, mex=M, bits=bits,

                mem=("sparse", node, "none", "children[2*log(U)]"),
                note="per add of a new value, one node per level of its root path; U = hi - lo + 1. C++: one shared "
                     "node pool (node 0 = empty), call resetPool() between test cases; Python: dicts keyed by heap index")


# ------------------------------------------------------------------------------------------------ AVL tree, treap, splay tree

def bst_common_py(s):
    """Read-only walks of the AVL tree (Python): K key, C copies, Z copies below, S sum below, D distinct below,
    L / R children."""
    return f'''
    def _lt(self, x):  # copies of values < x
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t, res = self.root, 0
        while t:
            if K[t] < x:
                res += Z[L[t]] + C[t]
                t = R[t]
            else:
                t = L[t]
        return res

    def _le(self, x):  # copies of values <= x
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t, res = self.root, 0
        while t:
            if x < K[t]:
                t = L[t]
            else:
                res += Z[L[t]] + C[t]
                t = R[t]
        return res

    def _countOf(self, x):
        K, L, R = self.K, self.L, self.R
        t = self.root
        while t and K[t] != x:
            t = L[t] if x < K[t] else R[t]
        return self.C[t]
{f"""
    def _slt(self, x):  # sum of the values < x
        K, C, S, L, R = self.K, self.C, self.S, self.L, self.R
        t, res = self.root, 0
        while t:
            if K[t] < x:
                res += S[L[t]] + C[t] * K[t]
                t = R[t]
            else:
                t = L[t]
        return res

    def _sle(self, x):  # sum of the values <= x
        K, C, S, L, R = self.K, self.C, self.S, self.L, self.R
        t, res = self.root, 0
        while t:
            if x < K[t]:
                t = L[t]
            else:
                res += S[L[t]] + C[t] * K[t]
                t = R[t]
        return res
""" if s else ""}
    def _kth(self, k):
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t = self.root
        while True:
            zl = Z[L[t]]
            if k <= zl:
                t = L[t]
            elif k <= zl + C[t]:
                return K[t]
            else:
                k -= zl + C[t]
                t = R[t]

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies{", sum before it" if s else ""})
        K, C, Z,{" S," if s else ""} L, R = self.K, self.C, self.Z,{" self.S," if s else ""} self.L, self.R
        t, before{", acc" if s else ""} = self.root, 0{", 0" if s else ""}
        while True:
            l = L[t]
            zl = before + Z[l]
            if k <= zl:
                t = l
            elif k <= zl + C[t]:
                return K[t], zl, C[t]{", acc + S[l]" if s else ""}
            else:
                before = zl + C[t]
{"                acc += S[l] + C[t] * K[t]" + chr(10) if s else ""}                t = R[t]

@mex{{
    def _distinctLt(self, x):  # distinct values < x
        K, D, L, R = self.K, self.D, self.L, self.R
        t, res = self.root, 0
        while t:
            if K[t] < x:
                res += D[L[t]] + 1
                t = R[t]
            else:
                t = L[t]
        return res

    # smallest non-negative integer not in the set. With c0 distinct negatives, the distinct values >= 0
    # in order v_0 < v_1 < ... satisfy v_j >= j, and v_j == j means 0..v_j are all present; the answer is the first j
    # with v_j > j (or how many there are). One walk down: at a node of distinct rank c0 + j, go right if v_j == j.
    def _findMex(self):
        K, D, L, R = self.K, self.D, self.L, self.R
        c0 = self._distinctLt(0)
        t, before, res = self.root, -c0, self.d - c0  # before: distinct values >= 0 left of t's subtree
        while t:
            j = before + D[L[t]]
            if K[t] < 0 or K[t] == j:
                before = j + 1
                t = R[t]
            else:
                res = j
                t = L[t]
        return res
@mex}}
'''


def bst_common_cpp(s):
    return f'''
    long long lt(T x) {{  // copies of values < x
        int t = root;
        long long res = 0;
        while (t) {{
            if (pool[t].key < x) res += pool[pool[t].l].z + pool[t].c, t = pool[t].r;
            else t = pool[t].l;
        }}
        return res;
    }}

    long long le(T x) {{  // copies of values <= x
        int t = root;
        long long res = 0;
        while (t) {{
            if (x < pool[t].key) t = pool[t].l;
            else res += pool[pool[t].l].z + pool[t].c, t = pool[t].r;
        }}
        return res;
    }}

    long long countOf(T x) {{
        int t = root;
        while (t && pool[t].key != x) t = x < pool[t].key ? pool[t].l : pool[t].r;
        return pool[t].c;
    }}
{f"""
    S slt(T x) {{  // sum of the values < x
        int t = root;
        S res = 0;
        while (t) {{
            if (pool[t].key < x) res += pool[pool[t].l].s + S(pool[t].c) * pool[t].key, t = pool[t].r;
            else t = pool[t].l;
        }}
        return res;
    }}

    S sle(T x) {{  // sum of the values <= x
        int t = root;
        S res = 0;
        while (t) {{
            if (x < pool[t].key) t = pool[t].l;
            else res += pool[pool[t].l].s + S(pool[t].c) * pool[t].key, t = pool[t].r;
        }}
        return res;
    }}
""" if s else ""}
    T kthAt(long long k) {{
        int t = root;
        while (true) {{
            long long zl = pool[pool[t].l].z;
            if (k <= zl) t = pool[t].l;
            else if (k <= zl + pool[t].c) return pool[t].key;
            else k -= zl + pool[t].c, t = pool[t].r;
        }}
    }}

    Info kthInfo(long long k) {{  // the k-th smallest, copies before it, its copies{", sum before it" if s else ""}
        int t = root;
        long long before = 0;
{"        S acc = 0;" + chr(10) if s else ""}        while (true) {{
            const Node& v = pool[t];
            long long zl = before + pool[v.l].z;
            if (k <= zl) t = v.l;
            else if (k <= zl + v.c) return {{v.key, zl, v.c{", acc + pool[v.l].s" if s else ""}}};
            else before = zl + v.c{", acc += pool[v.l].s + S(v.c) * v.key" if s else ""}, t = v.r;
        }}
    }}

@mex{{
    long long distinctLt(T x) {{  // distinct values < x
        int t = root;
        long long res = 0;
        while (t) {{
            if (pool[t].key < x) res += pool[pool[t].l].dn + 1, t = pool[t].r;
            else t = pool[t].l;
        }}
        return res;
    }}

    // smallest non-negative integer not in the set. With c0 distinct negatives, the distinct values >= 0
    // in order v_0 < v_1 < ... satisfy v_j >= j, and v_j == j means 0..v_j are all present; the answer is the first j
    // with v_j > j (or how many there are). One walk down: at a node of distinct rank c0 + j, go right if v_j == j.
    long long findMex() {{
        long long c0 = distinctLt(0), before = -c0, res = d - c0;  // before: distinct values >= 0 left of t's subtree
        int t = root;
        while (t) {{
            long long j = before + pool[pool[t].l].dn;
            if (pool[t].key < 0 || pool[t].key == T(j)) before = j + 1, t = pool[t].r;
            else res = j, t = pool[t].l;
        }}
        return res;
    }}
@mex}}
'''


def treap(sums, mex, bits=(False, False, False)):
    s, M = sums, mex
    X, O, A = bits
    agg = "".join(f", {w}" for w, on in (("xor", X), ("OR", O), ("AND", A)) if on)
    py = f'''from random import random


# Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
# its value, its copies, and the copies{", sum" if s else ""}{agg}{" and distinct values" if M else ""} in its subtree. Nodes live in parallel lists (a node
# pool; node 0 is the empty tree) and removed nodes are reused. Updates split around x and merge back.


class TreapMultiset:
    __slots__ = ("K", "C", "Z",{' "S",' if s else ""}{' "X",' if X else ""}{' "O",' if O else ""}{' "A",' if A else ""}{' "D",' if M else ""} "P", "L", "R", "free", "root", "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z{", self.S" if s else ""} = [0], [0], [0]{", [0]" if s else ""}  # key, copies, copies below{", sum below" if s else ""}
        self.D = [0]  # distinct values below  @mex
        self.X = [0]  # xor of the values below with an odd count  @xor
        self.O = [0]  # OR of the values below  @or
        self.A = [-1]  # AND of the values below (the empty tree's: every bit)  @and
        self.P, self.L, self.R = [0.0], [0], [0]  # priority, children
        self.free = []  # removed nodes, reused first
        self.root = self.n = {"self.total = " if s else ""}self.d = 0

    def _new(self, x):
        if self.free:
            t = self.free.pop()
            self.K[t], self.C[t], self.P[t], self.L[t], self.R[t] = x, 0, random(), 0, 0
            return t
        self.K.append(x)
        self.C.append(0)
        self.Z.append(0)
{"        self.S.append(0)" + chr(10) if s else ""}        self.D.append(0)  @mex
        self.X.append(0)  @xor
        self.O.append(0)  @or
        self.A.append(-1)  @and
        self.P.append(random())
        self.L.append(0)
        self.R.append(0)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
{"        self.S[t] = self.S[l] + self.S[r] + self.C[t] * self.K[t]" + chr(10) if s else ""}        self.D[t] = self.D[l] + self.D[r] + 1  @mex
        self.X[t] = self.X[l] ^ self.X[r] ^ (self.K[t] if self.C[t] & 1 else 0)  @xor
        self.O[t] = self.O[l] | self.O[r] | self.K[t]  @or
        self.A[t] = self.A[l] & self.A[r] & self.K[t]  @and

    def _split(self, t, x):  # (keys < x, keys >= x)
        if not t:
            return 0, 0
        if self.K[t] < x:
            a, b = self._split(self.R[t], x)
            self.R[t] = a
            self._pull(t)
            return t, b
        a, b = self._split(self.L[t], x)
        self.L[t] = b
        self._pull(t)
        return a, t

    def _splitLe(self, t, x):  # (keys <= x, keys > x)
        if not t:
            return 0, 0
        if x < self.K[t]:
            a, b = self._splitLe(self.L[t], x)
            self.L[t] = b
            self._pull(t)
            return a, t
        a, b = self._splitLe(self.R[t], x)
        self.R[t] = a
        self._pull(t)
        return t, b

    def _merge(self, a, b):  # every key in a < every key in b
        if not a or not b:
            return a or b
        if self.P[a] > self.P[b]:
            self.R[a] = self._merge(self.R[a], b)
            self._pull(a)
            return a
        self.L[b] = self._merge(a, self.L[b])
        self._pull(b)
        return b

    def _insert(self, x, c):
        a, b = self._split(self.root, x)
        m, b = self._splitLe(b, x)  # m: the node of x, or 0
        if not m:
            m = self._new(x)
            self.d += 1
        f = self.C[m] = self.C[m] + c
        if f:
            self._pull(m)
        else:
            self.free.append(m)
            m = 0
            self.d -= 1
        self.root = self._merge(self._merge(a, m), b)
        return f  # (x's new count)
''' + bst_common_py(s)
    sfield = "S s; " if s else ""
    cpp = f'''
// Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
// its value, its copies, and the copies{", sum" if s else ""}{agg}{" and distinct values" if M else ""} in its subtree. Nodes live in one pool shared by every
// TreapMultiset<T> (call resetPool() between test cases); node 0 is the empty tree and removed nodes are reused.
// Updates split around x and merge back. T: an integer type; sums in S (long long for small T).
template <typename T>
struct TreapMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node {{ T key; long long c, z; {sfield}{"long long dn; " if M else ""}{"T xr; " if X else ""}{"T orv; " if O else ""}{"T andv = ~T(0); " if A else ""}unsigned prio; int l, r; }};  // copies; copies{", sum" if s else ""}{", distinct" if M else ""} below
    static inline vector<Node> pool{{Node{{}}}};
    static inline vector<int> freeList;
    static inline mt19937 rng{{(unsigned)chrono::steady_clock::now().time_since_epoch().count()}};
    int root = 0;
    long long n = 0, d = 0;
{"    S total = 0;" + chr(10) if s else ""}
    // O(1) -- an empty multiset
    TreapMultiset() {{}}

    // O(1) -- forget every node of every TreapMultiset<T>; call between test cases, then build new ones
    static void resetPool() {{ pool.resize(1), freeList.clear(); }}

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) {{ pool.reserve(nodes); }}

    static int make(T x) {{
        int t;
        if (!freeList.empty()) t = freeList.back(), freeList.pop_back();
        else pool.push_back(Node{{}}), t = (int)pool.size() - 1;
        pool[t] = Node{{}};
        pool[t].key = x, pool[t].prio = rng();
        return t;
    }}

    static void pull(int t) {{
        Node& v = pool[t];
        const Node &a = pool[v.l], &b = pool[v.r];
        v.z = a.z + b.z + v.c;
        v.dn = a.dn + b.dn + 1;  @mex
        v.xr = a.xr ^ b.xr ^ (v.c & 1 ? v.key : T(0));  @xor
        v.orv = a.orv | b.orv | v.key;  @or
        v.andv = a.andv & b.andv & v.key;  @and
{"        v.s = a.s + b.s + S(v.c) * v.key;" + chr(10) if s else ""}    }}

    static void split(int t, T x, int& a, int& b) {{  // (keys < x, keys >= x)
        if (!t) {{
            a = b = 0;
            return;
        }}
        if (pool[t].key < x) {{
            int ra, rb;
            split(pool[t].r, x, ra, rb);
            pool[t].r = ra, pull(t), a = t, b = rb;
        }} else {{
            int la, lb;
            split(pool[t].l, x, la, lb);
            pool[t].l = lb, pull(t), a = la, b = t;
        }}
    }}

    static void splitLe(int t, const T& x, int& a, int& b) {{  // a: keys <= x, b: keys > x
        if (!t) {{
            a = b = 0;
            return;
        }}
        if (x < pool[t].key) {{
            int la, lb;
            splitLe(pool[t].l, x, la, lb);
            pool[t].l = lb, pull(t), a = la, b = t;
        }} else {{
            int ra, rb;
            splitLe(pool[t].r, x, ra, rb);
            pool[t].r = ra, pull(t), a = t, b = rb;
        }}
    }}

    static int merge(int a, int b) {{  // every key in a < every key in b
        if (!a || !b) return a ? a : b;
        if (pool[a].prio > pool[b].prio) {{
            int r = merge(pool[a].r, b);
            pool[a].r = r, pull(a);
            return a;
        }}
        int l = merge(a, pool[b].l);
        pool[b].l = l, pull(b);
        return b;
    }}

    long long insert(T x, long long c) {{  // returns x's new count
        int a, b, m;
        split(root, x, a, b);
        splitLe(b, x, m, b);  // m: the node of x, or 0
        if (!m) m = make(x), d++;
        long long f = pool[m].c += c;
        if (f) pull(m);
        else freeList.push_back(m), m = 0, d--;
        root = merge(merge(a, m), b);
        return f;
    }}
''' + bst_common_cpp(s)
    comps = {op: "log(N) expected" for op in OPS}
    comps.update({"size": "1", "sumAll": "1", "countDistinct": "1", "min": "1", "max": "1", "build": "1"})
    node = "key[1*N] cnt[1*N] size[1*N]" + (" dn[1*N]" if M else "") + (" sum[1*N]" if s else "") + "".join(
        f" {f}[1*N]" for f, on in (("xor", X), ("or", O), ("and", A)) if on)
    comps.update({"xorOfAll": "1", "orOfAll": "1", "andOfAll": "1"})
    return dict(name="TreapMultiset", dtype="treap", values="online", py=keep_aggs(keep_mex(py, M), X, O, A),
                cpp=keep_aggs(keep_mex(cpp, M), X, O, A), comps=comps, mex=M, bits=bits,
                mem=("none", node, "none", "children[2*N] prio[1*N]"),
                note="N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, "
                     "call resetPool() between test cases; Python: parallel lists per tree")


def avl(sums, mex, bits=(False, False, False)):
    s, M = sums, mex
    X, O, A = bits
    agg = "".join(f", {w}" for w, on in (("xor", X), ("OR", O), ("AND", A)) if on)
    py = f'''
# Ordered multiset (online: any values, nothing known ahead): an AVL tree with one node per distinct value, so every
# operation is O(log N) worst case (height <= 1.44 log2 N). Each node keeps its value, its copies, and the copies{", sum" if s else ""}{agg}
# {"and distinct values " if M else ""}in its subtree. Nodes live in parallel lists (a node pool; node 0 is the empty tree) and removed
# nodes are reused.


class AVLMultiset:
    __slots__ = ("K", "C", "Z",{' "S",' if s else ""}{' "X",' if X else ""}{' "O",' if O else ""}{' "A",' if A else ""}{' "D",' if M else ""} "H", "L", "R", "free", "root", "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z{", self.S" if s else ""} = [0], [0], [0]{", [0]" if s else ""}  # key, copies, copies below{", sum below" if s else ""}
        self.D = [0]  # distinct values below  @mex
        self.X = [0]  # xor of the values below with an odd count  @xor
        self.O = [0]  # OR of the values below  @or
        self.A = [-1]  # AND of the values below (the empty tree's: every bit)  @and
        self.H, self.L, self.R = [0], [0], [0]  # height (empty tree 0), children
        self.free = []  # removed nodes, reused first
        self.root = self.n = {"self.total = " if s else ""}self.d = 0

    def _new(self, x, c):
        if self.free:
            t = self.free.pop()
            self.K[t], self.C[t], self.L[t], self.R[t] = x, c, 0, 0
            return t
        self.K.append(x)
        self.C.append(c)
        self.Z.append(0)
{"        self.S.append(0)" + chr(10) if s else ""}        self.D.append(0)  @mex
        self.X.append(0)  @xor
        self.O.append(0)  @or
        self.A.append(-1)  @and
        self.H.append(0)
        self.L.append(0)
        self.R.append(0)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
{"        self.S[t] = self.S[l] + self.S[r] + self.C[t] * self.K[t]" + chr(10) if s else ""}        self.D[t] = self.D[l] + self.D[r] + 1  @mex
        self.X[t] = self.X[l] ^ self.X[r] ^ (self.K[t] if self.C[t] & 1 else 0)  @xor
        self.O[t] = self.O[l] | self.O[r] | self.K[t]  @or
        self.A[t] = self.A[l] & self.A[r] & self.K[t]  @and
        hl, hr = self.H[l], self.H[r]
        self.H[t] = (hl if hl > hr else hr) + 1

    def _rotR(self, t):  # t's left child moves up
        L, R = self.L, self.R
        l = L[t]
        L[t], R[l] = R[l], t
        self._pull(t)
        self._pull(l)
        return l

    def _rotL(self, t):  # t's right child moves up
        L, R = self.L, self.R
        r = R[t]
        R[t], L[r] = L[r], t
        self._pull(t)
        self._pull(r)
        return r

    def _bal(self, t):  # pull t and restore |height(left) - height(right)| <= 1; returns the subtree's new root
        H, L, R = self.H, self.L, self.R
        self._pull(t)
        b = H[L[t]] - H[R[t]]
        if b > 1:
            if H[L[L[t]]] < H[R[L[t]]]:
                L[t] = self._rotL(L[t])
            return self._rotR(t)
        if b < -1:
            if H[R[R[t]]] < H[L[R[t]]]:
                R[t] = self._rotR(R[t])
            return self._rotL(t)
        return t

    def _popMin(self, t):  # (t without its smallest node, that node)
        if not self.L[t]:
            return self.R[t], t
        self.L[t], m = self._popMin(self.L[t])
        return self._bal(t), m

    def _ins(self, t, x, c):  # c copies of x into subtree t; returns its new root
        if not t:
            self.d += 1
            self.newCount = c  @newcount
            t = self._new(x, c)
            self._pull(t)
            return t
        K = self.K
        if x < K[t]:
            self.L[t] = self._ins(self.L[t], x, c)
        elif x > K[t]:
            self.R[t] = self._ins(self.R[t], x, c)
        else:
            self.C[t] += c
            self.newCount = self.C[t]  @newcount
            if not self.C[t]:  # x is gone: replace its node by the smallest node on its right
                self.d -= 1
                self.free.append(t)
                l, r = self.L[t], self.R[t]
                if not l or not r:
                    return l or r
                r, m = self._popMin(r)
                self.L[m], self.R[m] = l, r
                return self._bal(m)
        return self._bal(t)

    def _insert(self, x, c):
        self.root = self._ins(self.root, x, c)
        return self.newCount  # (x's new count)  @newcount
''' + bst_common_py(s)
    sfield = "S s; " if s else ""
    cpp = f'''
// Ordered multiset (online: any values, nothing known ahead): an AVL tree with one node per distinct value, so every
// operation is O(log N) worst case (height <= 1.44 log2 N). Each node keeps its value, its copies, and the copies{", sum" if s else ""}{agg}
// {"and distinct values " if M else ""}in its subtree. Nodes live in one pool shared by every AVLMultiset<T> (call resetPool() between
// test cases); node 0 is the empty tree and removed nodes are reused. T: an integer type; sums in S.
template <typename T>
struct AVLMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node {{ T key; long long c, z; {sfield}{"long long dn; " if M else ""}{"T xr; " if X else ""}{"T orv; " if O else ""}{"T andv = ~T(0); " if A else ""}int h, l, r; }};  // copies; copies{", sum" if s else ""}{", distinct" if M else ""} below; height
    static inline vector<Node> pool{{Node{{}}}};
    static inline vector<int> freeList;
    int root = 0;
    long long n = 0, d = 0;
{"    S total = 0;" + chr(10) if s else ""}
    // O(1) -- an empty multiset
    AVLMultiset() {{}}

    // O(1) -- forget every node of every AVLMultiset<T>; call between test cases, then build new ones
    static void resetPool() {{ pool.resize(1), freeList.clear(); }}

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) {{ pool.reserve(nodes); }}

    static int make(T x, long long c) {{
        int t;
        if (!freeList.empty()) t = freeList.back(), freeList.pop_back();
        else pool.push_back(Node{{}}), t = (int)pool.size() - 1;
        pool[t] = Node{{}};
        pool[t].key = x, pool[t].c = c;
        pull(t);
        return t;
    }}

    static void pull(int t) {{
        Node& v = pool[t];
        const Node &a = pool[v.l], &b = pool[v.r];
        v.z = a.z + b.z + v.c, v.h = std::max(a.h, b.h) + 1;
        v.dn = a.dn + b.dn + 1;  @mex
        v.xr = a.xr ^ b.xr ^ (v.c & 1 ? v.key : T(0));  @xor
        v.orv = a.orv | b.orv | v.key;  @or
        v.andv = a.andv & b.andv & v.key;  @and
{"        v.s = a.s + b.s + S(v.c) * v.key;" + chr(10) if s else ""}    }}

    static int rotR(int t) {{  // t's left child moves up
        int l = pool[t].l;
        pool[t].l = pool[l].r, pool[l].r = t;
        pull(t), pull(l);
        return l;
    }}

    static int rotL(int t) {{  // t's right child moves up
        int r = pool[t].r;
        pool[t].r = pool[r].l, pool[r].l = t;
        pull(t), pull(r);
        return r;
    }}

    static int bal(int t) {{  // pull t and restore |height(left) - height(right)| <= 1; returns the subtree's new root
        pull(t);
        int b = pool[pool[t].l].h - pool[pool[t].r].h;
        if (b > 1) {{
            int l = pool[t].l;
            if (pool[pool[l].l].h < pool[pool[l].r].h) pool[t].l = rotL(l);
            return rotR(t);
        }}
        if (b < -1) {{
            int r = pool[t].r;
            if (pool[pool[r].r].h < pool[pool[r].l].h) pool[t].r = rotR(r);
            return rotL(t);
        }}
        return t;
    }}

    static int popMin(int t, int& m) {{  // t without its smallest node, which goes to m
        if (!pool[t].l) {{
            m = t;
            return pool[t].r;
        }}
        int l = popMin(pool[t].l, m);
        pool[t].l = l;
        return bal(t);
    }}

    int ins(int t, T x, long long c) {{  // c copies of x into subtree t; returns its new root
        if (!t) {{
            d++;
            newCount = c;  @newcount
            return make(x, c);
        }}
        if (x < pool[t].key) {{
            int l = ins(pool[t].l, x, c);
            pool[t].l = l;
        }} else if (pool[t].key < x) {{
            int r = ins(pool[t].r, x, c);
            pool[t].r = r;
        }} else if (!(pool[t].c += c)) {{  // x is gone: replace its node by the smallest node on its right  @nonewcount
        }} else if (!(newCount = pool[t].c += c)) {{  // x is gone: replace its node by the smallest node on its right  @newcount
            d--, freeList.push_back(t);
            int l = pool[t].l, r = pool[t].r, m;
            if (!l || !r) return l ? l : r;
            r = popMin(r, m);
            pool[m].l = l, pool[m].r = r;
            return bal(m);
        }}
        return bal(t);
    }}

    long long newCount = 0;  // ins leaves x's new count here  @newcount
    void insert(T x, long long c) {{ root = ins(root, x, c); }}  @nonewcount
    long long insert(T x, long long c) {{ root = ins(root, x, c); return newCount; }}  // returns x's new count  @newcount
''' + bst_common_cpp(s)
    comps = {op: "log(N)" for op in OPS}
    comps.update({"size": "1", "sumAll": "1", "countDistinct": "1", "build": "1"})
    node = "key[1*N] cnt[1*N] size[1*N]" + (" dn[1*N]" if M else "") + (" sum[1*N]" if s else "") + "".join(
        f" {f}[1*N]" for f, on in (("xor", X), ("or", O), ("and", A)) if on)
    comps.update({"xorOfAll": "1", "orOfAll": "1", "andOfAll": "1"})
    return dict(name="AVLMultiset", dtype="avl", values="online", py=keep_aggs(keep_mex(py, M), X, O, A),
                cpp=keep_aggs(keep_mex(cpp, M), X, O, A), comps=comps, mex=M, bits=bits,
                mem=("none", node, "none", "children[2*N] height[1*N]"),
                note="N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, "
                     "call resetPool() between test cases; Python: parallel lists per tree")


def splay_walks_py(s):
    """The AVL walks (bst_common_py), but each splays the last node it visited, which is what makes the splay tree's
    bounds amortized O(log N)."""
    return f'''
    def _lt(self, x):  # copies of values < x
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if K[t] < x:
                res += Z[L[t]] + C[t]
                t = R[t]
            else:
                t = L[t]
        self._touch(last)
        return res

    def _le(self, x):  # copies of values <= x
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if x < K[t]:
                t = L[t]
            else:
                res += Z[L[t]] + C[t]
                t = R[t]
        self._touch(last)
        return res

    def _countOf(self, x):
        K, L, R = self.K, self.L, self.R
        t, last = self.root, 0
        while t and K[t] != x:
            last = t
            t = L[t] if x < K[t] else R[t]
        self._touch(t or last)
        return self.C[t]
{f"""
    def _slt(self, x):  # sum of the values < x
        K, C, S, L, R = self.K, self.C, self.S, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if K[t] < x:
                res += S[L[t]] + C[t] * K[t]
                t = R[t]
            else:
                t = L[t]
        self._touch(last)
        return res

    def _sle(self, x):  # sum of the values <= x
        K, C, S, L, R = self.K, self.C, self.S, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if x < K[t]:
                t = L[t]
            else:
                res += S[L[t]] + C[t] * K[t]
                t = R[t]
        self._touch(last)
        return res
""" if s else ""}
    def _kth(self, k):
        K, C, Z, L, R = self.K, self.C, self.Z, self.L, self.R
        t = self.root
        while True:
            zl = Z[L[t]]
            if k <= zl:
                t = L[t]
            elif k <= zl + C[t]:
                self._touch(t)
                return K[t]
            else:
                k -= zl + C[t]
                t = R[t]
    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies{", sum before it" if s else ""})
        K, C, Z,{" S," if s else ""} L, R = self.K, self.C, self.Z,{" self.S," if s else ""} self.L, self.R
        t, before{", acc" if s else ""} = self.root, 0{", 0" if s else ""}
        while True:
            l = L[t]
            zl = before + Z[l]
            if k <= zl:
                t = l
            elif k <= zl + C[t]:
                res = K[t], zl, C[t]{", acc + S[l]" if s else ""}
                self._touch(t)
                return res
            else:
                before = zl + C[t]
{"                acc += S[l] + C[t] * K[t]" + chr(10) if s else ""}                t = R[t]
@mex{{
    def _distinctLt(self, x):  # distinct values < x
        K, D, L, R = self.K, self.D, self.L, self.R
        t, res, last = self.root, 0, 0
        while t:
            last = t
            if K[t] < x:
                res += D[L[t]] + 1
                t = R[t]
            else:
                t = L[t]
        self._touch(last)
        return res

    # smallest non-negative integer not in the set. With c0 distinct negatives, the distinct values >= 0
    # in order v_0 < v_1 < ... satisfy v_j >= j, and v_j == j means 0..v_j are all present; the answer is the first j
    # with v_j > j (or how many there are). One walk down: at a node of distinct rank c0 + j, go right if v_j == j.
    def _findMex(self):
        K, D, L, R = self.K, self.D, self.L, self.R
        c0 = self._distinctLt(0)
        t, before, last, res = self.root, -c0, 0, self.d - c0  # before: distinct values >= 0 left of t's subtree
        while t:
            last = t
            j = before + D[L[t]]
            if K[t] < 0 or K[t] == j:
                before = j + 1
                t = R[t]
            else:
                res = j
                t = L[t]
        self._touch(last)
        return res
@mex}}
'''


def splay_walks_cpp(s):
    return f'''
    long long lt(T x) {{  // copies of values < x
        int t = root, last = 0;
        long long res = 0;
        while (t) {{
            last = t;
            if (pool[t].key < x) res += pool[pool[t].l].z + pool[t].c, t = pool[t].r;
            else t = pool[t].l;
        }}
        touch(last);
        return res;
    }}

    long long le(T x) {{  // copies of values <= x
        int t = root, last = 0;
        long long res = 0;
        while (t) {{
            last = t;
            if (x < pool[t].key) t = pool[t].l;
            else res += pool[pool[t].l].z + pool[t].c, t = pool[t].r;
        }}
        touch(last);
        return res;
    }}

    long long countOf(T x) {{
        int t = root, last = 0;
        while (t && pool[t].key != x) last = t, t = x < pool[t].key ? pool[t].l : pool[t].r;
        touch(t ? t : last);
        return pool[t].c;
    }}
{f"""
    S slt(T x) {{  // sum of the values < x
        int t = root, last = 0;
        S res = 0;
        while (t) {{
            last = t;
            if (pool[t].key < x) res += pool[pool[t].l].s + S(pool[t].c) * pool[t].key, t = pool[t].r;
            else t = pool[t].l;
        }}
        touch(last);
        return res;
    }}

    S sle(T x) {{  // sum of the values <= x
        int t = root, last = 0;
        S res = 0;
        while (t) {{
            last = t;
            if (x < pool[t].key) t = pool[t].l;
            else res += pool[pool[t].l].s + S(pool[t].c) * pool[t].key, t = pool[t].r;
        }}
        touch(last);
        return res;
    }}
""" if s else ""}
    T kthAt(long long k) {{
        int t = root;
        while (true) {{
            long long zl = pool[pool[t].l].z;
            if (k <= zl) t = pool[t].l;
            else if (k <= zl + pool[t].c) {{
                touch(t);
                return pool[t].key;
            }} else k -= zl + pool[t].c, t = pool[t].r;
        }}
    }}
    Info kthInfo(long long k) {{  // the k-th smallest, copies before it, its copies{", sum before it" if s else ""}
        int t = root;
        long long before = 0;
{"        S acc = 0;" + chr(10) if s else ""}        while (true) {{
            const Node& v = pool[t];
            long long zl = before + pool[v.l].z;
            if (k <= zl) t = v.l;
            else if (k <= zl + v.c) {{
                Info res{{v.key, zl, v.c{", acc + pool[v.l].s" if s else ""}}};
                touch(t);
                return res;
            }} else before = zl + v.c{", acc += pool[v.l].s + S(v.c) * v.key" if s else ""}, t = v.r;
        }}
    }}
@mex{{
    long long distinctLt(T x) {{  // distinct values < x
        int t = root, last = 0;
        long long res = 0;
        while (t) {{
            last = t;
            if (pool[t].key < x) res += pool[pool[t].l].dn + 1, t = pool[t].r;
            else t = pool[t].l;
        }}
        touch(last);
        return res;
    }}

    // smallest non-negative integer not in the set. With c0 distinct negatives, the distinct values >= 0
    // in order v_0 < v_1 < ... satisfy v_j >= j, and v_j == j means 0..v_j are all present; the answer is the first j
    // with v_j > j (or how many there are). One walk down: at a node of distinct rank c0 + j, go right if v_j == j.
    long long findMex() {{
        long long c0 = distinctLt(0), before = -c0, res = d - c0;  // before: distinct values >= 0 left of t's subtree
        int t = root, last = 0;
        while (t) {{
            last = t;
            long long j = before + pool[pool[t].l].dn;
            if (pool[t].key < 0 || pool[t].key == T(j)) before = j + 1, t = pool[t].r;
            else res = j, t = pool[t].l;
        }}
        touch(last);
        return res;
    }}
@mex}}
'''


def splay(sums, mex, bits=(False, False, False)):
    s, M = sums, mex
    X, O, A = bits
    agg = "".join(f", {w}" for w, on in (("xor", X), ("OR", O), ("AND", A)) if on)
    py = f'''
# Ordered multiset (online: any values, nothing known ahead): a splay tree with one node per distinct value. Each node
# keeps its value, its copies, and the copies{", sum" if s else ""}{agg}{" and distinct values" if M else ""} in its subtree; every operation splays the
# last node it touched to the root, which makes each one O(log N) amortized. Nodes live in parallel lists (a node pool;
# node 0 is the empty tree) and removed nodes are reused.


class SplayMultiset:
    __slots__ = ("K", "C", "Z",{' "S",' if s else ""}{' "X",' if X else ""}{' "O",' if O else ""}{' "A",' if A else ""}{' "D",' if M else ""} "L", "R", "P", "free", "root", "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z{", self.S" if s else ""} = [0], [0], [0]{", [0]" if s else ""}  # key, copies, copies below{", sum below" if s else ""}
        self.D = [0]  # distinct values below  @mex
        self.X = [0]  # xor of the values below with an odd count  @xor
        self.O = [0]  # OR of the values below  @or
        self.A = [-1]  # AND of the values below (the empty tree's: every bit)  @and
        self.L, self.R, self.P = [0], [0], [0]  # children, parent
        self.free = []  # removed nodes, reused first
        self.root = self.n = {"self.total = " if s else ""}self.d = 0

    def _new(self, x, parent):
        if self.free:
            t = self.free.pop()
            self.K[t], self.C[t], self.L[t], self.R[t], self.P[t] = x, 0, 0, 0, parent
            return t
        self.K.append(x)
        self.C.append(0)
        self.Z.append(0)
{"        self.S.append(0)" + chr(10) if s else ""}        self.D.append(0)  @mex
        self.X.append(0)  @xor
        self.O.append(0)  @or
        self.A.append(-1)  @and
        self.L.append(0)
        self.R.append(0)
        self.P.append(parent)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
{"        self.S[t] = self.S[l] + self.S[r] + self.C[t] * self.K[t]" + chr(10) if s else ""}        self.D[t] = self.D[l] + self.D[r] + 1  @mex
        self.X[t] = self.X[l] ^ self.X[r] ^ (self.K[t] if self.C[t] & 1 else 0)  @xor
        self.O[t] = self.O[l] | self.O[r] | self.K[t]  @or
        self.A[t] = self.A[l] & self.A[r] & self.K[t]  @and

    def _rotate(self, x):  # x moves above its parent
        L, R, P = self.L, self.R, self.P
        p = P[x]
        g = P[p]
        if L[p] == x:
            b = R[x]
            L[p], R[x] = b, p
        else:
            b = L[x]
            R[p], L[x] = b, p
        if b:
            P[b] = p
        P[p], P[x] = x, g
        if g:
            if L[g] == p:
                L[g] = x
            else:
                R[g] = x
        self._pull(p)
        self._pull(x)

    def _splay(self, x):  # x becomes the root of its tree
        P, L = self.P, self.L
        while P[x]:
            p = P[x]
            g = P[p]
            if g:
                self._rotate(p if (L[g] == p) == (L[p] == x) else x)
            self._rotate(x)
        return x

    def _touch(self, t):
        if t:
            self.root = self._splay(t)

    def _insert(self, x, c):
        K, L, R = self.K, self.L, self.R
        t = self.root
        while t and K[t] != x:
            nxt = L[t] if x < K[t] else R[t]
            if not nxt:
                break
            t = nxt
        if t and K[t] == x:  # x is already here
            f = self.C[t] = self.C[t] + c
            self._pull(t)
            self.root = self._splay(t)
            if not f:
                self._erase(t)
            return f  # (x's new count)
        u = self._new(x, t)
        self.C[u] = c
        self._pull(u)
        if t:
            if x < K[t]:
                L[t] = u
            else:
                R[t] = u
        self.root = self._splay(u)
        self.d += 1
        return c

    def _erase(self, t):  # t is the root
        L, R, P = self.L, self.R, self.P
        l, r = L[t], R[t]
        if l:
            P[l] = 0
        if r:
            P[r] = 0
        if not l:
            self.root = r
        else:
            m = l
            while R[m]:
                m = R[m]
            m = self._splay(m)  # the largest key on the left becomes the left tree's root, with no right child
            R[m] = r
            if r:
                P[r] = m
            self._pull(m)
            self.root = m
        self.free.append(t)
        self.d -= 1
''' + splay_walks_py(s)
    sfield = "S s; " if s else ""
    cpp = f'''
// Ordered multiset (online: any values, nothing known ahead): a splay tree with one node per distinct value. Each node
// keeps its value, its copies, and the copies{", sum" if s else ""}{agg}{" and distinct values" if M else ""} in its subtree; every operation splays the
// last node it touched to the root, which makes each one O(log N) amortized. Nodes live in one pool shared by every
// SplayMultiset<T> (call resetPool() between test cases); node 0 is the empty tree and removed nodes are reused.
// T: an integer type; sums in S (long long for small T).
template <typename T>
struct SplayMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node {{ T key; long long c, z; {sfield}{"long long dn; " if M else ""}{"T xr; " if X else ""}{"T orv; " if O else ""}{"T andv = ~T(0); " if A else ""}int l, r, p; }};  // copies; copies{", sum" if s else ""}{", distinct" if M else ""} below; parent
    static inline vector<Node> pool{{Node{{}}}};
    static inline vector<int> freeList;
    int root = 0;
    long long n = 0, d = 0;
{"    S total = 0;" + chr(10) if s else ""}
    // O(1) -- an empty multiset
    SplayMultiset() {{}}

    // O(1) -- forget every node of every SplayMultiset<T>; call between test cases, then build new ones
    static void resetPool() {{ pool.resize(1), freeList.clear(); }}

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) {{ pool.reserve(nodes); }}

    static int make(T x, int parent) {{
        int t;
        if (!freeList.empty()) t = freeList.back(), freeList.pop_back();
        else pool.push_back(Node{{}}), t = (int)pool.size() - 1;
        pool[t] = Node{{}};
        pool[t].key = x, pool[t].p = parent;
        return t;
    }}

    static void pull(int t) {{
        Node& v = pool[t];
        const Node &a = pool[v.l], &b = pool[v.r];
        v.z = a.z + b.z + v.c;
        v.dn = a.dn + b.dn + 1;  @mex
        v.xr = a.xr ^ b.xr ^ (v.c & 1 ? v.key : T(0));  @xor
        v.orv = a.orv | b.orv | v.key;  @or
        v.andv = a.andv & b.andv & v.key;  @and
{"        v.s = a.s + b.s + S(v.c) * v.key;" + chr(10) if s else ""}    }}

    static void rotate(int x) {{  // x moves above its parent
        int p = pool[x].p, g = pool[p].p, b;
        if (pool[p].l == x) b = pool[x].r, pool[p].l = b, pool[x].r = p;
        else b = pool[x].l, pool[p].r = b, pool[x].l = p;
        if (b) pool[b].p = p;
        pool[p].p = x, pool[x].p = g;
        if (g) (pool[g].l == p ? pool[g].l : pool[g].r) = x;
        pull(p), pull(x);
    }}

    static int splay(int x) {{  // x becomes the root of its tree
        while (int p = pool[x].p) {{
            if (int g = pool[p].p) rotate((pool[g].l == p) == (pool[p].l == x) ? p : x);
            rotate(x);
        }}
        return x;
    }}

    void touch(int t) {{
        if (t) root = splay(t);
    }}

    long long insert(T x, long long c) {{  // returns x's new count
        int t = root;
        while (t && pool[t].key != x) {{
            int nxt = x < pool[t].key ? pool[t].l : pool[t].r;
            if (!nxt) break;
            t = nxt;
        }}
        if (t && pool[t].key == x) {{  // x is already here
            long long f = pool[t].c += c;
            pull(t);
            root = splay(t);
            if (!f) erase(t);
            return f;
        }}
        int u = make(x, t);
        pool[u].c = c;
        pull(u);
        if (t) (x < pool[t].key ? pool[t].l : pool[t].r) = u;
        root = splay(u);
        d++;
        return c;
    }}

    void erase(int t) {{  // t is the root
        int l = pool[t].l, r = pool[t].r;
        if (l) pool[l].p = 0;
        if (r) pool[r].p = 0;
        if (!l) root = r;
        else {{
            int m = l;
            while (pool[m].r) m = pool[m].r;
            m = splay(m);  // the largest key on the left becomes the left tree's root, with no right child
            pool[m].r = r;
            if (r) pool[r].p = m;
            pull(m);
            root = m;
        }}
        freeList.push_back(t);
        d--;
    }}
''' + splay_walks_cpp(s)
    comps = {op: "log(N) amortized" for op in OPS}
    comps.update({"size": "1", "sumAll": "1", "countDistinct": "1", "min": "1", "max": "1", "build": "1"})
    node = "key[1*N] cnt[1*N] size[1*N]" + (" dn[1*N]" if M else "") + (" sum[1*N]" if s else "") + "".join(
        f" {f}[1*N]" for f, on in (("xor", X), ("or", O), ("and", A)) if on)
    comps.update({"xorOfAll": "1", "orOfAll": "1", "andOfAll": "1"})
    return dict(name="SplayMultiset", dtype="splay", values="online", py=keep_aggs(keep_mex(py, M), X, O, A),
                cpp=keep_aggs(keep_mex(cpp, M), X, O, A), comps=comps, mex=M, bits=bits,
                mem=("none", node, "none", "children[2*N] parent[1*N]"),
                note="N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, "
                     "call resetPool() between test cases; Python: parallel lists per tree")


def blocks(sums, bits=(False, False, False)):
    s = sums
    X, O, A = bits
    words = [w for w, on in (("xor", X), ("OR", O), ("AND", A)) if on]
    agg = " and each block's " + " / ".join(words) if words else ""
    ops_imp = [f for f, on in (("and_", X or A), ("or_", O), ("xor", X)) if on]
    imports = (("from functools import reduce\n" if X or O or A else "") + (
        "from itertools import accumulate" + (", compress, repeat" if X else "") + "\n") + (
        "from operator import " + ", ".join(ops_imp) + "\n" if ops_imp else "")).rstrip("\n")
    py = f'''from bisect import bisect_left, bisect_right, insort
{imports}


# Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
# LOAD..2*LOAD, each block keeping its values' copies{" and copies * value" if s else ""} plus block totals{agg}, and a Fenwick tree over the
# block totals (rebuilt only after a block splits or empties). A query finds its block by binary search (or by
# lifting over the block Fenwick for k-th) and then works inside one block with C-level list operations.


class BlockMultiset:
    LOAD = 64
    __slots__ = ("keys", "cnts",{' "sums",' if s else ""} "maxes", "bc",{' "bs",' if s else ""} "fc",{' "fs",' if s else ""}{' "bx", "fx",' if X else ""}{' "bo",' if O else ""}{' "ba",' if A else ""} "cnt", "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.keys = []  # blocks of sorted distinct values
        self.cnts = []  # per block: copies of each value
{"        self.sums = []  # per block: copies * value" + chr(10) if s else ""}        self.maxes = []  # last value of each block
        self.bc = []  # per block: total copies
{"        self.bs = []  # per block: total sum" + chr(10) if s else ""}        self.fc = None  # Fenwick over bc (None: stale)
{"        self.fs = None  # Fenwick over bs (None: stale)" + chr(10) if s else ""}        self.bx = []  # per block: xor of the values with an odd count  @xor
        self.fx = None  # xor Fenwick over bx (None: stale)  @xor
        self.bo = []  # per block: OR of its values  @or
        self.ba = []  # per block: AND of its values  @and
        self.cnt = {{}}  # value -> copies
        self.n = {"self.total = " if s else ""}self.d = 0

    @staticmethod
    def _build(a):
        f = [0] + a
        for i in range(1, len(f)):
            j = i + (i & -i)
            if j < len(f):
                f[j] += f[i]
        return f

    @staticmethod
    def _fen(f, i, v):
        if f is not None:
            i += 1
            while i < len(f):
                f[i] += v
                i += i & -i

    def _pre(self, which, k):  # total of blocks 0..k-1
        f = self.fc if which == 0 else {"self.fs" if s else "None"}
        if f is None:
            f = self._build(self.bc if which == 0 else {"self.bs" if s else "None"})
            if which == 0:
                self.fc = f
{"            else:" + chr(10) + "                self.fs = f" + chr(10) if s else ""}        res = 0
        while k > 0:
            res += f[k]
            k &= k - 1
        return res

    def _insert(self, x, c):
        old = self.cnt.get(x, 0)
        if old:
            k = bisect_left(self.maxes, x)
            j = bisect_left(self.keys[k], x)
            if c & 1:  # x's parity flips  @xor
                self.bx[k] ^= x  @xor
                self._fenx(self.fx, k, x)  @xor
            if old + c:
                self.cnt[x] = old + c
                self.cnts[k][j] += c
{"                self.sums[k][j] += c * x" + chr(10) if s else ""}                self.bc[k] += c
                self._fen(self.fc, k, c)
{"                self.bs[k] += c * x" + chr(10) + "                self._fen(self.fs, k, c * x)" + chr(10) if s else ""}                return old + c
            del self.cnt[x]
            self.d -= 1
            del self.keys[k][j], self.cnts[k][j]
{"            del self.sums[k][j]" + chr(10) if s else ""}            if not self.keys[k]:  # the block is empty: drop it
                del self.keys[k], self.cnts[k], self.maxes[k], self.bc[k]
{"                del self.sums[k], self.bs[k]" + chr(10) if s else ""}                del self.bx[k]  @xor
                del self.bo[k]  @or
                del self.ba[k]  @and
                self.fc = {"self.fs = " if s else ""}None
                self.fx = None  @xor
                return 0
            self.maxes[k] = self.keys[k][-1]
            self.bo[k] = reduce(or_, self.keys[k], 0)  # x left: the block's OR / AND again  @or
            self.ba[k] = reduce(and_, self.keys[k], -1)  @and
            self.bc[k] += c
            self._fen(self.fc, k, c)
{"            self.bs[k] += c * x" + chr(10) + "            self._fen(self.fs, k, c * x)" + chr(10) if s else ""}            return 0
        self.cnt[x] = c
        self.d += 1
        if not self.keys:
            self.keys.append([x])
            self.cnts.append([c])
{"            self.sums.append([c * x])" + chr(10) if s else ""}            self.maxes.append(x)
            self.bc.append(c)
{"            self.bs.append(c * x)" + chr(10) if s else ""}            self.bx.append(x if c & 1 else 0)  @xor
            self.bo.append(x)  @or
            self.ba.append(x)  @and
            self.fc = {"self.fs = " if s else ""}None
            self.fx = None  @xor
            return c
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            k -= 1
        j = bisect_left(self.keys[k], x)
        self.keys[k].insert(j, x)
        self.cnts[k].insert(j, c)
{"        self.sums[k].insert(j, c * x)" + chr(10) if s else ""}        self.maxes[k] = self.keys[k][-1]
        self.bc[k] += c
        self._fen(self.fc, k, c)
{"        self.bs[k] += c * x" + chr(10) + "        self._fen(self.fs, k, c * x)" + chr(10) if s else ""}        if c & 1:  @xor
            self.bx[k] ^= x  @xor
            self._fenx(self.fx, k, x)  @xor
        self.bo[k] |= x  @or
        self.ba[k] &= x  @and
        if len(self.keys[k]) > 2 * self.LOAD:  # split the block in half
            h = self.LOAD
            for arr in (self.keys, self.cnts{", self.sums" if s else ""}):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
{"            self.bs[k:k + 1] = [sum(self.sums[k]), sum(self.sums[k + 1])]" + chr(10) if s else ""}            self.bx[k:k + 1] = [self._xodd(self.keys[k], self.cnts[k]), self._xodd(self.keys[k + 1], self.cnts[k + 1])]  @xor
            self.bo[k:k + 1] = [reduce(or_, self.keys[k], 0), reduce(or_, self.keys[k + 1], 0)]  @or
            self.ba[k:k + 1] = [reduce(and_, self.keys[k], -1), reduce(and_, self.keys[k + 1], -1)]  @and
            self.fc = {"self.fs = " if s else ""}None
            self.fx = None  @xor
        return c

    def _count(self, x, strict, which):  # copies (which=0){" or sums (which=1)" if s else ""} of the values < x (strict) or <= x
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            return self.n{" if which == 0 else self.total" if s else ""}
        j = (bisect_left if strict else bisect_right)(self.keys[k], x)
        return self._pre(which, k) + sum((self.cnts{" if which == 0 else self.sums" if s else ""})[k][:j])

    def _lt(self, x):
        return self._count(x, True, 0)

    def _le(self, x):
        return self._count(x, False, 0)

    def _countOf(self, x):
        return self.cnt.get(x, 0)
{f"""
    def _slt(self, x):
        return self._count(x, True, 1)

    def _sle(self, x):
        return self._count(x, False, 1)
""" if s else ""}
    def _locate(self, k):  # (block, copies before it, {"sum before it" if s else "0"}) for the block holding the k-th smallest
        self._pre(0, 0)
{"        self._pre(1, 0)" + chr(10) if s else ""}        fc{", fs" if s else ""} = self.fc{", self.fs" if s else ""}
        pos, before, acc = 0, 0, 0
        step = 1 << (len(self.bc).bit_length() - 1) if self.bc else 0
        while step:
            nxt = pos + step
            if nxt <= len(self.bc) and before + fc[nxt] < k:
                pos = nxt
                before += fc[nxt]
{"                acc += fs[nxt]" + chr(10) if s else ""}            step >>= 1
        return pos, before, acc

    def _kth(self, k):
        b, before, _ = self._locate(k)
        return self.keys[b][bisect_left(list(accumulate(self.cnts[b])), k - before)]
    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies{", sum before it" if s else ""})
        b, before, acc = self._locate(k)
        cn = self.cnts[b]
        pre = list(accumulate(cn))
        j = bisect_left(pre, k - before)
        return self.keys[b][j], before + pre[j] - cn[j], cn[j]{", acc + sum(self.sums[b][:j])" if s else ""}
    # smallest non-negative integer not in the set: walk the blocks from 0 while the values run 0, 1, 2, ...
    def _findMex(self):
        keys = self.keys
        k = bisect_left(self.maxes, 0)
        if k == len(keys):
            return 0
        j = bisect_left(keys[k], 0)
        want = 0
        while k < len(keys):
            blk = keys[k]
            if blk[j] != want:
                return want
            if blk[-1] - blk[j] == len(blk) - 1 - j:  # this block continues the run to its end
                want = blk[-1] + 1
                k, j = k + 1, 0
                continue
            a, b = j, len(blk) - 1  # the run breaks inside: first p with blk[p] - p > blk[j] - j
            while a < b:
                mid = (a + b) // 2
                if blk[mid] - mid > blk[j] - j:
                    b = mid
                else:
                    a = mid + 1
            return blk[a - 1] + 1
        return want
'''
    cpp = f'''
// Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
// LOAD..2*LOAD, each block keeping its values' copies{" and copies * value" if s else ""} plus block totals{agg}, and a Fenwick tree over the
// block totals (rebuilt only after a block splits or empties). A query finds its block by binary search (or by
// lifting over the block Fenwick for k-th) and then works inside one block. T: an integer type; sums in S.
template <typename T>
struct BlockMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr int LOAD = 512;
    vector<vector<T>> keys;  // blocks of sorted distinct values
    vector<vector<long long>> cnts;  // per block: copies of each value
{"    vector<vector<S>> sums;  // per block: copies * value" + chr(10) if s else ""}    vector<T> maxes;  // last value of each block
    vector<long long> bc, fc;  // per block total copies; Fenwick over it
{"    vector<S> bs, fs;  // per block total sum; Fenwick over it" + chr(10) if s else ""}    vector<T> bx, fx;  // per block xor of the values with an odd count; xor Fenwick over it  @xor
    vector<T> bo;  // per block OR of its values  @or
    vector<T> ba;  // per block AND of its values  @and
    bool stale = true;  // the Fenwicks need a rebuild
    long long n = 0, d = 0;
{"    S total = 0;" + chr(10) if s else ""}
    // O(1) -- an empty multiset
    BlockMultiset() {{}}

    template <class V>
    static void build(vector<V>& f, const vector<V>& a) {{
        f.assign(a.size() + 1, 0);
        for (size_t i = 1; i < f.size(); i++) {{
            f[i] += a[i - 1];
            size_t j = i + (i & -i);
            if (j < f.size()) f[j] += f[i];
        }}
    }}

    void fresh() {{
        if (!stale) return;
        build(fc, bc);
{"        build(fs, bs);" + chr(10) if s else ""}        buildx(fx, bx);  @xor
        stale = false;
    }}

    template <class V>
    void fen(vector<V>& f, int i, V v) {{
        if (stale) return;
        for (i++; i < (int)f.size(); i += i & -i) f[i] += v;
    }}

    template <class V>
    V pre(const vector<V>& f, int k) {{  // total of blocks 0..k-1
        fresh();
        V res = 0;
        for (; k > 0; k &= k - 1) res += f[k];
        return res;
    }}

    int blockOf(T x) const {{ return int(lower_bound(maxes.begin(), maxes.end(), x) - maxes.begin()); }}

    long long insert(T x, long long c) {{  // returns x's new count
        int k = blockOf(x);
        if (k < (int)keys.size()) {{
            int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
            if (j < (int)keys[k].size() && keys[k][j] == x) {{  // x is already here
                if (c & 1) bx[k] ^= x, fenx(k, x);  // x's parity flips  @xor
                if (cnts[k][j] + c) {{
                    cnts[k][j] += c, bc[k] += c, fen(fc, k, c);
{"                    sums[k][j] += S(c) * x, bs[k] += S(c) * x, fen(fs, k, S(c) * x);" + chr(10) if s else ""}                    return cnts[k][j];
                }}
                d--;
                keys[k].erase(keys[k].begin() + j), cnts[k].erase(cnts[k].begin() + j);
{"                sums[k].erase(sums[k].begin() + j);" + chr(10) if s else ""}                if (keys[k].empty()) {{  // the block is empty: drop it
                    keys.erase(keys.begin() + k), cnts.erase(cnts.begin() + k), maxes.erase(maxes.begin() + k), bc.erase(bc.begin() + k);
{"                    sums.erase(sums.begin() + k), bs.erase(bs.begin() + k);" + chr(10) if s else ""}                    bx.erase(bx.begin() + k);  @xor
                    bo.erase(bo.begin() + k);  @or
                    ba.erase(ba.begin() + k);  @and
                    stale = true;
                    return 0;
                }}
                bo[k] = accumulate(keys[k].begin(), keys[k].end(), T(0), bit_or<T>());  // x left: the block's OR / AND again  @or
                ba[k] = accumulate(keys[k].begin(), keys[k].end(), ~T(0), bit_and<T>());  @and
                maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
{"                bs[k] += S(c) * x, fen(fs, k, S(c) * x);" + chr(10) if s else ""}                return 0;
            }}
        }}
        d++;
        if (keys.empty()) {{
            keys.push_back({{x}}), cnts.push_back({{c}}), maxes.push_back(x), bc.push_back(c);
{"            sums.push_back({S(c) * x}), bs.push_back(S(c) * x);" + chr(10) if s else ""}            bx.push_back(c & 1 ? x : T(0));  @xor
            bo.push_back(x);  @or
            ba.push_back(x);  @and
            stale = true;
            return c;
        }}
        if (k == (int)keys.size()) k--;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        keys[k].insert(keys[k].begin() + j, x), cnts[k].insert(cnts[k].begin() + j, c);
{"        sums[k].insert(sums[k].begin() + j, S(c) * x), bs[k] += S(c) * x, fen(fs, k, S(c) * x);" + chr(10) if s else ""}        maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
        if (c & 1) bx[k] ^= x, fenx(k, x);  @xor
        bo[k] |= x;  @or
        ba[k] &= x;  @and
        if ((int)keys[k].size() > 2 * LOAD) {{  // split the block in half
            auto half = [&](auto& arr) {{
                arr.insert(arr.begin() + k + 1, decay_t<decltype(arr[k])>(arr[k].begin() + LOAD, arr[k].end()));
                arr[k].resize(LOAD);
            }};
            half(keys), half(cnts);
{"            half(sums);" + chr(10) if s else ""}            maxes[k] = keys[k].back(), maxes.insert(maxes.begin() + k + 1, keys[k + 1].back());
            bc[k] = accumulate(cnts[k].begin(), cnts[k].end(), 0LL);
            bc.insert(bc.begin() + k + 1, accumulate(cnts[k + 1].begin(), cnts[k + 1].end(), 0LL));
{"            bs[k] = accumulate(sums[k].begin(), sums[k].end(), S(0));" + chr(10) + "            bs.insert(bs.begin() + k + 1, accumulate(sums[k + 1].begin(), sums[k + 1].end(), S(0)));" + chr(10) if s else ""}            bx[k] = xodd(k), bx.insert(bx.begin() + k + 1, xodd(k + 1));  @xor
            bo[k] = accumulate(keys[k].begin(), keys[k].end(), T(0), bit_or<T>());  @or
            bo.insert(bo.begin() + k + 1, accumulate(keys[k + 1].begin(), keys[k + 1].end(), T(0), bit_or<T>()));  @or
            ba[k] = accumulate(keys[k].begin(), keys[k].end(), ~T(0), bit_and<T>());  @and
            ba.insert(ba.begin() + k + 1, accumulate(keys[k + 1].begin(), keys[k + 1].end(), ~T(0), bit_and<T>()));  @and
            stale = true;
        }}
        return c;
    }}

    long long countBelow(T x, bool strict) {{  // copies of the values < x (strict) or <= x
        int k = blockOf(x);
        if (k == (int)keys.size()) return n;
        const vector<T>& b = keys[k];
        int j = int((strict ? lower_bound(b.begin(), b.end(), x) : upper_bound(b.begin(), b.end(), x)) - b.begin());
        return pre(fc, k) + accumulate(cnts[k].begin(), cnts[k].begin() + j, 0LL);
    }}

    long long lt(T x) {{ return countBelow(x, true); }}
    long long le(T x) {{ return countBelow(x, false); }}

    long long countOf(T x) const {{
        int k = blockOf(x);
        if (k == (int)keys.size()) return 0;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        return j < (int)keys[k].size() && keys[k][j] == x ? cnts[k][j] : 0;
    }}
{f"""
    S sumBelow(T x, bool strict) {{  // sum of the values < x (strict) or <= x
        int k = blockOf(x);
        if (k == (int)keys.size()) return total;
        const vector<T>& b = keys[k];
        int j = int((strict ? lower_bound(b.begin(), b.end(), x) : upper_bound(b.begin(), b.end(), x)) - b.begin());
        return pre(fs, k) + accumulate(sums[k].begin(), sums[k].begin() + j, S(0));
    }}

    S slt(T x) {{ return sumBelow(x, true); }}
    S sle(T x) {{ return sumBelow(x, false); }}
""" if s else ""}
    // the block holding the k-th smallest value: (block, copies before it, sum before it)
    tuple<int, long long, S> locate(long long k) {{
        fresh();
        int pos = 0, m = (int)bc.size();
        long long before = 0;
        S acc{{}};
        for (int step = m ? 1 << (31 - __builtin_clz(m)) : 0; step; step >>= 1)
            if (pos + step <= m && before + fc[pos + step] < k) {{
                pos += step, before += fc[pos];
{"                acc += fs[pos];" + chr(10) if s else ""}            }}
        return {{pos, before, acc}};
    }}

    T kthAt(long long k) {{
        auto [b, before, acc] = locate(k);
        (void)acc;
        k -= before;
        for (size_t j = 0;; j++) {{
            if (k <= cnts[b][j]) return keys[b][j];
            k -= cnts[b][j];
        }}
    }}
    Info kthInfo(long long k) {{  // the k-th smallest, copies before it, its copies{", sum before it" if s else ""}
        auto [b, before, acc] = locate(k);
{"" if s else "        (void)acc;" + chr(10)}        for (size_t j = 0;; j++) {{
            if (k <= before + cnts[b][j]) return {{keys[b][j], before, cnts[b][j]{", acc" if s else ""}}};
            before += cnts[b][j]{", acc += sums[b][j]" if s else ""};
        }}
    }}
    // smallest non-negative integer not in the set: walk the blocks from 0 while the values run 0, 1, 2, ...
    long long findMex() {{
        int k = blockOf(T(0));
        if (k == (int)keys.size()) return 0;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), T(0)) - keys[k].begin());
        long long want = 0;
        for (; k < (int)keys.size(); k++, j = 0) {{
            const vector<T>& b = keys[k];
            if (b[j] != T(want)) return want;
            long long len = (long long)b.size();
            if ((long long)b.back() - b[j] == len - 1 - j) {{  // this block continues the run to its end
                want = (long long)b.back() + 1;
                continue;
            }}
            int lo = j, hi = (int)len - 1;  // the run breaks inside: first p with b[p] - p > b[j] - j
            while (lo < hi) {{
                int mid = (lo + hi) / 2;
                if ((long long)b[mid] - mid > (long long)b[j] - j) hi = mid;
                else lo = mid + 1;
            }}
            return (long long)b[lo - 1] + 1;
        }}
        return want;
    }}
'''
    comps = {op: "sqrt(N)" for op in OPS}
    comps.update({"size": "1", "sumAll": "1", "countDistinct": "1", "min": "1", "max": "1", "count": "log(N)", "build": "1"})
    node = "keys[1*N] cnts[1*N]" + (" sums[1*N]" if s else "")
    other = "maxes[1*sqrt(N)] bc[2*sqrt(N)]" + (" bs[2*sqrt(N)]" if s else "") + (" bx[2*sqrt(N)]" if X else "") + (
        " bo[1*sqrt(N)]" if O else "") + (" ba[1*sqrt(N)]" if A else "") + " cnt[1*N]"
    comps["xorOfAll"] = "1"
    return dict(name="BlockMultiset", dtype="blocks", values="online", py=keep_aggs(py, X, O, A), cpp=keep_aggs(cpp, X, O, A),
                comps=comps, bits=bits,

                mem=("none", node, "none", other),
                note="N = distinct values present; blocks of LOAD..2*LOAD values (Python LOAD = 64, C++ 512); each "
                     "operation costs a few binary searches plus one block's worth of C-level list work")


def blocks_fenwick(sums, bits=(False, False, False)):
    s = sums
    X = bits[0]  # (xor only: OR / AND would need more than prefix Fenwicks)
    py = f'''from bisect import bisect_left, bisect_right
{"from functools import reduce" + chr(10) if X else ""}from itertools import accumulate
from operator import and_, sub{", xor" if X else ""}


# Ordered multiset (online: any values, nothing known ahead), sqrt-style with a Fenwick tree inside every block: the
# distinct values in sorted blocks of LOAD..2*LOAD, each block keeping its values' copies{" and copies * value" if s else ""}{" and xor" if X else ""} plus a Fenwick
# tree over them, and a Fenwick tree over the block totals. Every query is two Fenwick walks (over blocks, then inside
# one), so O(log N); an update that adds or drops a distinct value rebuilds its block's Fenwick (O(sqrt N), C-level).


class BlockFenwickMultiset:
    LOAD = 64
    __slots__ = ("keys", "cnts", "fcs",{' "sums", "fss",' if s else ""}{' "xvs", "fxs",' if X else ""} "maxes", "bc", "fc",{' "bs", "fs",' if s else ""}{' "bx", "fx",' if X else ""} "cnt", "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.keys = []  # blocks of sorted distinct values
        self.cnts, self.fcs = [], []  # per block: copies of each value; Fenwick over them
{"        self.sums, self.fss = [], []  # per block: copies * value; Fenwick over them" + chr(10) if s else ""}        self.maxes = []  # last value of each block
        self.bc, self.fc = [], [0]  # per block: total copies; Fenwick over them
{"        self.bs, self.fs = [], [0]  # per block: total sum; Fenwick over them" + chr(10) if s else ""}        self.xvs, self.fxs = [], []  # per block: each value where its count is odd (else 0); xor Fenwick over them  @xor
        self.bx, self.fx = [], [0]  # per block: xor of those; xor Fenwick over them  @xor
        self.cnt = {{}}  # value -> copies
        self.n = {"self.total = " if s else ""}self.d = 0

    @staticmethod
    def _build(a):  # Fenwick tree over a in C-level passes: f[i] = (prefix sum to i) - (prefix sum to i & (i - 1))
        p = list(accumulate(a, initial=0))
        m = len(p)
        return list(map(sub, p, map(p.__getitem__, map(and_, range(m), range(-1, m - 1)))))

    @staticmethod
    def _fen(f, i, v):
        i += 1
        while i < len(f):
            f[i] += v
            i += i & -i

    @staticmethod
    def _pre(f, i):  # f's total over positions 0..i-1
        res = 0
        while i > 0:
            res += f[i]
            i &= i - 1
        return res

    def _reblock(self):
        self.fc = self._build(self.bc)
{"        self.fs = self._build(self.bs)" + chr(10) if s else ""}        self.fx = self._buildx(self.bx)  @xor

    def _reinner(self, k):
        self.fcs[k] = self._build(self.cnts[k])
{"        self.fss[k] = self._build(self.sums[k])" + chr(10) if s else ""}        self.fxs[k] = self._buildx(self.xvs[k])  @xor

    def _insert(self, x, c):
        old = self.cnt.get(x, 0)
        if old:
            k = bisect_left(self.maxes, x)
            j = bisect_left(self.keys[k], x)
            self.bc[k] += c
            self._fen(self.fc, k, c)
{"            self.bs[k] += c * x" + chr(10) + "            self._fen(self.fs, k, c * x)" + chr(10) if s else ""}            if c & 1:  # x's parity flips  @xor
                self.bx[k] ^= x  @xor
                self._fenx(self.fx, k, x)  @xor
            if old + c:  # x stays: point updates only
                self.cnt[x] = old + c
                self.cnts[k][j] += c
                self._fen(self.fcs[k], j, c)
{"                self.sums[k][j] += c * x" + chr(10) + "                self._fen(self.fss[k], j, c * x)" + chr(10) if s else ""}                if c & 1:  @xor
                    self.xvs[k][j] ^= x  @xor
                    self._fenx(self.fxs[k], j, x)  @xor
                return old + c
            del self.cnt[x]
            self.d -= 1
            del self.keys[k][j], self.cnts[k][j]
{"            del self.sums[k][j]" + chr(10) if s else ""}            del self.xvs[k][j]  @xor
            if not self.keys[k]:  # the block is empty: drop it
                del self.keys[k], self.cnts[k], self.fcs[k], self.maxes[k], self.bc[k]
{"                del self.sums[k], self.fss[k], self.bs[k]" + chr(10) if s else ""}                del self.xvs[k], self.fxs[k], self.bx[k]  @xor
                self._reblock()
                return 0
            self.maxes[k] = self.keys[k][-1]
            self._reinner(k)
            return 0
        self.cnt[x] = c
        self.d += 1
        if not self.keys:
            self.keys.append([x])
            self.cnts.append([c])
            self.fcs.append(None)
{"            self.sums.append([c * x])" + chr(10) + "            self.fss.append(None)" + chr(10) + "            self.bs.append(c * x)" + chr(10) if s else ""}            self.xvs.append([x if c & 1 else 0])  @xor
            self.fxs.append(None)  @xor
            self.bx.append(x if c & 1 else 0)  @xor
            self.maxes.append(x)
            self.bc.append(c)
            self._reinner(0)
            self._reblock()
            return c
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            k -= 1
        j = bisect_left(self.keys[k], x)
        self.keys[k].insert(j, x)
        self.cnts[k].insert(j, c)
{"        self.sums[k].insert(j, c * x)" + chr(10) + "        self.bs[k] += c * x" + chr(10) + "        self._fen(self.fs, k, c * x)" + chr(10) if s else ""}        self.xvs[k].insert(j, x if c & 1 else 0)  @xor
        if c & 1:  @xor
            self.bx[k] ^= x  @xor
            self._fenx(self.fx, k, x)  @xor
        self.maxes[k] = self.keys[k][-1]
        self.bc[k] += c
        self._fen(self.fc, k, c)
        if len(self.keys[k]) > 2 * self.LOAD:  # split the block in half
            h = self.LOAD
            for arr in (self.keys, self.cnts{", self.sums" if s else ""}{", self.xvs" if X else ""}):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.fcs.insert(k + 1, None)
{"            self.fss.insert(k + 1, None)" + chr(10) if s else ""}            self.fxs.insert(k + 1, None)  @xor
            self._reinner(k)
            self._reinner(k + 1)
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
{"            self.bs[k:k + 1] = [sum(self.sums[k]), sum(self.sums[k + 1])]" + chr(10) if s else ""}            self.bx[k:k + 1] = [reduce(xor, self.xvs[k], 0), reduce(xor, self.xvs[k + 1], 0)]  @xor
            self._reblock()
        else:
            self._reinner(k)
        return c

    def _lt(self, x):
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            return self.n
        return self._pre(self.fc, k) + self._pre(self.fcs[k], bisect_left(self.keys[k], x))

    def _le(self, x):
        k = bisect_right(self.maxes, x)  # the first block whose last value is > x
        if k == len(self.keys):
            return self.n
        return self._pre(self.fc, k) + self._pre(self.fcs[k], bisect_right(self.keys[k], x))
{f"""
    def _slt(self, x):
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            return self.total
        return self._pre(self.fs, k) + self._pre(self.fss[k], bisect_left(self.keys[k], x))

    def _sle(self, x):
        k = bisect_right(self.maxes, x)
        if k == len(self.keys):
            return self.total
        return self._pre(self.fs, k) + self._pre(self.fss[k], bisect_right(self.keys[k], x))
""" if s else ""}
    def _countOf(self, x):
        return self.cnt.get(x, 0)

    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies{", sum before it" if s else ""}): lift over blocks, then inside one
        fc{", fs" if s else ""} = self.fc{", self.fs" if s else ""}
        m = len(self.bc)
        b, before{", acc" if s else ""} = 0, 0{", 0" if s else ""}
        step = 1 << (m.bit_length() - 1)
        while step:
            nxt = b + step
            if nxt <= m and before + fc[nxt] < k:
                b = nxt
                before += fc[nxt]
{"                acc += fs[nxt]" + chr(10) if s else ""}            step >>= 1
        f{", g" if s else ""} = self.fcs[b]{", self.fss[b]" if s else ""}
        m = len(self.keys[b])
        j = 0
        step = 1 << (m.bit_length() - 1)
        while step:
            nxt = j + step
            if nxt <= m and before + f[nxt] < k:
                j = nxt
                before += f[nxt]
{"                acc += g[nxt]" + chr(10) if s else ""}            step >>= 1
        return self.keys[b][j], before, self.cnts[b][j]{", acc" if s else ""}

    def _kth(self, k):
        return self._kthInfo(k)[0]

    def _findMex(self):  # smallest non-negative integer not in the set: walk the blocks from 0 while the values run 0, 1, ...
        keys = self.keys
        k = bisect_left(self.maxes, 0)
        if k == len(keys):
            return 0
        j = bisect_left(keys[k], 0)
        want = 0
        while k < len(keys):
            blk = keys[k]
            if blk[j] != want:
                return want
            if blk[-1] - blk[j] == len(blk) - 1 - j:  # this block continues the run to its end
                want = blk[-1] + 1
                k, j = k + 1, 0
                continue
            a, b = j, len(blk) - 1  # the run breaks inside: first p with blk[p] - p > blk[j] - j
            while a < b:
                mid = (a + b) // 2
                if blk[mid] - mid > blk[j] - j:
                    b = mid
                else:
                    a = mid + 1
            return blk[a - 1] + 1
        return want
'''
    sv = "S(c) * x"
    cpp = f'''
// Ordered multiset (online: any values, nothing known ahead), sqrt-style with a Fenwick tree inside every block: the
// distinct values in sorted blocks of LOAD..2*LOAD, each block keeping its values' copies{" and copies * value" if s else ""}{" and xor" if X else ""} plus a Fenwick
// tree over them, and a Fenwick tree over the block totals. Every query is two Fenwick walks (over blocks, then inside
// one), so O(log N); an update that adds or drops a distinct value rebuilds its block's Fenwick (O(sqrt N)).
// T: an integer type; sums in S.
template <typename T>
struct BlockFenwickMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr int LOAD = 512;
    vector<vector<T>> keys;  // blocks of sorted distinct values
    vector<vector<long long>> cnts, fcs;  // per block: copies of each value; Fenwick over them
{"    vector<vector<S>> sums, fss;  // per block: copies * value; Fenwick over them" + chr(10) if s else ""}    vector<T> maxes;  // last value of each block
    vector<long long> bc, fc{{0}};  // per block total copies; Fenwick over them
{"    vector<S> bs, fs{0};  // per block total sum; Fenwick over them" + chr(10) if s else ""}    vector<vector<T>> xvs, fxs;  // per block: each value where its count is odd (else 0); xor Fenwick over them  @xor
    vector<T> bx, fx{{0}};  // per block xor of those; xor Fenwick over them  @xor
    long long n = 0, d = 0;
{"    S total = 0;" + chr(10) if s else ""}
    // O(1) -- an empty multiset
    BlockFenwickMultiset() {{}}

    template <class V>
    static vector<V> build(const vector<V>& a) {{
        vector<V> f(a.size() + 1, 0);
        for (size_t i = 1; i < f.size(); i++) {{
            f[i] += a[i - 1];
            size_t j = i + (i & -i);
            if (j < f.size()) f[j] += f[i];
        }}
        return f;
    }}

    template <class V>
    static void fen(vector<V>& f, int i, V v) {{
        for (i++; i < (int)f.size(); i += i & -i) f[i] += v;
    }}

    template <class V>
    static V pre(const vector<V>& f, int i) {{  // f's total over positions 0..i-1
        V res = 0;
        for (; i > 0; i &= i - 1) res += f[i];
        return res;
    }}

    void reblock() {{
        fc = build(bc);
{"        fs = build(bs);" + chr(10) if s else ""}        fx = buildx(bx);  @xor
    }}

    void reinner(int k) {{
        fcs[k] = build(cnts[k]);
{"        fss[k] = build(sums[k]);" + chr(10) if s else ""}        fxs[k] = buildx(xvs[k]);  @xor
    }}

    int blockOf(T x) const {{ return int(lower_bound(maxes.begin(), maxes.end(), x) - maxes.begin()); }}

    long long insert(T x, long long c) {{  // returns x's new count
        int k = blockOf(x);
        if (k < (int)keys.size()) {{
            int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
            if (j < (int)keys[k].size() && keys[k][j] == x) {{  // x is already here
                bc[k] += c, fen(fc, k, c);
{f"                bs[k] += {sv}, fen(fs, k, {sv});" + chr(10) if s else ""}                if (c & 1) bx[k] ^= x, fenx(fx, k, x);  // x's parity flips  @xor
                if (cnts[k][j] + c) {{  // x stays: point updates only
                    cnts[k][j] += c, fen(fcs[k], j, c);
{f"                    sums[k][j] += {sv}, fen(fss[k], j, {sv});" + chr(10) if s else ""}                    if (c & 1) xvs[k][j] ^= x, fenx(fxs[k], j, x);  @xor
                    return cnts[k][j];
                }}
                d--;
                keys[k].erase(keys[k].begin() + j), cnts[k].erase(cnts[k].begin() + j);
{"                sums[k].erase(sums[k].begin() + j);" + chr(10) if s else ""}                xvs[k].erase(xvs[k].begin() + j);  @xor
                if (keys[k].empty()) {{  // the block is empty: drop it
                    keys.erase(keys.begin() + k), cnts.erase(cnts.begin() + k), fcs.erase(fcs.begin() + k);
                    maxes.erase(maxes.begin() + k), bc.erase(bc.begin() + k);
{"                    sums.erase(sums.begin() + k), fss.erase(fss.begin() + k), bs.erase(bs.begin() + k);" + chr(10) if s else ""}                    xvs.erase(xvs.begin() + k), fxs.erase(fxs.begin() + k), bx.erase(bx.begin() + k);  @xor
                    reblock();
                    return 0;
                }}
                maxes[k] = keys[k].back();
                reinner(k);
                return 0;
            }}
        }}
        d++;
        if (keys.empty()) {{
            keys.push_back({{x}}), cnts.push_back({{c}}), fcs.emplace_back(), maxes.push_back(x), bc.push_back(c);
{f"            sums.push_back({{{sv}}}), fss.emplace_back(), bs.push_back({sv});" + chr(10) if s else ""}            xvs.push_back({{c & 1 ? x : T(0)}}), fxs.emplace_back(), bx.push_back(c & 1 ? x : T(0));  @xor
            reinner(0), reblock();
            return c;
        }}
        if (k == (int)keys.size()) k--;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        keys[k].insert(keys[k].begin() + j, x), cnts[k].insert(cnts[k].begin() + j, c);
{f"        sums[k].insert(sums[k].begin() + j, {sv}), bs[k] += {sv}, fen(fs, k, {sv});" + chr(10) if s else ""}        xvs[k].insert(xvs[k].begin() + j, c & 1 ? x : T(0));  @xor
        if (c & 1) bx[k] ^= x, fenx(fx, k, x);  @xor
        maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
        if ((int)keys[k].size() > 2 * LOAD) {{  // split the block in half
            auto half = [&](auto& arr) {{
                arr.insert(arr.begin() + k + 1, decay_t<decltype(arr[k])>(arr[k].begin() + LOAD, arr[k].end()));
                arr[k].resize(LOAD);
            }};
            half(keys), half(cnts);
            fcs.emplace(fcs.begin() + k + 1);
{"            half(sums), fss.emplace(fss.begin() + k + 1);" + chr(10) if s else ""}            half(xvs), fxs.emplace(fxs.begin() + k + 1);  @xor
            reinner(k), reinner(k + 1);
            maxes[k] = keys[k].back(), maxes.insert(maxes.begin() + k + 1, keys[k + 1].back());
            bc[k] = accumulate(cnts[k].begin(), cnts[k].end(), 0LL);
            bc.insert(bc.begin() + k + 1, accumulate(cnts[k + 1].begin(), cnts[k + 1].end(), 0LL));
{"            bs[k] = accumulate(sums[k].begin(), sums[k].end(), S(0));" + chr(10) + "            bs.insert(bs.begin() + k + 1, accumulate(sums[k + 1].begin(), sums[k + 1].end(), S(0)));" + chr(10) if s else ""}            bx[k] = accumulate(xvs[k].begin(), xvs[k].end(), T(0), bit_xor<T>());  @xor
            bx.insert(bx.begin() + k + 1, accumulate(xvs[k + 1].begin(), xvs[k + 1].end(), T(0), bit_xor<T>()));  @xor
            reblock();
        }} else reinner(k);
        return c;
    }}

    template <class V>
    V below(T x, bool strict, const vector<V>& outer, const vector<vector<V>>& inner, V all) const {{  // over values < x / <= x
        int k = int((strict ? lower_bound(maxes.begin(), maxes.end(), x) : upper_bound(maxes.begin(), maxes.end(), x)) - maxes.begin());
        if (k == (int)keys.size()) return all;
        const vector<T>& b = keys[k];
        int j = int((strict ? lower_bound(b.begin(), b.end(), x) : upper_bound(b.begin(), b.end(), x)) - b.begin());
        return pre(outer, k) + pre(inner[k], j);
    }}

    long long lt(T x) {{ return below(x, true, fc, fcs, n); }}
    long long le(T x) {{ return below(x, false, fc, fcs, n); }}
{"    S slt(T x) { return below(x, true, fs, fss, total); }" + chr(10) + "    S sle(T x) { return below(x, false, fs, fss, total); }" + chr(10) if s else ""}
    long long countOf(T x) const {{
        int k = blockOf(x);
        if (k == (int)keys.size()) return 0;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        return j < (int)keys[k].size() && keys[k][j] == x ? cnts[k][j] : 0;
    }}

    Info kthInfo(long long k) {{  // the k-th smallest, copies before it, its copies{", sum before it" if s else ""}: lift over blocks, then inside one
        int m = (int)bc.size(), b = 0, j = 0;
        long long before = 0;
{"        S acc = 0;" + chr(10) if s else ""}        for (int step = 1 << (31 - __builtin_clz(m)); step; step >>= 1)
            if (b + step <= m && before + fc[b + step] < k) b += step, before += fc[b]{", acc += fs[b]" if s else ""};
        const vector<long long>& f = fcs[b];
        m = (int)keys[b].size();
        for (int step = 1 << (31 - __builtin_clz(m)); step; step >>= 1)
            if (j + step <= m && before + f[j + step] < k) j += step, before += f[j]{", acc += fss[b][j]" if s else ""};
        return {{keys[b][j], before, cnts[b][j]{", acc" if s else ""}}};
    }}

    T kthAt(long long k) {{ return kthInfo(k).v; }}

    long long findMex() {{  // smallest non-negative integer not in the set: walk the blocks from 0 while the values run 0, 1, ...
        int k = blockOf(T(0));
        if (k == (int)keys.size()) return 0;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), T(0)) - keys[k].begin());
        long long want = 0;
        for (; k < (int)keys.size(); k++, j = 0) {{
            const vector<T>& b = keys[k];
            if (b[j] != T(want)) return want;
            long long len = (long long)b.size();
            if ((long long)b.back() - b[j] == len - 1 - j) {{  // this block continues the run to its end
                want = (long long)b.back() + 1;
                continue;
            }}
            int lo = j, hi = (int)len - 1;  // the run breaks inside: first p with b[p] - p > b[j] - j
            while (lo < hi) {{
                int mid = (lo + hi) / 2;
                if ((long long)b[mid] - mid > (long long)b[j] - j) hi = mid;
                else lo = mid + 1;
            }}
            return (long long)b[lo - 1] + 1;
        }}
        return want;
    }}
'''
    comps = {op: "log(N)" for op in OPS}
    comps.update({op: "sqrt(N)" for op in ("add", "addCount", "remove", "removeCount", "removeAll", "popMin", "popMax")})
    comps.update({"size": "1", "sumAll": "1", "countDistinct": "1", "build": "1"})
    node = "keys[1*N] cnts[1*N] fcs[1*N]" + (" sums[1*N] fss[1*N]" if s else "") + (" xvs[1*N] fxs[1*N]" if X else "")
    other = "maxes[1*sqrt(N)] bc[2*sqrt(N)]" + (" bs[2*sqrt(N)]" if s else "") + (" bx[2*sqrt(N)]" if X else "") + " cnt[1*N]"
    comps["xorOfAll"] = "1"
    return dict(name="BlockFenwickMultiset", dtype="blocks-fenwick", values="online", py=keep_aggs(py, X), cpp=keep_aggs(cpp, X),
                comps=comps, bits=(X, False, False),

                mem=("none", node, "none", other),
                note="N = distinct values present; blocks of LOAD..2*LOAD values (Python LOAD = 64, C++ 512); queries are "
                     "O(log N), and only updates that add or drop a distinct value pay O(sqrt N) (one block rebuilt)")


def pbds():
    cpp = '''
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

// Ordered multiset (online: any values, nothing known ahead) on GCC's order-statistics tree (pb_ds): one node per
// copy, keyed (value, id) so equal values stay distinct. No sums, no bulk adds. T: any type with < (and +1 for le).
template <typename T>
struct PbdsMultiset {
    using Tree = __gnu_pbds::tree<pair<T, int>, __gnu_pbds::null_type, less<pair<T, int>>, __gnu_pbds::rb_tree_tag,
                                  __gnu_pbds::tree_order_statistics_node_update>;
    Tree t;
    int ids = 0;
    long long n = 0, d = 0;

    // O(1) -- an empty multiset
    PbdsMultiset() {}

    long long insert(T x, long long c) {  // c = +1 or -1; returns x's new count
        if (c > 0) {
            long long k = countOf(x);
            if (!k) d++;
            t.insert({x, ids++});
            return k + 1;
        }
        t.erase(t.lower_bound({x, INT_MIN}));
        long long k = countOf(x);
        if (!k) d--;
        return k;
    }

    long long lt(T x) { return (long long)t.order_of_key({x, INT_MIN}); }
    long long le(T x) { return (long long)t.order_of_key({x, INT_MAX}); }
    T kthAt(long long k) { return t.find_by_order(k - 1)->first; }
    long long countOf(T x) { return le(x) - lt(x); }

    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies
        T v = kthAt(k);
        long long b = lt(v);
        return {v, b, le(v) - b};
    }
'''
    ops = ["add", "remove", "popMin", "popMax", "size", "count", "countDistinct", "min", "max", "medianLow", "medianHigh",
           "kth", "pop", "largestLtX", "largestLteX", "smallestGtX", "smallestGteX", "countLtX",
           "countLteX", "countGtX", "countGteX", "countInValRange", "firstIndex", "lastIndex", "clear", "removeInValRange"]
    comps = {op: "log(N)" for op in OPS}
    comps.update({"size": "1", "countDistinct": "1", "min": "1", "max": "1", "build": "1"})
    cpp_own = {  # its insert moves one copy at a time, so a range is removed copy by copy
        "removeInValRange": ("long long", "if (hi < lo) return 0;\nlong long removed = 0;\nwhile (n) {  // the smallest value >= lo, while it is <= hi\n    auto it = t.lower_bound({lo, INT_MIN});\n    if (it == t.end() || hi < it->first) break;\n    addRaw(it->first, -1), removed++;\n}\nreturn removed;"),
    }
    return dict(name="PbdsMultiset", dtype="pbds", values="online", py=None, cpp=cpp, comps=comps, cpp_own=cpp_own,
                mem=("none", "key[2*N] size[1*N] color[1*N]", "none", "children[2*N] parent[1*N]"),
                note="N = copies present: one red-black tree node per copy, keyed (value, id), with its subtree size", ops=ops)


def fastset():
    """The user's FastSet (a 64-ary bit trie over [lo, hi]) as a multiset: a count per value, and the trie bit for a
    value is set while its count is positive. add / remove / predecessor / successor touch one word per level, so
    log_64(U) steps. No ranks, so no k-th, no counting below x, no sums."""
    py = """
# Ordered multiset of integers in [lo, hi] (FastSet): a 64-ary bit trie over the U = hi - lo + 1 slots, a bit meaning
# "this value (or something under this word) is present", plus a count per value. add / remove / smallest >= x /
# largest <= x touch one word per level: log_64(U) levels, about 4 for U = 10^7. It keeps no ranks, so no k-th and
# no "how many below x".


class FastSetMultiset:
    __slots__ = ("lo", "hi", "u", "seg", "cnt", "n", "d")

    # O(U) -- lo, hi: every value added lies in [lo, hi] (any integers, negative is fine); U = hi - lo + 1
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        u = self.u = hi - lo + 1
        self.cnt = [0] * u  # copies of lo + i
        self.seg = []  # seg[h][w] = 64 bits, one per word of level h - 1 (level 0: one per value)
        width = max(u, 1)
        while True:
            words = (width + 63) >> 6
            self.seg.append([0] * words)
            if words == 1:
                break
            width = words
        self.n = self.d = 0

    def _insert(self, x, c):
        i = x - self.lo  # x must lie in [lo, hi]
        old = self.cnt[i]
        new = self.cnt[i] = old + c
        if not old:  # first copy: set its bit on every level
            self.d += 1
            for level in self.seg:
                level[i >> 6] |= 1 << (i & 63)
                i >>= 6
        elif not new:  # last copy: clear bits upward while the word empties
            self.d -= 1
            for level in self.seg:
                j = i >> 6
                w = level[j] & ~(1 << (i & 63))
                level[j] = w
                if w:
                    break
                i = j
        return new

    def _countOf(self, x):
        return self.cnt[x - self.lo] if self.lo <= x <= self.hi else 0

    def _next(self, i):  # smallest present slot >= i, or -1
        if i < 0:
            i = 0
        if i >= self.u:
            return -1
        seg = self.seg
        for h in range(len(seg)):
            idx = i >> 6
            if idx >= len(seg[h]):
                break
            v = seg[h][idx] >> (i & 63)
            if v:
                i += (v & -v).bit_length() - 1
                for g in range(h - 1, -1, -1):
                    w = seg[g][i]
                    i = (i << 6) + (w & -w).bit_length() - 1
                return i
            i = idx + 1
        return -1

    def _prev(self, i):  # largest present slot <= i, or -1
        if i >= self.u:
            i = self.u - 1
        if i < 0:
            return -1
        seg = self.seg
        for h in range(len(seg)):
            idx = i >> 6
            v = seg[h][idx] & ((1 << ((i & 63) + 1)) - 1)
            if v:
                i = (idx << 6) + v.bit_length() - 1
                for g in range(h - 1, -1, -1):
                    i = (i << 6) + seg[g][i].bit_length() - 1
                return i
            if not idx:
                return -1
            i = idx - 1
        return -1

    def _kth(self, k):  # only the min (k = 1) or the max (k = n), for _add: the trie has no ranks
        return self.lo + (self._next(0) if k == 1 else self._prev(self.u - 1))
"""
    cpp = """
// Ordered multiset of integers in [lo, hi] (FastSet): a 64-ary bit trie over the U = hi - lo + 1 slots, a bit meaning
// "this value (or something under this word) is present", plus a count per value. add / remove / smallest >= x /
// largest <= x touch one word per level: log_64(U) levels, about 4 for U = 10^7. It keeps no ranks, so no k-th and
// no "how many below x". T: int, long long, ...
template <typename T>
struct FastSetMultiset {
    long long lo, hi;
    int u;
    vector<vector<unsigned long long>> seg;  // seg[h][w] = 64 bits, one per word of level h - 1 (level 0: one per value)
    vector<long long> cnt;                   // copies of lo + i
    long long n = 0, d = 0;

    // O(U) -- lo, hi: every value added lies in [lo, hi] (any integers, negative is fine); U = hi - lo + 1
    FastSetMultiset(long long lo, long long hi) : lo(lo), hi(hi), u(int(hi - lo + 1)), cnt(u) {
        for (int width = std::max(u, 1);;) {  // (std::: the struct's own max() hides it)
            int words = (width + 63) >> 6;
            seg.emplace_back(words, 0);
            if (words == 1) break;
            width = words;
        }
    }

    long long insert(T x, long long c) {  // returns x's new count
        int i = int((long long)x - lo);  // x must lie in [lo, hi]
        long long old = cnt[i];
        cnt[i] += c;
        if (!old) {  // first copy: set its bit on every level
            d++;
            for (auto& level : seg) level[i >> 6] |= 1ULL << (i & 63), i >>= 6;
        } else if (!cnt[i]) {  // last copy: clear bits upward while the word empties
            d--;
            for (auto& level : seg) {
                int j = i >> 6;
                if (level[j] &= ~(1ULL << (i & 63))) break;
                i = j;
            }
        }
        return cnt[(long long)x - lo];
    }

    long long countOf(T x) const { return (long long)x >= lo && (long long)x <= hi ? cnt[(long long)x - lo] : 0; }

    long long next(long long i) const {  // smallest present slot >= i, or -1
        if (i < 0) i = 0;
        if (i >= u) return -1;
        for (int h = 0; h < (int)seg.size(); h++) {
            long long idx = i >> 6;
            if (idx >= (long long)seg[h].size()) break;
            unsigned long long v = seg[h][idx] >> (i & 63);
            if (v) {
                i += __builtin_ctzll(v);
                for (int g = h - 1; g >= 0; g--) i = (i << 6) + __builtin_ctzll(seg[g][i]);
                return i;
            }
            i = idx + 1;
        }
        return -1;
    }

    long long prev(long long i) const {  // largest present slot <= i, or -1
        if (i >= u) i = u - 1;
        if (i < 0) return -1;
        for (int h = 0; h < (int)seg.size(); h++) {
            long long idx = i >> 6;
            unsigned long long v = seg[h][idx] & (~0ULL >> (63 - (i & 63)));
            if (v) {
                i = (idx << 6) + 63 - __builtin_clzll(v);
                for (int g = h - 1; g >= 0; g--) i = (i << 6) + 63 - __builtin_clzll(seg[g][i]);
                return i;
            }
            if (!idx) return -1;
            i = idx - 1;
        }
        return -1;
    }

    T kthAt(long long k) const { return T(lo + (k == 1 ? next(0) : prev(u - 1))); }  // only the min (k = 1) or the max (k = n): no ranks

    Info kthInfo(long long k) const { return {kthAt(k), 0, 0}; }  // never called: this structure has no median ops
"""
    ops = ["add", "addCount", "remove", "removeCount", "removeAll", "popMin", "popMax", "size", "count", "countDistinct",
           "min", "max", "smallestGteX", "smallestGtX", "largestLteX", "largestLtX", "clear", "removeInValRange"]
    py_own = {
        "removeInValRange": "if lo > hi:\n    return 0\nremoved = 0\ni = self._next(lo - self.lo)\nwhile i >= 0 and self.lo + i <= hi:  # each present value in [lo, hi]: drop all its copies\n    k = self.cnt[i]\n    self._add(self.lo + i, -k)\n    removed += k\n    i = self._next(i + 1)\nreturn removed",
        "smallestGteX": "i = self._next(x - self.lo)\nreturn None if i < 0 else self.lo + i",
        "smallestGtX": "i = self._next(x - self.lo + 1)\nreturn None if i < 0 else self.lo + i",
        "largestLteX": "i = self._prev(x - self.lo)\nreturn None if i < 0 else self.lo + i",
        "largestLtX": "i = self._prev(x - self.lo - 1)\nreturn None if i < 0 else self.lo + i",
    }
    cpp_own = {
        "removeInValRange": ("long long", "if (hi < lo) return 0;\nlong long removed = 0;\nfor (long long i = next((long long)lo - this->lo); i >= 0 && this->lo + i <= (long long)hi; i = next(i + 1)) {  // each present value in [lo, hi]\n    long long k = cnt[i];\n    addRaw(T(this->lo + i), -k), removed += k;\n}\nreturn removed;"),
        "smallestGteX": ("optional<T>", "long long i = next((long long)x - lo);\nif (i < 0) return nullopt;\nreturn T(lo + i);"),
        "smallestGtX": ("optional<T>", "long long i = next((long long)x - lo + 1);\nif (i < 0) return nullopt;\nreturn T(lo + i);"),
        "largestLteX": ("optional<T>", "long long i = prev((long long)x - lo);\nif (i < 0) return nullopt;\nreturn T(lo + i);"),
        "largestLtX": ("optional<T>", "long long i = prev((long long)x - lo - 1);\nif (i < 0) return nullopt;\nreturn T(lo + i);"),
    }
    comps = {op: "log64(U)" for op in OPS}
    comps.update({"size": "1", "count": "1", "countDistinct": "1", "build": "U"})
    return dict(name="FastSetMultiset", dtype="fastset", values="online-range", py=py, cpp=cpp, comps=comps, ops=ops,
                py_own=py_own, cpp_own=cpp_own, mem=("none", "cnt[1*U]", "none", "none"),
                note="U = hi - lo + 1: a count per value, plus the trie's U / 64 + U / 4096 + ... 64-bit words (about U / 63)")


# ------------------------------------------------------------------------------------------------ binary trie

def keep_tags(text, **flags):
    """Lines ending in '  @a' are kept only when flag a holds ('  @a|b': a or b; '  @!a': not a); the tag is dropped."""
    out = []
    for line in text.split("\n"):
        m = re.search(r"  @(!?)([A-Za-z|]+)$", line)
        if m:
            on = any(flags[f] for f in m.group(2).split("|"))
            if on == bool(m.group(1)):
                continue
            line = line[:m.start()]
        out.append(line)
    return "\n".join(out)


TRIE_PY = '''
# Ordered multiset of integers in [0, 2^bits) as a binary trie: one level per bit, highest bit first; each node keeps
# how many copies@DESC@ are below it. Besides the usual ordered queries it answers questions
# about v ^ x over every value v (max / min / k-th / counts / closest to a bound / limits on v@XDESC@) by walking one bit
# per level, so O(bits) each. Nodes live in parallel lists (node 0 = empty, node 1 = the root) and are never removed.
# xorAll(y) replaces every value v by v ^ y in O(1): the values are stored as v ^ mask and only the mask changes.  @K


class TrieMultiset:
    __slots__ = ("B", "top", "L", "R", "C",@SLOTS@ "n",@TOTSLOT@ "d")

    # O(1) -- an empty multiset for integers in [0, 2^bits) (bits = 30 holds values up to 1073741823)
    def __init__(self, bits):
        self.B = bits
        self.top = (1 << bits) - 1  # the largest value it can hold
        self.L, self.R, self.C = [0, 0], [0, 0], [0, 0]  # child for bit 0 / bit 1, copies below; node 0 = empty, 1 = root
        self.S = [0, 0]  # sum of the copies below  @s
        self.P = [0, 0]  # distinct values below  @M
        self.MN, self.MX = [0, 0], [0, 0]  # smallest / largest value below (meaningful while its count > 0)  @V
        self.bc = [0] * bits  # bc[h] = copies with bit h set  @X
        self.X = [0, 0]  # xor of the stored values below with an odd count  @xor
        self.O = [0, 0]  # OR of the values below  @or
        self.A = [-1, -1]  # AND of the values below (an empty node's: every bit)  @and
        self.mask = 0  # every value v is stored as v ^ mask  @K
        self.n = @TOTINIT@self.d = 0

    def _new(self):  # a new empty node
        self.L.append(0)
        self.R.append(0)
        self.C.append(0)
        self.S.append(0)  @s
        self.P.append(0)  @M
        self.MN.append(0)  @V
        self.MX.append(0)  @V
        self.X.append(0)  @xor
        self.O.append(0)  @or
        self.A.append(-1)  @and
        return len(self.C) - 1

    def _clearData(self):  # fresh node lists (the old ones are freed in bulk)
        self.L, self.R, self.C = [0, 0], [0, 0], [0, 0]
        self.S = [0, 0]  @s
        self.P = [0, 0]  @M
        self.MN, self.MX = [0, 0], [0, 0]  @V
        self.bc = [0] * self.B  @X
        self.X = [0, 0]  @xor
        self.O = [0, 0]  @or
        self.A = [-1, -1]  @and
        self.mask = 0  @K

    def _insert(self, x, c):  # c copies of x; returns x's new count
        L, R, C = self.L, self.R, self.C
        S = self.S  @s
        bc = self.bc  @X
        y = x ^ self.mask  # where x is stored  @K
        X, xv = self.X, @Y@ if c & 1 else 0  # (with an odd c the stored value flips in or out of each xor on its path)  @xor
        t = 1
        C[1] += c
        S[1] += c * x  @s
        X[1] ^= xv  @xor
        path = [1]  @M|V|or|and
        for h in range(self.B - 1, -1, -1):
            if @Y@ >> h & 1:
                bc[h] += c  @X
                u = R[t]
                if not u:
                    u = R[t] = self._new()
            else:
                u = L[t]
                if not u:
                    u = L[t] = self._new()
            t = u
            C[t] += c
            S[t] += c * x  @s
            X[t] ^= xv  @xor
            path.append(t)  @M|V|or|and
        f = C[t]
        if not f or f == c:  # x appeared or disappeared
            self.d += 1 if f else -1
            P, g = self.P, 1 if f else -1  @M
            for u in path:  @M
                P[u] += g  @M
            MN, MX = self.MN, self.MX  @V
            if f:  @V
                MN[t] = MX[t] = x  @V
            O = self.O  @or
            A = self.A  @and
            O[t] = x if f else 0  @or
            A[t] = x if f else -1  @and
            for u in reversed(path[:-1]):  # from the bottom: what is present below each node changed  @V|or|and
                l, r = L[u], R[u]  @V|or|and
                MN[u] = MN[l] if C[l] else MN[r]  @V
                MX[u] = MX[r] if C[r] else MX[l]  @V
                O[u] = O[l] | O[r]  @or
                A[u] = A[l] & A[r]  @and
        return f

    def _cntLt(self, b, key):  # copies whose stored value ^ key is < b
        if b <= 0:
            return 0
        if b > self.top:
            return self.n
        L, R, C = self.L, self.R, self.C
        t, res = 1, 0
        for h in range(self.B - 1, -1, -1):
            kb = key >> h & 1
            if b >> h & 1:  # everything below the child with result bit 0 is < b
                res += C[R[t] if kb else L[t]]
                t = L[t] if kb else R[t]
            else:
                t = R[t] if kb else L[t]
            if not t:
                break
        return res

    def _kthX(self, k, key):  # the k-th smallest (1-indexed) stored value ^ key
        L, R, C = self.L, self.R, self.C
        t, res = 1, 0
        for h in range(self.B - 1, -1, -1):
            if key >> h & 1:
                z, o = R[t], L[t]
            else:
                z, o = L[t], R[t]
            if k <= C[z]:
                t = z
            else:
                k -= C[z]
                t = o
                res |= 1 << h
        return res

    def _extreme(self, t, h, key, big):  # bits h..0 of the largest (big) / smallest stored value ^ key below node t
        L, R, C = self.L, self.R, self.C
        res = 0
        while h >= 0:
            p = (key >> h & 1) ^ big  # the child whose result bit is 1 (big) / 0
            u = R[t] if p else L[t]
            if C[u]:
                t = u
                if big:
                    res |= 1 << h
            else:
                t = L[t] if p else R[t]
                if not big:
                    res |= 1 << h
            h -= 1
        return res

    def _lt(self, x):
        return self._cntLt(x, @MK@)

    def _le(self, x):
        return self._cntLt(x + 1, @MK@)

    def _countOf(self, x):
        if not 0 <= x <= self.top:
            return 0
        y = x ^ self.mask  @K
        L, R = self.L, self.R
        t = 1
        for h in range(self.B - 1, -1, -1):
            t = R[t] if @Y@ >> h & 1 else L[t]
            if not t:
                return 0
        return self.C[t]

    def _kth(self, k):
        return self._kthX(k, @MK@)
@KTHINFO@@SUMS@@MEX@@SUMX@@BEST@'''

TRIE_PY_KTHINFO = '''
    def _kthInfo(self, k):  # (k-th smallest, copies before it, its copies@SB@)
        L, R, C = self.L, self.R, self.C
        S, acc = self.S, 0  @s
        t, v, before = 1, 0, 0
        for h in range(self.B - 1, -1, -1):
            l = L[t]
            if before + C[l] < k:
                before += C[l]
                acc += S[l]  @s
                t = R[t]
                v |= 1 << h
            else:
                t = l
        return v, before, C[t]@ACC@
'''

TRIE_PY_SUMS = '''
    def _slt(self, x):  # sum of the values < x
        if x <= 0:
            return 0
        if x > self.top:
            return self.total
        L, R, S = self.L, self.R, self.S
        t, res = 1, 0
        for h in range(self.B - 1, -1, -1):
            if x >> h & 1:
                res += S[L[t]]
                t = R[t]
            else:
                t = L[t]
            if not t:
                break
        return res

    def _sle(self, x):
        return self._slt(x + 1)
'''

TRIE_PY_MEX = '''
    def _mexX(self, key):  # smallest m >= 0 with no value stored as m ^ key
        L, R, P = self.L, self.R, self.P
        if P[1] > self.top:  # every value is present
            return self.top + 1
        t, res = 1, 0
        for h in range(self.B - 1, -1, -1):
            if key >> h & 1:
                z, o = R[t], L[t]
            else:
                z, o = L[t], R[t]
            if P[z] == 1 << h:  # that half is full: the answer has bit h set
                res |= 1 << h
                t = o
            else:
                t = z
            if not t:
                break
        return res

    def _findMex(self):
        return self._mexX(@MK@)

    def _distinctLt(self, x):  # distinct values < x
        if x <= 0:
            return 0
        if x > self.top:
            return self.d
        L, R, P = self.L, self.R, self.P
        key = @MK@
        t, res = 1, 0
        for h in range(self.B - 1, -1, -1):
            kb = key >> h & 1
            if x >> h & 1:
                res += P[R[t] if kb else L[t]]
                t = L[t] if kb else R[t]
            else:
                t = R[t] if kb else L[t]
            if not t:
                break
        return res
'''

TRIE_PY_SUMX = '''
    def _sumX(self, key):  # sum of stored value ^ key over every copy: bit by bit from the per-bit counts
        bc, n, res = self.bc, self.n, 0
        for h in range(self.B):
            res += (n - bc[h] if key >> h & 1 else bc[h]) << h
        return res
'''

# limits on v, with the smallest / largest value under each node: one greedy walk per side, O(bits)
TRIE_PY_BEST_V = '''
    def _bestIn(self, x, lo, hi, big):  # the largest (big) / smallest v ^ x over the values v in [lo, hi]; None if none
        lo, hi = max(lo, 0), min(hi, self.top)
        if lo > hi:
            return None
        L, R, C = self.L, self.R, self.C
        t, h = 1, self.B - 1
        while h >= 0 and (lo >> h & 1) == (hi >> h & 1):  # the bits lo and hi share: one path
            t = R[t] if lo >> h & 1 else L[t]
            h -= 1
        if not C[t]:
            return None
        if h < 0:  # lo == hi, present
            return lo ^ x
        # where they split, the left child only needs v >= lo and the right child only v <= hi
        a = self._bestSide(L[t], h - 1, x, lo, True, big)
        b = self._bestSide(R[t], h - 1, x, hi, False, big)
        if a is None or b is None:
            return b if a is None else a
        return max(a, b) if big else min(a, b)

    def _bestSide(self, t, h, x, bound, ge, big):  # best v ^ x below node t with v >= bound (ge) / v <= bound
        L, R, C, MN, MX = self.L, self.R, self.C, self.MN, self.MX
        if not C[t] or (MX[t] < bound if ge else MN[t] > bound):
            return None
        while h >= 0:
            p = (x >> h & 1) ^ big  # the child whose bit of v ^ x is 1 (big) / 0
            u = R[t] if p else L[t]
            if C[u] and (MX[u] >= bound if ge else MN[u] <= bound):
                t = u
            else:
                t = L[t] if p else R[t]
            h -= 1
        return MN[t] ^ x
'''

# limits on v from counts alone: [lo, hi] splits into at most 2 * bits whole subtrees, each one greedy walk: O(bits^2)
TRIE_PY_BEST_COVER = '''
    def _bestIn(self, x, lo, hi, big):  # the largest (big) / smallest v ^ x over the values v in [lo, hi]; None if none
        lo, hi = max(lo, 0), min(hi, self.top)
        if lo > hi:
            return None
        L, R, C = self.L, self.R, self.C
        mk = @MK@
        key = x ^ mk  # v ^ x = stored value ^ key
        best = None
        stack = [(1, 1 << self.B, 0)]  # (node, how many values it spans, the first of them)
        while stack:
            t, size, a = stack.pop()
            if not C[t] or a > hi or a + size - 1 < lo:
                continue
            if lo <= a and a + size - 1 <= hi:  # wholly inside: the best of this subtree
                v = a ^ x if size == 1 else ((a ^ x) & -size) | self._extreme(t, size.bit_length() - 2, key, big)
                if best is None or (v > best if big else v < best):
                    best = v
                continue
            half = size >> 1
            h = half.bit_length() - 1
            if mk >> h & 1:  # the stored child for v's bit h = 0 is the bit-1 child
                stack.append((R[t], half, a))
                stack.append((L[t], half, a + half))
            else:
                stack.append((L[t], half, a))
                stack.append((R[t], half, a + half))
        return best
'''

TRIE_CPP = '''
// Ordered multiset of integers in [0, 2^bits) as a binary trie: one level per bit, highest bit first; each node keeps
// how many copies@DESC@ are below it. Besides the usual ordered queries it answers questions
// about v ^ x over every value v (max / min / k-th / counts / closest to a bound / limits on v@XDESC@) by walking one bit
// per level, so O(bits) each. Each multiset owns its node arrays (node 0 = empty, node 1 = the root); nodes are never
// removed. T: int, long long, ...; sums in S (long long for small T).
// xorAll(y) replaces every value v by v ^ y in O(1): the values are stored as v ^ mask and only the mask changes.  @K
template <typename T>
struct TrieMultiset {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int B;
    long long top;  // the largest value it can hold
    vector<array<int, 2>> ch{{0, 0}, {0, 0}};  // child for bit 0 / bit 1; node 0 = empty, node 1 = the root
    vector<long long> c{0, 0};  // copies below
    vector<S> sm{0, 0};  // sum of the copies below  @s
    vector<long long> p{0, 0};  // distinct values below  @M
    vector<long long> mnv{0, 0}, mxv{0, 0};  // smallest / largest value below (meaningful while its count > 0)  @V
    vector<long long> bc;  // bc[h] = copies with bit h set  @X
    vector<T> xr{0, 0};  // xor of the stored values below with an odd count  @xor
    vector<T> orv{0, 0};  // OR of the values below  @or
    vector<T> andv{~T(0), ~T(0)};  // AND of the values below (an empty node's: every bit)  @and
    long long mask = 0;  // every value v is stored as v ^ mask  @K
    long long n = 0, d = 0;
    S total = 0;  @s

    // O(1) -- an empty multiset for integers in [0, 2^bits) (bits = 30 holds values up to 1073741823)
    TrieMultiset(int bits) : B(bits), top((1LL << bits) - 1) {}  @!X
    TrieMultiset(int bits) : B(bits), top((1LL << bits) - 1), bc(bits, 0) {}  @X

    int newNode() {  // a new empty node
        ch.push_back({0, 0}), c.push_back(0);
        sm.push_back(0);  @s
        p.push_back(0);  @M
        mnv.push_back(0), mxv.push_back(0);  @V
        xr.push_back(0);  @xor
        orv.push_back(0);  @or
        andv.push_back(~T(0));  @and
        return int(c.size()) - 1;
    }

    void clearData() {  // back to just the root (the arrays keep their capacity)
        ch.assign(2, array<int, 2>{0, 0}), c.assign(2, 0);
        sm.assign(2, 0);  @s
        p.assign(2, 0);  @M
        mnv.assign(2, 0), mxv.assign(2, 0);  @V
        bc.assign(B, 0);  @X
        xr.assign(2, 0);  @xor
        orv.assign(2, 0);  @or
        andv.assign(2, ~T(0));  @and
        mask = 0;  @K
    }

    long long insert(T x, long long k) {  // k copies of x; returns x's new count
        long long y = (long long)x ^ mask;  // where x is stored  @K
        long long y = (long long)x;  @!K
        int t = 1;
        c[1] += k;
        sm[1] += S(k) * x;  @s
        T xv = k & 1 ? T(y) : T(0);  // (with an odd k the stored value flips in or out of each xor on its path)  @xor
        xr[1] ^= xv;  @xor
        int path[66], dep = 0;  @M|V|or|and
        path[dep++] = 1;  @M|V|or|and
        for (int h = B - 1; h >= 0; h--) {
            int b = int(y >> h & 1);
            if (b) bc[h] += k;  @X
            if (!ch[t][b]) {
                int u = newNode();
                ch[t][b] = u;
            }
            t = ch[t][b];
            c[t] += k;
            sm[t] += S(k) * x;  @s
            xr[t] ^= xv;  @xor
            path[dep++] = t;  @M|V|or|and
        }
        long long f = c[t];
        if (!f || f == k) {  // x appeared or disappeared
            d += f ? 1 : -1;
            for (int i = 0; i < dep; i++) p[path[i]] += f ? 1 : -1;  @M
            if (f) mnv[t] = mxv[t] = (long long)x;  @V
            orv[t] = f ? x : T(0);  @or
            andv[t] = f ? x : ~T(0);  @and
            for (int i = dep - 2; i >= 0; i--) {  // from the bottom: what is present below each node changed  @V|or|and
                int u = path[i], l = ch[u][0], r = ch[u][1];  @V|or|and
                mnv[u] = c[l] ? mnv[l] : mnv[r];  @V
                mxv[u] = c[r] ? mxv[r] : mxv[l];  @V
                orv[u] = orv[l] | orv[r];  @or
                andv[u] = andv[l] & andv[r];  @and
            }  @V|or|and
        }
        return f;
    }

    long long cntLt(long long b, long long key) const {  // copies whose stored value ^ key is < b
        if (b <= 0) return 0;
        if (b > top) return n;
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            int kb = int(key >> h & 1);
            if (b >> h & 1) res += c[ch[t][kb]], t = ch[t][kb ^ 1];  // everything below the result-bit-0 child is < b
            else t = ch[t][kb];
        }
        return res;
    }

    long long kthX(long long k, long long key) const {  // the k-th smallest (1-indexed) stored value ^ key
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0; h--) {
            int kb = int(key >> h & 1), z = ch[t][kb];
            if (k <= c[z]) t = z;
            else k -= c[z], t = ch[t][kb ^ 1], res |= 1LL << h;
        }
        return res;
    }

    long long extreme(int t, int h, long long key, bool big) const {  // bits h..0 of the largest (big) / smallest stored value ^ key below t
        long long res = 0;
        for (; h >= 0; h--) {
            int pb = int(key >> h & 1) ^ int(big);  // the child whose result bit is 1 (big) / 0
            if (c[ch[t][pb]]) {
                t = ch[t][pb];
                if (big) res |= 1LL << h;
            } else {
                t = ch[t][pb ^ 1];
                if (!big) res |= 1LL << h;
            }
        }
        return res;
    }

    long long lt(T x) const { return cntLt((long long)x, @MK@); }
    long long le(T x) const { return cntLt((long long)x + 1, @MK@); }

    long long countOf(T x) const {
        if ((long long)x < 0 || (long long)x > top) return 0;
        long long y = (long long)x ^ mask;  @K
        long long y = (long long)x;  @!K
        int t = 1;
        for (int h = B - 1; h >= 0 && t; h--) t = ch[t][y >> h & 1];
        return c[t];
    }

    T kthAt(long long k) const { return T(kthX(k, @MK@)); }
@KTHINFO@@SUMS@@MEX@@SUMX@@BEST@'''

TRIE_CPP_KTHINFO = '''
    Info kthInfo(long long k) const {  // the k-th smallest, copies before it, its copies@SB@
        int t = 1;
        long long v = 0, before = 0;
        S acc = 0;  @s
        for (int h = B - 1; h >= 0; h--) {
            int l = ch[t][0];
            if (before + c[l] < k) before += c[l], t = ch[t][1], v |= 1LL << h;  @!s
            if (before + c[l] < k) before += c[l], acc += sm[l], t = ch[t][1], v |= 1LL << h;  @s
            else t = l;
        }
        return {T(v), before, c[t]@ACC@};
    }
'''

TRIE_CPP_SUMS = '''
    S slt(T x) const {  // sum of the values < x
        long long b = (long long)x;
        if (b <= 0) return 0;
        if (b > top) return total;
        int t = 1;
        S res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            if (b >> h & 1) res += sm[ch[t][0]], t = ch[t][1];
            else t = ch[t][0];
        }
        return res;
    }

    S sle(T x) const { return slt(T((long long)x + 1)); }
'''

TRIE_CPP_MEX = '''
    long long mexX(long long key) const {  // smallest m >= 0 with no value stored as m ^ key
        if (p[1] > top) return top + 1;  // every value is present
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            int kb = int(key >> h & 1), z = ch[t][kb];
            if (p[z] == 1LL << h) res |= 1LL << h, t = ch[t][kb ^ 1];  // that half is full: the answer has bit h set
            else t = z;
        }
        return res;
    }

    long long findMex() const { return mexX(@MK@); }

    long long distinctLt(T x) const {  // distinct values < x
        long long b = (long long)x, key = @MK@;
        if (b <= 0) return 0;
        if (b > top) return d;
        int t = 1;
        long long res = 0;
        for (int h = B - 1; h >= 0 && t; h--) {
            int kb = int(key >> h & 1);
            if (b >> h & 1) res += p[ch[t][kb]], t = ch[t][kb ^ 1];
            else t = ch[t][kb];
        }
        return res;
    }
'''

TRIE_CPP_SUMX = '''
    S sumX(long long key) const {  // sum of stored value ^ key over every copy: bit by bit from the per-bit counts
        S res = 0;
        for (int h = 0; h < B; h++) res += S(key >> h & 1 ? n - bc[h] : bc[h]) << h;
        return res;
    }
'''

TRIE_CPP_BEST_V = '''
    optional<T> bestIn(long long x, long long lo, long long hi, bool big) const {  // the largest (big) / smallest v ^ x over the values v in [lo, hi]
        lo = std::max(lo, 0LL), hi = std::min(hi, top);
        if (lo > hi) return nullopt;
        int t = 1, h = B - 1;
        for (; h >= 0 && (lo >> h & 1) == (hi >> h & 1); h--) t = ch[t][lo >> h & 1];  // the bits lo and hi share: one path
        if (!c[t]) return nullopt;
        if (h < 0) return T(lo ^ x);  // lo == hi, present
        // where they split, the left child only needs v >= lo and the right child only v <= hi
        optional<T> a = bestSide(ch[t][0], h - 1, x, lo, true, big), b = bestSide(ch[t][1], h - 1, x, hi, false, big);
        if (!a || !b) return a ? a : b;
        return big ? std::max(*a, *b) : std::min(*a, *b);
    }

    optional<T> bestSide(int t, int h, long long x, long long bound, bool ge, bool big) const {  // best v ^ x below t with v >= bound (ge) / v <= bound
        auto ok = [&](int u) { return c[u] && (ge ? mxv[u] >= bound : mnv[u] <= bound); };
        if (!ok(t)) return nullopt;
        for (; h >= 0; h--) {
            int pb = int(x >> h & 1) ^ int(big);  // the child whose bit of v ^ x is 1 (big) / 0
            t = ok(ch[t][pb]) ? ch[t][pb] : ch[t][pb ^ 1];
        }
        return T(mnv[t] ^ x);
    }
'''

TRIE_CPP_BEST_COVER = '''
    optional<T> bestIn(long long x, long long lo, long long hi, bool big) const {  // the largest (big) / smallest v ^ x over the values v in [lo, hi]
        lo = std::max(lo, 0LL), hi = std::min(hi, top);
        if (lo > hi) return nullopt;
        long long mk = @MK@, key = x ^ mk;  // v ^ x = stored value ^ key
        bool found = false;
        long long best = 0;
        struct Part { int t; long long size, a; };  // a node, how many values it spans, the first of them
        Part st[140];
        int sp = 0;
        st[sp++] = {1, 1LL << B, 0};
        while (sp) {
            auto [t, size, a] = st[--sp];
            if (!c[t] || a > hi || a + size - 1 < lo) continue;
            if (lo <= a && a + size - 1 <= hi) {  // wholly inside: the best of this subtree
                long long v = size == 1 ? a ^ x : ((a ^ x) & -size) | extreme(t, 62 - __builtin_clzll(size), key, big);
                if (!found || (big ? v > best : v < best)) best = v, found = true;
                continue;
            }
            long long half = size >> 1;
            int h = 63 - __builtin_clzll(half), z = int(mk >> h & 1);  // the stored child for v's bit h = 0
            st[sp++] = {ch[t][z], half, a};
            st[sp++] = {ch[t][z ^ 1], half, a + half};
        }
        if (!found) return nullopt;
        return T(best);
    }
'''

TRIE_OPS_PY = {
    "maxXorAgainstX": "if not self.n:\n    return None\nreturn self._extreme(1, self.B - 1, @KX@, True)",
    "minXorAgainstX": "if not self.n:\n    return None\nreturn self._extreme(1, self.B - 1, @KX@, False)",
    "kthXor": "if not 0 <= i < self.n:\n    raise IndexError(f\"kthXor: needs 0 <= i < size, got i = {i}, size = {self.n}\")\nreturn self._kthX(i + 1, @KX@)",
    "countXorLtK": "return self._cntLt(k, @KX@)",
    "countXorLteK": "return self._cntLt(k + 1, @KX@)",
    "countXorGtK": "return self.n - self._cntLt(k + 1, @KX@)",
    "countXorGteK": "return self.n - self._cntLt(k, @KX@)",
    "largestXorLtK": "key = @KX@\nc = self._cntLt(k, key)\nreturn self._kthX(c, key) if c else None",
    "largestXorLteK": "key = @KX@\nc = self._cntLt(k + 1, key)\nreturn self._kthX(c, key) if c else None",
    "smallestXorGtK": "key = @KX@\nc = self._cntLt(k + 1, key)\nreturn self._kthX(c + 1, key) if c < self.n else None",
    "smallestXorGteK": "key = @KX@\nc = self._cntLt(k, key)\nreturn self._kthX(c + 1, key) if c < self.n else None",
    "mexXor": "return self._mexX(@KX@)",
    "sumXor": "return self._sumX(@KX@)",
    "maxXorWithVLtM": "return self._bestIn(x, 0, m - 1, True)",
    "maxXorWithVLteM": "return self._bestIn(x, 0, m, True)",
    "maxXorWithVGtM": "return self._bestIn(x, m + 1, self.top, True)",
    "maxXorWithVGteM": "return self._bestIn(x, m, self.top, True)",
    "minXorWithVLtM": "return self._bestIn(x, 0, m - 1, False)",
    "minXorWithVLteM": "return self._bestIn(x, 0, m, False)",
    "minXorWithVGtM": "return self._bestIn(x, m + 1, self.top, False)",
    "minXorWithVGteM": "return self._bestIn(x, m, self.top, False)",
    "maxXorWithVInValRange": "return self._bestIn(x, lo, hi, True)",
    "minXorWithVInValRange": "return self._bestIn(x, lo, hi, False)",
    "xorAll": "self.mask ^= y",
}

TRIE_OPS_CPP = {
    "maxXorAgainstX": ("optional<T>", "if (!n) return nullopt;\nreturn T(extreme(1, B - 1, @KX@, true));"),
    "minXorAgainstX": ("optional<T>", "if (!n) return nullopt;\nreturn T(extreme(1, B - 1, @KX@, false));"),
    "kthXor": ("T", "if (i < 0 || i >= n) throw out_of_range(\"kthXor: needs 0 <= i < size\");\nreturn T(kthX(i + 1, @KX@));"),
    "countXorLtK": ("long long", "return cntLt(k, @KX@);"),
    "countXorLteK": ("long long", "return cntLt(k + 1, @KX@);"),
    "countXorGtK": ("long long", "return n - cntLt(k + 1, @KX@);"),
    "countXorGteK": ("long long", "return n - cntLt(k, @KX@);"),
    "largestXorLtK": ("optional<T>", "long long key = @KX@, c0 = cntLt(k, key);\nif (!c0) return nullopt;\nreturn T(kthX(c0, key));"),
    "largestXorLteK": ("optional<T>", "long long key = @KX@, c0 = cntLt(k + 1, key);\nif (!c0) return nullopt;\nreturn T(kthX(c0, key));"),
    "smallestXorGtK": ("optional<T>", "long long key = @KX@, c0 = cntLt(k + 1, key);\nif (c0 == n) return nullopt;\nreturn T(kthX(c0 + 1, key));"),
    "smallestXorGteK": ("optional<T>", "long long key = @KX@, c0 = cntLt(k, key);\nif (c0 == n) return nullopt;\nreturn T(kthX(c0 + 1, key));"),
    "mexXor": ("long long", "return mexX(@KX@);"),
    "sumXor": ("S", "return sumX(@KX@);"),
    "maxXorWithVLtM": ("optional<T>", "return bestIn(x, 0, m - 1, true);"),
    "maxXorWithVLteM": ("optional<T>", "return bestIn(x, 0, m, true);"),
    "maxXorWithVGtM": ("optional<T>", "return bestIn(x, m + 1, top, true);"),
    "maxXorWithVGteM": ("optional<T>", "return bestIn(x, m, top, true);"),
    "minXorWithVLtM": ("optional<T>", "return bestIn(x, 0, m - 1, false);"),
    "minXorWithVLteM": ("optional<T>", "return bestIn(x, 0, m, false);"),
    "minXorWithVGtM": ("optional<T>", "return bestIn(x, m + 1, top, false);"),
    "minXorWithVGteM": ("optional<T>", "return bestIn(x, m, top, false);"),
    "maxXorWithVInValRange": ("optional<T>", "return bestIn(x, lo, hi, true);"),
    "minXorWithVInValRange": ("optional<T>", "return bestIn(x, lo, hi, false);"),
    "xorAll": ("void", "mask ^= (long long)y;"),
}


def trie(sums, mex, vbound=False, sumxor=False, mask=False, bits=(False, False, False)):
    """The binary trie over [0, 2^bits). Its own dimensions besides the usual ones: vbound (smallest / largest value
    under each node: the limits-on-v queries in O(bits) instead of O(bits^2)), sumxor (a count per bit: sum of v ^ x),
    mask (xorAll(y) in O(1); no caches then, since xorAll changes every value at once)."""
    s, M, V, X, K = sums, mex, vbound, sumxor, mask
    XR, OR, AN = bits
    assert not (K and (s or V or OR or AN)), "xorAll keeps no sums / per-node value bounds / OR / AND"
    flags = {"s": s, "M": M, "V": V, "X": X, "K": K, "xor": XR, "or": OR, "and": AN}
    desc = (", their sum" if s else "") + (", how many distinct values" if M else "") + (
        ", the smallest and largest value" if V else "") + "".join(
        f", their {w}" for w, on in (("xor", XR), ("OR", OR), ("AND", AN)) if on)
    xdesc = (", sum" if X else "") + (", mex" if M else "")

    def fill(text, py):
        mk = ("self.mask" if py else "mask") if K else "0"
        kx = ("x ^ self.mask" if py else "(long long)x ^ mask") if K else ("x" if py else "(long long)x")
        parts = {
            "@KTHINFO@": "" if K else (TRIE_PY_KTHINFO if py else TRIE_CPP_KTHINFO),
            "@SUMS@": (TRIE_PY_SUMS if py else TRIE_CPP_SUMS) if s else "",
            "@MEX@": (TRIE_PY_MEX if py else TRIE_CPP_MEX) if M else "",
            "@SUMX@": (TRIE_PY_SUMX if py else TRIE_CPP_SUMX) if X else "",
            "@BEST@": (TRIE_PY_BEST_V if py else TRIE_CPP_BEST_V) if V else (TRIE_PY_BEST_COVER if py else TRIE_CPP_BEST_COVER),
        }
        for k, v in parts.items():
            text = text.replace(k, v)
        slots = "".join(f' "{a}",' for a, on in (("S", s), ("P", M), ("MN", V), ("MX", V), ("bc", X), ("X", XR), ("O", OR),
                                                 ("A", AN), ("mask", K)) if on)
        text = (text.replace("@SLOTS@", slots).replace("@TOTSLOT@", ' "total",' if s else "")
                .replace("@TOTINIT@", "self.total = " if s else "").replace("@DESC@", desc).replace("@XDESC@", xdesc)
                .replace("@SB@", ", sum before it" if s else "").replace("@ACC@", ", acc" if s else "")
                .replace("@MK@", mk).replace("@KX@", kx).replace("@Y@", "y" if K else "x"))
        return keep_tags(text, **flags)

    py, cpp = fill(TRIE_PY, True), fill(TRIE_CPP, False)
    group2 = "log(U)" if V else "log(U)*log(U)"
    comps = {op: "log(U)" for op in OPS}
    comps.update({"size": "1", "countDistinct": "1", "build": "1", "xorAll": "1",
                  "sumAll": "1" if s else "log(U)"})
    comps.update({op: group2 for op in TRIE_GROUP2})
    py_own = {op: fill(b, True) for op, b in TRIE_OPS_PY.items()}
    cpp_own = {op: (r, fill(b, False)) for op, (r, b) in TRIE_OPS_CPP.items()}
    final = {}
    if V:  # the root's smallest / largest value: min / max in O(1) (so no separate min / max cache)
        final = {"min": "1", "max": "1", "popMin": "log(U)", "popMax": "log(U)"}
        for op, field, lst in (("min", "MN", "mnv"), ("max", "MX", "mxv")):
            py_own[op] = f"if not self.n:\n    return None\nreturn self.{field}[1]"
            cpp_own[op] = ("optional<T>", f"if (!n) return nullopt;\nreturn T({lst}[1]);")
            py_own["pop" + op.title()] = f"if not self.n:\n    return None\nv = self.{field}[1]\nself._add(v, -1)\nreturn v"
            cpp_own["pop" + op.title()] = ("optional<T>", f"if (!n) return nullopt;\nT v = T({lst}[1]);\naddRaw(v, -1);\nreturn v;")
    if X and not s:  # the sum of every value, from the per-bit counts
        py_own["sumAll"] = fill("return self._sumX(@MK@)", True)
        cpp_own["sumAll"] = ("S", fill("return sumX(@MK@);", False))
    node = "c[1*log(U)]" + (" s[1*log(U)]" if s else "") + (" p[1*log(U)]" if M else "") + (" mn[1*log(U)] mx[1*log(U)]" if V else "") + "".join(
        f" {f}[1*log(U)]" for f, on in (("xor", XR), ("or", OR), ("and", AN)) if on)
    comps.update({"xorOfAll": "1", "orOfAll": "1", "andOfAll": "1"})
    if XR and K:  # xorAll(y) xors y into every copy: the xor of all of them changes when there is an odd number
        py_own["xorAll"] = "self.mask ^= y\nif self.n & 1:\n    self.xtotal ^= y"
        cpp_own["xorAll"] = ("void", "mask ^= (long long)y;\nif (n & 1) xtotal ^= y;")
    return dict(name="TrieMultiset", dtype="trie", values="online-bits", py=py, cpp=cpp, comps=comps, mex=M,
                py_own=py_own, cpp_own=cpp_own, trie=dict(vbound=V, sumxor=X, mask=K), final=final, bits=bits,
                mem=("sparse", node, "none", "children[2*log(U)]"),
                note="per add of a new value, one node per bit of its path; U = 2^bits. Each multiset owns its nodes "
                     "(clear() keeps the arrays' capacity)")


def fastset_distinct(minmax=False, gaps=False):
    """FastSet without duplicates (fastset[-with-...]/distinct.*, the drawer's "fast build" option): just the bit trie,
    no count per value, so building is the trie's ~U / 63 words. Adding a value already in the set does nothing. Like
    the counted FastSet it comes with min / max walked (about 4 steps) or cached, and with or without the gaps; each
    update does only the work of what its variant keeps."""
    trie_py = fastset()["py"]
    nxt = trie_py[trie_py.index("    def _next(self, i):"):trie_py.index("    def _kth(self, k):")]
    py = """
# Ordered set of DISTINCT integers in [lo, hi] (FastSet): a 64-ary bit trie over the U = hi - lo + 1 slots, a bit
# meaning "this value (or something under this word) is present". No duplicates: adding a value that is already in
# the set does nothing, so there is no count per value and building is just the trie's ~U / 63 words. Every op touches
# one word per level: log_64(U) levels, about 4 for U = 10^7.


class FastSet:
    __slots__ = ("lo", "hi", "u", "seg", "n"@slots)

    # O(U/64) -- lo, hi: every value added lies in [lo, hi] (any integers, negative is fine); U = hi - lo + 1
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        u = self.u = hi - lo + 1
        self.seg = []  # seg[h][w] = 64 bits, one per word of level h - 1 (level 0: one per value)
        width = max(u, 1)
        while True:
            words = (width + 63) >> 6
            self.seg.append([0] * words)
            if words == 1:
                break
            width = words
        self.n = 0
""" + ("        self.mn = self.mx = 0  # kept current while n > 0\n" if minmax else "") + (
        "        self.gc, self.gmin, self.gmax = {}, [], []  # gaps: size -> how many; min / max heaps\n" if gaps else "") + """
""" + nxt + """    # O(log64(U)) -- add x (nothing if x is already in the set: no duplicates)
    def add(self, x):
        i = x - self.lo  # x must lie in [lo, hi]
        seg = self.seg
        if (seg[0][i >> 6] >> (i & 63)) & 1:
            return
        self.n += 1
""" + ("""        p, q = self._prev(i - 1), self._next(i + 1)  # gaps: x splits the gap between its neighbours
        if p >= 0 and q >= 0:
            self._gap(q - p, -1)
        if p >= 0:
            self._gap(i - p, 1)
        if q >= 0:
            self._gap(q - i, 1)
""" if gaps else "") + ("""        if self.n == 1:
            self.mn = self.mx = x
        elif x < self.mn:
            self.mn = x
        elif x > self.mx:
            self.mx = x
""" if minmax else "") + """        for level in seg:
            level[i >> 6] |= 1 << (i & 63)
            i >>= 6

    # O(log64(U)) -- remove x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        i = x - self.lo
        if not 0 <= i < self.u or not (self.seg[0][i >> 6] >> (i & 63)) & 1:
            return 0
        self.n -= 1
        for level in self.seg:
            j = i >> 6
            w = level[j] & ~(1 << (i & 63))
            level[j] = w
            if w:
                break
            i = j
""" + ("""        k = x - self.lo
""" if minmax or gaps else "") + ("""        p, q = self._prev(k - 1), self._next(k + 1)  # gaps: the gap between x's neighbours comes back
        if p >= 0:
            self._gap(k - p, -1)
        if q >= 0:
            self._gap(q - k, -1)
        if p >= 0 and q >= 0:
            self._gap(q - p, 1)
""" if gaps else "") + ("""        if self.n:
            if x == self.mn:
                self.mn = self.lo + self._next(k)
            if x == self.mx:
                self.mx = self.lo + self._prev(k)
""" if minmax else "") + """        return 1

    # O(N log64(U)) -- remove everything (N = values in it): as newly built, so reuse it instead of building a new one
    def clear(self):
        self.n = 0
""" + ("        self.gc, self.gmin, self.gmax = {}, [], []\n" if gaps else "") + """        self._clearWords()
""" + FASTSET_CLEAR_PY.replace("    def _clearData(self):", "    def _clearWords(self):").replace("{counts}", "").replace("{cntvar}", " = self.seg").replace("{cnt}", "") + """
    # O(log64(U) amortized) -- remove every value v with lo <= v <= hi; returns how many were removed (0 if lo > hi)
    def removeInValRange(self, lo, hi):
        if lo > hi:
            return 0
        removed = 0
        i = self._next(lo - self.lo)
        while i >= 0 and self.lo + i <= hi:
            self.remove(self.lo + i)
            removed += 1
            i = self._next(i + 1)
        return removed

    # O(1) -- 1 if x is in the set, else 0
    def count(self, x):
        i = x - self.lo
        return (self.seg[0][i >> 6] >> (i & 63)) & 1 if 0 <= i < self.u else 0

    # O(1) -- how many values (no duplicates, so also how many distinct)
    def countDistinct(self):
        return self.n

    # O(1) -- how many values
    def size(self):
        return self.n

    # O(1) -- same as size()
    def __len__(self):
        return self.n

""" + ("""    # O(1) -- smallest value; None if empty
    def min(self):
        return self.mn if self.n else None

    # O(1) -- largest value; None if empty
    def max(self):
        return self.mx if self.n else None
""" if minmax else """    # O(log64(U)) -- smallest value; None if empty
    def min(self):
        i = self._next(0)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- largest value; None if empty
    def max(self):
        i = self._prev(self.u - 1)
        return None if i < 0 else self.lo + i
""") + """
    # O(log64(U)) -- remove and return the smallest value; None if empty
    def popMin(self):
        v = self.min()
        if v is not None:
            self.remove(v)
        return v

    # O(log64(U)) -- remove and return the largest value; None if empty
    def popMax(self):
        v = self.max()
        if v is not None:
            self.remove(v)
        return v

    # O(log64(U)) -- smallest value >= x; None if there is none
    def smallestGteX(self, x):
        i = self._next(x - self.lo)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- smallest value > x; None if there is none
    def smallestGtX(self, x):
        i = self._next(x - self.lo + 1)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- largest value <= x; None if there is none
    def largestLteX(self, x):
        i = self._prev(x - self.lo)
        return None if i < 0 else self.lo + i

    # O(log64(U)) -- largest value < x; None if there is none
    def largestLtX(self, x):
        i = self._prev(x - self.lo - 1)
        return None if i < 0 else self.lo + i
""" + ("""
    def _gap(self, g, c):  # one more (c = 1) / fewer (c = -1) gap of size g
        gc = self.gc
        k = gc.get(g, 0) + c
        if k:
            gc[g] = k
            if k == 1 and c > 0:  # (a size already present has an entry in both heaps)
                if len(self.gmin) > 2 * len(gc) + 8:  # mostly sizes no longer present: rebuild from the live ones
                    self.gmin = sorted(gc)
                    self.gmax = [-v for v in reversed(self.gmin)]
                else:
                    heappush(self.gmin, g)
                    heappush(self.gmax, -g)
        else:
            del gc[g]

    # O(1 amortized) -- smallest difference between two values in the set; None if fewer than 2 values
    def minAdjacentDiff(self):
        if self.n < 2:
            return None
        h, gc = self.gmin, self.gc
        while h[0] not in gc:  # heap tops of sizes no longer present are dropped as they surface
            heappop(h)
        return h[0]

    # O(1 amortized) -- largest difference between two neighbouring values; None if fewer than 2 values
    def maxGap(self):
        if self.n < 2:
            return None
        h, gc = self.gmax, self.gc
        while -h[0] not in gc:
            heappop(h)
        return -h[0]
""" if gaps else "")
    trie_cpp = fastset()["cpp"]
    nxt_cpp = trie_cpp[trie_cpp.index("    long long next(long long i) const {"):trie_cpp.index("    T kthAt(long long k) const")]
    cpp = """
// Ordered set of DISTINCT integers in [lo, hi] (FastSet): a 64-ary bit trie over the U = hi - lo + 1 slots, a bit
// meaning "this value (or something under this word) is present". No duplicates: adding a value that is already in
// the set does nothing, so there is no count per value and building is just the trie's ~U / 63 words. Every op touches
// one word per level: log_64(U) levels, about 4 for U = 10^7. T: int, long long, ...
template <typename T>
struct FastSet {
    long long lo, hi;
    int u;
    vector<vector<unsigned long long>> seg;  // seg[h][w] = 64 bits, one per word of level h - 1 (level 0: one per value)
    long long n = 0;
""" + ("    T mn{}, mx{};  // kept current while n > 0\n" if minmax else "") + (
        "    multiset<long long> gaps;  // differences between neighbouring values\n" if gaps else "") + """
    // O(U/64) -- lo, hi: every value added lies in [lo, hi] (any integers, negative is fine); U = hi - lo + 1
    FastSet(long long lo, long long hi) : lo(lo), hi(hi), u(int(hi - lo + 1)) {
        for (int width = std::max(u, 1);;) {  // (std::: the struct's own max() hides it)
            int words = (width + 63) >> 6;
            seg.emplace_back(words, 0);
            if (words == 1) break;
            width = words;
        }
    }

""" + nxt_cpp + """    // O(log64(U)) -- add x (nothing if x is already in the set: no duplicates)
    void add(T x) {
        int i = int((long long)x - lo);  // x must lie in [lo, hi]
        if (seg[0][i >> 6] >> (i & 63) & 1) return;
        n++;
""" + ("""        long long p = prev(i - 1), q = next(i + 1);  // gaps: x splits the gap between its neighbours
        if (p >= 0 && q >= 0) gaps.erase(gaps.find(q - p));
        if (p >= 0) gaps.insert(i - p);
        if (q >= 0) gaps.insert(q - i);
""" if gaps else "") + ("""        if (n == 1) mn = mx = x;
        else if (x < mn) mn = x;
        else if (x > mx) mx = x;
""" if minmax else "") + """        for (auto& level : seg) level[i >> 6] |= 1ULL << (i & 63), i >>= 6;
    }

    // O(log64(U)) -- remove x if present; returns how many were removed (0 or 1)
    long long remove(T x) {
        long long i = (long long)x - lo;
        if (i < 0 || i >= u || !(seg[0][i >> 6] >> (i & 63) & 1)) return 0;
        n--;
        for (auto& level : seg) {
            long long j = i >> 6;
            if (level[j] &= ~(1ULL << (i & 63))) break;
            i = j;
        }
""" + ("""        long long k = (long long)x - lo;
""" if minmax or gaps else "") + ("""        long long p = prev(k - 1), q = next(k + 1);  // gaps: the gap between x's neighbours comes back
        if (p >= 0) gaps.erase(gaps.find(k - p));
        if (q >= 0) gaps.erase(gaps.find(q - k));
        if (p >= 0 && q >= 0) gaps.insert(q - p);
""" if gaps else "") + ("""        if (n) {
            if (x == mn) mn = T(lo + next(k));
            if (x == mx) mx = T(lo + prev(k));
        }
""" if minmax else "") + """        return 1;
    }

    // O(N log64(U)) -- remove everything (N = values in it): as newly built, so reuse it instead of building a new one
    void clear() {
        n = 0;
""" + ("        gaps.clear();\n" if gaps else "") + """        clearData();
    }
""" + FASTSET_CLEAR_CPP.replace("{cnt}", "") + """
    // O(log64(U) amortized) -- remove every value v with lo <= v <= hi; returns how many were removed (0 if lo > hi)
    long long removeInValRange(T lo, T hi) {
        if (hi < lo) return 0;
        long long removed = 0;
        for (long long i = next((long long)lo - this->lo); i >= 0 && this->lo + i <= (long long)hi; i = next(i + 1))
            remove(T(this->lo + i)), removed++;
        return removed;
    }

    // O(1) -- 1 if x is in the set, else 0
    long long count(T x) const {
        long long i = (long long)x - lo;
        return i >= 0 && i < u ? (long long)(seg[0][i >> 6] >> (i & 63) & 1) : 0;
    }

    // O(1) -- how many values (no duplicates, so also how many distinct)
    long long countDistinct() const { return n; }

    // O(1) -- how many values
    long long size() const { return n; }

""" + ("""    // O(1) -- smallest value; nullopt if empty
    optional<T> min() const {
        if (!n) return nullopt;
        return mn;
    }

    // O(1) -- largest value; nullopt if empty
    optional<T> max() const {
        if (!n) return nullopt;
        return mx;
    }
""" if minmax else """    // O(log64(U)) -- smallest value; nullopt if empty
    optional<T> min() const {
        long long i = next(0);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(log64(U)) -- largest value; nullopt if empty
    optional<T> max() const {
        long long i = prev(u - 1);
        if (i < 0) return nullopt;
        return T(lo + i);
    }
""") + """
    // O(log64(U)) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        optional<T> v = min();
        if (v) remove(*v);
        return v;
    }

    // O(log64(U)) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        optional<T> v = max();
        if (v) remove(*v);
        return v;
    }

    // O(log64(U)) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) const {
        long long i = next((long long)x - lo);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(log64(U)) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) const {
        long long i = next((long long)x - lo + 1);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(log64(U)) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) const {
        long long i = prev((long long)x - lo);
        if (i < 0) return nullopt;
        return T(lo + i);
    }

    // O(log64(U)) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) const {
        long long i = prev((long long)x - lo - 1);
        if (i < 0) return nullopt;
        return T(lo + i);
    }
""" + ("""
    // O(1) -- smallest difference between two values in the set; nullopt if fewer than 2 values
    optional<long long> minAdjacentDiff() const {
        if (n < 2) return nullopt;
        return *gaps.begin();
    }

    // O(1) -- largest difference between two neighbouring values; nullopt if fewer than 2 values
    optional<long long> maxGap() const {
        if (n < 2) return nullopt;
        return *gaps.rbegin();
    }
""" if gaps else "") + """};
"""
    py = py.replace("@slots", (', "mn", "mx"' if minmax else "") + (', "gc", "gmin", "gmax"' if gaps else ""))
    if gaps:
        py = "from heapq import heappop, heappush\n" + py
    ops = sorted(["add", "remove", "count", "countDistinct", "size", "min", "max", "popMin", "popMax", "smallestGteX",
                  "smallestGtX", "largestLteX", "largestLtX", "clear", "removeInValRange"] + (["minAdjacentDiff", "maxGap"] if gaps else []))
    comps = {op: "log64(U)" for op in ops}
    comps.update({"count": "1", "countDistinct": "1", "size": "1", "clear": "N*log64(U)", "removeInValRange": "log64(U) amortized",
                  "build": "U/64"})
    if minmax:
        comps.update(min="1", max="1")
    if gaps:
        comps.update(minAdjacentDiff="1 amortized", maxGap="1 amortized")
    extras = (["minmax"] if minmax else []) + (["gaps"] if gaps else [])
    folder = "fastset" + ("-with-" + "-".join(extras) if extras else "")
    spec = dict(dtype="fastset", values="online-range", keys="numbers", tracks=" ".join(extras) or "none", comps=comps,
                mem=("none", "seg[1*U/64]", "none", "none"),
                note="U = hi - lo + 1: just the trie's U / 64 + U / 4096 + ... 64-bit words (about U / 63); no duplicates")
    path = os.path.join(ROOT, folder)
    for ext, cm, body in (("py", "#", py), ("cpp", "//", cpp)):
        attribution = f"{cm} Template by {GITHUB_USER}\n{cm} {GITHUB_FILES}{folder}/distinct.{ext}\n"
        open(os.path.join(path, f"distinct.{ext}"), "w").write(attribution + header(cm, ops, spec) + body)
    print(f"wrote {folder}/distinct")


# ------------------------------------------------------------------------------------------------ distinct values < x
# countDistinctInValRange needs "distinct values < x". The mex variants already keep what it takes (a Fenwick / per-node
# count of present values), and sorted blocks get it from their keys, so it costs those templates nothing extra.
DISTINCT_LT_PY = {
    "fenwick": """
    def _distinctLt(self, x):  # distinct values < x: the Fenwick of present values
        return self._pre(self.fp, bisect_left(self.vals, x))
""",
    "value-tree": """
    def _distinctLt(self, x):  # distinct values < x
        return self._prefix(self.p, x)
""",
    "blocks": """
    def _distinctLt(self, x):  # distinct values < x: every block before x's, then a binary search in x's block
        keys = self.keys
        b = bisect_left(self.maxes, x)
        return sum(map(len, keys[:b])) + (bisect_left(keys[b], x) if b < len(keys) else 0)
""",
}
DISTINCT_LT_PY["blocks-fenwick"] = DISTINCT_LT_PY["blocks"]
DISTINCT_LT_CPP = {
    "fenwick": """
    long long distinctLt(T x) { return pre(fp, lowerIdx(x)); }  // distinct values < x: the Fenwick of present values
""",
    "value-tree": """
    long long distinctLt(T x) const {  // distinct values < x
        if (x <= lo) return 0;
        if (x > hi) return pool[root].p;
        long long res = 0, a = lo, b = hi;
        int y = root;
        while (y && a < b) {
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else res += pool[pool[y].l].p, y = pool[y].r, a = m + 1;
        }
        return res;
    }
""",
    "blocks": """
    long long distinctLt(T x) const {  // distinct values < x: every block before x's, then a binary search in x's block
        int b = int(lower_bound(maxes.begin(), maxes.end(), x) - maxes.begin());
        long long res = 0;
        for (int k = 0; k < b; k++) res += (long long)keys[k].size();
        if (b < (int)keys.size()) res += lower_bound(keys[b].begin(), keys[b].end(), x) - keys[b].begin();
        return res;
    }
""",
}
DISTINCT_LT_CPP["blocks-fenwick"] = DISTINCT_LT_CPP["blocks"]


# ------------------------------------------------------------------------------------------------ clear()
# Every structure empties itself in the cheapest way it can without any other op paying for it (no version stamps,
# nothing recorded on updates): it touches only what is in use where it can find that cheaply, else it wipes in bulk.
CLEAR_COST = {"fenwick": "N", "value-tree": "N*log(U)", "avl": "N", "treap": "N", "splay": "N", "blocks": "N",
              "blocks-fenwick": "N", "pbds": "N", "fastset": "N*log64(U)", "trie": "1 amortized"}


def clear_py(dtype, sums, mex, mexc, mode=False, gaps=False, bits=(False, False, False), shift=False):
    X, O, A = bits
    reset = (["        self.mexV = 0"] if mexc else []) + (["        self.bk, self.maxF = {}, 0"] if mode else []) + (
        ["        self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0"] if gaps else []) + ["        self.n = self.d = 0"] + (
        ["        self.total = 0"] if sums else []) + (["        self.xtotal = 0"] if X else []) + (["        self.off = 0"] if shift else [])
    out = "\n    def _resetCached(self):  # nothing counted: as newly built\n" + "\n".join(reset) + "\n"
    f = (["fs"] if sums else []) + (["fp"] if mex else []) + (["fx"] if X else [])
    if dtype == "fenwick":
        bind = (", ".join(f) + " = " + ", ".join("self." + a for a in f)) if f else "pass"
        zero = "".join(f"\n                    {a}[j] = 0" for a in ["fc"] + f)
        dense = "".join(f"\n            self.{a} = [0] * (m + 1)" for a in ["fc"] + f)
        out += f"""
    def _clearData(self):  # few distinct values present: zero only their slots and Fenwick paths, else wipe in bulk
        m, fc, cnt = self.m, self.fc, self.cnt
        if self.d * (self.top.bit_length() + 1) * 8 < m:
            {bind}
            slots, k = [], 1
            while k <= self.n:  # the slot of the k-th smallest, by binary lifting; then skip its copies
                pos, step, before = 0, self.top, 0
                while step:
                    nxt = pos + step
                    if nxt <= m and before + fc[nxt] < k:
                        pos, before = nxt, before + fc[nxt]
                    step >>= 1
                slots.append(pos)
                k = before + cnt[pos] + 1
            for i in slots:
                cnt[i] = 0
                j = i + 1
                while j <= m:{zero}
                    j += j & -j
        else:
            self.cnt = [0] * m{dense}
"""
    elif dtype == "value-tree":
        out += "\n    def _clearData(self):\n" + "".join(f"        self.{a} = {{}}\n" for a in ["c"] + (["s"] if sums else []) + (["p"] if mex else []) + [
            a for a, on in (("x", X), ("o", O), ("a", A)) if on])
    elif dtype in ("avl", "treap", "splay"):
        lists = ["K", "C", "Z"] + (["S"] if sums else []) + (["D"] if mex else []) + [a for a, on in (("X", X), ("O", O)) if on] + {
            "avl": ["H", "L", "R"], "treap": ["L", "R"], "splay": ["L", "R", "P"]}[dtype]
        out += ("\n    def _clearData(self):  # fresh node lists (the old ones are freed in bulk)\n" +
                "".join(f"        self.{a} = [0]\n" for a in lists) + ("        self.A = [-1]\n" if A else "") +
                ("        self.P = [0.0]\n" if dtype == "treap" else "") +
                "        self.free = []\n        self.root = 0\n")
    elif dtype == "blocks":
        out += ("\n    def _clearData(self):\n        self.keys, self.cnts, self.maxes, self.bc = [], [], [], []\n        self.fc = None\n"
                "        self.cnt = {}\n" + ("        self.sums, self.bs = [], []\n        self.fs = None\n" if sums else "") +
                ("        self.bx, self.fx = [], None\n" if X else "") + ("        self.bo = []\n" if O else "") + ("        self.ba = []\n" if A else ""))
    elif dtype == "blocks-fenwick":
        out += ("\n    def _clearData(self):\n        self.keys, self.cnts, self.fcs, self.maxes, self.bc = [], [], [], [], []\n"
                "        self.fc = [0]\n        self.cnt = {}\n" + ("        self.sums, self.fss, self.bs = [], [], []\n        self.fs = [0]\n" if sums else "") +
                ("        self.xvs, self.fxs, self.bx = [], [], []\n        self.fx = [0]\n" if X else ""))
    elif dtype == "fastset":
        out += (FASTSET_CLEAR_PY.replace("{counts}", ", and the counts of the values present")
                .replace("{cnt}", "                else:\n                    cnt[base + b] = 0\n").replace("{cntvar}", ", cnt = self.seg, self.cnt"))
    return out


FASTSET_CLEAR_PY = """
    def _clearData(self):  # zero only the trie words in use (walking down from the top through set bits){counts}
        seg{cntvar}
        stack = [(len(seg) - 1, 0)]
        while stack:
            h, w = stack.pop()
            bits = seg[h][w]
            if not bits:
                continue
            seg[h][w] = 0
            base = w << 6
            while bits:
                b = (bits & -bits).bit_length() - 1
                bits &= bits - 1
                if h:
                    stack.append((h - 1, base + b))
{cnt}"""


def clear_cpp(dtype, sums, mex, mexc, mode=False, gaps=False, bits=(False, False, False), shift=False):
    X, O, A = bits
    reset = (["        mexV = 0;"] if mexc else []) + (["        bk.clear();"] if mode else []) + (["        gaps.clear(), dups = 0;"] if gaps else []) + [
        "        n = d = 0;"] + (["        total = 0;"] if sums else []) + (["        xtotal = 0;"] if X else []) + (["        off = 0;"] if shift else [])
    out = "\n    void resetCached() {  // nothing counted: as newly built\n" + "\n".join(reset) + "\n    }\n"
    f = (["fs"] if sums else []) + (["fp"] if mex else []) + (["fx"] if X else [])
    if dtype == "fenwick":
        out += ("""
    void clearData() {  // few distinct values present: zero only their slots and Fenwick paths, else wipe in bulk
        if (d * (65 - __builtin_clzll((unsigned long long)top | 1)) * 8 < m) {
            vector<int> slots;
            for (long long k = 1; k <= n;) {  // the slot of the k-th smallest, by binary lifting; then skip its copies
                int pos = 0;
                long long before = 0;
                for (int step = top; step; step >>= 1)
                    if (pos + step <= m && before + fc[pos + step] < k) pos += step, before += fc[pos];
                slots.push_back(pos);
                k = before + cnt[pos] + 1;
            }
            for (int i : slots) {
                cnt[i] = 0;
                for (int j = i + 1; j <= m; j += j & -j) fc[j] = 0""" + "".join(f", {a}[j] = 0" for a in f) + """;
            }
        } else {
            fill(cnt.begin(), cnt.end(), 0), fill(fc.begin(), fc.end(), 0)""" + "".join(f", fill({a}.begin(), {a}.end(), 0)" for a in f) + """;
        }
    }
""")
    elif dtype == "value-tree":
        zero = "v.c = 0" + (", v.s = 0" if sums else "") + (", v.p = 0" if mex else "") + (", v.xr = 0" if X else "") + (
            ", v.orv = 0" if O else "") + (", v.andv = ~T(0)" if A else "")
        out += f"""
    void clearData() {{  // zero this tree's nonzero nodes in place: the next adds reuse them, so nothing leaks
        vector<int> st;
        if (root && pool[root].c) st.push_back(root);
        while (!st.empty()) {{
            Node& v = pool[st.back()];
            st.pop_back();
            {zero};
            if (v.l && pool[v.l].c) st.push_back(v.l);
            if (v.r && pool[v.r].c) st.push_back(v.r);
        }}
    }}
"""
    elif dtype in ("avl", "treap", "splay"):
        out += """
    void clearData() {  // hand this tree's nodes back to the shared pool's free list
        vector<int> st;
        if (root) st.push_back(root);
        while (!st.empty()) {
            int t = st.back();
            st.pop_back();
            if (pool[t].l) st.push_back(pool[t].l);
            if (pool[t].r) st.push_back(pool[t].r);
            freeList.push_back(t);
        }
        root = 0;
    }
"""
    elif dtype == "blocks":
        out += ("\n    void clearData() {\n        keys.clear(), cnts.clear(), maxes.clear(), bc.clear(), fc.clear();\n" +
                ("        sums.clear(), bs.clear(), fs.clear();\n" if sums else "") + ("        bx.clear(), fx.clear();\n" if X else "") +
                ("        bo.clear();\n" if O else "") + ("        ba.clear();\n" if A else "") + "        stale = true;\n    }\n")
    elif dtype == "blocks-fenwick":
        out += ("\n    void clearData() {\n        keys.clear(), cnts.clear(), fcs.clear(), maxes.clear(), bc.clear();\n        fc.assign(1, 0);\n" +
                ("        sums.clear(), fss.clear(), bs.clear();\n        fs.assign(1, S(0));\n" if sums else "") +
                ("        xvs.clear(), fxs.clear(), bx.clear();\n        fx.assign(1, T(0));\n" if X else "") + "    }\n")
    elif dtype == "pbds":
        out += "\n    void clearData() {\n        t.clear();\n        ids = 0;\n    }\n"
    elif dtype == "fastset":
        out += FASTSET_CLEAR_CPP.replace("{cnt}", "                else cnt[base + b] = 0;\n")
    return out


FASTSET_CLEAR_CPP = """
    void clearData() {  // zero only the trie words in use (walking down from the top through set bits)
        vector<pair<int, int>> st{{(int)seg.size() - 1, 0}};
        while (!st.empty()) {
            auto [h, w] = st.back();
            st.pop_back();
            unsigned long long bits = seg[h][w];
            if (!bits) continue;
            seg[h][w] = 0;
            int base = w << 6;
            for (; bits; bits &= bits - 1) {
                int b = __builtin_ctzll(bits);
                if (h) st.push_back({h - 1, base + b});
{cnt}            }
        }
    }
"""


# ------------------------------------------------------------------------------------------------ bitwise aggregates
# xor / OR / AND over the values, each a dimension of its own (only the variants that answer them maintain them).
# xor is a group like +, so it works like the sums: prefix xors and differences, and copies count (an even count
# cancels). OR and AND have no inverse but ignore copies: a structure keeps the OR / AND of each subtree (or block)
# and answers a value range by a range walk; the k smallest / a rank range are the values up to / between k-th's.

def keep_aggs(text, xor=False, orv=False, andv=False):
    """Lines ending in '  @xor', '  @or', '  @and' (or several joined by |, or '  @!xor' ...) are kept only when one
    of those aggregates is on; the tag is dropped. Other tags are left alone."""
    flags = {"xor": xor, "or": orv, "and": andv}
    out = []
    for line in text.split("\n"):
        m = re.search(r"  @(!?)((?:xor|or|and)(?:\|(?:xor|or|and))*)$", line)
        if m:
            on = any(flags[f] for f in m.group(2).split("|"))
            if on == bool(m.group(1)):
                continue
            line = line[:m.start()]
        out.append(line)
    return "\n".join(out)


def agg_sub(text, kind, py, field=None, blockfield=None):
    """An OR template made into OR or AND: @N@ name, @W@ word, @OP@ operator, @ID@ identity (OR 0, AND all ones),
    @F@ the structure's field, @BF@ its per-block field, @FN@ the operator function (Python)."""
    o = kind == "or"
    rep = {"@N@": kind, "@W@": "OR" if o else "AND", "@OP@": "|" if o else "&",
           "@ID@": ("0" if o else "-1") if py else ("T(0)" if o else "~T(0)"), "@FN@": "or_" if o else "and_"}
    if field:
        rep["@F@"] = field[kind]
    if blockfield:
        rep["@BF@"] = blockfield[kind]
    for k, v in rep.items():
        text = text.replace(k, v)
    return text


AGG_PY_OPS = {
    "xorOfAll": "return self.xtotal",
    "xorOfLtX": "return self._xlt(x)",
    "xorOfLteX": "return self._xle(x)",
    "xorOfGtX": "return self.xtotal ^ self._xle(x)",
    "xorOfGteX": "return self.xtotal ^ self._xlt(x)",
    "xorOfInValRange": "return self._xle(hi) ^ self._xlt(lo) if lo <= hi else 0",
    "xorOfSmallestK": "if not 0 <= k <= self.n:\n    raise IndexError(f\"xorOfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}\")\nreturn self._xorFirst(k)",
    "xorOfLargestK": "if not 0 <= k <= self.n:\n    raise IndexError(f\"xorOfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}\")\nreturn self.xtotal ^ self._xorFirst(self.n - k)",
    "xorOfKthSmallestRange": "if not 1 <= kFrom <= kTo <= self.n:\n    raise IndexError(f\"xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}\")\nreturn self._xorFirst(kTo) ^ self._xorFirst(kFrom - 1)",
    "xorOfKthLargestRange": "if not 1 <= kFrom <= kTo <= self.n:\n    raise IndexError(f\"xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}\")\nreturn self._xorFirst(self.n - kFrom + 1) ^ self._xorFirst(self.n - kTo)",
}
AGG_CPP_OPS = {
    "xorOfAll": ("T", "return xtotal;"),
    "xorOfLtX": ("T", "return xlt(x);"),
    "xorOfLteX": ("T", "return xle(x);"),
    "xorOfGtX": ("T", "return xtotal ^ xle(x);"),
    "xorOfGteX": ("T", "return xtotal ^ xlt(x);"),
    "xorOfInValRange": ("T", "return lo <= hi ? T(xle(hi) ^ xlt(lo)) : T(0);"),
    "xorOfSmallestK": ("T", "if (k < 0 || k > n) throw out_of_range(\"xorOfSmallestK: needs 0 <= k <= size\");\nreturn xorFirst(k);"),
    "xorOfLargestK": ("T", "if (k < 0 || k > n) throw out_of_range(\"xorOfLargestK: needs 0 <= k <= size\");\nreturn xtotal ^ xorFirst(n - k);"),
    "xorOfKthSmallestRange": ("T", "if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range(\"xorOfKthSmallestRange: needs 1 <= kFrom <= kTo <= size\");\nreturn xorFirst(kTo) ^ xorFirst(kFrom - 1);"),
    "xorOfKthLargestRange": ("T", "if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range(\"xorOfKthLargestRange: needs 1 <= kFrom <= kTo <= size\");\nreturn xorFirst(n - kFrom + 1) ^ xorFirst(n - kTo);"),
}
# OR / AND: the values up to / from / between bounds (integers, so < x is <= x - 1); the k smallest are the values up
# to the k-th smallest, copies or not
BIT_PY_OPS = {
    "LtX": "return self._@N@Le(x - 1)",
    "LteX": "return self._@N@Le(x)",
    "GtX": "return self._@N@Ge(x + 1)",
    "GteX": "return self._@N@Ge(x)",
    "InValRange": "return self._@N@In(lo, hi) if lo <= hi else @ID@",
    "SmallestK": "if not 0 <= k <= self.n:\n    raise IndexError(f\"@N@OfSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}\")\nreturn self._@N@Le(self._kth(k)) if k else @ID@",
    "LargestK": "if not 0 <= k <= self.n:\n    raise IndexError(f\"@N@OfLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}\")\nreturn self._@N@Ge(self._kth(self.n - k + 1)) if k else @ID@",
    "KthSmallestRange": "if not 1 <= kFrom <= kTo <= self.n:\n    raise IndexError(f\"@N@OfKthSmallestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}\")\nreturn self._@N@In(self._kth(kFrom), self._kth(kTo))",
    "KthLargestRange": "if not 1 <= kFrom <= kTo <= self.n:\n    raise IndexError(f\"@N@OfKthLargestRange: needs 1 <= kFrom <= kTo <= size, got kFrom = {kFrom}, kTo = {kTo}, size = {self.n}\")\nreturn self._@N@In(self._kth(self.n - kTo + 1), self._kth(self.n - kFrom + 1))",
}
BIT_CPP_OPS = {
    "LtX": "if (x == numeric_limits<T>::min()) return @ID@;\nreturn @N@Le(x - 1);",
    "LteX": "return @N@Le(x);",
    "GtX": "if (x == numeric_limits<T>::max()) return @ID@;\nreturn @N@Ge(x + 1);",
    "GteX": "return @N@Ge(x);",
    "InValRange": "return lo <= hi ? @N@In(lo, hi) : @ID@;",
    "SmallestK": "if (k < 0 || k > n) throw out_of_range(\"@N@OfSmallestK: needs 0 <= k <= size\");\nreturn k ? @N@Le(kthAt(k)) : @ID@;",
    "LargestK": "if (k < 0 || k > n) throw out_of_range(\"@N@OfLargestK: needs 0 <= k <= size\");\nreturn k ? @N@Ge(kthAt(n - k + 1)) : @ID@;",
    "KthSmallestRange": "if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range(\"@N@OfKthSmallestRange: needs 1 <= kFrom <= kTo <= size\");\nT a = kthAt(kFrom);\nreturn @N@In(a, kthAt(kTo));",
    "KthLargestRange": "if (kFrom < 1 || kFrom > kTo || kTo > n) throw out_of_range(\"@N@OfKthLargestRange: needs 1 <= kFrom <= kTo <= size\");\nT a = kthAt(n - kTo + 1);\nreturn @N@In(a, kthAt(n - kFrom + 1));",
}
# the OR / AND of everything: where each structure keeps it
BIT_ALL = {  # dtype -> (Python, C++)
    "avl": ("return self.@F@[self.root]", "return pool[root].@F@;"),
    "value-tree": ("return self.@F@.get(1, @ID@)", "return pool[root].@F@;"),
    "trie": ("return self.@F@[1]", "return @F@[1];"),
    "blocks": ("return reduce(@FN@, self.@BF@, @ID@)", "T res = @ID@;\nfor (T v : @BF@) res @OP@= v;\nreturn res;"),
}
BIT_ALL["treap"] = BIT_ALL["splay"] = BIT_ALL["avl"]
BIT_FIELDS = {  # dtype -> (Python field, C++ field) per kind
    "avl": ({"or": "O", "and": "A"}, {"or": "orv", "and": "andv"}),
    "value-tree": ({"or": "o", "and": "a"}, {"or": "orv", "and": "andv"}),
    "trie": ({"or": "O", "and": "A"}, {"or": "orv", "and": "andv"}),
    "blocks": ({"or": "bo", "and": "ba"}, {"or": "bo", "and": "ba"}),
}
BIT_FIELDS["treap"] = BIT_FIELDS["splay"] = BIT_FIELDS["avl"]


def agg_ops(dtype, xor, orv, andv):
    """The public bodies of the enabled aggregates (Python dict, C++ dict)."""
    py, cpp = {}, {}
    if xor:
        py.update(AGG_PY_OPS)
        cpp.update(AGG_CPP_OPS)
    for kind, on in (("or", orv), ("and", andv)):
        if not on:
            continue
        pf, cf = BIT_FIELDS[dtype]
        allpy, allcpp = BIT_ALL[dtype]
        py[kind + "OfAll"] = agg_sub(allpy, kind, True, pf, pf)
        cpp[kind + "OfAll"] = ("T", agg_sub(allcpp, kind, False, cf, cf))
        for suf, body in BIT_PY_OPS.items():
            py[kind + "Of" + suf] = agg_sub(body, kind, True)
        for suf, body in BIT_CPP_OPS.items():
            cpp[kind + "Of" + suf] = ("T", agg_sub(body, kind, False))
    return py, cpp


# --- AVL / treap / splay: X = xor of the copies below, O / A = OR / AND of the values below (splay: '@splay' lines)
BST_XOR_PY = '''
    def _xlt(self, x):  # xor of the values < x (copies count)
        K, C, X, L, R = self.K, self.C, self.X, self.L, self.R
        t, res = self.root, 0  @!splay
        t, res, last = self.root, 0, 0  @splay
        while t:
            last = t  @splay
            if K[t] < x:
                res ^= X[L[t]] ^ (K[t] if C[t] & 1 else 0)
                t = R[t]
            else:
                t = L[t]
        self._touch(last)  @splay
        return res

    def _xle(self, x):  # xor of the values <= x (copies count)
        K, C, X, L, R = self.K, self.C, self.X, self.L, self.R
        t, res = self.root, 0  @!splay
        t, res, last = self.root, 0, 0  @splay
        while t:
            last = t  @splay
            if x < K[t]:
                t = L[t]
            else:
                res ^= X[L[t]] ^ (K[t] if C[t] & 1 else 0)
                t = R[t]
        self._touch(last)  @splay
        return res

    def _xorFirst(self, k):  # xor of the k smallest values (copies count)
        if k <= 0:
            return 0
        K, C, Z, X, L, R = self.K, self.C, self.Z, self.X, self.L, self.R
        t, res = self.root, 0
        while True:
            l = L[t]
            zl = Z[l]
            if k <= zl:
                t = l
            elif k <= zl + C[t]:
                self._touch(t)  @splay
                return res ^ X[l] ^ (K[t] if (k - zl) & 1 else 0)
            else:
                k -= zl + C[t]
                res ^= X[l] ^ (K[t] if C[t] & 1 else 0)
                t = R[t]
'''

BST_BIT_PY = '''
    def _@N@Le(self, x):  # @W@ of the values <= x
        K, F, L, R = self.K, self.@F@, self.L, self.R
        t, res = self.root, @ID@  @!splay
        t, res, last = self.root, @ID@, 0  @splay
        while t:
            last = t  @splay
            if x < K[t]:
                t = L[t]
            else:
                res @OP@= F[L[t]] @OP@ K[t]
                t = R[t]
        self._touch(last)  @splay
        return res

    def _@N@Ge(self, x):  # @W@ of the values >= x
        K, F, L, R = self.K, self.@F@, self.L, self.R
        t, res = self.root, @ID@  @!splay
        t, res, last = self.root, @ID@, 0  @splay
        while t:
            last = t  @splay
            if K[t] < x:
                t = R[t]
            else:
                res @OP@= F[R[t]] @OP@ K[t]
                t = L[t]
        self._touch(last)  @splay
        return res

    def _@N@In(self, lo, hi):  # @W@ of the values in [lo, hi] (lo <= hi)
        K, F, L, R = self.K, self.@F@, self.L, self.R
        t = self.root
        last = 0  @splay
        while t and not lo <= K[t] <= hi:  # down to the highest node inside [lo, hi]
            last = t  @splay
            t = L[t] if hi < K[t] else R[t]
        if not t:
            self._touch(last)  @splay
            return @ID@
        res = K[t]
        a, na = t, 0  @splay
        u = L[t]  # its left side is <= hi: keep what is >= lo
        while u:
            a, na = u, na + 1  @splay
            if lo <= K[u]:
                res @OP@= K[u] @OP@ F[R[u]]
                u = L[u]
            else:
                u = R[u]
        b, nb = t, 0  @splay
        u = R[t]  # its right side is >= lo: keep what is <= hi
        while u:
            b, nb = u, nb + 1  @splay
            if K[u] <= hi:
                res @OP@= K[u] @OP@ F[L[u]]
                u = R[u]
            else:
                u = L[u]
        self._touch(a if na >= nb else b)  # the end of the longer path pays for both  @splay
        return res
'''

BST_XOR_CPP = '''
    T xlt(T x) {  // xor of the values < x (copies count)
        int t = root;
        int last = 0;  @splay
        T res = 0;
        while (t) {
            last = t;  @splay
            const Node& v = pool[t];
            if (v.key < x) res ^= pool[v.l].xr ^ (v.c & 1 ? v.key : T(0)), t = v.r;
            else t = v.l;
        }
        touch(last);  @splay
        return res;
    }

    T xle(T x) {  // xor of the values <= x (copies count)
        int t = root;
        int last = 0;  @splay
        T res = 0;
        while (t) {
            last = t;  @splay
            const Node& v = pool[t];
            if (x < v.key) t = v.l;
            else res ^= pool[v.l].xr ^ (v.c & 1 ? v.key : T(0)), t = v.r;
        }
        touch(last);  @splay
        return res;
    }

    T xorFirst(long long k) {  // xor of the k smallest values (copies count)
        if (k <= 0) return 0;
        int t = root;
        T res = 0;
        while (true) {
            const Node& v = pool[t];
            long long zl = pool[v.l].z;
            if (k <= zl) t = v.l;
            else if (k <= zl + v.c) {
                res ^= pool[v.l].xr ^ ((k - zl) & 1 ? v.key : T(0));
                touch(t);  @splay
                return res;
            } else k -= zl + v.c, res ^= pool[v.l].xr ^ (v.c & 1 ? v.key : T(0)), t = v.r;
        }
    }
'''

BST_BIT_CPP = '''
    T @N@Le(T x) {  // @W@ of the values <= x
        int t = root;
        int last = 0;  @splay
        T res = @ID@;
        while (t) {
            last = t;  @splay
            if (x < pool[t].key) t = pool[t].l;
            else res @OP@= pool[pool[t].l].@F@ @OP@ pool[t].key, t = pool[t].r;
        }
        touch(last);  @splay
        return res;
    }

    T @N@Ge(T x) {  // @W@ of the values >= x
        int t = root;
        int last = 0;  @splay
        T res = @ID@;
        while (t) {
            last = t;  @splay
            if (pool[t].key < x) t = pool[t].r;
            else res @OP@= pool[pool[t].r].@F@ @OP@ pool[t].key, t = pool[t].l;
        }
        touch(last);  @splay
        return res;
    }

    T @N@In(T lo, T hi) {  // @W@ of the values in [lo, hi] (lo <= hi)
        int t = root;
        int last = 0;  @splay
        while (t && (pool[t].key < lo || hi < pool[t].key)) {  // down to the highest node inside [lo, hi]
            last = t;  @splay
            t = hi < pool[t].key ? pool[t].l : pool[t].r;
        }
        if (!t) {
            touch(last);  @splay
            return @ID@;
        }
        T res = pool[t].key;
        int a = t, na = 0, b = t, nb = 0;  @splay
        for (int u = pool[t].l; u;) {  // its left side is <= hi: keep what is >= lo
            a = u, na++;  @splay
            if (lo <= pool[u].key) res @OP@= pool[u].key @OP@ pool[pool[u].r].@F@, u = pool[u].l;
            else u = pool[u].r;
        }
        for (int u = pool[t].r; u;) {  // its right side is >= lo: keep what is <= hi
            b = u, nb++;  @splay
            if (pool[u].key <= hi) res @OP@= pool[u].key @OP@ pool[pool[u].l].@F@, u = pool[u].r;
            else u = pool[u].l;
        }
        touch(na >= nb ? a : b);  // the end of the longer path pays for both  @splay
        return res;
    }
'''

# --- value tree: x / o / a dicts (Python, by heap index), xr / orv / andv node fields (C++)
VT_XOR_PY = '''
    def _xprefix(self, x):  # xor of the values < x (copies count)
        if x <= self.lo:
            return 0
        if x > self.hi:
            return self.xtotal
        f = self.x
        i = self.cap + x - self.lo
        res = 0
        while i > 1:
            if i & 1:
                res ^= f.get(i - 1, 0)
            i >>= 1
        return res

    def _xlt(self, x):
        return self._xprefix(x)

    def _xle(self, x):
        return self._xprefix(x + 1)

    def _xorFirst(self, k):  # xor of the k smallest values (copies count)
        if k <= 0:
            return 0
        c, f, i, size, res = self.c, self.x, 1, self.cap, 0
        while i < size:
            i <<= 1
            cl = c.get(i, 0)
            if k > cl:
                k -= cl
                res ^= f.get(i, 0)
                i += 1
        return res ^ (i - size + self.lo) if k & 1 else res  # k copies of the leaf's value left
'''

VT_BIT_PY = '''
    def _@N@In(self, lo, hi):  # @W@ of the values in [lo, hi]: bottom-up over the heap-indexed blocks
        lo, hi = max(lo, self.lo), min(hi, self.hi)
        if lo > hi:
            return @ID@
        f, res = self.@F@, @ID@
        l, r = self.cap + lo - self.lo, self.cap + hi - self.lo + 1
        while l < r:
            if l & 1:
                res @OP@= f.get(l, @ID@)
                l += 1
            if r & 1:
                r -= 1
                res @OP@= f.get(r, @ID@)
            l >>= 1
            r >>= 1
        return res

    def _@N@Le(self, x):  # @W@ of the values <= x
        return self._@N@In(self.lo, x)

    def _@N@Ge(self, x):  # @W@ of the values >= x
        return self._@N@In(x, self.hi)
'''

VT_XOR_CPP = '''
    T xprefix(T x) const {  // xor of the values < x (copies count)
        if (x <= lo) return 0;
        if (x > hi) return pool[root].xr;
        T res = 0;
        int y = root;
        long long a = lo, b = hi;
        while (y && a < b) {
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else res ^= pool[pool[y].l].xr, y = pool[y].r, a = m + 1;
        }
        return res;  // y is now the leaf of x (or empty): values < x only
    }

    T xlt(T x) const { return xprefix(x); }
    T xle(T x) const { return xprefix(x + 1); }

    T xorFirst(long long k) const {  // xor of the k smallest values (copies count)
        if (k <= 0) return 0;
        int y = root;
        long long a = lo, b = hi;
        T res = 0;
        while (a < b) {
            long long m = a + (b - a) / 2;
            const Node& L = pool[pool[y].l];
            if (k <= L.c) y = pool[y].l, b = m;
            else k -= L.c, res ^= L.xr, y = pool[y].r, a = m + 1;
        }
        return k & 1 ? T(res ^ T(a)) : res;  // k copies of the leaf's value left
    }
'''

VT_BIT_CPP = '''
    T @N@Walk(int y, long long a, long long b, long long ql, long long qr) const {  // @W@ of node y's values in [ql, qr]
        if (!y || qr < a || b < ql) return @ID@;
        if (ql <= a && b <= qr) return pool[y].@F@;
        long long m = a + (b - a) / 2;
        return @N@Walk(pool[y].l, a, m, ql, qr) @OP@ @N@Walk(pool[y].r, m + 1, b, ql, qr);
    }

    T @N@In(T ql, T qr) const { return @N@Walk(root, lo, hi, ql, qr); }  // @W@ of the values in [ql, qr]
    T @N@Le(T x) const { return @N@Walk(root, lo, hi, lo, x); }  // @W@ of the values <= x
    T @N@Ge(T x) const { return @N@Walk(root, lo, hi, x, hi); }  // @W@ of the values >= x
'''

# --- binary trie: X = xor of the stored values of the copies below (with xorAll: v ^ mask per copy, fixed up by the
# parity of how many copies were taken), O / A = OR / AND of the values below
TRIE_XOR_PY = '''
    def _xlt(self, x):  # xor of the values < x (copies count)
        if x <= 0:
            return 0
        if x > self.top:
            return self.xtotal
        L, R, X = self.L, self.R, self.X
        C, key, cnt = self.C, self.mask, 0  # (stored as v ^ mask: an odd number of copies taken leaves one mask)  @K
        t, res = 1, 0
        for h in range(self.B - 1, -1, -1):
            if x >> h & 1:  @!K
                res ^= X[L[t]]  @!K
                t = R[t]  @!K
            else:  @!K
                t = L[t]  @!K
            kb = key >> h & 1  @K
            if x >> h & 1:  # everything below the child with bit 0 is < x  @K
                u = R[t] if kb else L[t]  @K
                res ^= X[u]  @K
                cnt += C[u]  @K
                t = L[t] if kb else R[t]  @K
            else:  @K
                t = R[t] if kb else L[t]  @K
            if not t:
                break
        return res ^ key if cnt & 1 else res  @K
        return res  @!K

    def _xle(self, x):
        return self._xlt(x + 1)

    def _xorFirst(self, k):  # xor of the k smallest values (copies count)
        if k <= 0:
            return 0
        L, R, C, X = self.L, self.R, self.C, self.X
        key, k0 = self.mask, k  @K
        t, res, y = 1, 0, 0  # y: the stored value of the leaf reached
        for h in range(self.B - 1, -1, -1):
            l = L[t]  @!K
            if k <= C[l]:  @!K
                t = l  @!K
            else:  @!K
                k -= C[l]  @!K
                res ^= X[l]  @!K
                t = R[t]  @!K
                y |= 1 << h  @!K
            kb = key >> h & 1  @K
            z = R[t] if kb else L[t]  # the child whose values have bit h = 0  @K
            if k <= C[z]:  @K
                t = z  @K
                y |= kb << h  @K
            else:  @K
                k -= C[z]  @K
                res ^= X[z]  @K
                t = L[t] if kb else R[t]  @K
                y |= (kb ^ 1) << h  @K
        if k & 1:  # k copies of the leaf's value left
            res ^= y
        return res ^ key if k0 & 1 else res  @K
        return res  @!K
'''

TRIE_BIT_PY = '''
    def _@N@In(self, lo, hi):  # @W@ of the values in [lo, hi]
        lo, hi = max(lo, 0), min(hi, self.top)
        if lo > hi:
            return @ID@
        L, R, F = self.L, self.R, self.@F@
        t, h = 1, self.B - 1
        while h >= 0 and (lo >> h & 1) == (hi >> h & 1):  # the bits lo and hi share: one path
            t = R[t] if lo >> h & 1 else L[t]
            h -= 1
        if h < 0 or not t:
            return F[t]
        res = @ID@
        u = L[t]  # where they split, the left child only needs v >= lo
        for g in range(h - 1, -1, -1):
            if not u:
                break
            if lo >> g & 1:
                u = R[u]
            else:
                res @OP@= F[R[u]]
                u = L[u]
        res @OP@= F[u]
        u = R[t]  # and the right child only v <= hi
        for g in range(h - 1, -1, -1):
            if not u:
                break
            if hi >> g & 1:
                res @OP@= F[L[u]]
                u = R[u]
            else:
                u = L[u]
        return res @OP@ F[u]

    def _@N@Le(self, x):  # @W@ of the values <= x
        return self._@N@In(0, x)

    def _@N@Ge(self, x):  # @W@ of the values >= x
        return self._@N@In(x, self.top)
'''

TRIE_XOR_CPP = '''
    T xlt(T x) const {  // xor of the values < x (copies count)
        long long b = (long long)x;
        if (b <= 0) return 0;
        if (b > top) return xtotal;
        int t = 1;
        T res = 0;
        long long cnt = 0;  // (stored as v ^ mask: an odd number of copies taken leaves one mask)  @K
        for (int h = B - 1; h >= 0 && t; h--) {
            if (b >> h & 1) res ^= xr[ch[t][0]], t = ch[t][1];  @!K
            else t = ch[t][0];  @!K
            int kb = int(mask >> h & 1);  @K
            if (b >> h & 1) res ^= xr[ch[t][kb]], cnt += c[ch[t][kb]], t = ch[t][kb ^ 1];  // everything below the bit-0 child is < x  @K
            else t = ch[t][kb];  @K
        }
        return cnt & 1 ? T(res ^ T(mask)) : res;  @K
        return res;  @!K
    }

    T xle(T x) const { return xlt(T((long long)x + 1)); }

    T xorFirst(long long k) const {  // xor of the k smallest values (copies count)
        if (k <= 0) return 0;
        long long k0 = k;  @K
        int t = 1;
        long long y = 0;  // the stored value of the leaf reached
        T res = 0;
        for (int h = B - 1; h >= 0; h--) {
            int l = ch[t][0];  @!K
            if (k <= c[l]) t = l;  @!K
            else k -= c[l], res ^= xr[l], t = ch[t][1], y |= 1LL << h;  @!K
            int kb = int(mask >> h & 1), z = ch[t][kb];  // z: the child whose values have bit h = 0  @K
            if (k <= c[z]) t = z, y |= (long long)kb << h;  @K
            else k -= c[z], res ^= xr[z], t = ch[t][kb ^ 1], y |= (long long)(kb ^ 1) << h;  @K
        }
        if (k & 1) res ^= T(y);  // k copies of the leaf's value left
        return k0 & 1 ? T(res ^ T(mask)) : res;  @K
        return res;  @!K
    }
'''

TRIE_BIT_CPP = '''
    T @N@In(T ql, T qr) const {  // @W@ of the values in [ql, qr]
        long long lo = std::max<long long>(ql, 0), hi = std::min<long long>(qr, top);
        if (lo > hi) return @ID@;
        int t = 1, h = B - 1;
        for (; h >= 0 && (lo >> h & 1) == (hi >> h & 1); h--) t = ch[t][lo >> h & 1];  // the bits lo and hi share: one path
        if (h < 0 || !t) return @F@[t];
        T res = @ID@;
        int u = ch[t][0];  // where they split, the left child only needs v >= lo
        for (int g = h - 1; g >= 0 && u; g--) {
            if (lo >> g & 1) u = ch[u][1];
            else res @OP@= @F@[ch[u][1]], u = ch[u][0];
        }
        res @OP@= @F@[u];
        u = ch[t][1];  // and the right child only v <= hi
        for (int g = h - 1; g >= 0 && u; g--) {
            if (hi >> g & 1) res @OP@= @F@[ch[u][0]], u = ch[u][1];
            else u = ch[u][0];
        }
        return res @OP@ @F@[u];
    }

    T @N@Le(T x) const { return @N@In(T(0), x); }  // @W@ of the values <= x
    T @N@Ge(T x) const { return @N@In(x, T(top)); }  // @W@ of the values >= x
'''

# --- Fenwick (offline): fx = a Fenwick of xor over the values with an odd count
FEN_XOR_PY = '''
    def _xpre(self, i):  # xor over positions 0..i-1
        f, res = self.fx, 0
        while i > 0:
            res ^= f[i]
            i &= i - 1
        return res

    def _xlt(self, x):
        return self._xpre(bisect_left(self.vals, x))

    def _xle(self, x):
        return self._xpre(bisect_right(self.vals, x))

    def _xorFirst(self, k):  # xor of the k smallest values (copies count): binary lifting, as for the k-th
        if k <= 0:
            return 0
        fc, fx, m = self.fc, self.fx, self.m
        pos, step, before, res = 0, self.top, 0, 0
        while step:
            nxt = pos + step
            if nxt <= m and before + fc[nxt] < k:
                pos = nxt
                before += fc[nxt]
                res ^= fx[nxt]
            step >>= 1
        return res ^ self.vals[pos] if (k - before) & 1 else res  # k - before copies of the answer's value
'''

FEN_XOR_CPP = '''
    T xpre(int i) const {  // xor over positions 0..i-1
        T res = 0;
        for (; i > 0; i &= i - 1) res ^= fx[i];
        return res;
    }

    T xlt(T x) const { return xpre(lowerIdx(x)); }
    T xle(T x) const { return xpre(upperIdx(x)); }

    T xorFirst(long long k) const {  // xor of the k smallest values (copies count): binary lifting, as for the k-th
        if (k <= 0) return 0;
        int pos = 0;
        long long before = 0;
        T res = 0;
        for (int step = top; step; step >>= 1)
            if (pos + step <= m && before + fc[pos + step] < k) pos += step, before += fc[pos], res ^= fx[pos];
        return (k - before) & 1 ? T(res ^ vals[pos]) : res;  // k - before copies of the answer's value
    }
'''

# --- sorted blocks: bx = per block xor of the values with an odd count, fx = a Fenwick of xor over bx (stale like
# fc); bo / ba = per block OR / AND, recomputed from the block when a value leaves it
BLK_XOR_PY = '''
    @staticmethod
    def _buildx(a):  # xor Fenwick over a
        f = [0] + a
        for i in range(1, len(f)):
            j = i + (i & -i)
            if j < len(f):
                f[j] ^= f[i]
        return f

    @staticmethod
    def _fenx(f, i, v):
        if f is not None:
            i += 1
            while i < len(f):
                f[i] ^= v
                i += i & -i

    def _xpre(self, k):  # xor of blocks 0..k-1
        f = self.fx
        if f is None:
            f = self.fx = self._buildx(self.bx)
        res = 0
        while k > 0:
            res ^= f[k]
            k &= k - 1
        return res

    @staticmethod
    def _xodd(keys, cnts):  # xor of the values with an odd count
        return reduce(xor, compress(keys, map(and_, cnts, repeat(1))), 0)

    def _xbelow(self, x, strict):  # xor of the values < x (strict) or <= x (copies count)
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            return self.xtotal
        j = (bisect_left if strict else bisect_right)(self.keys[k], x)
        return self._xpre(k) ^ self._xodd(self.keys[k][:j], self.cnts[k][:j])

    def _xlt(self, x):
        return self._xbelow(x, True)

    def _xle(self, x):
        return self._xbelow(x, False)

    def _xorFirst(self, k):  # xor of the k smallest values (copies count)
        if k <= 0:
            return 0
        b, before, _ = self._locate(k)
        cn = self.cnts[b]
        pre = list(accumulate(cn))
        j = bisect_left(pre, k - before)
        res = self._xpre(b) ^ self._xodd(self.keys[b][:j], cn[:j])
        return res ^ self.keys[b][j] if (k - before - pre[j] + cn[j]) & 1 else res  # (copies of the k-th taken)
'''

BLK_BIT_PY = '''
    def _@N@Le(self, x):  # @W@ of the values <= x
        b = bisect_right(self.maxes, x)  # blocks before b hold only values <= x
        res = reduce(@FN@, self.@BF@[:b], @ID@)
        if b < len(self.keys):
            blk = self.keys[b]
            res = reduce(@FN@, blk[:bisect_right(blk, x)], res)
        return res

    def _@N@Ge(self, x):  # @W@ of the values >= x
        a = bisect_left(self.maxes, x)  # blocks after a hold only values >= x
        if a == len(self.keys):
            return @ID@
        blk = self.keys[a]
        return reduce(@FN@, self.@BF@[a + 1:], reduce(@FN@, blk[bisect_left(blk, x):], @ID@))

    def _@N@In(self, lo, hi):  # @W@ of the values in [lo, hi] (lo <= hi)
        keys = self.keys
        a, b = bisect_left(self.maxes, lo), bisect_right(self.maxes, hi)
        if a == len(keys):
            return @ID@
        blk = keys[a]
        i = bisect_left(blk, lo)
        if a == b:  # one block holds them all
            return reduce(@FN@, blk[i:bisect_right(blk, hi)], @ID@)
        res = reduce(@FN@, self.@BF@[a + 1:b], reduce(@FN@, blk[i:], @ID@))  # blocks a + 1 .. b - 1 lie wholly inside
        if b < len(keys):
            res = reduce(@FN@, keys[b][:bisect_right(keys[b], hi)], res)
        return res
'''

BLK_XOR_CPP = '''
    static void buildx(vector<T>& f, const vector<T>& a) {  // xor Fenwick over a
        f.assign(a.size() + 1, 0);
        for (size_t i = 1; i < f.size(); i++) {
            f[i] ^= a[i - 1];
            size_t j = i + (i & -i);
            if (j < f.size()) f[j] ^= f[i];
        }
    }

    void fenx(int i, T v) {
        if (stale) return;
        for (i++; i < (int)fx.size(); i += i & -i) fx[i] ^= v;
    }

    T xpre(int k) {  // xor of blocks 0..k-1
        fresh();
        T res = 0;
        for (; k > 0; k &= k - 1) res ^= fx[k];
        return res;
    }

    T xbelow(T x, bool strict) {  // xor of the values < x (strict) or <= x (copies count)
        int k = blockOf(x);
        if (k == (int)keys.size()) return xtotal;
        const vector<T>& b = keys[k];
        int j = int((strict ? lower_bound(b.begin(), b.end(), x) : upper_bound(b.begin(), b.end(), x)) - b.begin());
        T res = xpre(k);
        for (int i = 0; i < j; i++)
            if (cnts[k][i] & 1) res ^= b[i];
        return res;
    }

    T xlt(T x) { return xbelow(x, true); }
    T xle(T x) { return xbelow(x, false); }

    T xodd(int k) const {  // xor of block k's values with an odd count
        T res = 0;
        for (size_t j = 0; j < keys[k].size(); j++)
            if (cnts[k][j] & 1) res ^= keys[k][j];
        return res;
    }

    T xorFirst(long long k) {  // xor of the k smallest values (copies count)
        if (k <= 0) return 0;
        auto [b, before, acc] = locate(k);
        (void)acc;
        T res = xpre(b);
        for (size_t j = 0;; j++) {
            if (k <= before + cnts[b][j]) return (k - before) & 1 ? T(res ^ keys[b][j]) : res;
            before += cnts[b][j];
            if (cnts[b][j] & 1) res ^= keys[b][j];
        }
    }
'''

BLK_BIT_CPP = '''
    T @N@Le(T x) const {  // @W@ of the values <= x
        int b = int(upper_bound(maxes.begin(), maxes.end(), x) - maxes.begin());  // blocks before b hold only values <= x
        T res = @ID@;
        for (int k = 0; k < b; k++) res @OP@= @BF@[k];
        if (b < (int)keys.size())
            for (T v : keys[b]) {
                if (x < v) break;
                res @OP@= v;
            }
        return res;
    }

    T @N@Ge(T x) const {  // @W@ of the values >= x
        int a = blockOf(x);  // blocks after a hold only values >= x
        T res = @ID@;
        if (a == (int)keys.size()) return res;
        for (int k = a + 1; k < (int)keys.size(); k++) res @OP@= @BF@[k];
        for (auto it = lower_bound(keys[a].begin(), keys[a].end(), x); it != keys[a].end(); ++it) res @OP@= *it;
        return res;
    }

    T @N@In(T lo, T hi) const {  // @W@ of the values in [lo, hi] (lo <= hi)
        int a = blockOf(lo), b = int(upper_bound(maxes.begin(), maxes.end(), hi) - maxes.begin());
        T res = @ID@;
        if (a == (int)keys.size()) return res;
        auto it = lower_bound(keys[a].begin(), keys[a].end(), lo);
        if (a == b) {  // one block holds them all
            for (; it != keys[a].end() && !(hi < *it); ++it) res @OP@= *it;
            return res;
        }
        for (; it != keys[a].end(); ++it) res @OP@= *it;
        for (int k = a + 1; k < b; k++) res @OP@= @BF@[k];  // blocks a + 1 .. b - 1 lie wholly inside
        if (b < (int)keys.size())
            for (T v : keys[b]) {
                if (hi < v) break;
                res @OP@= v;
            }
        return res;
    }
'''

# --- blocks with Fenwicks: xvs = per block the value where its count is odd (else 0), fxs = xor Fenwicks over them;
# bx = per block xor, fx = xor Fenwick over bx. Rebuilt with the count Fenwicks, point-updated when only parity flips.
BF_XOR_PY = '''
    @staticmethod
    def _buildx(a):  # xor Fenwick over a, in C-level passes like _build
        p = list(accumulate(a, xor, initial=0))
        m = len(p)
        return list(map(xor, p, map(p.__getitem__, map(and_, range(m), range(-1, m - 1)))))

    @staticmethod
    def _fenx(f, i, v):
        i += 1
        while i < len(f):
            f[i] ^= v
            i += i & -i

    @staticmethod
    def _xpre(f, i):  # xor over positions 0..i-1
        res = 0
        while i > 0:
            res ^= f[i]
            i &= i - 1
        return res

    def _xlt(self, x):  # xor of the values < x (copies count)
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            return self.xtotal
        return self._xpre(self.fx, k) ^ self._xpre(self.fxs[k], bisect_left(self.keys[k], x))

    def _xle(self, x):  # xor of the values <= x (copies count)
        k = bisect_right(self.maxes, x)
        if k == len(self.keys):
            return self.xtotal
        return self._xpre(self.fx, k) ^ self._xpre(self.fxs[k], bisect_right(self.keys[k], x))

    def _xorFirst(self, k):  # xor of the k smallest values (copies count): lift over blocks, then inside one
        if k <= 0:
            return 0
        fc, fx = self.fc, self.fx
        m = len(self.bc)
        b, before, res = 0, 0, 0
        step = 1 << (m.bit_length() - 1)
        while step:
            nxt = b + step
            if nxt <= m and before + fc[nxt] < k:
                b = nxt
                before += fc[nxt]
                res ^= fx[nxt]
            step >>= 1
        f, g = self.fcs[b], self.fxs[b]
        m = len(self.keys[b])
        j = 0
        step = 1 << (m.bit_length() - 1)
        while step:
            nxt = j + step
            if nxt <= m and before + f[nxt] < k:
                j = nxt
                before += f[nxt]
                res ^= g[nxt]
            step >>= 1
        return res ^ self.keys[b][j] if (k - before) & 1 else res  # k - before copies of the answer's value
'''

BF_XOR_CPP = '''
    static vector<T> buildx(const vector<T>& a) {  // xor Fenwick over a
        vector<T> f(a.size() + 1, 0);
        for (size_t i = 1; i < f.size(); i++) {
            f[i] ^= a[i - 1];
            size_t j = i + (i & -i);
            if (j < f.size()) f[j] ^= f[i];
        }
        return f;
    }

    static void fenx(vector<T>& f, int i, T v) {
        for (i++; i < (int)f.size(); i += i & -i) f[i] ^= v;
    }

    static T xpre(const vector<T>& f, int i) {  // xor over positions 0..i-1
        T res = 0;
        for (; i > 0; i &= i - 1) res ^= f[i];
        return res;
    }

    T xbelow(T x, bool strict) const {  // xor of the values < x (strict) or <= x (copies count)
        int k = int((strict ? lower_bound(maxes.begin(), maxes.end(), x) : upper_bound(maxes.begin(), maxes.end(), x)) - maxes.begin());
        if (k == (int)keys.size()) return xtotal;
        const vector<T>& b = keys[k];
        int j = int((strict ? lower_bound(b.begin(), b.end(), x) : upper_bound(b.begin(), b.end(), x)) - b.begin());
        return xpre(fx, k) ^ xpre(fxs[k], j);
    }

    T xlt(T x) const { return xbelow(x, true); }
    T xle(T x) const { return xbelow(x, false); }

    T xorFirst(long long k) const {  // xor of the k smallest values (copies count): lift over blocks, then inside one
        if (k <= 0) return 0;
        int m = (int)bc.size(), b = 0, j = 0;
        long long before = 0;
        T res = 0;
        for (int step = 1 << (31 - __builtin_clz(m)); step; step >>= 1)
            if (b + step <= m && before + fc[b + step] < k) b += step, before += fc[b], res ^= fx[b];
        const vector<long long>& f = fcs[b];
        m = (int)keys[b].size();
        for (int step = 1 << (31 - __builtin_clz(m)); step; step >>= 1)
            if (j + step <= m && before + f[j + step] < k) j += step, before += f[j], res ^= fxs[b][j];
        return (k - before) & 1 ? T(res ^ keys[b][j]) : res;  // k - before copies of the answer's value
    }
'''

AGG_HELPERS = {  # dtype -> (Python xor, Python OR template, C++ xor, C++ OR template)
    "fenwick": (FEN_XOR_PY, None, FEN_XOR_CPP, None),
    "value-tree": (VT_XOR_PY, VT_BIT_PY, VT_XOR_CPP, VT_BIT_CPP),
    "avl": (BST_XOR_PY, BST_BIT_PY, BST_XOR_CPP, BST_BIT_CPP),
    "trie": (TRIE_XOR_PY, TRIE_BIT_PY, TRIE_XOR_CPP, TRIE_BIT_CPP),
    "blocks": (BLK_XOR_PY, BLK_BIT_PY, BLK_XOR_CPP, BLK_BIT_CPP),
    "blocks-fenwick": (BF_XOR_PY, None, BF_XOR_CPP, None),
}
AGG_HELPERS["treap"] = AGG_HELPERS["splay"] = AGG_HELPERS["avl"]


def agg_helpers(dtype, py, xor, orv, andv, mask=False):
    """The private walks behind the enabled aggregates, for one language."""
    xp, bp, xc, bc = AGG_HELPERS[dtype]
    xs, bs = (xp, bp) if py else (xc, bc)
    out = ""
    if xor:
        out += xs
    for kind, on in (("or", orv), ("and", andv)):
        if on:
            pf, cf = BIT_FIELDS[dtype]
            f = pf if py else cf
            out += agg_sub(bs, kind, py, f, f)
    for tag, on in (("splay", dtype == "splay"), ("K", mask)):  # (not keep_tags: '    @staticmethod' looks like a tag)
        out = "\n".join(line[:-len(f"  @{tag}")] if line.endswith(f"  @{tag}") and on else
                         line[:-len(f"  @!{tag}")] if line.endswith(f"  @!{tag}") and not on else line
                         for line in out.split("\n") if not (line.endswith(f"  @{tag}") and not on or line.endswith(f"  @!{tag}") and on))
    return out


# ------------------------------------------------------------------------------------------------ shiftAll
# shiftAll(d) adds d to every value in O(1): a variant with it stores each value v as v - off, so the structure and
# every cache (min / max, medians, mode, mex) stay in stored values and shiftAll only moves off. The public ops turn
# their value arguments into stored ones and their value results back; sums add off once per value summed; gaps and
# |v - x| sums don't change under a shift. Only comparison structures (no value range or bits fixed up front), and no
# xor / OR / AND (a shift changes bits unpredictably).
SHIFT_DTYPES = {"avl", "treap", "splay", "blocks", "blocks-fenwick", "pbds"}
SHIFT_VALUE_OPS = {"popMin", "popMax", "pop", "kth", "min", "max", "medianLow", "medianHigh", "largestLtX", "largestLteX",
                   "smallestGtX", "smallestGteX", "mex"}  # results that are values: + off on the way out
SHIFT_VALUE_ARGS = {"x": ["x"], "xc": ["x"], "v": ["val"], "vc": ["val"], "lohi": ["lo", "hi"]}
SHIFT_SUMS_PY = {
    "sumAll": "return self.total + self.off * self.n",
    "sumLtX": "x -= self.off\nreturn self._slt(x) + self.off * self._lt(x)",
    "sumLteX": "x -= self.off\nreturn self._sle(x) + self.off * self._le(x)",
    "sumGtX": "x -= self.off\nreturn self.total - self._sle(x) + self.off * (self.n - self._le(x))",
    "sumGteX": "x -= self.off\nreturn self.total - self._slt(x) + self.off * (self.n - self._lt(x))",
    "sumInValRange": "if lo > hi:\n    return 0\nlo -= self.off\nhi -= self.off\nreturn self._sle(hi) - self._slt(lo) + self.off * (self._le(hi) - self._lt(lo))",
    "sumSmallestK": "@CHECK@\nreturn self._sumFirst(k) + self.off * k",
    "sumLargestK": "@CHECK@\nreturn self.total - self._sumFirst(self.n - k) + self.off * k",
    "sumKthSmallestRange": "@CHECK@\nreturn self._sumFirst(kTo) - self._sumFirst(kFrom - 1) + self.off * (kTo - kFrom + 1)",
    "sumKthLargestRange": "@CHECK@\nreturn self._sumFirst(self.n - kFrom + 1) - self._sumFirst(self.n - kTo) + self.off * (kTo - kFrom + 1)",
}
SHIFT_SUMS_CPP = {
    "sumAll": "return total + S(off) * n;",
    "sumLtX": "x -= off;\nreturn slt(x) + S(off) * lt(x);",
    "sumLteX": "x -= off;\nreturn sle(x) + S(off) * le(x);",
    "sumGtX": "x -= off;\nreturn total - sle(x) + S(off) * (n - le(x));",
    "sumGteX": "x -= off;\nreturn total - slt(x) + S(off) * (n - lt(x));",
    "sumInValRange": "if (hi < lo) return 0;\nlo -= off, hi -= off;\nreturn sle(hi) - slt(lo) + S(off) * (le(hi) - lt(lo));",
    "sumSmallestK": "@CHECK@\nreturn sumFirst(k) + S(off) * k;",
    "sumLargestK": "@CHECK@\nreturn total - sumFirst(n - k) + S(off) * k;",
    "sumKthSmallestRange": "@CHECK@\nreturn sumFirst(kTo) - sumFirst(kFrom - 1) + S(off) * (kTo - kFrom + 1);",
    "sumKthLargestRange": "@CHECK@\nreturn sumFirst(n - kFrom + 1) - sumFirst(n - kTo) + S(off) * (kTo - kFrom + 1);",
}
# the mex walks start at 0; in stored values the real values >= 0 are the stored ones >= -off
SHIFT_MEX = {
    "bst-py": [("c0 = self._distinctLt(0)", "base = -self.off  # (stored as v - off: the real values >= 0 are the stored ones >= -off)\n        c0 = self._distinctLt(base)"),
               ("if K[t] < 0 or K[t] == j:", "if K[t] < base or K[t] == base + j:"),
               ("        return res\n", "        return base + res  # (a stored value)\n")],
    "bst-cpp": [("long long c0 = distinctLt(0),", "T base = -off;  // (stored as v - off: the real values >= 0 are the stored ones >= -off)\n        long long c0 = distinctLt(base),"),
                ("if (pool[t].key < 0 || pool[t].key == T(j))", "if (pool[t].key < base || pool[t].key == T(base + j))"),
                ("        return res;\n", "        return base + res;  // (a stored value)\n")],
    "blocks-py": [("        k = bisect_left(self.maxes, 0)\n        if k == len(keys):\n            return 0\n        j = bisect_left(keys[k], 0)\n        want = 0\n",
                   "        base = -self.off  # (stored as v - off: the real values >= 0 are the stored ones >= -off)\n"
                   "        k = bisect_left(self.maxes, base)\n        if k == len(keys):\n            return base\n        j = bisect_left(keys[k], base)\n        want = base\n")],
    "blocks-cpp": [("        int k = blockOf(T(0));\n        if (k == (int)keys.size()) return 0;\n        int j = int(lower_bound(keys[k].begin(), keys[k].end(), T(0)) - keys[k].begin());\n        long long want = 0;\n",
                    "        T base = -off;  // (stored as v - off: the real values >= 0 are the stored ones >= -off)\n"
                    "        int k = blockOf(base);\n        if (k == (int)keys.size()) return base;\n"
                    "        int j = int(lower_bound(keys[k].begin(), keys[k].end(), base) - keys[k].begin());\n        long long want = base;\n")],
}


def shift_mex(body, dtype, py):
    """The structure's mex walk, started at -off (stored values) instead of 0."""
    key = ("blocks" if dtype.startswith("blocks") else "bst") + ("-py" if py else "-cpp")
    start = body.find("    def _findMex(self):" if py else "    long long findMex() {")
    if start < 0:
        return body
    end = body.find("\n    def " if py else "\n    }\n", start + 10)
    end = len(body) if end < 0 else end + (0 if py else len("\n    }\n"))
    part = body[start:end]
    for old, new in SHIFT_MEX[key]:
        assert part.count(old) == 1, (dtype, py, old)
        part = part.replace(old, new)
    return body[:start] + part + body[end:]


def shift_body(op, body, py, mexc):
    """A public op of a shiftAll variant: value arguments to stored values, value results back to real ones."""
    if op == "shiftAll":
        return ("self.off += d" + ("\nself.mexV = self._findMex()  # (the mex of the shifted values)" if mexc else "") if py
                else "off += d;" + ("\nmexV = findMex();  // (the mex of the shifted values)" if mexc else ""))
    if op in SHIFT_SUMS_PY:
        b = (SHIFT_SUMS_PY if py else SHIFT_SUMS_CPP)[op]
        if "@CHECK@" in b:  # the op's own argument check (Python: an if and a raise)
            b = b.replace("@CHECK@", "\n".join(body.split("\n")[:2 if py else 1]))
        return b
    if op == "mode":
        return (body.replace("return next(iter(self.bk[f])), f", "return next(iter(self.bk[f])) + self.off, f") if py
                else body.replace("{*vs.begin(), f}", "{T(*vs.begin() + off), f}"))
    if op in ("remove", "removeCount", "removeAll"):  # (count(x) would shift x a second time)
        body = body.replace("self.count(", "self._countOf(") if py else re.sub(r"\bcount\(", "countOf(", body)
    lines = body.split("\n")
    if op in SHIFT_VALUE_OPS:
        for i, line in enumerate(lines):
            if py:
                m = re.match(r"^(\s*)return (.+) if (.+) else None$", line)
                if m:
                    lines[i] = f"{m.group(1)}return {m.group(2)} + self.off if {m.group(3)} else None"
                elif re.match(r"^\s*return (?!None$)", line):
                    lines[i] = line + " + self.off"
            else:
                m = re.match(r"^(\s*)(.*)return (.+);$", line)
                if m and m.group(3) != "nullopt":
                    e = m.group(3)
                    e = f"({e})" if "?" in e else e
                    lines[i] = f"{m.group(1)}{m.group(2)}return T({e} + off);" if op != "mex" else f"{m.group(1)}{m.group(2)}return {e} + off;"
    pre = [(f"{a} -= self.off" if py else f"{a} -= off;") for a in SHIFT_VALUE_ARGS.get(OPS[op][0], [])]
    if pre and not py:
        pre = [f"{', '.join(a + ' -= off' for a in SHIFT_VALUE_ARGS[OPS[op][0]])};"]
    return "\n".join(pre + lines)



# ================================================================================================ assembly

def header(cm, ops, spec):
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: {spec['dtype']}",
             f"{cm} @values: {spec['values']}", f"{cm} @keys: {spec['keys']}", f"{cm} @tracks: {spec['tracks']}",
             f"{cm} @complexities:"]
    lines += [f"{cm}   {op}: {spec['comps'][op]}" for op in ops] + [f"{cm}   build: {spec['comps']['build']}"]
    layout, node, tags, other = spec["mem"]
    lines += [f"{cm} @memory:", f"{cm}   layout: {layout}", f"{cm}   node: {node}", f"{cm}   tags: {tags}",
              f"{cm}   other: {other}", f"{cm}   note: {spec['note']}"]
    return "\n".join(lines) + "\n"


def with_cached(body, ext, sums, minmax, medians, mexc, mode=False, gaps=False, xor=False, shift=False):
    """Adds the fields of the whole-set answers this variant caches (kept current by _add / addRaw)."""
    if ext == "py":
        extra = (' "mn", "mx",' if minmax else "") + (' "lowV", "lowB", "lowC",' + (' "lowS",' if sums else "") + ' "highV", "highB", "highC",'
                                                       if medians else "") + (' "mexV",' if mexc else "") + (' "bk", "maxF",' if mode else "") + (
            ' "gc", "gmin", "gmax", "dups",' if gaps else "") + (' "xtotal",' if xor else "") + (' "off",' if shift else "")
        body = body.replace('"n",', '"n",' + extra, 1)
        if xor:
            body = re.sub(r"^( +)(.*self\.n = .*)$", r"\1self.xtotal = 0  # xor of all values (copies count)\n\1\2", body, count=1, flags=re.M)
        if shift:
            body = re.sub(r"^( +)(.*self\.n = .*)$", r"\1self.off = 0  # every value v is stored as v - off: shiftAll only moves off\n\1\2", body, count=1, flags=re.M)
        if gaps:
            body = re.sub(r"^( +)(.*self\.n = .*)$", r"\1self.gc, self.gmin, self.gmax, self.dups = {}, [], [], 0  # gaps: size -> how many; min / max heaps; values with 2+ copies\n\1\2",
                          body, count=1, flags=re.M)
        if mode:
            body = re.sub(r"^( +)(.*self\.n = .*)$", r"\1self.bk, self.maxF = {}, 0  # mode: count -> the values with that many copies; the highest count\n\1\2",
                          body, count=1, flags=re.M)
        if mexc:
            body = re.sub(r"^( +)(.*self\.n = .*)$", r"\1self.mexV = 0  # the mex, kept current (0 for the empty set)\n\1\2", body, count=1, flags=re.M)
        return body
    fields = ["struct Info { T v; long long before, c; " + ("S sb; " if sums else "") + "};  // a value, copies before it, its copies" +
              (", sum before it" if sums else "")]
    fields += ["T mn{}, mx{};  // kept current by addRaw while n > 0"] if minmax else []
    fields += ["Info low{}, high{};  // both medians, kept current by addRaw while n > 0"] if medians else []
    fields += ["long long mexV = 0;  // the mex, kept current (0 for the empty set)"] if mexc else []
    fields += ["map<long long, set<T>> bk;  // mode: count -> the values with that many copies"] if mode else []
    fields += ["multiset<long long> gaps;  // differences between neighbouring distinct values", "long long dups = 0;  // values with 2+ copies"] if gaps else []
    fields += ["T xtotal = 0;  // xor of all values (copies count)"] if xor else []
    fields += ["T off = 0;  // every value v is stored as v - off: shiftAll only moves off"] if shift else []
    return re.sub(r"^( +)(.*n = 0, d = 0;.*)$", lambda m: m.group(0) + "\n" + "\n".join(m.group(1) + f for f in fields),
                  body, count=1, flags=re.M)


# Each structure is written once per combination of the whole-set answers it may cache: min / max, both medians, and
# (where it supports mex at all) the mex, computed per query or cached. A cached answer is O(1) to read and every update
# keeps it current; without the cache that query walks the structure and updates do nothing for it. No flags: every
# variant is a separate static template. @tracks lists what a template keeps current on every update, so the picker
# and the Pareto check know a variant that tracks more is not free.
MODE_PY = "if not self.n:\n    return None\nf = self.maxF\nreturn next(iter(self.bk[f])), f"
MODE_CPP = ("optional<pair<T, long long>>", "if (!n) return nullopt;\nauto& [f, vs] = *bk.rbegin();\nreturn pair<T, long long>{*vs.begin(), f};")


GAPS_PY = {"minAdjacentDiff": "if self.n < 2:\n    return None\nreturn 0 if self.dups else self._minGap()",
           "maxGap": "return self._maxGap() if self.d >= 2 else None"}
GAPS_CPP = {"minAdjacentDiff": ("optional<long long>", "if (n < 2) return nullopt;\nif (dups) return 0LL;\nreturn *gaps.begin();"),
            "maxGap": ("optional<long long>", "if (d < 2) return nullopt;\nreturn *gaps.rbegin();")}


def write(spec, sums, minmax=False, medians=False, mexc=False, mode=False, gaps=False, shift=False):
    ops = sorted(spec.get("ops") or (op for op in (list(OPS) if sums else COUNT_OPS) if op != "mex" or spec.get("mex", True)))
    X, O, A = spec.get("bits") or (False, False, False)  # the bitwise aggregates this variant maintains
    ops = [op for op in ops if not any(op in AGG_OPS[k] and not on for k, on in (("xor", X), ("or", O), ("and", A)))]
    assert not shift or (spec["dtype"] in SHIFT_DTYPES and not (X or O or A)), "shiftAll: comparison structures, no bitwise aggregates"
    ops = sorted([op for op in ops if op != "shiftAll"] + (["shiftAll"] if shift else []))
    mex = "mex" in ops
    # distinct counts in a value range: wherever "distinct values < x" is already kept (mex variants, sorted blocks)
    distinct = mex and spec["dtype"] in ("fenwick", "value-tree", "avl", "treap", "splay", "blocks", "blocks-fenwick", "trie")
    tri = spec.get("trie")
    if tri is None:  # the XOR ops are the trie's
        ops = [op for op in ops if op not in TRIE_OPS]
    else:
        drop = {op for op, gone in (("mexXor", not mex), ("sumXor", not tri["sumxor"]), ("xorAll", not tri["mask"])) if gone}
        ops = sorted({op for op in ops if op not in drop} | ({"sumAll"} if tri["sumxor"] else set()))
    if not distinct:
        ops = [op for op in ops if op != "countDistinctInValRange"]
    ops = sorted(set(ops) | {"mode"}) if mode else [op for op in ops if op != "mode"]
    ops = sorted(set(ops) | {"minAdjacentDiff", "maxGap"}) if gaps else [op for op in ops if op not in ("minAdjacentDiff", "maxGap")]
    spec = dict(spec, comps=dict(spec["comps"]))
    # any: values only need to compare (tuples, pairs, ...); numbers: the structure indexes by value range, keeps running
    # sums, or keeps the mex (an integer) current
    spec["keys"] = ("numbers" if sums or mexc or gaps or X or O or A or shift or spec["values"] in ("online-range", "online-bits") or (spec["dtype"] == "fenwick" and spec.get("mex"))
                    else "any")  # (the Fenwick's mex keeps an array of "is 0 / 1 / 2 ... present", so it needs numbers)
    trie_extras = [k for k in ("vbound", "sumxor", "mask") if (spec.get("trie") or {}).get(k)]
    spec["tracks"] = " ".join(trie_extras + (["minmax"] if minmax else []) + (["medians"] if medians else []) + (["mex"] if mexc else []) +
                              (["mode"] if mode else []) + (["gaps"] if gaps else []) + (["shift"] if shift else [])) or "none"
    c = spec["comps"]  # first / last index = a count of x, then a count of the values below / up to it: the slower of the two
    order = ["1", "log64(U)", "log(N)", "log(U)", "sqrt(N)"]
    base = lambda cost: order.index(cost.split(" ")[0])  # noqa: E731 ("log(N) expected" ranks as log(N))
    slower = lambda a, b: a if base(a) > base(b) else b  # noqa: E731
    c["firstIndex"] = slower(c["countLtX"], c["count"])
    c["lastIndex"] = slower(c["countLteX"], c["count"])
    c["pop"] = slower(c["kth"], c["remove"])  # a k-th, then a remove
    c["clear"] = CLEAR_COST[spec["dtype"]]
    c["mode"] = "1"
    c["minAdjacentDiff"] = c["maxGap"] = "1 amortized"  # (Python drops stale heap tops; C++ reads a multiset's ends)
    if distinct:
        c["countDistinctInValRange"] = "sqrt(N)" if spec["dtype"].startswith("blocks") else slower(c["countInValRange"], c["count"])
    rm = slower(c["remove"], c["kth"])  # per distinct value removed: a search, then dropping its copies
    c["removeInValRange"] = rm if " " in rm else rm + " amortized"  # each value is removed at most once after its add
    walk = c["kth"]  # what a query without its cache costs
    c["min"] = c["max"] = "1" if minmax else walk
    c["popMin"] = c["popMax"] = c["remove"] if minmax else slower(walk, c["remove"])
    c["medianLow"] = c["medianHigh"] = c["sumAbsDiffToMedian"] = "1" if medians else walk
    c.update(spec.get("final") or {})  # a structure's own answers that beat any cache (the trie's root min / max)
    if shift:  # moving the offset; a cached mex is walked again
        c["shiftAll"] = ("sqrt(N)" if spec["dtype"].startswith("blocks") else c["mex"]) if mexc else "1"
    if mex:  # (sorted blocks find the mex by walking their blocks)
        c["mex"] = "1" if mexc else ("sqrt(N)" if spec["dtype"].startswith("blocks") else c["mex"])
    # named by structure and extras (the op list would pass the 255-character name limit); "mex" = computed per query
    extras = ((["sums"] if sums else []) + [k for k, on in (("xor", X), ("or", O), ("and", A)) if on] +
              (["mex"] if mex and not mexc and "mex" in spec else []) + (["cachedmex"] if mexc else []) +
              (["minmax"] if minmax else []) + (["medians"] if medians else []) + (["mode"] if mode else []) + (["gaps"] if gaps else []) +
              (["shift"] if shift else []))
    extras = (["mask"] if "mask" in trie_extras else []) + extras + [k for k in trie_extras if k != "mask"]
    folder = spec["dtype"] + ("-with-" + "-".join(extras) if extras else "")
    path = os.path.join(ROOT, folder)
    os.makedirs(path, exist_ok=True)
    py_c, cpp_c = cached_ops(minmax, medians, mexc)
    for ext, cm in (("py", "#"), ("cpp", "//")):
        body = spec["py"] if ext == "py" else spec["cpp"]
        if body is None:
            continue
        cls_end = "" if ext == "py" else "};\n"
        own = dict(spec.get(f"{ext}_own") or {}, **(py_c if ext == "py" else cpp_c), mode=MODE_PY if ext == "py" else MODE_CPP,
                   **(GAPS_PY if ext == "py" else GAPS_CPP))
        own.update({op: (spec.get(f"{ext}_own") or {})[op] for op in spec.get("final") or {}})
        agg_py, agg_cpp = agg_ops(spec["dtype"], X, O, A)
        own.update({op: b for op, b in (agg_py if ext == "py" else agg_cpp).items() if op not in (spec.get(f"{ext}_own") or {})})
        bits = (X, O, A)
        add = (py_add(sums, mexc, minmax, medians, mode, gaps, X, shift) + clear_py(spec["dtype"], sums, mex, mexc, mode, gaps, bits, shift)
               if ext == "py" else
               cpp_add(sums, mexc, minmax, medians, mode, gaps, X, shift) + clear_cpp(spec["dtype"], sums, mex, mexc, mode, gaps, bits, shift))
        if distinct:
            add += (DISTINCT_LT_PY if ext == "py" else DISTINCT_LT_CPP).get(spec["dtype"], "")
        if X or O or A:
            add += agg_helpers(spec["dtype"], ext == "py", X, O, A, mask=bool((spec.get("trie") or {}).get("mask")))
        if shift:  # every public op in stored values (see shift_body)
            base_ops = PY_OPS if ext == "py" else CPP_OPS
            for op in ops:
                b = own.get(op) or base_ops.get(op) or ("" if ext == "py" else ("void", ""))
                own[op] = shift_body(op, b, True, mexc) if ext == "py" else (b[0], shift_body(op, b[1], False, mexc))
            if mex:
                body = shift_mex(body, spec["dtype"], ext == "py")
        shared = py_ops(ops, c, own) if ext == "py" else cpp_ops(ops, c, own)
        nc = needs_count(mexc, minmax, mode, gaps)  # (AVL keeps the new count in a field only when it is used)
        body = "\n".join(line.replace("  @newcount", "").replace("  @nonewcount", "") for line in body.split("\n")
                          if not line.endswith("  @newcount" if not nc else "  @nonewcount"))
        if ext == "py" and nc and spec["dtype"] == "avl":
            body = body.replace('"root", "n",', '"root", "newCount", "n",', 1)
        if ext == "py" and gaps and "heappush" not in body:
            body = "from heapq import heappop, heappush\n" + body
        text = header(cm, ops, spec) + with_cached(body, ext, sums, minmax, medians, mexc, mode, gaps, X, shift) + add + "\n" + shared + cls_end
        attribution = f"{cm} Template by {GITHUB_USER}\n{cm} {GITHUB_FILES}{folder}/template.{ext}\n"
        open(os.path.join(path, f"template.{ext}"), "w").write(attribution + text)
    return folder


if __name__ == "__main__":
    import shutil
    for d in os.listdir(ROOT):  # every variant folder is regenerated (names follow the variants; loose files stay)
        if os.path.isdir(os.path.join(ROOT, d)):
            shutil.rmtree(os.path.join(ROOT, d))
    written = []
    BOOL = (False, True)
    EXTRA = [(mode, gaps) for mode in BOOL for gaps in BOOL]  # dimensions every structure takes
    BITS = [(x, o, a) for x in BOOL for o in BOOL for a in BOOL]  # xor / OR / AND kept, where a structure can keep them
    XOR_ONLY = [(x, False, False) for x in BOOL]  # (Fenwick trees need an inverse: no OR / AND)
    # shiftAll: comparison structures only (a value range / bits fixed up front can't move), without xor / OR / AND
    shifts = lambda make, bits: BOOL if make in (avl, treap, splay, blocks, blocks_fenwick) and not any(bits) else (False,)  # noqa: E731
    for make in (fenwick, value_tree, avl, treap, splay):  # mex costs these extra arrays, so it is a dimension of its own
        for sums in BOOL:
            for bits in XOR_ONLY if make is fenwick else BITS:
                for mexmode in (None, "query", "cached"):
                    for minmax in BOOL:
                        for medians in BOOL:
                            for mode, gaps in EXTRA:
                                for shift in shifts(make, bits):
                                    written.append(write(make(sums, mexmode is not None, bits), sums, minmax, medians,
                                                         mexmode == "cached", mode, gaps, shift))
    for make in (blocks, blocks_fenwick):  # their mex comes from the keys: computed per query, or cached
        for sums in BOOL:
            for bits in BITS if make is blocks else XOR_ONLY:
                for mexc in BOOL:
                    for minmax in BOOL:
                        for medians in BOOL:
                            for mode, gaps in EXTRA:
                                for shift in shifts(make, bits):
                                    written.append(write(make(sums, bits), sums, minmax, medians, mexc, mode, gaps, shift))
    for minmax in BOOL:
        for medians in BOOL:
            for mode, gaps in EXTRA:
                for shift in BOOL:
                    written.append(write(pbds(), False, minmax, medians, mode=mode, gaps=gaps, shift=shift))
    for minmax in BOOL:
        for mode, gaps in EXTRA:
            written.append(write(fastset(), False, minmax, mode=mode, gaps=gaps))
    for sums in BOOL:  # the binary trie: the usual dimensions, and its own (per-node value bounds, per-bit counts)
        for bits in BITS:
            for mexmode in (None, "query", "cached"):
                for minmax in BOOL:
                    for medians in BOOL:
                        for mode, gaps in EXTRA:
                            for vbound in BOOL:
                                for sumxor in BOOL:
                                    if vbound and minmax:  # (vbound already has min / max at the root)
                                        continue
                                    written.append(write(trie(sums, mexmode is not None, vbound, sumxor, bits=bits), sums, minmax,
                                                         medians, mexmode == "cached", mode, gaps))
    for mex in BOOL:  # with xorAll: no caches, sums, value bounds, OR or AND (xorAll changes every value at once)
        for sumxor in BOOL:
            for bits in XOR_ONLY:
                written.append(write(trie(False, mex, sumxor=sumxor, mask=True, bits=bits), False))
    for minmax in BOOL:  # the no-duplicates FastSets (fast O(U/64) build); a mode means nothing without duplicates
        for gaps in BOOL:
            fastset_distinct(minmax, gaps)
    assert len(set(written)) == len(written), "two variants share a folder"
    print(f"wrote {len(written)} set templates (+ 4 no-duplicates FastSets)")
