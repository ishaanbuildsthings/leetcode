"""Implicit treaps with segment tree beats: range chmin / chmax with range sums, plus everything a treap does.

    python3 gen_treap_beats.py

The gen_beats.py design on a treap. A node keeps, over its subtree (its own value included), for the side(s) it has:
  chmin: mx, mx2 (strict second max), cmx (copies of the max)      chmax: mn, mn2, cmn
plus the sum sm, and an add tag only with rangeAdd. No chmin / chmax tags: a node's own mx / mn ARE its pending clamp
(push clamps each child to them), and no assign tag: a node whose values are all equal pushes that value down as an
assign. A chmin x stops at a node with mx2 < x (only the copies of the max move: sm drops by (mx - x) * cmx, and the
node's own value moves if it was the max) and walks further down only where x <= mx2. Variants, as gen_beats.py:
  side:  chmin, chmax, or both;  add: with or without rangeAdd;  extra: (one-sided) the other extreme kept plainly
each with reverse or not and cut / paste or not (cut / paste treaps share one node pool). The sequence ops, searches,
point ops and pieces are gen_treap_algebra.py's. The beats bound is proven for a fixed tree; split / merge reshape the
treap, so the chmin / chmax costs carry a ?.
"""
import itertools
import os
import shutil

from gen_treap import no_push, wrap
from gen_treap_algebra import (CPP_BUILD, CPP_PIECES, CPP_SEQ, CPP_TAIL, PY_PIECES, PY_SEQ, PY_TAIL, Spec, cpp_public, py_public,
                               rev_line)
from gen_treap_more import slots_line
from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
MARK = "Implicit treap with segment tree beats"
_ = (CPP_PIECES, CPP_SEQ, PY_PIECES, PY_SEQ)  # (pulled in through py_public / cpp_public)


class B:
    def __init__(self, side, add, extra, rev, ptr):
        self.side, self.add, self.extra, self.rev, self.ptr = side, add, extra, rev, ptr
        self.CN, self.CX = side in ("chmin", "both"), side in ("chmax", "both")
        self.MX = self.CN or (extra and side == "chmax")  # mx kept (with mx2 / cmx only on the chmin side)
        self.MN = self.CX or (extra and side == "chmin")
        mods = ("sum",) + (("min",) if self.MN else ()) + (("max",) if self.MX else ())
        self.base = Spec(mods, "", (), rev, ptr)  # (the treap ops, queries and searches come from it)
        self.ops = sorted(set(self.base.ops) | {"rangeAssign"} | ({"rangeChmin"} if self.CN else set()) |
                          ({"rangeChmax"} if self.CX else set()) | ({"rangeAdd"} if add else set()))

    def fields(self):  # (name, C++ type, Python node-0 value, C++ node-0 value)
        f = [("sm", "S", "0", "0")]
        if self.MX:
            f.append(("mx", "T", "0", "T(0)"))
        if self.CN:
            f += [("mx2", "T", "NEG", "NEG"), ("cmx", "int", "0", "0")]
        if self.MN:
            f.append(("mn", "T", "0", "T(0)"))
        if self.CX:
            f += [("mn2", "T", "INF", "INF"), ("cmn", "int", "0", "0")]
        return f

    def tags(self):
        return ([("rev", "char", "0", "0")] if self.rev else []) + ([("add", "T", "0", "T(0)")] if self.add else [])

    def name(self):
        return ("treap-beats-" + self.side + ("-add" if self.add else "") + ("-extra" if self.extra else "") +
                ("-rev" if self.rev else "") + ("-pointers" if self.ptr else ""))

    def uniform(self, py):  # "every value in the subtree is the same"
        if self.CN and self.CX:
            return "self.mn[t] == self.mx[t]" if py else "mn[t] == mx[t]"
        if self.CN:
            return "self.mx2[t] == NEG" if py else "mx2[t] == NEG"
        return "self.mn2[t] == INF" if py else "mn2[t] == INF"

    def top(self, py):  # the subtree's value when it is uniform
        f = "mx" if self.MX else "mn"
        return f"self.{f}[t]" if py else f"{f}[t]"


class BB:
    """AND / OR apply (bit beats) with any of sum / min / max: a node keeps the AND and the OR of its subtree, so the bits
    that differ inside it are an ^ orr. An op x -> (x & A) | O is applied at a node in O(1) when it leaves every
    differing bit alone (each value moves by the same amount: sums, mins and maxes shift) or forces every one of them
    (the subtree becomes one value); else it walks down, and a differing bit it touches stops differing there."""
    def __init__(self, aggs, rev, ptr):
        self.aggs, self.rev, self.ptr = aggs, rev, ptr
        self.MX, self.MN, self.SM = "max" in aggs, "min" in aggs, "sum" in aggs
        mods = (("sum",) if self.SM else ()) + (("min",) if self.MN else ()) + (("max",) if self.MX else ()) + ("and", "or")
        self.base = Spec(mods, "", (), rev, ptr)
        self.ops = sorted(set(self.base.ops) | {"rangeAndApply", "rangeOrApply", "rangeAssign"})

    def fields(self):
        return ([("sm", "S", "0", "0")] if self.SM else []) + ([("mn", "T", "0", "T(0)")] if self.MN else []) + \
            ([("mx", "T", "0", "T(0)")] if self.MX else []) + [("an", "T", "-1", "~T(0)"), ("orr", "T", "0", "T(0)")]

    def tags(self):
        return ([("rev", "char", "0", "0")] if self.rev else []) + [("tA", "T", "-1", "~T(0)"), ("tO", "T", "0", "T(0)")]

    def name(self):
        return "treap-bitbeats-" + "-".join(self.aggs) + ("-rev" if self.rev else "") + ("-pointers" if self.ptr else "")


def variants():
    out = []
    for k in (1, 2, 3):  # (none of them: gen_treap_algebra's and / or treaps, with plain tags)
        for aggs in itertools.combinations(("sum", "min", "max"), k):
            for rev in (False, True):
                for ptr in (False, True):
                    out.append(BB(aggs, rev, ptr))
    for side in ("chmin", "chmax", "both"):
        for add in (False, True):
            for extra in ((False, True) if side != "both" else (False,)):
                for rev in (False, True):
                    for ptr in (False, True):
                        out.append(B(side, add, extra, rev, ptr))
    return out


def cost(b, op):
    if op in ("rangeAndApply", "rangeOrApply"):
        return "log(N)*log(U) amortized ?"
    if op in ("rangeChmin", "rangeChmax"):
        return "log^2(N) amortized ?" if b.add else "log(N) amortized ?"
    return "N" if op == "getAll" else "log(N) expected"


def header(cm, b):
    lines = [f"@operations: {' '.join(b.ops)}", "@data-structure-type: treap", "@complexities:"]
    lines += [f"  {op}: {cost(b, op)}" for op in b.ops] + ["  build: N", "@memory:", "  layout: none"]
    lines += ["  node: " + " ".join(f"{f}[1*N]" for f in ["val", "sz", "L", "R", "pri"] + [x[0] for x in b.fields()]),
              "  tags: " + (" ".join(f"{t[0]}[1*N]" for t in b.tags()) or "none"), "  other: none",
              ("  note: N = every value ever inserted; an and / or / assign is one pending map x -> (x & tA) | tO per node, "
               "applied at a node only where it is uniform there (it leaves every differing bit alone, or forces them all)"
               if isinstance(b, BB) else
               "  note: N = every value ever inserted; no chmin / chmax / assign tags: a node's own max / min are its pending "
               "clamp, and a node whose values are all equal pushes that value as an assign") +
              ("; every ImplicitTreap<T> shares one node pool (cut / paste move nodes between them): resetPool() between "
               "test cases" if b.ptr else "")]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def describe(b):
    if isinstance(b, BB):
        keeps = ", ".join(x for x, ok in (("its sum", b.SM), ("its min", b.MN), ("its max", b.MX)) if ok)
        return (f"Implicit treap with bit beats: range AND / OR apply (a[i] &= v, a[i] |= v) and range assign with range AND / OR"
                " queries" + ", range sums" * b.SM + ", the range min" * b.MN + ", the range max" * b.MX + ", on an array you "
                "can insert into / erase from anywhere, " + ("reverse, " if b.rev else "") + "rotate, move" +
                (" and cut / paste between treaps" if b.ptr else "") + f". Each node keeps {keeps}, the AND and the OR of its "
                "subtree (its own value included), so the bits that differ inside it are AND ^ OR. An op x -> (x & A) | O "
                "is applied at a node in O(1) when it leaves every differing bit alone (every value moves by the same "
                "amount) or forces every one of them (the subtree becomes one value); otherwise it walks down, and each "
                "differing bit it touches stops differing there (a node has at most logU of them). Values must be "
                "non-negative. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT "
                "array; searches return -1 when nothing qualifies.")
    sides = {"chmin": "range chmin (a[i] = min(a[i], x))", "chmax": "range chmax (a[i] = max(a[i], x))",
             "both": "range chmin and chmax"}[b.side]
    keeps = {"chmin": "its max, strict second max and copies of the max", "chmax": "its min, strict second min and copies of the min",
             "both": "its max / min, strict second max / min and their copies"}[b.side]
    return (f"{MARK}: {sides}" + (", range add" if b.add else "") + " and range assign with range sums" +
            (", the range max" if b.MX else "") + (", the range min" if b.MN else "") + ", on an array you can insert into / "
            "erase from anywhere, " + ("reverse, " if b.rev else "") + "rotate, move" + (" and cut / paste between treaps" if b.ptr else "") +
            f". Each node keeps {keeps} over its subtree (its own value included), plus the sum. A chmin x stops at a node with "
            "second max < x: only the copies of the max move (the sum drops by (max - x) * copies). A node's own max / min "
            "double as its pending clamp: push clamps each child to them, so there are no chmin / chmax tags; and when all of "
            "a node's values are equal, push hands that value to both children as an assign, so there is no assign tag. All "
            "indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1 "
            "when nothing qualifies.")


# ================================================================================================ Python

def py(b):
    F, TG = b.fields(), b.tags()
    names = ["val", "pri", "L", "R", "sz"] + [f[0] for f in F] + [t[0] for t in TG]
    out = [header("#", b), "\n", wrap(describe(b), "#"), "import random\n\n\n", 'INF, NEG = float("inf"), float("-inf")\n\n\n',
           "class ImplicitTreap:\n"]
    if b.ptr:
        out.append("    # one node pool shared by every ImplicitTreap: cut / paste move nodes between them (node 0 = the empty tree)\n")
        out.append("".join(f"    {n} = [{ident}]\n" for n, ident in
                           [("val", "0"), ("pri", "0"), ("L", "0"), ("R", "0"), ("sz", "0")] + [(f[0], f[2]) for f in F] + [(t[0], t[2]) for t in TG]))
        out.append('    __slots__ = ("root",)\n\n')
        out.append('''    # O(N) -- arr: the initial array (may be empty)
    def __init__(self, arr=()):
        self.root = self._build(list(arr))

    # O(1) -- forget every node of every ImplicitTreap (call between test cases, then build new ones)
    @classmethod
    def resetPool(cls):
''' + "".join(f"        del cls.{n}[1:]\n" for n in names) + "\n")
    else:
        out.append(slots_line(["root"] + names))
        out.append("    # O(N) -- arr: the initial array (may be empty)\n    def __init__(self, arr):\n" +
                   "        self.val, self.pri, self.L, self.R, self.sz = [0], [0], [0], [0], [0]  # node 0 = the empty tree\n" +
                   "".join(f"        self.{f[0]} = [{f[2]}]\n" for f in F) + "".join(f"        self.{t[0]} = [{t[2]}]\n" for t in TG) +
                   "        self.root = self._build(list(arr))\n\n")
    out.append("    # O(1) -- the current length of the array\n    def size(self):\n        return self.sz[self.root]\n\n")
    pub = py_public(b.base)
    pub.update(py_updates(b))
    out.append("\n".join(pub[op] for op in b.ops if op in pub))
    out.append(py_internals(b))
    return "".join(out)


def py_updates(b):
    if isinstance(b, BB):
        return {op: f'''    # {"amortized O(logN logU) expected" if op != "rangeAssign" else "O(logN) expected"} -- {doc}
    def {op}(self, l, r, v):
        a, b, c = self._cut(l, r)
        self._bits(b, {args})
        self._join(a, b, c)
''' for op, args, doc in (("rangeAndApply", "v, 0", "a[i] &= v for i in [l, r]"), ("rangeOrApply", "-1, v", "a[i] |= v for i in [l, r]"),
                            ("rangeAssign", "0, v", "a[i] = v for i in [l, r]"))}
    pub = {}
    J = "self._join(a, b, c)"
    for op, call, doc in (("rangeAssign", "self._applyAssign(b, v)", "a[i] = v for i in [l, r]"),
                          ("rangeAdd", "self._applyAdd(b, v)", "a[i] += v for i in [l, r]"),
                          ("rangeChmin", "self._chmin(b, v)", "a[i] = min(a[i], v) for i in [l, r]"),
                          ("rangeChmax", "self._chmax(b, v)", "a[i] = max(a[i], v) for i in [l, r]")):
        if op in b.ops:
            c = cost(b, op)
            tc = ("amortized O(log^2 N) expected" if "^2" in c else "amortized O(logN) expected") if "amortized" in c else "O(logN) expected"
            pub[op] = f'''    # {tc} -- {doc}
    def {op}(self, l, r, v):
        a, b, c = self._cut(l, r)
        {call}
        {J}
'''
    return pub


def py_internals(b):
    if isinstance(b, BB):
        return py_internals_bits(b)
    F = [f[0] for f in b.fields()]
    new = ["        self.sm.append(v)"] + [f"        self.{f}.append(v)" for f in ("mx", "mn") if f in F]
    new += ["        self.mx2.append(NEG)", "        self.cmx.append(1)"] if b.CN else []
    new += ["        self.mn2.append(INF)", "        self.cmn.append(1)"] if b.CX else []
    new += [f"        self.{t[0]}.append(0)" for t in b.tags()]
    out = ['''
    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
''' + "".join(x + "\n" for x in new) + '''        return x

    # a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    def _build(self, vals):
        pri, L, R = self.pri, self.L, self.R
        stack = []
        for v in vals:
            x, last = self._newNode(v), 0
            while stack and pri[stack[-1]] < pri[x]:
                last = stack.pop()
            L[x] = last
            if stack:
                R[stack[-1]] = x
            stack.append(x)
        root = stack[0] if stack else 0
        order, todo = [], ([root] if root else [])
        while todo:
            x = todo.pop()
            order.append(x)
            if L[x]:
                todo.append(L[x])
            if R[x]:
                todo.append(R[x])
        for x in reversed(order):
            self._pull(x)
        return root

    def _pull(self, x):  # recompute x from its children (its own value is one more value of the subtree)
        l, r = self.L[x], self.R[x]
        self.sz[x] = self.sz[l] + self.sz[r] + 1
        v = self.val[x]
        self.sm[x] = self.sm[l] + v + self.sm[r]
''']
    for side, f, f2, cnt, c, worse in (("CN", "mx", "mx2", "cmx", ">", "NEG"), ("CX", "mn", "mn2", "cmn", "<", "INF")):
        if getattr(b, side):  # (top, second, copies) of the node alone, then joined with each child's
            out.append(f'''        m, m2, k = v, {worse}, 1
        for y in (l, r):
            if y:
                a, a2 = self.{f}[y], self.{f2}[y]
                if a {c} m:
                    m, m2, k = a, (a2 if a2 {c} m else m), self.{cnt}[y]
                elif a == m:
                    k += self.{cnt}[y]
                    if a2 {c} m2:
                        m2 = a2
                elif a {c} m2:
                    m2 = a
        self.{f}[x], self.{f2}[x], self.{cnt}[x] = m, m2, k
''')
    for f, c in (("mx", ">"), ("mn", "<")):
        if f in F and not (f == "mx" and b.CN or f == "mn" and b.CX):
            out.append(f'''        m = v
        if l and self.{f}[l] {c} m:
            m = self.{f}[l]
        if r and self.{f}[r] {c} m:
            m = self.{f}[r]
        self.{f}[x] = m
''')
    asg = ["            n = self.sz[t]", "            self.val[t] = v", "            self.sm[t] = v * n"]
    asg += [f"            self.{f}[t] = v" for f in ("mx", "mn") if f in F]
    asg += ["            self.mx2[t], self.cmx[t] = NEG, n"] if b.CN else []
    asg += ["            self.mn2[t], self.cmn[t] = INF, n"] if b.CX else []
    asg += ["            self.add[t] = 0"] if b.add else []
    out.append("\n    def _applyAssign(self, t, v):  # every value of t's subtree becomes v\n        if t:\n" + "".join(x + "\n" for x in asg))
    if b.add:
        a = ["        self.val[t] += v", "        self.sm[t] += v * self.sz[t]"] + [f"        self.{f}[t] += v" for f in ("mx", "mn") if f in F]
        a += ["        if self.mx2[t] != NEG:", "            self.mx2[t] += v"] if b.CN else []
        a += ["        if self.mn2[t] != INF:", "            self.mn2[t] += v"] if b.CX else []
        out.append(f'''
    def _applyAdd(self, t, v):  # every value of t's subtree gains v (a uniform one stays an assign)
        if not t:
            return
        if {b.uniform(True)}:
            self._applyAssign(t, {b.top(True)} + v)
            return
''' + "".join(x + "\n" for x in a) + "            self.add[t] += v\n".replace("            ", "        "))
    if b.CN:
        out.append(f'''
    def _applyChmin(self, t, v):  # chmin by v on t, with mx2 < v < mx: only the copies of the max move
        if self.mx2[t] == NEG:  # (all equal)
            self._applyAssign(t, v)
            return
        if self.val[t] == self.mx[t]:
            self.val[t] = v
''' + ("        if self.mn2[t] == self.mx[t]:\n            self.mn2[t] = v\n" if b.CX else "") + '''        self.sm[t] -= (self.mx[t] - v) * self.cmx[t]
        self.mx[t] = v

    def _chmin(self, t, x):  # a[i] = min(a[i], x) over t's subtree, walking down only where x <= the second max
        if not t or self.mx[t] <= x:
            return
        if self.mx2[t] < x:
            self._applyChmin(t, x)
            return
        self._push(t)
        if self.val[t] > x:
            self.val[t] = x
        self._chmin(self.L[t], x)
        self._chmin(self.R[t], x)
        self._pull(t)
''')
    if b.CX:
        out.append(f'''
    def _applyChmax(self, t, v):  # chmax by v on t, with mn < v < mn2: only the copies of the min move
        if self.mn2[t] == INF:  # (all equal)
            self._applyAssign(t, v)
            return
        if self.val[t] == self.mn[t]:
            self.val[t] = v
''' + ("        if self.mx2[t] == self.mn[t]:\n            self.mx2[t] = v\n" if b.CN else "") + '''        self.sm[t] += (v - self.mn[t]) * self.cmn[t]
        self.mn[t] = v

    def _chmax(self, t, x):  # a[i] = max(a[i], x) over t's subtree, walking down only where x >= the second min
        if not t or self.mn[t] >= x:
            return
        if self.mn2[t] > x:
            self._applyChmax(t, x)
            return
        self._push(t)
        if self.val[t] < x:
            self.val[t] = x
        self._chmax(self.L[t], x)
        self._chmax(self.R[t], x)
        self._pull(t)
''')
    if b.rev:
        out.append('''
    def _applyRev(self, x):  # reverse x's subtree (every kept aggregate reads the same both ways)
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
''')
    push = ['''
    def _push(self, t):  # hand t's pending changes to its children: all one value (an assign), else the add, then its clamp
        l, r = self.L[t], self.R[t]
''']
    if b.rev:
        push.append("        if self.rev[t]:\n            self._applyRev(l)\n            self._applyRev(r)\n            self.rev[t] = 0\n")
    push.append(f"        if {b.uniform(True)}:\n            v = {b.top(True)}\n            self._applyAssign(l, v)\n            self._applyAssign(r, v)\n" +
                ("            self.add[t] = 0\n" if b.add else "") + "            return\n")
    if b.add:
        push.append("        if self.add[t]:\n            self._applyAdd(l, self.add[t])\n            self._applyAdd(r, self.add[t])\n            self.add[t] = 0\n")
    for side, f, fn, c in (("CN", "mx", "_applyChmin", ">"), ("CX", "mn", "_applyChmax", "<")):
        if getattr(b, side):
            push.append(f"        for y in (l, r):\n            if y and self.{f}[y] {c} self.{f}[t]:\n                self.{fn}(y, self.{f}[t])\n")
    out.append("".join(push))
    out.append(PY_TAIL)
    return "".join(out)


# ================================================================================================ C++

def cpp(b):
    F, TG = b.fields(), b.tags()
    fl, tn = [f[0] for f in F], [t[0] for t in TG]
    st = "static inline " if b.ptr else ""
    out = [header("//", b), "\n", wrap(describe(b), "//"), "// T: int, long long, ...; sums are kept in S (long long for small T).",
           "\ntemplate <typename T>\nstruct ImplicitTreap {\n", "    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n",
           "    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();  // (no second max / min)\n",
           "    int root = 0;\n"]
    if b.ptr:
        out.append("    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them (node 0 = the empty tree)\n")
    out.append(f"    {st}vector<T> val{{T(0)}};\n    {st}vector<unsigned long long> pri{{0}};\n    {st}vector<int> L{{0}}, R{{0}}, sz{{0}};\n")
    out += [f"    {st}vector<{f[1]}> {f[0]}{{{f[3]}}};\n" for f in F] + [f"    {st}vector<{t[1]}> {t[0]}{{{t[3]}}};\n" for t in TG]
    out.append('''
    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N) -- arr: the initial array (may be empty)
    explicit ImplicitTreap(const vector<T>& arr = {}) { root = build(arr); }
''' + ('''
    // O(1) -- forget every node of every ImplicitTreap<T> (call between test cases, then build new ones)
    static void resetPool() {
''' + "".join(f"        {n}.resize(1);\n" for n in ["val", "pri", "L", "R", "sz"] + fl + tn) + "    }\n" if b.ptr else "") + '''
    // O(1) -- the current length of the array
    int size() const { return sz[root]; }

''')
    pub = cpp_public(b.base)
    pub.update(cpp_updates(b))
    out.append("\n".join(pub[op] for op in b.ops if op in pub))
    out.append(cpp_internals(b))
    return "".join(out)


def cpp_updates(b):
    if isinstance(b, BB):
        return {op: f'''    // {"amortized O(logN logU) expected" if op != "rangeAssign" else "O(logN) expected"} -- {doc}
    void {op}(int l, int r, T v) {{
        int a, b, c;
        cut(l, r, a, b, c);
        bits(b, {args});
        root = merge(merge(a, b), c);
    }}
''' for op, args, doc in (("rangeAndApply", "v, T(0)", "a[i] &= v for i in [l, r]"), ("rangeOrApply", "~T(0), v", "a[i] |= v for i in [l, r]"),
                            ("rangeAssign", "T(0), v", "a[i] = v for i in [l, r]"))}
    pub = {}
    for op, call, doc in (("rangeAssign", "applyAssign(b, v)", "a[i] = v for i in [l, r]"), ("rangeAdd", "applyAdd(b, v)", "a[i] += v for i in [l, r]"),
                          ("rangeChmin", "chmin(b, v)", "a[i] = min(a[i], v) for i in [l, r]"),
                          ("rangeChmax", "chmax(b, v)", "a[i] = max(a[i], v) for i in [l, r]")):
        if op in b.ops:
            c = cost(b, op)
            tc = ("amortized O(log^2 N) expected" if "^2" in c else "amortized O(logN) expected") if "amortized" in c else "O(logN) expected"
            pub[op] = f'''    // {tc} -- {doc}
    void {op}(int l, int r, T v) {{
        int a, b, c;
        cut(l, r, a, b, c);
        {call};
        root = merge(merge(a, b), c);
    }}
'''
    return pub


def cpp_internals(b):
    if isinstance(b, BB):
        return cpp_internals_bits(b)
    fl = [f[0] for f in b.fields()]
    new = ["sm.push_back(S(v))"] + [f"{f}.push_back(v)" for f in ("mx", "mn") if f in fl]
    new += ["mx2.push_back(NEG)", "cmx.push_back(1)"] if b.CN else []
    new += ["mn2.push_back(INF)", "cmn.push_back(1)"] if b.CX else []
    new += [f"{t[0]}.push_back({t[3]})" for t in b.tags()]
    out = ['''
    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1);
        ''' + rev_line(new) + '''
        return (int)val.size() - 1;
    }
''' + CPP_BUILD + '''
    void pull(int x) {  // recompute x from its children (its own value is one more value of the subtree)
        int l = L[x], r = R[x];
        sz[x] = sz[l] + sz[r] + 1;
        T v = val[x];
        sm[x] = sm[l] + S(v) + sm[r];
''']
    for side, f, f2, cnt, c, worse in (("CN", "mx", "mx2", "cmx", ">", "NEG"), ("CX", "mn", "mn2", "cmn", "<", "INF")):
        if getattr(b, side):  # (top, second, copies) of the node alone, then joined with each child's
            out.append(f'''        {{
            T m = v, m2 = {worse};
            int k = 1;
            for (int y : {{l, r}}) {{
                if (!y) continue;
                T a = {f}[y], a2 = {f2}[y];
                if (a {c} m) m2 = a2 {c} m ? a2 : m, m = a, k = {cnt}[y];
                else if (a == m) k += {cnt}[y], m2 = a2 {c} m2 ? a2 : m2;
                else if (a {c} m2) m2 = a;
            }}
            {f}[x] = m, {f2}[x] = m2, {cnt}[x] = k;
        }}
''')
    for f, c in (("mx", ">"), ("mn", "<")):
        if f in fl and not (f == "mx" and b.CN or f == "mn" and b.CX):
            out.append(f"        {f}[x] = v;\n        if (l && {f}[l] {c} {f}[x]) {f}[x] = {f}[l];\n        if (r && {f}[r] {c} {f}[x]) {f}[x] = {f}[r];\n")
    out.append("    }\n")
    asg = ["int n = sz[t];", "val[t] = v, sm[t] = S(v) * n;"] + [f"{f}[t] = v;" for f in ("mx", "mn") if f in fl]
    asg += ["mx2[t] = NEG, cmx[t] = n;"] if b.CN else []
    asg += ["mn2[t] = INF, cmn[t] = n;"] if b.CX else []
    asg += ["add[t] = T(0);"] if b.add else []
    out.append("\n    void applyAssign(int t, T v) {  // every value of t's subtree becomes v\n        if (!t) return;\n" +
               "".join(f"        {x}\n" for x in asg) + "    }\n")
    if b.add:
        a = ["val[t] += v, sm[t] += S(v) * sz[t];"] + [f"{f}[t] += v;" for f in ("mx", "mn") if f in fl]
        a += ["if (mx2[t] != NEG) mx2[t] += v;"] if b.CN else []
        a += ["if (mn2[t] != INF) mn2[t] += v;"] if b.CX else []
        a.append("add[t] += v;")
        out.append(f'''
    void applyAdd(int t, T v) {{  // every value of t's subtree gains v (a uniform one stays an assign)
        if (!t) return;
        if ({b.uniform(False)}) {{ applyAssign(t, T({b.top(False)} + v)); return; }}
''' + "".join(f"        {x}\n" for x in a) + "    }\n")
    if b.CN:
        out.append('''
    void applyChmin(int t, T v) {  // chmin by v on t, with mx2 < v < mx: only the copies of the max move
        if (mx2[t] == NEG) { applyAssign(t, v); return; }  // (all equal)
        if (val[t] == mx[t]) val[t] = v;
''' + ("        if (mn2[t] == mx[t]) mn2[t] = v;\n" if b.CX else "") + '''        sm[t] -= S(mx[t] - v) * cmx[t];
        mx[t] = v;
    }

    void chmin(int t, T x) {  // a[i] = min(a[i], x) over t's subtree, walking down only where x <= the second max
        if (!t || mx[t] <= x) return;
        if (mx2[t] < x) { applyChmin(t, x); return; }
        push(t);
        if (val[t] > x) val[t] = x;
        chmin(L[t], x), chmin(R[t], x);
        pull(t);
    }
''')
    if b.CX:
        out.append('''
    void applyChmax(int t, T v) {  // chmax by v on t, with mn < v < mn2: only the copies of the min move
        if (mn2[t] == INF) { applyAssign(t, v); return; }  // (all equal)
        if (val[t] == mn[t]) val[t] = v;
''' + ("        if (mx2[t] == mn[t]) mx2[t] = v;\n" if b.CN else "") + '''        sm[t] += S(v - mn[t]) * cmn[t];
        mn[t] = v;
    }

    void chmax(int t, T x) {  // a[i] = max(a[i], x) over t's subtree, walking down only where x >= the second min
        if (!t || mn[t] >= x) return;
        if (mn2[t] > x) { applyChmax(t, x); return; }
        push(t);
        if (val[t] < x) val[t] = x;
        chmax(L[t], x), chmax(R[t], x);
        pull(t);
    }
''')
    if b.rev:
        out.append('''
    void applyRev(int x) {  // reverse x's subtree (every kept aggregate reads the same both ways)
        if (x) swap(L[x], R[x]), rev[x] ^= 1;
    }
''')
    push = ["\n    void push(int t) {  // hand t's pending changes to its children: all one value (an assign), else the add, then its clamp\n",
            "        int l = L[t], r = R[t];\n"]
    if b.rev:
        push.append("        if (rev[t]) applyRev(l), applyRev(r), rev[t] = 0;\n")
    push.append(f"        if ({b.uniform(False)}) {{\n            applyAssign(l, {b.top(False)}), applyAssign(r, {b.top(False)});\n" +
                ("            add[t] = T(0);\n" if b.add else "") + "            return;\n        }\n")
    if b.add:
        push.append("        if (add[t] != T(0)) applyAdd(l, add[t]), applyAdd(r, add[t]), add[t] = T(0);\n")
    for side, f, fn, c in (("CN", "mx", "applyChmin", ">"), ("CX", "mn", "applyChmax", "<")):
        if getattr(b, side):
            push.append(f"        for (int y : {{l, r}})\n            if (y && {f}[y] {c} {f}[t]) {fn}(y, {f}[t]);\n")
    push.append("    }\n")
    out.append("".join(push))
    out.append(CPP_TAIL)
    return "".join(out)


def py_internals_bits(b):
    new = [f"        self.{f[0]}.append(v)" for f in b.fields()] + [f"        self.{t[0]}.append({t[2]})" for t in b.tags()]
    mm = "".join(f'''        m = v
        if l and self.{f}[l] {c} m:
            m = self.{f}[l]
        if r and self.{f}[r] {c} m:
            m = self.{f}[r]
        self.{f}[x] = m
''' for f, c, ok in (("mn", "<", b.MN), ("mx", ">", b.MX)) if ok)
    one = "".join(f"            self.{f}[t] = {e}\n" for f, e, ok in (("sm", "v * self.sz[t]", b.SM), ("mn", "v", b.MN), ("mx", "v", b.MX)) if ok)
    shift = "".join(f"            self.{f}[t] += {e}\n" for f, e, ok in (("sm", "c * self.sz[t]", b.SM), ("mn", "c", b.MN), ("mx", "c", b.MX)) if ok)
    out = '''
    # ---- internals ----

    def _newNode(self, v):
        x = len(self.val)
        self.val.append(v)
        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
''' + "".join(x + "\n" for x in new) + '''        return x

    # a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    def _build(self, vals):
        pri, L, R = self.pri, self.L, self.R
        stack = []
        for v in vals:
            x, last = self._newNode(v), 0
            while stack and pri[stack[-1]] < pri[x]:
                last = stack.pop()
            L[x] = last
            if stack:
                R[stack[-1]] = x
            stack.append(x)
        root = stack[0] if stack else 0
        order, todo = [], ([root] if root else [])
        while todo:
            x = todo.pop()
            order.append(x)
            if L[x]:
                todo.append(L[x])
            if R[x]:
                todo.append(R[x])
        for x in reversed(order):
            self._pull(x)
        return root

    def _pull(self, x):  # recompute x from its children (its own value is one more value of the subtree)
        l, r = self.L[x], self.R[x]
        self.sz[x] = self.sz[l] + self.sz[r] + 1
        v = self.val[x]
''' + ("        self.sm[x] = self.sm[l] + v + self.sm[r]\n" if b.SM else "") + mm + '''        self.an[x] = self.an[l] & v & self.an[r]  # (node 0: the AND of nothing, -1)
        self.orr[x] = self.orr[l] | v | self.orr[r]

    def _bits(self, t, A, O):  # every value x of t's subtree becomes (x & A) | O
        if not t:
            return
        d = self.an[t] ^ self.orr[t]  # the bits that differ inside t
        if not d & A & ~O:  # every differing bit is forced: the subtree becomes one value
            v = (self.an[t] & A) | O
            self.val[t] = self.an[t] = self.orr[t] = v
''' + one + '''            self.tA[t], self.tO[t] = 0, v
        elif not d & (~A | O):  # no differing bit is touched: every value moves by the same c
            c = ((self.an[t] & A) | O) - self.an[t]
            self.val[t] = (self.val[t] & A) | O
''' + shift + '''            self.an[t] = (self.an[t] & A) | O
            self.orr[t] = (self.orr[t] & A) | O
            self.tA[t] &= A
            self.tO[t] = (self.tO[t] & A) | O
        else:  # (each differing bit this touches stops differing here)
            self._push(t)
            self.val[t] = (self.val[t] & A) | O
            self._bits(self.L[t], A, O)
            self._bits(self.R[t], A, O)
            self._pull(t)
''' + ('''
    def _applyRev(self, x):  # reverse x's subtree (every kept aggregate reads the same both ways)
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
''' if b.rev else "") + '''
    def _push(self, t):  # hand t's pending map to its children (it is uniform at each of them, so O(1))
        l, r = self.L[t], self.R[t]
''' + ("        if self.rev[t]:\n            self._applyRev(l)\n            self._applyRev(r)\n            self.rev[t] = 0\n" if b.rev else "") + '''        if self.tA[t] != -1 or self.tO[t]:
            self._bits(l, self.tA[t], self.tO[t])
            self._bits(r, self.tA[t], self.tO[t])
            self.tA[t], self.tO[t] = -1, 0
'''
    return out + PY_TAIL


def cpp_internals_bits(b):
    new = [f"{f[0]}.push_back({'S(v)' if f[1] == 'S' else 'v'})" for f in b.fields()] + [f"{t[0]}.push_back({t[3]})" for t in b.tags()]
    mm = "".join(f"        {f}[x] = v;\n        if (l && {f}[l] {c} {f}[x]) {f}[x] = {f}[l];\n        if (r && {f}[r] {c} {f}[x]) {f}[x] = {f}[r];\n"
                 for f, c, ok in (("mn", "<", b.MN), ("mx", ">", b.MX)) if ok)
    one = "".join(f", {f}[t] = {e}" for f, e, ok in (("sm", "S(v) * sz[t]", b.SM), ("mn", "v", b.MN), ("mx", "v", b.MX)) if ok)
    shift = "".join(f"            {f}[t] += {e};\n" for f, e, ok in (("sm", "S(c) * sz[t]", b.SM), ("mn", "c", b.MN), ("mx", "c", b.MX)) if ok)
    return '''
    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1);
        ''' + rev_line(new) + '''
        return (int)val.size() - 1;
    }
''' + CPP_BUILD + '''
    void pull(int x) {  // recompute x from its children (its own value is one more value of the subtree)
        int l = L[x], r = R[x];
        sz[x] = sz[l] + sz[r] + 1;
        T v = val[x];
''' + ("        sm[x] = sm[l] + S(v) + sm[r];\n" if b.SM else "") + mm + '''        an[x] = an[l] & v & an[r];  // (node 0: the AND of nothing, ~0)
        orr[x] = orr[l] | v | orr[r];
    }

    void bits(int t, T A, T O) {  // every value x of t's subtree becomes (x & A) | O
        if (!t) return;
        T d = an[t] ^ orr[t];  // the bits that differ inside t
        if (!(d & A & ~O)) {  // every differing bit is forced: the subtree becomes one value
            T v = (an[t] & A) | O;
            val[t] = an[t] = orr[t] = v''' + one + ''';
            tA[t] = T(0), tO[t] = v;
        } else if (!(d & (~A | O))) {  // no differing bit is touched: every value moves by the same c
            T c = ((an[t] & A) | O) - an[t];
            val[t] = (val[t] & A) | O;
''' + shift + '''            an[t] = (an[t] & A) | O, orr[t] = (orr[t] & A) | O;
            tA[t] &= A, tO[t] = (tO[t] & A) | O;
        } else {  // (each differing bit this touches stops differing here)
            push(t);
            val[t] = (val[t] & A) | O;
            bits(L[t], A, O), bits(R[t], A, O);
            pull(t);
        }
    }
''' + ('''
    void applyRev(int x) {  // reverse x's subtree (every kept aggregate reads the same both ways)
        if (x) swap(L[x], R[x]), rev[x] ^= 1;
    }
''' if b.rev else "") + '''
    void push(int t) {  // hand t's pending map to its children (it is uniform at each of them, so O(1))
        int l = L[t], r = R[t];
''' + ("        if (rev[t]) applyRev(l), applyRev(r), rev[t] = 0;\n" if b.rev else "") + '''        if (tA[t] != ~T(0) || tO[t] != T(0)) {
            bits(l, tA[t], tO[t]), bits(r, tA[t], tO[t]);
            tA[t] = ~T(0), tO[t] = T(0);
        }
    }
''' + CPP_TAIL


def main():
    for d in os.listdir(DIR):
        t = os.path.join(DIR, d, "template.py")
        if os.path.exists(t) and (MARK in open(t).read() or "Implicit treap with bit beats" in open(t).read()):
            shutil.rmtree(os.path.join(DIR, d))
    n = 0
    for b in variants():
        name = folder_name(b.ops)
        folder = name if len(name) <= 180 else b.name()
        os.makedirs(os.path.join(DIR, folder), exist_ok=True)
        write_template(os.path.join(DIR, folder, "template.py"), py(b))
        write_template(os.path.join(DIR, folder, "template.cpp"), cpp(b))
        n += 1
    print("wrote", n, "beats treaps")


if __name__ == "__main__":
    main()
