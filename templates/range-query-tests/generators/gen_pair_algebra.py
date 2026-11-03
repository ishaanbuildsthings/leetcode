"""rangeTwinSpin(l, r) (swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ...) with the composable aggregates and updates
of gen_treap_algebra.py.

    python3 gen_pair_algebra.py

The array is two implicit treaps (lanes) in one node pool: E holds the values at even positions, O the odd ones; each
lane is an algebra treap (same nodes, pull, tags, split, merge). A range [l, r] is a slice of each lane, and the pieces
of the sequence edits are lane pairs too: after a piece of odd length the next piece's even positions are odd ones, so
its lanes trade places when they are joined on. Swapping pairs trades the two lanes of [l, r]; a reverse reverses each
lane, and trades them when the length is even.

Only aggregates a range can rebuild from its two lanes are kept: sum, min, max, xor, AND, OR, gcd (with range add: the
gcd of a[l], a[l + 1] - a[l] and each lane's differences 2 apart, which generate the same group as all the adjacent
differences) and the hashes (each lane hashes in base B^2; a range's two lane hashes weave back into base B). The
order-bound ones (best prefix / suffix / subarray sums, equal runs, alternating sums) are not: they need the values in
array order inside one subtree. Updates act on each lane alone (an arithmetic sequence add gives each lane its own start
and twice the step). find works as in the plain treap: an index is 2 * (lane index) + (0 for E, 1 for O).
"""
import itertools
import os
import shutil

import gen_treap_algebra as A
from gen_treap import CPP_HASH_HELPERS, PY_HASH_CONST, no_push, wrap
from gen_treap_algebra import (CMP, OK, PIECES, POINT, QDOC, QOPS, SEARCH, SHRINK_COST, UDOC, UOP, UPDATE_SETS, Spec,
                               allowed, bits_args, clamp_args, cpp_internals, cpp_public, cpp_skeleton, gcd_costs,
                               piece_example, py_internals, py_public, py_skeleton)
from aos import aosify
from note_lang import folder_name, write_template

DIR = A.DIR
DTYPE = "pair-treap"
CLS = "PairSwapTreap"
P_SEQ = ["append", "appendLeft", "getAll", "insertAt", "insertCopiesAt", "rangeRotateLeft", "rangeRotateRight", "rangeTwinSpin"]
P_OTHER = ["xor", "and", "or", "gcd"]  # (the lane-friendly families beyond sum / min / max / hash)


class PairSpec(Spec):
    def __init__(self, mods, fam, ups, rev, find=False):
        super().__init__(mods, fam, ups, rev, find)
        m = set(mods)
        self.ops = sorted(set(P_SEQ + POINT + [UOP[x] for x in self.ups] + (["rangeReverse"] if rev else []) + PIECES +
                              (["find"] if find else []) + [q for mod in mods for q in QOPS[mod]] +
                              [op for op, (_, c) in SEARCH.items() if ("max" if c.startswith("G") else "min") in m]))

    def name(self):
        return "pair-" + super().name()


def mod_sets():
    """sum / min / max / hash with up to two of xor, and, or, gcd, then per update set the largest set it allows"""
    seen = []
    for k in range(4):
        for core in itertools.combinations(("sum", "min", "max"), k):
            for H in (False, True):
                base = core + (("hash",) if H else ())
                for j in range(3):
                    for ex in itertools.combinations(P_OTHER, j):
                        seen.append((base + ex, False))
                for fam, ups in UPDATE_SETS:
                    ex = [g for g in P_OTHER if fam in OK[g] | {""} and ("assign" not in ups or "assign" in OK[g])]
                    if len(ex) > 2:
                        seen.append((base + tuple(ex), (fam, ups)))
    return seen


def variants():
    out, have = [], set()
    for mods, only in mod_sets():
        for fam, ups in allowed(mods):
            if only and only != (fam, ups):
                continue
            for rev in (False, True):
                key = (mods, tuple(sorted(ups)), rev)
                if key not in have:
                    have.add(key)
                    out.append(PairSpec(mods, fam, ups, rev))
    for mods, only in mod_sets():  # find: only without range updates (as in the plain treap)
        if only and only != ("", ()):
            continue
        for rev in (False, True):
            key = (mods, (), rev, "find")
            if key not in have:
                have.add(key)
                out.append(PairSpec(mods, "", (), rev, find=True))
    return out


# ================================================================================================ shared text

def header(cm, s):
    h = A.header(cm, s).replace("@data-structure-type: treap", f"@data-structure-type: {DTYPE}")
    return h.replace("; every ImplicitTreap<T> shares one node pool", f"; two treaps per array (even / odd positions); every {CLS}<T> shares one node pool" +
                     ("; each lane hashes in base B^2" if s.has("hash") else ""))


def describe(s):
    keeps = ", ".join(A.DESC[m] for m in s.mods)
    ups = ", ".join(UOP[u] for u in sorted(s.ups))
    return ("Implicit treap pair: an array you can insert into anywhere, swap adjacent pairs in a range (rangeTwinSpin: "
            "a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ...), " + ("reverse, " if s.rev else "") + "rotate, cut pieces out of "
            "(that is how to erase) and paste them back in O(logN) expected each" +
            (", and find any value's index (values distinct)" if s.find else "") + (f", with {ups}" if ups else "") +
            ". The values at even positions a[0], a[2], ... are one treap (lane E) and the odd ones another (lane O), in one "
            "node pool; a range [l, r] is a slice of each" + (f", and each node keeps {keeps} over its subtree" if keeps else "") +
            ". All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches "
            "return -1 when nothing qualifies." + (" Lazy tags mean \"already applied to this node, not yet to its children\"" +
                                                   ("; a pending assign comes before a pending add." if s.asgTag and (s.addTag or s.ap or s.xorf) else ".")
                                                   if s.tags() else ""))


def upd_calls(s, u, lang):
    """the update u as one call per lane: (parameters, call for lane E, call for lane O); lane E's slice holds a[l],
    a[l + 2], ..., lane O's a[l + 1], a[l + 3], ..."""
    py = lang == "py"
    me, z, neg1, inf, ng = ("self._", "0", "-1", "INF", "NEG") if py else ("", "T(0)", "~T(0)", "INF", "NEG")
    if u == "ap":
        return (("start, step", f"{me}applyAP(be, start, 2 * step)", f"{me}applyAP(bo, start + step, 2 * step)") if py else
                ("T start, T step", "applyAP(be, start, T(2) * step)", "applyAP(bo, T(start + step), T(2) * step)"))
    call = {"assign": f"{me}applyAssign(b, v)" if s.asgTag else f"{me}applyClamp(b, " + clamp_args(s, "v", "v", z) + ")" if s.clamp
            else f"{me}applyBits(b, " + bits_args(s, z, "v") + ")",
            "add": f"{me}applyAP(b, v, {z})" if s.ap else f"{me}applyAdd(b, v)" if s.addTag else f"{me}applyClamp(b, " + clamp_args(s, inf, ng, "v") + ")",
            "chmin": f"{me}applyClamp(b, " + clamp_args(s, "v", ng, z) + ")",
            "chmax": f"{me}applyClamp(b, " + clamp_args(s, inf, "v", z) + ")",
            "and": f"{me}applyBits(b, " + bits_args(s, "v", z) + ")",
            "or": f"{me}applyBits(b, " + bits_args(s, neg1, "v") + ")",
            "xor": f"{me}applyXor(b, v)"}[u]
    return ("v" if py else "T v", call.replace("(b,", "(be,"), call.replace("(b,", "(bo,"))


# ================================================================================================ Python

def py(s):
    F, TG = s.fields(), s.tags()
    NEED_INF = s.clamp
    out = [header("#", s), "\n", wrap(describe(s), "#"), "import random\n" + ("from math import gcd\n" if s.has("gcd") else "") +
           ("from math import isqrt\n" if s.shrink else "") + "\n\n"]
    if s.has("hash"):
        out.append(PY_HASH_CONST.rstrip("\n") + "\n_HQ = _HB * _HB % _HP  # each lane hashes in base B^2 (its neighbours in the array are 2 apart)\n\n\n")
    if NEED_INF:
        out.append('INF, NEG = float("inf"), float("-inf")\n\n\n')
    ctor = '''    __slots__ = ("rE", "rO")

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        arr = list(arr)
        self.rE = self._build(arr[0::2])  # lane E: a[0], a[2], ...
        self.rO = self._build(arr[1::2])  # lane O: a[1], a[3], ...
'''
    out.append(py_skeleton(F, TG, [("where", "{}")] if s.find else [], cls=CLS, ctor=ctor))
    out.append("    # O(1) -- the current length of the array\n    def size(self):\n        return self.sz[self.rE] + self.sz[self.rO]\n\n")
    pub = py_pub(s)
    out.append("\n".join(pub[op] for op in s.ops if op in pub))
    internals = py_internals(s).replace("_HB", "_HQ")
    internals = internals.replace(A.PY_TAIL, PY_TAIL)
    out.append(internals + py_extra(s))
    text = A.fit_comments(gcd_costs(s, "".join(out))).rstrip("\n") + "\n" + piece_example("py", f"{CLS}([1, 2, 3, 4, 5])", list("12345"))
    return text if TG else no_push(text, "py")


def py_pub(s):
    base = py_public(s)  # (the point ops: they walk to one node, through _find)
    pub = {op: base[op] for op in ("pointAssign", "pointAdd", "pointChmax", "pointChmin")}
    J = "self._join(ae, ao, be, bo, ce, co)"
    C = "ae, ao, be, bo, ce, co = self._cut(l, r)"
    q = {"rangeSum": "self.sm[be] + self.sm[bo]",
         "rangeMin": "self.mn[be] if not bo else min(self.mn[be], self.mn[bo])",
         "rangeMax": "self.mx[be] if not bo else max(self.mx[be], self.mx[bo])",
         "rangeXorQuery": "self.xr[be] ^ self.xr[bo]", "rangeAndQuery": "self.an[be] & self.an[bo]",
         "rangeOrQuery": "self.orr[be] | self.orr[bo]", "rangeGcd": "gcd(self.g[be], self.g[bo])"}
    for op, expr in q.items():
        if op not in s.ops:
            continue
        if op == "rangeGcd" and s.gdiff:  # a[l], a[l + 1] - a[l] and each lane's differences 2 apart
            body = f'''        fv, g = self.fv, self.g
        res = gcd(gcd(fv[be], g[be]), g[bo])
        if bo:
            res = gcd(res, fv[bo] - fv[be])'''
        else:
            body = f"        res = {expr}"
        pub[op] = f'''    # O(logN) expected -- {QDOC[op]}
    def {op}(self, l, r):
        {C}
{body}
        {J}
        return res
'''
    if s.has("hash"):
        for op, expr in (("rangeHash", "self._hashes(l, r)[0]"), ("rangeHashReversed", "self._hashes(l, r)[1]")):
            pub[op] = f"    # O(logN) expected -- {QDOC[op]}\n    def {op}(self, l, r):\n        return {expr}\n"
        pub["isPalindrome"] = f'''    # O(logN) expected -- {QDOC["isPalindrome"]}
    def isPalindrome(self, l, r):
        f, b = self._hashes(l, r)
        return f == b
'''
        pub["rangesEqual"] = f'''    # O(logN) expected -- {QDOC["rangesEqual"]}
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self._hashes(l1, r1)[0] == self._hashes(l2, r2)[0]
'''
    for op, (side, cmp) in SEARCH.items():
        if op not in s.ops:
            continue
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        pick = "i if j < 0 else j if i < 0 else min(i, j)" if side == "leftmost" else "max(i, j)"
        pub[op] = f'''    # O(logN) expected -- the {"first" if side == "leftmost" else "last"} i in [l, r] with a[i] {o} x, or -1 (each lane's walk pruned by the subtree {"max" if f == "mx" else "min"})
    def {op}(self, l, r, x):
        {C}
        i, j = self._lane{op[0].upper() + op[1:]}(be, x), self._lane{op[0].upper() + op[1:]}(bo, x)
        {J}
        i = l + 2 * i if i >= 0 else -1  # (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = l + 1 + 2 * j if j >= 0 else -1
        return {pick}
'''
    shr = {"mod": ("x", "if x >= 1:\n            self._shrink(be, x, lambda v: v % x)\n            self._shrink(bo, x, lambda v: v % x)", "logN * logU"),
           "div": ("x", "if x >= 2:\n            self._shrink(be, 1, lambda v: v // x)\n            self._shrink(bo, 1, lambda v: v // x)", "logN * logU"),
           "sqrt": ("", "self._shrink(be, 2, isqrt)\n        self._shrink(bo, 2, isqrt)", "logN * loglogU")}
    for u in s.ups:
        if u in shr:
            args, call, c = shr[u]
            pub[UOP[u]] = f'''    # amortized O({c}) expected -- {UDOC[u]}
    def {UOP[u]}(self, l, r{", " + args if args else ""}):
        {C}
        {call}
        {J}
'''
            continue
        args, ce_, co_ = upd_calls(s, u, "py")
        pub[UOP[u]] = f'''    # O(logN) expected -- {UDOC[u]}
    def {UOP[u]}(self, l, r, {args}):
        {C}
        {ce_}
        {co_}
        {J}
'''
    pub.update({
        "pointGet": '''    # O(logN) expected -- a[i]
    def pointGet(self, i):
        return self.val[self._find(i)[0]]
''',
        "insertAt": '''    # O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
        ae, ao = self._pmerge(ae, ao, self._newNode(v), 0)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)
''',
        "insertCopiesAt": '''    # O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    def insertCopiesAt(self, i, v, k):
        if k > 0:
            ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
            ae, ao = self._pmerge(ae, ao, self._build([v] * ((k + 1) // 2)), self._build([v] * (k // 2)))
            self.rE, self.rO = self._pmerge(ae, ao, ce, co)
''',
        "append": '''    # O(logN) expected -- append v to the end
    def append(self, v):
        self.rE, self.rO = self._pmerge(self.rE, self.rO, self._newNode(v), 0)
''',
        "appendLeft": '''    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)
''',
        "rangeReverse": '''    # O(logN) expected -- reverse a[l..r] in place: each lane reverses, and with an even length they trade places
    def rangeReverse(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        self._applyRev(be)
        self._applyRev(bo)
        if (r - l + 1) % 2 == 0:
            be, bo = bo, be
        self._join(ae, ao, be, bo, ce, co)
''',
        "rangeTwinSpin": '''    # O(logN) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (odd length:
    # a[r] stays): the pairs' two lanes trade places
    def rangeTwinSpin(self, l, r):
        k = (r - l + 1) // 2
        if k:
            ae, ao, be, bo, ce, co = self._cut(l, l + 2 * k - 1)
            self._join(ae, ao, bo, be, ce, co)
''',
        "rangeRotateLeft": '''    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    # it is taken mod the length (negative shifts right)
    def rangeRotateLeft(self, l, r, k):
        k %= r - l + 1
        if k:
            ae, ao, be, bo, ce, co = self._cut(l, r)
            xe, xo, ye, yo = self._psplit(be, bo, k)
            be, bo = self._pmerge(ye, yo, xe, xo)
            self._join(ae, ao, be, bo, ce, co)
''',
        "rangeRotateRight": '''    # O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    # length (negative shifts left)
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)
''',
        "getAll": '''    # O(N) -- the whole current array, every pending tag applied on the way
    def getAll(self):
        ev, od = self._inorder(self.rE), self._inorder(self.rO)
        out = [0] * (len(ev) + len(od))
        out[0::2], out[1::2] = ev, od
        return out
''',
        "cut": f'''    # O(logN) expected -- remove a[l..r] and return it as a {CLS} of its own (indices from 0)
    def cut(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)
        piece = self._empty()
        piece.rE, piece.rO = be, bo
        return piece
''',
        "paste": f'''    # O(logN) expected -- insert all of other (any {CLS}, e.g. a cut piece) so it starts at a[i]
    # (0 <= i <= size()); other is left empty
    def paste(self, i, other):
        ae, ao, ce, co = self._psplit(self.rE, self.rO, i)
        ae, ao = self._pmerge(ae, ao, other.rE, other.rO)
        self.rE, self.rO = self._pmerge(ae, ao, ce, co)
        other.rE = other.rO = 0
''',
        "merge": '''    # O(logN) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.rE, self.rO = self._pmerge(self.rE, self.rO, other.rE, other.rO)
        other.rE = other.rO = 0
''',
        "split": f'''    # O(logN) expected -- (a[0..k-1], a[k..]) as two {CLS}s of their own; this one is left empty
    def split(self, k):
        left, right = self._empty(), self._empty()
        left.rE, left.rO, right.rE, right.rO = self._psplit(self.rE, self.rO, k)
        self.rE = self.rO = 0
        return left, right
''',
        "trisect": f'''    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three {CLS}s of their own; this one is left empty
    def trisect(self, l, r):
        left, mid, right = self._empty(), self._empty(), self._empty()
        left.rE, left.rO, mid.rE, mid.rO, right.rE, right.rO = self._cut(l, r)
        self.rE = self.rO = 0
        return left, mid, right
''',
    })
    if s.find:
        f = base["find"]
        a = "        if path[-1] != self.root:\n            return -1  # (erased, or in another treap)\n"
        assert a in f and f.endswith("        return i\n")
        f = f.replace(a, "        top = path[-1]\n        if top != self.rE and top != self.rO:\n            return -1  # (erased, or in another treap)\n")
        pub["find"] = f[:-len("        return i\n")] + "        return 2 * i + (top == self.rO)  # (lane index i: a[2i] in lane E, a[2i + 1] in lane O)\n"
    return pub


PY_TAIL = A.PY_TAIL[:A.PY_TAIL.index("    def _cut(self, l, r):")] + '''    # an array is a pair of lanes (E, O): E holds its values at even positions, O the odd ones

    def _psplit(self, e, o, k):  # lanes of (the first k values, the rest)
        e1, e2 = self._split(e, (k + 1) // 2)
        o1, o2 = self._split(o, k // 2)
        return (e1, o1, o2, e2) if k % 2 else (e1, o1, e2, o2)  # (an odd k: the rest starts on an odd position)

    def _pmerge(self, e1, o1, e2, o2):  # lanes of (the first array, then the second)
        if (self.sz[e1] + self.sz[o1]) % 2:
            e2, o2 = o2, e2  # (after an odd length the second's even positions are odd ones)
        return self._merge(e1, e2), self._merge(o1, o2)

    def _cut(self, l, r):  # lanes of a[..l-1], a[l..r], a[r+1..]
        ae, ao, be, bo = self._psplit(self.rE, self.rO, l)
        be, bo, ce, co = self._psplit(be, bo, r - l + 1)
        return ae, ao, be, bo, ce, co

    def _join(self, ae, ao, be, bo, ce, co):
        self.rE, self.rO = self._pmerge(*self._pmerge(ae, ao, be, bo), ce, co)

    def _find(self, i):  # (node holding a[i], the nodes above it), every tag on the way pushed
        L, sz, path, k = self.L, self.sz, [], i // 2
        t = self.rO if i % 2 else self.rE
        while True:
            self._push(t)
            ls = sz[L[t]]
            if k == ls:
                return t, path
            path.append(t)
            if k < ls:
                t = L[t]
            else:
                k -= ls + 1
                t = self.R[t]

    def _inorder(self, t):  # the values under t in order, every tag on the way pushed
        L, R, val = self.L, self.R, self.val
        out, stack = [], []
        while stack or t:
            while t:
                self._push(t)
                stack.append(t)
                t = L[t]
            t = stack.pop()
            out.append(val[t])
            t = R[t]
        return out
'''


def py_extra(s):
    """the lane helpers the public ops call: hashes woven from the lanes, one search walk per search op"""
    out = []
    if s.has("hash"):
        out.append('''
    # (forward, backward) hash of a[l..r]: lane E's slice x holds a[l], a[l + 2], ..., lane O's y the rest; in base B
    # the range reads x0 y0 x1 y1 ..., so forward = H(x) + B H(y) (odd length) or B H(x) + H(y) (even), and backward
    # = Hrev(x) + B Hrev(y)
    def _hashes(self, l, r):
        ae, ao, be, bo, ce, co = self._cut(l, r)
        P, B, fh, bh = _HP, _HB, self.fh, self.bh
        fwd = (fh[be] + B * fh[bo]) % P if (r - l) % 2 == 0 else (B * fh[be] + fh[bo]) % P
        bwd = (bh[be] + B * bh[bo]) % P
        self._join(ae, ao, be, bo, ce, co)
        return fwd, bwd
''')
    for op, (side, cmp) in SEARCH.items():
        if op not in s.ops:
            continue
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        if side == "leftmost":
            walk = f'''            if L[t] and F[L[t]] {o} x:
                t = L[t]
            elif val[t] {o} x:
                return i + sz[L[t]]
            else:
                i += sz[L[t]] + 1
                t = R[t]'''
        else:
            walk = f'''            if R[t] and F[R[t]] {o} x:
                i += sz[L[t]] + 1
                t = R[t]
            elif val[t] {o} x:
                return i + sz[L[t]]
            else:
                t = L[t]'''
        out.append(f'''
    def _lane{op[0].upper() + op[1:]}(self, t, x):  # the {"first" if side == "leftmost" else "last"} k with lane value k {o} x under t, or -1
        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.{f}
        if not t or not F[t] {o} x:
            return -1
        i = 0
        while True:
            self._push(t)
{walk}
''')
    return "".join(out)


# ================================================================================================ C++

def cpp(s):
    F, TG = s.fields(), s.tags()
    S_ = s.has("sum")
    out = [header("//", s), "\n", wrap(describe(s), "//"),
           "// T: int, long long, ..." + ("; sums are kept in S (long long for small T)." if S_ else ""), f"\ntemplate <typename T>\nstruct {CLS} {{\n"]
    if S_:
        out.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n")
    if s.has("hash"):
        out.append("    using U64 = unsigned long long;\n")
    if s.clamp:
        out.append("    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();\n")
    if s.find:
        out.append(A.SAFE_HASH)
    sk = cpp_skeleton(F, TG, [("unordered_map<T, int, SafeHash>", "where")] if s.find else [], cls=CLS)
    a = sk.index("    int root = 0;")
    sk = sk[:a] + f'''    int rE = 0, rO = 0;  // lane E: a[0], a[2], ...; lane O: a[1], a[3], ...

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit {CLS}(const vector<T>& arr = {{}}) {{
        vector<T> ev, od;
        for (size_t i = 0; i < arr.size(); i++) (i % 2 ? od : ev).push_back(arr[i]);
        rE = build(ev), rO = build(od);
    }}

    {CLS} makeEmpty() const {{ return {CLS}(); }}  // (a new, empty one)
'''
    out.append(sk)
    out.append('''
    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
''' + (CPP_HASH_HELPERS.replace(
        "    static unsigned long long hadd(unsigned long long a, unsigned long long b) { return a + b >= HP ? a + b - HP : a + b; }",
        "    static unsigned long long hadd(unsigned long long a, unsigned long long b) {\n        return a + b >= HP ? a + b - HP : a + b;\n    }") +
        "    static U64 HQ() {  // a lane's base: B^2 (its neighbours in the array are 2 apart)\n"
        "        static U64 q = hmul(HB(), HB());\n        return q;\n    }\n\n"
        if s.has("hash") else "") + '''
    // O(1) -- the current length of the array
    int size() const { return sz[rE] + sz[rO]; }

''')
    pub = cpp_pub(s)
    out.append("\n".join(pub[op] for op in s.ops if op in pub))
    internals = cpp_internals(s).replace("HB()", "HQ()")
    internals = internals.replace(A.CPP_TAIL, CPP_TAIL + cpp_extra(s) + "};\n")
    out.append(internals)
    text = A.fit_comments(gcd_costs(s, "".join(out))) + piece_example("cpp", f"{CLS}<int> t({{1, 2, 3, 4, 5}})", list("12345"))
    return text if TG else no_push(text, "cpp")


def cpp_pub(s):
    base = cpp_public(s)
    pub = {op: base[op] for op in ("pointAssign", "pointAdd", "pointChmax", "pointChmin")}
    C = "auto [ae, ao, be, bo, ce, co] = parts(l, r);"
    J = "join(ae, ao, be, bo, ce, co);"
    q = {"rangeSum": ("S", "sm[be] + sm[bo]"), "rangeMin": ("T", "bo ? min(mn[be], mn[bo]) : mn[be]"),
         "rangeMax": ("T", "bo ? max(mx[be], mx[bo]) : mx[be]"), "rangeXorQuery": ("T", "xr[be] ^ xr[bo]"),
         "rangeAndQuery": ("T", "an[be] & an[bo]"), "rangeOrQuery": ("T", "orr[be] | orr[bo]"), "rangeGcd": ("T", "gcd(g[be], g[bo])")}
    for op, (typ, expr) in q.items():
        if op not in s.ops:
            continue
        if op == "rangeGcd" and s.gdiff:  # a[l], a[l + 1] - a[l] and each lane's differences 2 apart
            body = "        T res = gcd(gcd(fv[be], g[be]), g[bo]);\n        if (bo) res = gcd(res, T(fv[bo] - fv[be]));"
        else:
            body = f"        {typ} res = {expr};"
        pub[op] = f'''    // O(logN) expected -- {QDOC[op]}
    {typ} {op}(int l, int r) {{
        {C}
{body}
        {J}
        return res;
    }}
'''
    if s.has("hash"):
        pub["rangeHash"] = f"    // O(logN) expected -- {QDOC['rangeHash']}\n    U64 rangeHash(int l, int r) {{ return hashes(l, r).first; }}\n"
        pub["rangeHashReversed"] = (f"    // O(logN) expected -- {QDOC['rangeHashReversed']}\n"
                                    "    U64 rangeHashReversed(int l, int r) { return hashes(l, r).second; }\n")
        pub["isPalindrome"] = f'''    // O(logN) expected -- {QDOC["isPalindrome"]}
    bool isPalindrome(int l, int r) {{
        auto [f, b] = hashes(l, r);
        return f == b;
    }}
'''
        pub["rangesEqual"] = f'''    // O(logN) expected -- {QDOC["rangesEqual"]}
    bool rangesEqual(int l1, int r1, int l2, int r2) {{
        return r1 - l1 == r2 - l2 && hashes(l1, r1).first == hashes(l2, r2).first;
    }}
'''
    for op, (side, cmp) in SEARCH.items():
        if op not in s.ops:
            continue
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        pick = "i < 0 ? j : j < 0 ? i : min(i, j)" if side == "leftmost" else "max(i, j)"
        lane = "lane" + op[0].upper() + op[1:]
        pub[op] = f'''    // O(logN) expected -- the {"first" if side == "leftmost" else "last"} i in [l, r] with a[i] {o} x, or -1 (each lane's walk pruned by the subtree {"max" if f == "mx" else "min"})
    int {op}(int l, int r, T x) {{
        {C}
        int i = {lane}(be, x), j = {lane}(bo, x);
        {J}
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return {pick};
    }}
'''
    shr = {"mod": ("T x", "if (x >= 1) shrink(be, x, [x](T v) { return T(v % x); }), shrink(bo, x, [x](T v) { return T(v % x); });", "logN * logU"),
           "div": ("T x", "if (x >= 2) shrink(be, T(1), [x](T v) { return T(v / x); }), shrink(bo, T(1), [x](T v) { return T(v / x); });", "logN * logU"),
           "sqrt": ("", "shrink(be, T(2), isqrtT), shrink(bo, T(2), isqrtT);", "logN * loglogU")}
    for u in s.ups:
        if u in shr:
            params, call, c = shr[u]
            pub[UOP[u]] = f'''    // amortized O({c}) expected -- {UDOC[u]}
    void {UOP[u]}(int l, int r{", " + params if params else ""}) {{
        {C}
        {call}
        {J}
    }}
'''
            continue
        params, ce_, co_ = upd_calls(s, u, "cpp")
        pub[UOP[u]] = f'''    // O(logN) expected -- {UDOC[u]}
    void {UOP[u]}(int l, int r, {params}) {{
        {C}
        {ce_}, {co_};
        {J}
    }}
'''
    pub.update({
        "pointGet": "    // O(logN) expected -- a[i]\n    T pointGet(int i) { return val[locate(i)]; }\n",
        "insertAt": '''    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, newNode(v), 0);
        tie(rE, rO) = pmerge(e, o, ce, co);
    }
''',
        "insertCopiesAt": '''    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, build(vector<T>((k + 1) / 2, v)), build(vector<T>(k / 2, v)));
        tie(rE, rO) = pmerge(e, o, ce, co);
    }
''',
        "append": "    // O(logN) expected -- append v to the end\n    void append(T v) { tie(rE, rO) = pmerge(rE, rO, newNode(v), 0); }\n",
        "appendLeft": "    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)\n    void appendLeft(T v) { insertAt(0, v); }\n",
        "rangeReverse": '''    // O(logN) expected -- reverse a[l..r] in place: each lane reverses, and with an even length they trade places
    void rangeReverse(int l, int r) {
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        applyRev(be), applyRev(bo);
        if ((r - l + 1) % 2 == 0) join(ae, ao, bo, be, ce, co);
        else join(ae, ao, be, bo, ce, co);
    }
''',
        "rangeTwinSpin": '''    // O(logN) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (odd length:
    // a[r] stays): the pairs' two lanes trade places
    void rangeTwinSpin(int l, int r) {
        int k = (r - l + 1) / 2;
        if (!k) return;
        auto [ae, ao, be, bo, ce, co] = parts(l, l + 2 * k - 1);
        join(ae, ao, bo, be, ce, co);
    }
''',
        "rangeRotateLeft": '''    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    // it is taken mod the length (negative shifts right)
    void rangeRotateLeft(int l, int r, long long k) {
        int len = r - l + 1;
        k = ((k % len) + len) % len;
        if (!k) return;
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        auto [xe, xo, ye, yo] = psplit(be, bo, (int)k);
        auto [e, o] = pmerge(ye, yo, xe, xo);
        join(ae, ao, e, o, ce, co);
    }
''',
        "rangeRotateRight": "    // O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the\n"
                            "    // length (negative shifts left)\n"
                            "    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }\n",
        "getAll": '''    // O(N) -- the whole current array, every pending tag applied on the way
    vector<T> getAll() {
        vector<T> ev = inorder(rE), od = inorder(rO), out(ev.size() + od.size());
        for (size_t i = 0; i < ev.size(); i++) out[2 * i] = ev[i];
        for (size_t i = 0; i < od.size(); i++) out[2 * i + 1] = od[i];
        return out;
    }
''',
        "cut": f'''    // O(logN) expected -- remove a[l..r] and return it as a {CLS} of its own (indices from 0)
    {CLS} cut(int l, int r) {{
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        tie(rE, rO) = pmerge(ae, ao, ce, co);
        {CLS} piece = makeEmpty();
        piece.rE = be, piece.rO = bo;
        return piece;
    }}
''',
        "paste": f'''    // O(logN) expected -- insert all of other (any {CLS}, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(int i, {CLS}& other) {{
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, other.rE, other.rO);
        tie(rE, rO) = pmerge(e, o, ce, co);
        other.rE = other.rO = 0;
    }}
''',
        "merge": f'''    // O(logN) expected -- append all of other at the end; other is left empty
    void merge({CLS}& other) {{
        tie(rE, rO) = pmerge(rE, rO, other.rE, other.rO);
        other.rE = other.rO = 0;
    }}
''',
        "split": f'''    // O(logN) expected -- (a[0..k-1], a[k..]) as two {CLS}s of their own; this one is left empty
    pair<{CLS}, {CLS}> split(int k) {{
        {CLS} left = makeEmpty(), right = makeEmpty();
        auto [le, lo, re, ro] = psplit(rE, rO, k);
        left.rE = le, left.rO = lo, right.rE = re, right.rO = ro;
        rE = rO = 0;
        return {{left, right}};
    }}
''',
        "trisect": f'''    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three {CLS}s of their own; this one is left empty
    tuple<{CLS}, {CLS}, {CLS}> trisect(int l, int r) {{
        {CLS} left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        left.rE = ae, left.rO = ao, mid.rE = be, mid.rO = bo, right.rE = ce, right.rO = co;
        rE = rO = 0;
        return {{left, mid, right}};
    }}
''',
    })
    if s.find:
        f = base["find"]
        a = "        if (path.back() != root) return -1;  // (erased, or in another treap)\n"
        b = "        return i;\n    }\n"
        assert a in f and f.endswith(b)
        f = f.replace(a, "        int top = path.back();\n        if (top != rE && top != rO) return -1;  // (erased, or in another treap)\n")
        pub["find"] = f[:-len(b)] + "        return 2 * i + (top == rO);  // (lane index i: a[2i] in lane E, a[2i + 1] in lane O)\n    }\n"
    return pub


CPP_TAIL = A.CPP_TAIL[:A.CPP_TAIL.index("    void cut(int l, int r, int& a, int& b, int& c) {")] + '''    // ---- the lanes: an array is a pair (E, O) of treaps, E holding its values at even positions, O the odd ones ----

    array<int, 4> psplit(int e, int o, int k) {  // lanes of (the first k values, the rest)
        int e1, e2, o1, o2;
        split(e, (k + 1) / 2, e1, e2);
        split(o, k / 2, o1, o2);
        if (k % 2) return {e1, o1, o2, e2};  // (an odd k: the rest starts on an odd position)
        return {e1, o1, e2, o2};
    }

    pair<int, int> pmerge(int e1, int o1, int e2, int o2) {  // lanes of (the first array, then the second)
        if ((sz[e1] + sz[o1]) % 2) swap(e2, o2);  // (after an odd length: its even positions are odd ones)
        return {merge(e1, e2), merge(o1, o2)};
    }

    array<int, 6> parts(int l, int r) {  // lanes of a[..l-1], a[l..r], a[r+1..]
        auto [ae, ao, xe, xo] = psplit(rE, rO, l);
        auto [be, bo, ce, co] = psplit(xe, xo, r - l + 1);
        return {ae, ao, be, bo, ce, co};
    }

    void join(int ae, int ao, int be, int bo, int ce, int co) {
        auto [e, o] = pmerge(ae, ao, be, bo);
        tie(rE, rO) = pmerge(e, o, ce, co);
    }

    int locate(int i, vector<int>* path = nullptr) {  // the node holding a[i], every tag on the way pushed
        int t = i % 2 ? rO : rE, k = i / 2;
        while (true) {
            push(t);
            int ls = sz[L[t]];
            if (k == ls) return t;
            if (path) path->push_back(t);
            if (k < ls) t = L[t];
            else k -= ls + 1, t = R[t];
        }
    }

    vector<T> inorder(int t) {  // the values under t in order, every tag on the way pushed
        vector<T> out;
        vector<int> st;
        while (!st.empty() || t) {
            while (t) push(t), st.push_back(t), t = L[t];
            t = st.back(), st.pop_back();
            out.push_back(val[t]);
            t = R[t];
        }
        return out;
    }
'''


def cpp_extra(s):
    out = []
    if s.has("hash"):
        out.append('''
    // (forward, backward) hash of a[l..r]: lane E's slice x holds a[l], a[l + 2], ..., lane O's y the rest; in base B
    // the range reads x0 y0 x1 y1 ..., so forward = H(x) + B H(y) (odd length) or B H(x) + H(y) (even), and backward
    // = Hrev(x) + B Hrev(y)
    pair<U64, U64> hashes(int l, int r) {
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        U64 B = HB();
        U64 fwd = (r - l) % 2 == 0 ? hadd(fh[be], hmul(B, fh[bo])) : hadd(hmul(B, fh[be]), fh[bo]);
        U64 bwd = hadd(bh[be], hmul(B, bh[bo]));
        join(ae, ao, be, bo, ce, co);
        return {fwd, bwd};
    }
''')
    for op, (side, cmp) in SEARCH.items():
        if op not in s.ops:
            continue
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        if side == "leftmost":
            walk = f'''            if (L[t] && {f}[L[t]] {o} x) t = L[t];
            else if (val[t] {o} x) return i + sz[L[t]];
            else i += sz[L[t]] + 1, t = R[t];'''
        else:
            walk = f'''            if (R[t] && {f}[R[t]] {o} x) i += sz[L[t]] + 1, t = R[t];
            else if (val[t] {o} x) return i + sz[L[t]];
            else t = L[t];'''
        out.append(f'''
    int lane{op[0].upper() + op[1:]}(int t, T x) {{  // the {"first" if side == "leftmost" else "last"} k with lane value k {o} x under t, or -1
        if (!t || !({f}[t] {o} x)) return -1;
        int i = 0;
        while (true) {{
            push(t);
{walk}
        }}
    }}
''')
    return "".join(out)


def main(only=None):
    if only is None:
        for d in os.listdir(DIR):
            t = os.path.join(DIR, d, "template.py")
            if os.path.exists(t) and f"@data-structure-type: {DTYPE}" in open(t).read():
                shutil.rmtree(os.path.join(DIR, d))
    seen = {}
    for s in variants():
        if only is not None and not only(s):
            continue
        name = folder_name(s.ops)
        folder = name if len(name) <= 180 else s.name()
        assert folder not in seen, (folder, seen.get(folder))
        seen[folder] = s.name()
        os.makedirs(os.path.join(DIR, folder), exist_ok=True)
        write_template(os.path.join(DIR, folder, "template.py"), py(s))
        write_template(os.path.join(DIR, folder, "template.cpp"), aosify(cpp(s)))
    print("wrote", len(seen), "pair treaps")


if __name__ == "__main__":
    main()
