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

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sets")
GITHUB_USER = "https://github.com/ishaanbuildsthings"
GITHUB_FILES = GITHUB_USER + "/leetcode/blob/main/templates/sets/"

# op -> (argument kind, result kind, description). Result kinds: none / int / opt (None in Python, nullopt in C++).
OPS = {
    "add": ("x", "none", "add one copy of x"),
    "addCount": ("vc", "none", "add cnt copies of val (nothing if cnt <= 0)"),
    "remove": ("x", "int", "remove one copy of x if present; returns how many were removed (0 or 1)"),
    "removeCount": ("vc", "int", "remove min(cnt, count(val)) copies of val; returns how many were removed"),
    "removeAll": ("v", "int", "remove every copy of val; returns how many were removed"),
    "popMin": ("", "opt", "remove and return the smallest value; {none} if empty"),
    "popMax": ("", "opt", "remove and return the largest value; {none} if empty"),
    "size": ("", "int", "how many values (copies count)"),
    "count": ("x", "int", "how many copies of x"),
    "sumAll": ("", "int", "sum of all values"),
    "countDistinct": ("", "int", "how many distinct values"),
    "min": ("", "opt", "smallest value; {none} if empty"),
    "max": ("", "opt", "largest value; {none} if empty"),
    "medianLow": ("", "opt", "lower median: the ceil(size/2)-th smallest value; {none} if empty"),
    "medianHigh": ("", "opt", "upper median: the (floor(size/2) + 1)-th smallest value; {none} if empty"),
    "mex": ("", "int", "smallest non-negative integer not in the set"),
    "sumAbsDiffToMedian": ("", "int", "sum of |v - medianLow()| over all values (min total moves to make all equal); 0 if empty"),
    "kthSmallest": ("k", "int", "k-th smallest value (1-indexed); {err} unless 1 <= k <= size"),
    "kthLargest": ("k", "int", "k-th largest value (1-indexed); {err} unless 1 <= k <= size"),
    "sumSmallestK": ("k", "int", "sum of the k smallest values; {err} unless 0 <= k <= size"),
    "sumLargestK": ("k", "int", "sum of the k largest values; {err} unless 0 <= k <= size"),
    "sumKthSmallestRange": ("ij", "int", "sum of the i-th..j-th smallest values (1-indexed, inclusive); {err} unless 1 <= i <= j <= size"),
    "sumKthLargestRange": ("ij", "int", "sum of the i-th..j-th largest values (1-indexed, inclusive; (5, 8) = 5th..8th biggest); {err} unless 1 <= i <= j <= size"),
    "largestLtX": ("x", "opt", "largest value < x; {none} if there is none"),
    "largestLteX": ("x", "opt", "largest value <= x; {none} if there is none"),
    "smallestGtX": ("x", "opt", "smallest value > x; {none} if there is none"),
    "smallestGteX": ("x", "opt", "smallest value >= x; {none} if there is none"),
    "countLtX": ("x", "int", "how many values < x"),
    "countLteX": ("x", "int", "how many values <= x"),
    "countGtX": ("x", "int", "how many values > x"),
    "countGteX": ("x", "int", "how many values >= x"),
    "countInValRange": ("lohi", "int", "how many values v with lo <= v <= hi (0 if lo > hi)"),
    "sumLtX": ("x", "int", "sum of the values < x"),
    "sumLteX": ("x", "int", "sum of the values <= x"),
    "sumGtX": ("x", "int", "sum of the values > x"),
    "sumGteX": ("x", "int", "sum of the values >= x"),
    "sumInValRange": ("lohi", "int", "sum of the values v with lo <= v <= hi (0 if lo > hi)"),
    "sumAbsDiffToX": ("x", "int", "sum of |v - x| over all values"),
}
SUM_OPS = {"sumAll", "sumAbsDiffToMedian", "sumSmallestK", "sumLargestK", "sumKthSmallestRange", "sumKthLargestRange",
           "sumLtX", "sumLteX", "sumGtX", "sumGteX", "sumInValRange", "sumAbsDiffToX"}
COUNT_OPS = [op for op in OPS if op not in SUM_OPS]
ARGS = {"x": ["x"], "xc": ["x", "c"], "v": ["val"], "vc": ["val", "cnt"], "k": ["k"], "ij": ["i", "j"], "lohi": ["lo", "hi"], "": []}

# ================================================================================================ shared ops

# Python bodies of the public ops, on top of the core (self.n = size, self.total = sum).
PY_OPS = {
    "add": "self._add(x, 1)",
    "addCount": "if cnt > 0:\n    self._add(val, cnt)",
    "remove": "if not self.count(x):\n    return 0\nself._add(x, -1)\nreturn 1",
    "removeCount": "k = min(cnt, self.count(val))\nif k <= 0:\n    return 0\nself._add(val, -k)\nreturn k",
    "removeAll": "k = self.count(val)\nif k:\n    self._add(val, -k)\nreturn k",
    "popMin": "if not self.n:\n    return None\nv = self.mn\nself._add(v, -1)\nreturn v",
    "popMax": "if not self.n:\n    return None\nv = self.mx\nself._add(v, -1)\nreturn v",
    "size": "return self.n",
    "count": "return self._countOf(x)",
    "sumAll": "return self.total",
    "countDistinct": "return self.d",
    "min": "return self.mn if self.n else None",
    "max": "return self.mx if self.n else None",
    "medianLow": "if not self.n:\n    return None\nif not self.med:\n    self._startMedians()\nreturn self.lowV",
    "medianHigh": "if not self.n:\n    return None\nif not self.med:\n    self._startMedians()\nreturn self.highV",
    "mex": "if self.mexV < 0:  # the first call: from now on _add keeps it current\n    self.mexV = self._findMex()\nreturn self.mexV",
    "sumAbsDiffToMedian": "if not self.n:\n    return 0\nif not self.med:\n    self._startMedians()\nv, b, c, s = self.lowV, self.lowB, self.lowC, self.lowS\nreturn v * b - s + (self.total - s - c * v) - v * (self.n - b - c)",
    "kthSmallest": "if not 1 <= k <= self.n:\n    raise IndexError(f\"kthSmallest: needs 1 <= k <= size, got k = {k}, size = {self.n}\")\nreturn self._kth(k)",
    "kthLargest": "if not 1 <= k <= self.n:\n    raise IndexError(f\"kthLargest: needs 1 <= k <= size, got k = {k}, size = {self.n}\")\nreturn self._kth(self.n - k + 1)",
    "sumSmallestK": "if not 0 <= k <= self.n:\n    raise IndexError(f\"sumSmallestK: needs 0 <= k <= size, got k = {k}, size = {self.n}\")\nreturn self._sumFirst(k)",
    "sumLargestK": "if not 0 <= k <= self.n:\n    raise IndexError(f\"sumLargestK: needs 0 <= k <= size, got k = {k}, size = {self.n}\")\nreturn self.total - self._sumFirst(self.n - k)",
    "sumKthSmallestRange": "if not 1 <= i <= j <= self.n:\n    raise IndexError(f\"sumKthSmallestRange: needs 1 <= i <= j <= size, got i = {i}, j = {j}, size = {self.n}\")\nreturn self._sumFirst(j) - self._sumFirst(i - 1)",
    "sumKthLargestRange": "if not 1 <= i <= j <= self.n:\n    raise IndexError(f\"sumKthLargestRange: needs 1 <= i <= j <= size, got i = {i}, j = {j}, size = {self.n}\")\nreturn self._sumFirst(self.n - i + 1) - self._sumFirst(self.n - j)",
    "largestLtX": "c = self._lt(x)\nreturn self._kth(c) if c else None",
    "largestLteX": "c = self._le(x)\nreturn self._kth(c) if c else None",
    "smallestGtX": "c = self._le(x)\nreturn self._kth(c + 1) if c < self.n else None",
    "smallestGteX": "c = self._lt(x)\nreturn self._kth(c + 1) if c < self.n else None",
    "countLtX": "return self._lt(x)",
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
    "popMin": ("optional<T>", "if (!n) return nullopt;\nT v = mn;\naddRaw(v, -1);\nreturn v;"),
    "popMax": ("optional<T>", "if (!n) return nullopt;\nT v = mx;\naddRaw(v, -1);\nreturn v;"),
    "size": ("long long", "return n;"),
    "count": ("long long", "return countOf(x);"),
    "sumAll": ("S", "return total;"),
    "countDistinct": ("long long", "return d;"),
    "min": ("optional<T>", "if (!n) return nullopt;\nreturn mn;"),
    "max": ("optional<T>", "if (!n) return nullopt;\nreturn mx;"),
    "medianLow": ("optional<T>", "if (!n) return nullopt;\nif (!med) startMedians();\nreturn low.v;"),
    "medianHigh": ("optional<T>", "if (!n) return nullopt;\nif (!med) startMedians();\nreturn high.v;"),
    "mex": ("long long", "if (mexV < 0) mexV = findMex();  // the first call: from now on addRaw keeps it current\nreturn mexV;"),
    "sumAbsDiffToMedian": ("S", "if (!n) return 0;\nif (!med) startMedians();\nconst Info& m = low;\nreturn S(m.v) * m.before - m.sb + (total - m.sb - S(m.v) * m.c) - S(m.v) * (n - m.before - m.c);"),
    "kthSmallest": ("T", "if (k < 1 || k > n) throw out_of_range(\"kthSmallest: needs 1 <= k <= size\");\nreturn kth(k);"),
    "kthLargest": ("T", "if (k < 1 || k > n) throw out_of_range(\"kthLargest: needs 1 <= k <= size\");\nreturn kth(n - k + 1);"),
    "sumSmallestK": ("S", "if (k < 0 || k > n) throw out_of_range(\"sumSmallestK: needs 0 <= k <= size\");\nreturn sumFirst(k);"),
    "sumLargestK": ("S", "if (k < 0 || k > n) throw out_of_range(\"sumLargestK: needs 0 <= k <= size\");\nreturn total - sumFirst(n - k);"),
    "sumKthSmallestRange": ("S", "if (i < 1 || i > j || j > n) throw out_of_range(\"sumKthSmallestRange: needs 1 <= i <= j <= size\");\nreturn sumFirst(j) - sumFirst(i - 1);"),
    "sumKthLargestRange": ("S", "if (i < 1 || i > j || j > n) throw out_of_range(\"sumKthLargestRange: needs 1 <= i <= j <= size\");\nreturn sumFirst(n - i + 1) - sumFirst(n - j);"),
    "largestLtX": ("optional<T>", "long long c = lt(x);\nif (!c) return nullopt;\nreturn kth(c);"),
    "largestLteX": ("optional<T>", "long long c = le(x);\nif (!c) return nullopt;\nreturn kth(c);"),
    "smallestGtX": ("optional<T>", "long long c = le(x);\nif (c == n) return nullopt;\nreturn kth(c + 1);"),
    "smallestGteX": ("optional<T>", "long long c = lt(x);\nif (c == n) return nullopt;\nreturn kth(c + 1);"),
    "countLtX": ("long long", "return lt(x);"),
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
CPP_PARAMS = {"x": "T x", "xc": "T x, long long c", "v": "T val", "vc": "T val, long long cnt", "k": "long long k", "ij": "long long i, long long j", "lohi": "T lo, T hi", "": ""}


def cost_text(c):
    """'log(N)' -> 'logN', 'log^2(N) expected' -> 'log^2 N expected', for code comments."""
    c = c.replace("log^2(N)", "log^2 N").replace("log(N)", "logN").replace("log(U)", "logU").replace("sqrt(N)", "sqrtN")
    return c.replace("*", " ")


def py_ops(ops, comps):
    out = []
    for op in ops:
        args = ARGS[OPS[op][0]]
        doc = OPS[op][2].format(none="None", err="raises IndexError")
        body = "\n".join("        " + line for line in PY_OPS[op].split("\n"))
        out.append(f"    # O({cost_text(comps[op])}) -- {doc}\n    def {op}(self{''.join(', ' + a for a in args)}):\n{body}\n")
    return "\n".join(out)


def cpp_ops(ops, comps):
    out = []
    for op in ops:
        ret, body = CPP_OPS[op]
        doc = OPS[op][2].format(none="nullopt", err="throws out_of_range")
        body = "\n".join("        " + line for line in body.split("\n"))
        out.append(f"    // O({cost_text(comps[op])}) -- {doc}\n    {ret} {op}({CPP_PARAMS[OPS[op][0]]}) {{\n{body}\n    }}\n")
    return "\n".join(out)


def py_add(sums, mex):
    """_add: every update goes through here. It keeps min / max current (O(1) to read), and once medianLow /
    medianHigh / sumAbsDiffToMedian or mex has been asked for, keeps those current too, for at most one extra search
    per update; until then updates pay nothing for them."""
    S = sums
    return f'''
    def _add(self, x, c):  # c copies of x (c < 0 removes); keeps min / max (and medians / mex once asked for) current
        self.n += c
{"        self.total += c * x" + chr(10) if S else ""}        self._insert(x, c)
        n = self.n
        if c > 0:
{"            if x == self.mexV and x >= 0:  # x filled the mex (mexV is -1 until mex() is first called)" + chr(10) + "                self.mexV = self._findMex()" + chr(10) if mex else ""}            if n == c:  # the set was empty
                self.mn = self.mx = x
                if self.med:
                    self.lowV = self.highV = x
                    self.lowB = self.highB = {"self.lowS = " if S else ""}0
                    self.lowC = self.highC = c
                return
            if x < self.mn:
                self.mn = x
            if x > self.mx:
                self.mx = x
        else:
{"            if 0 <= x < self.mexV and not self._countOf(x):  # the last copy of a value below the mex" + chr(10) + "                self.mexV = x" + chr(10) if mex else ""}            if not n:
                return
            if x == self.mn:
                self.mn = self._kth(1)
            if x == self.mx:
                self.mx = self._kth(n)
        if not self.med:
            return
        # each median is a tracked rank: shift its (value, copies before, copies{", sum before" if S else ""}), and search again only
        # when the rank leaves the tracked value
        if x < self.lowV:
            self.lowB += c
{"            self.lowS += c * x" + chr(10) if S else ""}        elif x == self.lowV:
            self.lowC += c
        r = (n + 1) >> 1
        if not self.lowB < r <= self.lowB + self.lowC:
            self.lowV, self.lowB, self.lowC{", self.lowS" if S else ""} = self._kthInfo(r)
        if x < self.highV:
            self.highB += c
        elif x == self.highV:
            self.highC += c
        r = (n >> 1) + 1
        if not self.highB < r <= self.highB + self.highC:
            self.highV, self.highB, self.highC = self._kthInfo(r){"[:3]" if S else ""}

    def _startMedians(self):  # the first median query (n > 0): from now on _add keeps both medians current
        self.med = True
        n = self.n
        self.lowV, self.lowB, self.lowC{", self.lowS" if S else ""} = self._kthInfo((n + 1) >> 1)
        self.highV, self.highB, self.highC = self._kthInfo((n >> 1) + 1){"[:3]" if S else ""}
{"""
    def _sumFirst(self, k):  # sum of the k smallest values
        if k <= 0:
            return 0
        v, b, _, s = self._kthInfo(k)
        return s + (k - b) * v
""" if S else ""}'''


def cpp_add(sums, mex):
    S = sums
    return f'''
    void addRaw(T x, long long c) {{  // c copies of x (c < 0 removes); keeps min / max (and medians / mex once asked for) current
        n += c;
{"        total += S(c) * x;" + chr(10) if S else ""}        insert(x, c);
        if (c > 0) {{
{"            if (x == T(mexV) && mexV >= 0) mexV = findMex();  // x filled the mex (mexV is -1 until mex() is first called)" + chr(10) if mex else ""}            if (n == c) {{  // the set was empty
                mn = mx = x;
                if (med) low = high = Info{{x, 0, c{", 0" if S else ""}}};
                return;
            }}
            if (x < mn) mn = x;
            if (x > mx) mx = x;
        }} else {{
{"            if (x >= 0 && x < T(mexV) && !countOf(x)) mexV = x;  // the last copy of a value below the mex" + chr(10) if mex else ""}            if (!n) return;
            if (x == mn) mn = kth(1);
            if (x == mx) mx = kth(n);
        }}
        if (!med) return;
        // each median is a tracked rank: shift its (value, copies before, copies{", sum before" if S else ""}), and search again only
        // when the rank leaves the tracked value
        if (x < low.v) low.before += c{", low.sb += S(c) * x" if S else ""};
        else if (x == low.v) low.c += c;
        long long r = (n + 1) / 2;
        if (r <= low.before || r > low.before + low.c) low = kthInfo(r);
        if (x < high.v) high.before += c{", high.sb += S(c) * x" if S else ""};
        else if (x == high.v) high.c += c;
        r = n / 2 + 1;
        if (r <= high.before || r > high.before + high.c) high = kthInfo(r);
    }}

    void startMedians() {{  // the first median query (n > 0): from now on addRaw keeps both medians current
        med = true;
        low = kthInfo((n + 1) / 2), high = kthInfo(n / 2 + 1);
    }}
{"""
    S sumFirst(long long k) {  // sum of the k smallest values
        if (k <= 0) return 0;
        Info f = kthInfo(k);
        return f.sb + S(k - f.before) * f.v;
    }
""" if S else ""}'''


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



def fenwick(sums, mex):
    s, M = sums, mex
    py = f'''from bisect import bisect_left, bisect_right


# Ordered multiset over values known ahead of time (offline): Fenwick trees over the sorted distinct values you pass
# to the constructor, one counting copies{", one summing them" if s else ""}{", one marking which values are present (for mex)" if M else ""}.
# k-th / sum of the k smallest walk down by binary lifting. The constructor only learns which values can appear (it
# compresses them); the multiset starts EMPTY. Every value you add must be one of them; query arguments (x, lo, hi)
# can be anything.


class FenwickMultiset:
    __slots__ = ("vals", "m", "top", "cnt", "fc",{' "fs",' if s else ""}{' "fp", "z", "run",' if M else ""} "n",{' "total",' if s else ""} "d")

    # O(N log N) -- allValuesThatWillEverBeInsertedForOfflineCompression: every value you will EVER add (any order, duplicates fine), only to compress values; this does NOT add them, the multiset starts empty; N = distinct values
    def __init__(self, allValuesThatWillEverBeInsertedForOfflineCompression):
        vals = self.vals = sorted(set(allValuesThatWillEverBeInsertedForOfflineCompression))
        m = self.m = len(vals)
        self.top = 1 << (m.bit_length() - 1) if m else 0  # highest power of two <= m, for binary lifting
        self.cnt = [0] * m  # copies of vals[i]
        self.fc = [0] * (m + 1)  # Fenwick: copies
{"        self.fs = [0] * (m + 1)  # Fenwick: copies * value" + chr(10) if s else ""}@mex{{
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
{"        self._fen(self.fs, i, c * x)" + chr(10) if s else ""}        if not old:
            self._fen(self.fp, i, 1)  @mex
            self.d += 1
        elif not old + c:
            self._fen(self.fp, i, -1)  @mex
            self.d -= 1

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
// to the constructor, one counting copies{", one summing them" if s else ""}{", one marking which values are present (for mex)" if M else ""}.
// k-th / sum of the k smallest walk down by binary lifting. The constructor only learns which values can appear (it
// compresses them); the multiset starts EMPTY. Every value you add must be one of them; query arguments (x, lo, hi)
// can be anything. T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct FenwickMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    vector<T> vals;  // the sorted distinct values
    int m, top{", z, run" if M else ""};
    vector<long long> cnt, fc{", fp" if M else ""};  // copies per value; Fenwick of copies{"; Fenwick of present values" if M else ""}
{"    vector<S> fs;  // Fenwick of copies * value" + chr(10) if s else ""}    long long n = 0, d = 0;
{"    S total = 0;" + chr(10) if s else ""}
    // O(N log N) -- allValuesThatWillEverBeInsertedForOfflineCompression: every value you will EVER add (any order, duplicates fine), only to compress values; this does NOT add them, the multiset starts empty; N = distinct values
    explicit FenwickMultiset(vector<T> allValuesThatWillEverBeInsertedForOfflineCompression) : vals(move(allValuesThatWillEverBeInsertedForOfflineCompression)) {{
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        m = (int)vals.size();
        top = m ? 1 << (31 - __builtin_clz(m)) : 0;  // highest power of two <= m, for binary lifting
        cnt.assign(m, 0), fc.assign(m + 1, 0);
        fp.assign(m + 1, 0);  @mex
{"        fs.assign(m + 1, 0);" + chr(10) if s else ""}@mex{{
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

    void insert(T x, long long c) {{
        int i = lowerIdx(x);  // x must be one of the given values
        long long old = cnt[i];
        cnt[i] += c;
        fen(fc, i, c);
{"        fen(fs, i, S(c) * x);" + chr(10) if s else ""}        if (!old) {"fen(fp, i, 1LL), " if M else ""}d++;
        else if (!cnt[i]) {"fen(fp, i, -1LL), " if M else ""}d--;
    }}

    long long lt(T x) {{ return pre(fc, lowerIdx(x)); }}
    long long le(T x) {{ return pre(fc, upperIdx(x)); }}

    long long countOf(T x) const {{
        int i = lowerIdx(x);
        return i < m && vals[i] == x ? cnt[i] : 0;
    }}
{"    S slt(T x) { return pre(fs, lowerIdx(x)); }" + chr(10) + "    S sle(T x) { return pre(fs, upperIdx(x)); }" + chr(10) if s else ""}
    T kth(long long k) {{  // binary lifting: the largest prefix with fewer than k copies ends right before the answer
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
    node = "cnt[1*N] fc[1*N]" + (" fp[1*N]" if M else "") + (" fs[1*N]" if s else "")
    return dict(name="FenwickMultiset", dtype="fenwick", values="offline", py=keep_mex(py, M), cpp=keep_mex(cpp, M), comps=comps, mex=M,
                mem=("none", node, "none", "vals[1*N]"),
                note="N = how many distinct values were given to the constructor; the arrays are allocated once")


# ------------------------------------------------------------------------------------------------ value tree

def value_tree(sums, mex):
    s, M = sums, mex
    py = f'''
# Ordered multiset of integers in a known range [lo, hi] (values not known ahead): a dynamic tree over the value range,
# each node keeping how many copies{", their sum," if s else ""}{" and how many distinct values (for mex)" if M else ""} are below it. Sparse: dicts keyed by heap
# index over a power-of-two cover of [lo, hi]; a missing key is an empty block. k-th / sums of the k smallest descend
# by counts{"; mex descends to the first value >= 0 whose block isn" + chr(39) + "t full" if M else ""}.


class ValueTreeMultiset:
    __slots__ = ("lo", "hi", "cap", "c",{' "s",' if s else ""}{' "p",' if M else ""} "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset for values in [lo, hi] (any integers, negative is fine)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.cap = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of value v is cap + (v - lo)
        self.c = {{}}  # node -> copies below it
{"        self.s = {}  # node -> sum of the copies below it" + chr(10) if s else ""}        self.p = {{}}  # node -> distinct values below it  @mex
        self.n = {"self.total = " if s else ""}self.d = 0

    def _insert(self, x, c):
        cc{", ss" if s else ""} = self.c{", self.s" if s else ""}
        pp = self.p  @mex
        i = self.cap + x - self.lo
        old = cc.get(i, 0)
        pres = (old + c > 0) - (old > 0)
        self.d += pres
        while i:
            cc[i] = cc.get(i, 0) + c
{"            ss[i] = ss.get(i, 0) + c * x" + chr(10) if s else ""}            if pres:  @mex
                pp[i] = pp.get(i, 0) + pres  @mex
            i >>= 1

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
// each node keeping how many copies{", their sum," if s else ""}{" and how many distinct values (for mex)" if M else ""} are below it. Nodes live in one pool
// shared by every ValueTreeMultiset<T> (call resetPool() between test cases); node 0 is the shared empty block.
// k-th / sums of the k smallest descend by counts{"; mex descends to the first value >= 0 whose block isn" + chr(39) + "t full" if M else ""}.
// T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct ValueTreeMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node {{ long long c; {sfield}{"long long p; " if M else ""}int l, r; }};  // copies{", sum" if s else ""}{", distinct values" if M else ""} below
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

    void insert(T x, long long c) {{
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
{"            v.s += S(c) * x;" + chr(10) if s else ""}        }}
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
    T kth(long long k) {{
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
    node = "c[1*log(U)]" + (" p[1*log(U)]" if M else "") + (" s[1*log(U)]" if s else "")
    return dict(name="ValueTreeMultiset", dtype="value-tree", values="online-range", py=keep_mex(py, M), cpp=keep_mex(cpp, M),
                comps=comps, mex=M,
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

    def _le(self, x):
        return self._lt(x + 1)

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

    def _sle(self, x):
        return self._slt(x + 1)
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

    long long le(T x) {{ return lt(x + 1); }}

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

    S sle(T x) {{ return slt(x + 1); }}
""" if s else ""}
    T kth(long long k) {{
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


def treap(sums, mex):
    s, M = sums, mex
    py = f'''from random import random


# Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
# its value, its copies, and the copies{", sum" if s else ""}{" and distinct values" if M else ""} in its subtree. Nodes live in parallel lists (a node
# pool; node 0 is the empty tree) and removed nodes are reused. Updates split around x and merge back.


class TreapMultiset:
    __slots__ = ("K", "C", "Z",{' "S",' if s else ""}{' "D",' if M else ""} "P", "L", "R", "free", "root", "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z{", self.S" if s else ""} = [0], [0], [0]{", [0]" if s else ""}  # key, copies, copies below{", sum below" if s else ""}
        self.D = [0]  # distinct values below  @mex
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
        self.P.append(random())
        self.L.append(0)
        self.R.append(0)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
{"        self.S[t] = self.S[l] + self.S[r] + self.C[t] * self.K[t]" + chr(10) if s else ""}        self.D[t] = self.D[l] + self.D[r] + 1  @mex

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
        m, b = self._split(b, x + 1)  # m: the node of x, or 0
        if not m:
            m = self._new(x)
            self.d += 1
        self.C[m] += c
        if self.C[m]:
            self._pull(m)
        else:
            self.free.append(m)
            m = 0
            self.d -= 1
        self.root = self._merge(self._merge(a, m), b)
''' + bst_common_py(s)
    sfield = "S s; " if s else ""
    cpp = f'''
// Ordered multiset (online: any values, nothing known ahead): a treap with one node per distinct value. Each node keeps
// its value, its copies, and the copies{", sum" if s else ""}{" and distinct values" if M else ""} in its subtree. Nodes live in one pool shared by every
// TreapMultiset<T> (call resetPool() between test cases); node 0 is the empty tree and removed nodes are reused.
// Updates split around x and merge back. T: an integer type; sums in S (long long for small T).
template <typename T>
struct TreapMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node {{ T key; long long c, z; {sfield}{"long long dn; " if M else ""}unsigned prio; int l, r; }};  // copies; copies{", sum" if s else ""}{", distinct" if M else ""} below
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

    void insert(T x, long long c) {{
        int a, b, m;
        split(root, x, a, b);
        split(b, x + 1, m, b);  // m: the node of x, or 0
        if (!m) m = make(x), d++;
        pool[m].c += c;
        if (pool[m].c) pull(m);
        else freeList.push_back(m), m = 0, d--;
        root = merge(merge(a, m), b);
    }}
''' + bst_common_cpp(s)
    comps = {op: "log(N) expected" for op in OPS}
    comps.update({"size": "1", "sumAll": "1", "countDistinct": "1", "min": "1", "max": "1", "build": "1"})
    node = "key[1*N] cnt[1*N] size[1*N]" + (" dn[1*N]" if M else "") + (" sum[1*N]" if s else "")
    return dict(name="TreapMultiset", dtype="treap", values="online", py=keep_mex(py, M), cpp=keep_mex(cpp, M), comps=comps, mex=M,
                mem=("none", node, "none", "children[2*N] prio[1*N]"),
                note="N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, "
                     "call resetPool() between test cases; Python: parallel lists per tree")


def avl(sums, mex):
    s, M = sums, mex
    py = f'''
# Ordered multiset (online: any values, nothing known ahead): an AVL tree with one node per distinct value, so every
# operation is O(log N) worst case (height <= 1.44 log2 N). Each node keeps its value, its copies, and the copies{", sum" if s else ""}
# {"and distinct values " if M else ""}in its subtree. Nodes live in parallel lists (a node pool; node 0 is the empty tree) and removed
# nodes are reused.


class AVLMultiset:
    __slots__ = ("K", "C", "Z",{' "S",' if s else ""}{' "D",' if M else ""} "H", "L", "R", "free", "root", "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z{", self.S" if s else ""} = [0], [0], [0]{", [0]" if s else ""}  # key, copies, copies below{", sum below" if s else ""}
        self.D = [0]  # distinct values below  @mex
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
        self.H.append(0)
        self.L.append(0)
        self.R.append(0)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
{"        self.S[t] = self.S[l] + self.S[r] + self.C[t] * self.K[t]" + chr(10) if s else ""}        self.D[t] = self.D[l] + self.D[r] + 1  @mex
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
''' + bst_common_py(s)
    sfield = "S s; " if s else ""
    cpp = f'''
// Ordered multiset (online: any values, nothing known ahead): an AVL tree with one node per distinct value, so every
// operation is O(log N) worst case (height <= 1.44 log2 N). Each node keeps its value, its copies, and the copies{", sum" if s else ""}
// {"and distinct values " if M else ""}in its subtree. Nodes live in one pool shared by every AVLMultiset<T> (call resetPool() between
// test cases); node 0 is the empty tree and removed nodes are reused. T: an integer type; sums in S.
template <typename T>
struct AVLMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node {{ T key; long long c, z; {sfield}{"long long dn; " if M else ""}int h, l, r; }};  // copies; copies{", sum" if s else ""}{", distinct" if M else ""} below; height
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
            return make(x, c);
        }}
        if (x < pool[t].key) {{
            int l = ins(pool[t].l, x, c);
            pool[t].l = l;
        }} else if (pool[t].key < x) {{
            int r = ins(pool[t].r, x, c);
            pool[t].r = r;
        }} else if (!(pool[t].c += c)) {{  // x is gone: replace its node by the smallest node on its right
            d--, freeList.push_back(t);
            int l = pool[t].l, r = pool[t].r, m;
            if (!l || !r) return l ? l : r;
            r = popMin(r, m);
            pool[m].l = l, pool[m].r = r;
            return bal(m);
        }}
        return bal(t);
    }}

    void insert(T x, long long c) {{ root = ins(root, x, c); }}
''' + bst_common_cpp(s)
    comps = {op: "log(N)" for op in OPS}
    comps.update({"size": "1", "sumAll": "1", "countDistinct": "1", "build": "1"})
    node = "key[1*N] cnt[1*N] size[1*N]" + (" dn[1*N]" if M else "") + (" sum[1*N]" if s else "")
    return dict(name="AVLMultiset", dtype="avl", values="online", py=keep_mex(py, M), cpp=keep_mex(cpp, M), comps=comps, mex=M,
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

    def _le(self, x):
        return self._lt(x + 1)

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

    def _sle(self, x):
        return self._slt(x + 1)
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

    long long le(T x) {{ return lt(x + 1); }}

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

    S sle(T x) {{ return slt(x + 1); }}
""" if s else ""}
    T kth(long long k) {{
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


def splay(sums, mex):
    s, M = sums, mex
    py = f'''
# Ordered multiset (online: any values, nothing known ahead): a splay tree with one node per distinct value. Each node
# keeps its value, its copies, and the copies{", sum" if s else ""}{" and distinct values" if M else ""} in its subtree; every operation splays the
# last node it touched to the root, which makes each one O(log N) amortized. Nodes live in parallel lists (a node pool;
# node 0 is the empty tree) and removed nodes are reused.


class SplayMultiset:
    __slots__ = ("K", "C", "Z",{' "S",' if s else ""}{' "D",' if M else ""} "L", "R", "P", "free", "root", "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.K, self.C, self.Z{", self.S" if s else ""} = [0], [0], [0]{", [0]" if s else ""}  # key, copies, copies below{", sum below" if s else ""}
        self.D = [0]  # distinct values below  @mex
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
        self.L.append(0)
        self.R.append(0)
        self.P.append(parent)
        return len(self.K) - 1

    def _pull(self, t):
        l, r = self.L[t], self.R[t]
        self.Z[t] = self.Z[l] + self.Z[r] + self.C[t]
{"        self.S[t] = self.S[l] + self.S[r] + self.C[t] * self.K[t]" + chr(10) if s else ""}        self.D[t] = self.D[l] + self.D[r] + 1  @mex

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
            self.C[t] += c
            self._pull(t)
            self.root = self._splay(t)
            if not self.C[t]:
                self._erase(t)
            return
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
// keeps its value, its copies, and the copies{", sum" if s else ""}{" and distinct values" if M else ""} in its subtree; every operation splays the
// last node it touched to the root, which makes each one O(log N) amortized. Nodes live in one pool shared by every
// SplayMultiset<T> (call resetPool() between test cases); node 0 is the empty tree and removed nodes are reused.
// T: an integer type; sums in S (long long for small T).
template <typename T>
struct SplayMultiset {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node {{ T key; long long c, z; {sfield}{"long long dn; " if M else ""}int l, r, p; }};  // copies; copies{", sum" if s else ""}{", distinct" if M else ""} below; parent
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

    void insert(T x, long long c) {{
        int t = root;
        while (t && pool[t].key != x) {{
            int nxt = x < pool[t].key ? pool[t].l : pool[t].r;
            if (!nxt) break;
            t = nxt;
        }}
        if (t && pool[t].key == x) {{  // x is already here
            pool[t].c += c;
            pull(t);
            root = splay(t);
            if (!pool[t].c) erase(t);
            return;
        }}
        int u = make(x, t);
        pool[u].c = c;
        pull(u);
        if (t) (x < pool[t].key ? pool[t].l : pool[t].r) = u;
        root = splay(u);
        d++;
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
    node = "key[1*N] cnt[1*N] size[1*N]" + (" dn[1*N]" if M else "") + (" sum[1*N]" if s else "")
    return dict(name="SplayMultiset", dtype="splay", values="online", py=keep_mex(py, M), cpp=keep_mex(cpp, M), comps=comps, mex=M,
                mem=("none", node, "none", "children[2*N] parent[1*N]"),
                note="N = most distinct values present at once (removed nodes are reused). C++: one shared node pool, "
                     "call resetPool() between test cases; Python: parallel lists per tree")


def blocks(sums):
    s = sums
    py = f'''from bisect import bisect_left, bisect_right, insort
from itertools import accumulate


# Ordered multiset (online: any values, nothing known ahead), sqrt-style: the distinct values in sorted blocks of
# LOAD..2*LOAD, each block keeping its values' copies{" and copies * value" if s else ""} plus block totals, and a Fenwick tree over the
# block totals (rebuilt only after a block splits or empties). A query finds its block by binary search (or by
# lifting over the block Fenwick for k-th) and then works inside one block with C-level list operations.


class BlockMultiset:
    LOAD = 64
    __slots__ = ("keys", "cnts",{' "sums",' if s else ""} "maxes", "bc",{' "bs",' if s else ""} "fc",{' "fs",' if s else ""} "cnt", "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.keys = []  # blocks of sorted distinct values
        self.cnts = []  # per block: copies of each value
{"        self.sums = []  # per block: copies * value" + chr(10) if s else ""}        self.maxes = []  # last value of each block
        self.bc = []  # per block: total copies
{"        self.bs = []  # per block: total sum" + chr(10) if s else ""}        self.fc = None  # Fenwick over bc (None: stale)
{"        self.fs = None  # Fenwick over bs (None: stale)" + chr(10) if s else ""}        self.cnt = {{}}  # value -> copies
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
            if old + c:
                self.cnt[x] = old + c
                self.cnts[k][j] += c
{"                self.sums[k][j] += c * x" + chr(10) if s else ""}                self.bc[k] += c
                self._fen(self.fc, k, c)
{"                self.bs[k] += c * x" + chr(10) + "                self._fen(self.fs, k, c * x)" + chr(10) if s else ""}                return
            del self.cnt[x]
            self.d -= 1
            del self.keys[k][j], self.cnts[k][j]
{"            del self.sums[k][j]" + chr(10) if s else ""}            if not self.keys[k]:  # the block is empty: drop it
                del self.keys[k], self.cnts[k], self.maxes[k], self.bc[k]
{"                del self.sums[k], self.bs[k]" + chr(10) if s else ""}                self.fc = {"self.fs = " if s else ""}None
                return
            self.maxes[k] = self.keys[k][-1]
            self.bc[k] += c
            self._fen(self.fc, k, c)
{"            self.bs[k] += c * x" + chr(10) + "            self._fen(self.fs, k, c * x)" + chr(10) if s else ""}            return
        self.cnt[x] = c
        self.d += 1
        if not self.keys:
            self.keys.append([x])
            self.cnts.append([c])
{"            self.sums.append([c * x])" + chr(10) if s else ""}            self.maxes.append(x)
            self.bc.append(c)
{"            self.bs.append(c * x)" + chr(10) if s else ""}            self.fc = {"self.fs = " if s else ""}None
            return
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            k -= 1
        j = bisect_left(self.keys[k], x)
        self.keys[k].insert(j, x)
        self.cnts[k].insert(j, c)
{"        self.sums[k].insert(j, c * x)" + chr(10) if s else ""}        self.maxes[k] = self.keys[k][-1]
        self.bc[k] += c
        self._fen(self.fc, k, c)
{"        self.bs[k] += c * x" + chr(10) + "        self._fen(self.fs, k, c * x)" + chr(10) if s else ""}        if len(self.keys[k]) > 2 * self.LOAD:  # split the block in half
            h = self.LOAD
            for arr in (self.keys, self.cnts{", self.sums" if s else ""}):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
{"            self.bs[k:k + 1] = [sum(self.sums[k]), sum(self.sums[k + 1])]" + chr(10) if s else ""}            self.fc = {"self.fs = " if s else ""}None

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
// LOAD..2*LOAD, each block keeping its values' copies{" and copies * value" if s else ""} plus block totals, and a Fenwick tree over the
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
{"    vector<S> bs, fs;  // per block total sum; Fenwick over it" + chr(10) if s else ""}    bool stale = true;  // the Fenwicks need a rebuild
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
{"        build(fs, bs);" + chr(10) if s else ""}        stale = false;
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

    void insert(T x, long long c) {{
        int k = blockOf(x);
        if (k < (int)keys.size()) {{
            int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
            if (j < (int)keys[k].size() && keys[k][j] == x) {{  // x is already here
                if (cnts[k][j] + c) {{
                    cnts[k][j] += c, bc[k] += c, fen(fc, k, c);
{"                    sums[k][j] += S(c) * x, bs[k] += S(c) * x, fen(fs, k, S(c) * x);" + chr(10) if s else ""}                    return;
                }}
                d--;
                keys[k].erase(keys[k].begin() + j), cnts[k].erase(cnts[k].begin() + j);
{"                sums[k].erase(sums[k].begin() + j);" + chr(10) if s else ""}                if (keys[k].empty()) {{  // the block is empty: drop it
                    keys.erase(keys.begin() + k), cnts.erase(cnts.begin() + k), maxes.erase(maxes.begin() + k), bc.erase(bc.begin() + k);
{"                    sums.erase(sums.begin() + k), bs.erase(bs.begin() + k);" + chr(10) if s else ""}                    stale = true;
                    return;
                }}
                maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
{"                bs[k] += S(c) * x, fen(fs, k, S(c) * x);" + chr(10) if s else ""}                return;
            }}
        }}
        d++;
        if (keys.empty()) {{
            keys.push_back({{x}}), cnts.push_back({{c}}), maxes.push_back(x), bc.push_back(c);
{"            sums.push_back({S(c) * x}), bs.push_back(S(c) * x);" + chr(10) if s else ""}            stale = true;
            return;
        }}
        if (k == (int)keys.size()) k--;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        keys[k].insert(keys[k].begin() + j, x), cnts[k].insert(cnts[k].begin() + j, c);
{"        sums[k].insert(sums[k].begin() + j, S(c) * x), bs[k] += S(c) * x, fen(fs, k, S(c) * x);" + chr(10) if s else ""}        maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
        if ((int)keys[k].size() > 2 * LOAD) {{  // split the block in half
            auto half = [&](auto& arr) {{
                arr.insert(arr.begin() + k + 1, decay_t<decltype(arr[k])>(arr[k].begin() + LOAD, arr[k].end()));
                arr[k].resize(LOAD);
            }};
            half(keys), half(cnts);
{"            half(sums);" + chr(10) if s else ""}            maxes[k] = keys[k].back(), maxes.insert(maxes.begin() + k + 1, keys[k + 1].back());
            bc[k] = accumulate(cnts[k].begin(), cnts[k].end(), 0LL);
            bc.insert(bc.begin() + k + 1, accumulate(cnts[k + 1].begin(), cnts[k + 1].end(), 0LL));
{"            bs[k] = accumulate(sums[k].begin(), sums[k].end(), S(0));" + chr(10) + "            bs.insert(bs.begin() + k + 1, accumulate(sums[k + 1].begin(), sums[k + 1].end(), S(0)));" + chr(10) if s else ""}            stale = true;
        }}
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
        S acc = 0;
        for (int step = m ? 1 << (31 - __builtin_clz(m)) : 0; step; step >>= 1)
            if (pos + step <= m && before + fc[pos + step] < k) {{
                pos += step, before += fc[pos];
{"                acc += fs[pos];" + chr(10) if s else ""}            }}
        return {{pos, before, acc}};
    }}

    T kth(long long k) {{
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
    other = "maxes[1*sqrt(N)] bc[2*sqrt(N)]" + (" bs[2*sqrt(N)]" if s else "") + (" cnt[1*N]" if True else "")
    return dict(name="BlockMultiset", dtype="blocks", values="online", py=py, cpp=cpp, comps=comps,
                mem=("none", node, "none", other),
                note="N = distinct values present; blocks of LOAD..2*LOAD values (Python LOAD = 64, C++ 512); each "
                     "operation costs a few binary searches plus one block's worth of C-level list work")


def blocks_fenwick(sums):
    s = sums
    py = f'''from bisect import bisect_left, bisect_right
from itertools import accumulate
from operator import and_, sub


# Ordered multiset (online: any values, nothing known ahead), sqrt-style with a Fenwick tree inside every block: the
# distinct values in sorted blocks of LOAD..2*LOAD, each block keeping its values' copies{" and copies * value" if s else ""} plus a Fenwick
# tree over them, and a Fenwick tree over the block totals. Every query is two Fenwick walks (over blocks, then inside
# one), so O(log N); an update that adds or drops a distinct value rebuilds its block's Fenwick (O(sqrt N), C-level).


class BlockFenwickMultiset:
    LOAD = 64
    __slots__ = ("keys", "cnts", "fcs",{' "sums", "fss",' if s else ""} "maxes", "bc", "fc",{' "bs", "fs",' if s else ""} "cnt", "n",{' "total",' if s else ""} "d")

    # O(1) -- an empty multiset
    def __init__(self):
        self.keys = []  # blocks of sorted distinct values
        self.cnts, self.fcs = [], []  # per block: copies of each value; Fenwick over them
{"        self.sums, self.fss = [], []  # per block: copies * value; Fenwick over them" + chr(10) if s else ""}        self.maxes = []  # last value of each block
        self.bc, self.fc = [], [0]  # per block: total copies; Fenwick over them
{"        self.bs, self.fs = [], [0]  # per block: total sum; Fenwick over them" + chr(10) if s else ""}        self.cnt = {{}}  # value -> copies
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
{"        self.fs = self._build(self.bs)" + chr(10) if s else ""}
    def _reinner(self, k):
        self.fcs[k] = self._build(self.cnts[k])
{"        self.fss[k] = self._build(self.sums[k])" + chr(10) if s else ""}
    def _insert(self, x, c):
        old = self.cnt.get(x, 0)
        if old:
            k = bisect_left(self.maxes, x)
            j = bisect_left(self.keys[k], x)
            self.bc[k] += c
            self._fen(self.fc, k, c)
{"            self.bs[k] += c * x" + chr(10) + "            self._fen(self.fs, k, c * x)" + chr(10) if s else ""}            if old + c:  # x stays: point updates only
                self.cnt[x] = old + c
                self.cnts[k][j] += c
                self._fen(self.fcs[k], j, c)
{"                self.sums[k][j] += c * x" + chr(10) + "                self._fen(self.fss[k], j, c * x)" + chr(10) if s else ""}                return
            del self.cnt[x]
            self.d -= 1
            del self.keys[k][j], self.cnts[k][j]
{"            del self.sums[k][j]" + chr(10) if s else ""}            if not self.keys[k]:  # the block is empty: drop it
                del self.keys[k], self.cnts[k], self.fcs[k], self.maxes[k], self.bc[k]
{"                del self.sums[k], self.fss[k], self.bs[k]" + chr(10) if s else ""}                self._reblock()
                return
            self.maxes[k] = self.keys[k][-1]
            self._reinner(k)
            return
        self.cnt[x] = c
        self.d += 1
        if not self.keys:
            self.keys.append([x])
            self.cnts.append([c])
            self.fcs.append(None)
{"            self.sums.append([c * x])" + chr(10) + "            self.fss.append(None)" + chr(10) + "            self.bs.append(c * x)" + chr(10) if s else ""}            self.maxes.append(x)
            self.bc.append(c)
            self._reinner(0)
            self._reblock()
            return
        k = bisect_left(self.maxes, x)
        if k == len(self.keys):
            k -= 1
        j = bisect_left(self.keys[k], x)
        self.keys[k].insert(j, x)
        self.cnts[k].insert(j, c)
{"        self.sums[k].insert(j, c * x)" + chr(10) + "        self.bs[k] += c * x" + chr(10) + "        self._fen(self.fs, k, c * x)" + chr(10) if s else ""}        self.maxes[k] = self.keys[k][-1]
        self.bc[k] += c
        self._fen(self.fc, k, c)
        if len(self.keys[k]) > 2 * self.LOAD:  # split the block in half
            h = self.LOAD
            for arr in (self.keys, self.cnts{", self.sums" if s else ""}):
                b = arr[k]
                arr[k:k + 1] = [b[:h], b[h:]]
            self.fcs.insert(k + 1, None)
{"            self.fss.insert(k + 1, None)" + chr(10) if s else ""}            self._reinner(k)
            self._reinner(k + 1)
            self.maxes[k:k + 1] = [self.keys[k][-1], self.keys[k + 1][-1]]
            self.bc[k:k + 1] = [sum(self.cnts[k]), sum(self.cnts[k + 1])]
{"            self.bs[k:k + 1] = [sum(self.sums[k]), sum(self.sums[k + 1])]" + chr(10) if s else ""}            self._reblock()
        else:
            self._reinner(k)

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
// distinct values in sorted blocks of LOAD..2*LOAD, each block keeping its values' copies{" and copies * value" if s else ""} plus a Fenwick
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
{"    vector<S> bs, fs{0};  // per block total sum; Fenwick over them" + chr(10) if s else ""}    long long n = 0, d = 0;
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
{"        fs = build(bs);" + chr(10) if s else ""}    }}

    void reinner(int k) {{
        fcs[k] = build(cnts[k]);
{"        fss[k] = build(sums[k]);" + chr(10) if s else ""}    }}

    int blockOf(T x) const {{ return int(lower_bound(maxes.begin(), maxes.end(), x) - maxes.begin()); }}

    void insert(T x, long long c) {{
        int k = blockOf(x);
        if (k < (int)keys.size()) {{
            int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
            if (j < (int)keys[k].size() && keys[k][j] == x) {{  // x is already here
                bc[k] += c, fen(fc, k, c);
{f"                bs[k] += {sv}, fen(fs, k, {sv});" + chr(10) if s else ""}                if (cnts[k][j] + c) {{  // x stays: point updates only
                    cnts[k][j] += c, fen(fcs[k], j, c);
{f"                    sums[k][j] += {sv}, fen(fss[k], j, {sv});" + chr(10) if s else ""}                    return;
                }}
                d--;
                keys[k].erase(keys[k].begin() + j), cnts[k].erase(cnts[k].begin() + j);
{"                sums[k].erase(sums[k].begin() + j);" + chr(10) if s else ""}                if (keys[k].empty()) {{  // the block is empty: drop it
                    keys.erase(keys.begin() + k), cnts.erase(cnts.begin() + k), fcs.erase(fcs.begin() + k);
                    maxes.erase(maxes.begin() + k), bc.erase(bc.begin() + k);
{"                    sums.erase(sums.begin() + k), fss.erase(fss.begin() + k), bs.erase(bs.begin() + k);" + chr(10) if s else ""}                    reblock();
                    return;
                }}
                maxes[k] = keys[k].back();
                reinner(k);
                return;
            }}
        }}
        d++;
        if (keys.empty()) {{
            keys.push_back({{x}}), cnts.push_back({{c}}), fcs.emplace_back(), maxes.push_back(x), bc.push_back(c);
{f"            sums.push_back({{{sv}}}), fss.emplace_back(), bs.push_back({sv});" + chr(10) if s else ""}            reinner(0), reblock();
            return;
        }}
        if (k == (int)keys.size()) k--;
        int j = int(lower_bound(keys[k].begin(), keys[k].end(), x) - keys[k].begin());
        keys[k].insert(keys[k].begin() + j, x), cnts[k].insert(cnts[k].begin() + j, c);
{f"        sums[k].insert(sums[k].begin() + j, {sv}), bs[k] += {sv}, fen(fs, k, {sv});" + chr(10) if s else ""}        maxes[k] = keys[k].back(), bc[k] += c, fen(fc, k, c);
        if ((int)keys[k].size() > 2 * LOAD) {{  // split the block in half
            auto half = [&](auto& arr) {{
                arr.insert(arr.begin() + k + 1, decay_t<decltype(arr[k])>(arr[k].begin() + LOAD, arr[k].end()));
                arr[k].resize(LOAD);
            }};
            half(keys), half(cnts);
            fcs.emplace(fcs.begin() + k + 1);
{"            half(sums), fss.emplace(fss.begin() + k + 1);" + chr(10) if s else ""}            reinner(k), reinner(k + 1);
            maxes[k] = keys[k].back(), maxes.insert(maxes.begin() + k + 1, keys[k + 1].back());
            bc[k] = accumulate(cnts[k].begin(), cnts[k].end(), 0LL);
            bc.insert(bc.begin() + k + 1, accumulate(cnts[k + 1].begin(), cnts[k + 1].end(), 0LL));
{"            bs[k] = accumulate(sums[k].begin(), sums[k].end(), S(0));" + chr(10) + "            bs.insert(bs.begin() + k + 1, accumulate(sums[k + 1].begin(), sums[k + 1].end(), S(0)));" + chr(10) if s else ""}            reblock();
        }} else reinner(k);
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

    T kth(long long k) {{ return kthInfo(k).v; }}

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
    node = "keys[1*N] cnts[1*N] fcs[1*N]" + (" sums[1*N] fss[1*N]" if s else "")
    other = "maxes[1*sqrt(N)] bc[2*sqrt(N)]" + (" bs[2*sqrt(N)]" if s else "") + " cnt[1*N]"
    return dict(name="BlockFenwickMultiset", dtype="blocks-fenwick", values="online", py=py, cpp=cpp, comps=comps,
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

    void insert(T x, long long c) {  // c = +1 or -1
        if (c > 0) {
            if (!count(x)) d++;
            t.insert({x, ids++});
        } else {
            t.erase(t.lower_bound({x, INT_MIN}));
            if (!count(x)) d--;
        }
    }

    long long lt(T x) { return (long long)t.order_of_key({x, INT_MIN}); }
    long long le(T x) { return (long long)t.order_of_key({x, INT_MAX}); }
    T kth(long long k) { return t.find_by_order(k - 1)->first; }
    long long countOf(T x) { return le(x) - lt(x); }

    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies
        T v = kth(k);
        long long b = lt(v);
        return {v, b, le(v) - b};
    }
'''
    ops = ["add", "remove", "popMin", "popMax", "size", "count", "countDistinct", "min", "max", "medianLow", "medianHigh",
           "kthSmallest", "kthLargest", "largestLtX", "largestLteX", "smallestGtX", "smallestGteX", "countLtX",
           "countLteX", "countGtX", "countGteX", "countInValRange"]
    comps = {op: "log(N)" for op in OPS}
    comps.update({"size": "1", "countDistinct": "1", "min": "1", "max": "1", "build": "1"})
    return dict(name="PbdsMultiset", dtype="pbds", values="online", py=None, cpp=cpp, comps=comps,
                mem=("none", "key[2*N] size[1*N] color[1*N]", "none", "children[2*N] parent[1*N]"),
                note="N = copies present: one red-black tree node per copy, keyed (value, id), with its subtree size", ops=ops)


# ================================================================================================ assembly

def header(cm, ops, spec):
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: {spec['dtype']}",
             f"{cm} @values: {spec['values']}", f"{cm} @complexities:"]
    lines += [f"{cm}   {op}: {spec['comps'][op]}" for op in ops] + [f"{cm}   build: {spec['comps']['build']}"]
    layout, node, tags, other = spec["mem"]
    lines += [f"{cm} @memory:", f"{cm}   layout: {layout}", f"{cm}   node: {node}", f"{cm}   tags: {tags}",
              f"{cm}   other: {other}", f"{cm}   note: {spec['note']}"]
    return "\n".join(lines) + "\n"


def with_cached(body, ext, sums, mex):
    """Adds the cached whole-set answers every structure shares (kept current by _add / addRaw)."""
    if ext == "py":
        body = body.replace('"n",', '"n", "mn", "mx", "med", "lowV", "lowB", "lowC",' + (' "lowS",' if sums else "")
                            + ' "highV", "highB", "highC",' + (' "mexV",' if mex else ""), 1)
        line = ("self.med" + (", self.mexV = False, -1" if mex else " = False")
                + "  # medians / mex are tracked from their first query on; min / max always (set by the first add)")
        return re.sub(r"^( +)(.*self\.n = .*)$", r"\1" + line + r"\n\1\2", body, count=1, flags=re.M)
    fields = ("struct Info { T v; long long before, c; " + ("S sb; " if sums else "") + "};  // a value, copies before it, "
              "its copies" + (", sum before it" if sums else "") + "\n"
              "T mn{}, mx{};  // kept current by addRaw while n > 0\n"
              "bool med = false;  // medians (low, high) are tracked from the first median query on\n"
              "Info low{}, high{};" + ("\nlong long mexV = -1;  // -1 until mex() is first called, then kept current" if mex else ""))
    return re.sub(r"^( +)(.*n = 0, d = 0;.*)$", lambda m: m.group(0) + "\n" + "\n".join(m.group(1) + f for f in fields.split("\n")),
                  body, count=1, flags=re.M)


# Whole-set answers _add / addRaw keep current, so reading them is O(1): min / max always; medians and mex from their
# first query on (that one search is charged to the updates before it, hence amortized). An update pays at most one
# extra search for them, so no update's bound changes.
CACHED_OPS = {"min": "1", "max": "1", "medianLow": "1 amortized", "medianHigh": "1 amortized", "mex": "1 amortized",
              "sumAbsDiffToMedian": "1 amortized"}


def write(spec, sums):
    ops = sorted(spec.get("ops") or (op for op in (list(OPS) if sums else COUNT_OPS) if op != "mex" or spec.get("mex", True)))
    spec["comps"].update(CACHED_OPS)
    # named by structure and extras (the op list would pass the 255-character name limit)
    extras = (["sums"] if sums else []) + (["mex"] if spec.get("mex") else [])
    folder = spec["dtype"] + ("-with-" + "-".join(extras) if extras else "")
    path = os.path.join(ROOT, folder)
    os.makedirs(path, exist_ok=True)
    for ext, cm in (("py", "#"), ("cpp", "//")):
        body = spec["py"] if ext == "py" else spec["cpp"]
        if body is None:
            continue
        cls_end = "" if ext == "py" else "};\n"
        mex = "mex" in ops
        add = py_add(sums, mex) if ext == "py" else cpp_add(sums, mex)
        shared = py_ops(ops, spec["comps"]) if ext == "py" else cpp_ops(ops, spec["comps"])
        text = header(cm, ops, spec) + with_cached(body, ext, sums, mex) + add + "\n" + shared + cls_end
        attribution = f"{cm} Template by {GITHUB_USER}\n{cm} {GITHUB_FILES}{folder}/template.{ext}\n"
        open(os.path.join(path, f"template.{ext}"), "w").write(attribution + text)
    print("wrote", folder)


if __name__ == "__main__":
    for make in (fenwick, value_tree, avl, treap, splay):  # mex costs these an extra array, so each comes with and without it
        for sums in (False, True):
            for mex in (False, True):
                write(make(sums, mex), sums)
    for make in (blocks, blocks_fenwick):
        for sums in (False, True):
            write(make(sums), sums)
    write(pbds(), False)
