"""Segment trees and lazy segment trees with composable aggregates: one template per (aggregates, range updates) a
2N iterative tree can keep, each carrying only the arrays its ops need. The same modules and update families as the
treaps (gen_treap_algebra.py), minus what needs sequence edits.

    python3 gen_seg_algebra.py

Every tree is the Al.Cash-style 2N layout: leaves tree[n..2n), node x's children 2x and 2x + 1. A node that covers a
range of a query or update is always a perfect subtree of 2^s leaves (s = its level), so its length is 1 << s and per
level tables replace per node ones (the hash powers B^(2^s) and 1 + B + ... + B^(2^s - 1)). Internal nodes that
straddle the wrap hold junk nobody reads. With range updates each internal node keeps its pending tags ("applied
here, not yet to my children"): an update pushes the tags on its two boundary leaf paths, tags the covering nodes,
then rebuilds the two paths, each node redoing its own pending tag on top of its children. A query pushes the same
two paths, then reads the covering nodes in order (left to right, so ordered aggregates fold correctly).

Aggregates and updates: see gen_treap_algebra.py (the OK table there says which update families each aggregate can
absorb; the same aggregate sets: sum / min / max / hash with up to two of the other families, and one cover per update
set for three or more). A pending add folds into a pending assign (an assign with a shifted value), and so does a
pending xor; a pending arithmetic add sits after a pending assign. Folders whose op set a hand-written template already
has are skipped (the hand-written one stays).
"""
import os
import shutil

from gen_treap import CPP_HASH_HELPERS, PY_HASH_CONST, wrap
from gen_treap_algebra import OK, QDOC, QOPS, SEARCH, CMP, UDOC, UOP, Spec, allowed, mod_sets, rev_line
from gen_treap_more import slots_line
from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
MARK = "with composable aggregates (2N iterative)"
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
VALUE_FROM = ["sm", "mn", "mx", "pre", "suf", "best", "xr", "an", "orr", "fv", "g", "a00"]  # a leaf field holding v
SIMPLE = {"rangeSum": ("sm", "S", "0", "res += {}"), "rangeMin": ("mn", "T", None, "min"), "rangeMax": ("mx", "T", None, "max"),
          "rangeXorQuery": ("xr", "T", "0", "res ^= {}"), "rangeAndQuery": ("an", "T", "-1", "res &= {}"),
          "rangeOrQuery": ("orr", "T", "0", "res |= {}")}
_ = OK  # (the compatibility table lives in gen_treap_algebra)


class SegSpec(Spec):
    def __init__(self, mods, fam, ups):
        super().__init__(mods, fam, ups, False, False)
        m = set(mods)
        self.ops = sorted(set(POINT + ["getAll"] + [UOP[x] for x in self.ups] + [q for mod in mods for q in QOPS[mod]] +
                              [op for op, (_, c) in SEARCH.items() if ("max" if c.startswith("G") else "min") in m]))
        self.lazy = bool(self.ups)
        fl = [f[0] for f in self.fields()]
        self.vf = next((f for f in VALUE_FROM if f in fl and not (f == "g" and self.gdiff)), None)  # None: decode the hash
        tn = [t[0] for t in self.tags()]
        # which internal functions need the node's level s (its length 1 << s)
        self.kAsg = self.asgTag and bool({"sm", "pre", "suf", "best", "xr", "pr", "a00", "fh"} & set(fl))
        self.kAdd = self.addTag and bool({"sm", "fh"} & set(fl))
        self.kAP = self.ap
        self.kXor = self.xorf
        self.kPush = self.kAsg or self.kAdd or self.kAP or self.kXor
        self.kPull = self.has("hash") or self.has("run") or self.kPush
        self.tn = tn

    def fields(self):
        return [f for f in super().fields() if f[0] not in ("pw", "gs")]

    def tags(self):
        return [t for t in super().tags() if t[0] != "rev"]

    def name(self):
        mods = "-".join(self.mods) or "plain"
        ups = "-".join(sorted(self.ups))
        return ("lazy-seg-" if self.lazy else "seg-") + mods + (f"-updates-{ups}" if ups else "")

    def cls(self):
        return "LazySegTree" if self.lazy else "SegTree"


def variants():
    out, have = [], set()
    for mods, only in mod_sets():
        if not mods:
            continue  # (tag-only trees: the hand-written ones)
        for fam, ups in allowed(mods):
            if only and only != (fam, ups):
                continue
            key = (mods, tuple(sorted(ups)))
            if key not in have:
                have.add(key)
                out.append(SegSpec(mods, fam, ups))
    return out


# ================================================================================================ shared text

def cost(s, op):
    g = s.has("gcd")
    if op == "getAll":
        return "N"
    if g and op == "rangeGcd":
        return "log(N)+log(U) ?"
    if g and (op in UOP.values() or op in POINT) and op != "pointGet":
        return "log(N)*log(U) ?"
    return "log(N)"


def header(cm, s):
    fields, tags = s.fields(), s.tags()
    lines = [f"@operations: {' '.join(s.ops)}", f"@data-structure-type: {'lazy-seg-tree' if s.lazy else 'seg-tree'}", "@complexities:"]
    lines += [f"  {op}: {cost(s, op)}" for op in s.ops] + [f"  build: {'N*log(U) ?' if s.has('gcd') else 'N'}", "@memory:",
                                                          "  layout: 2n-iterative"]
    other = (["PW[1*log(N)]"] + (["GS[1*log(N)]"] if s.G else [])) if s.has("hash") else []
    lines += ["  node: " + " ".join(f"{f[0]}[2*N]" for f in fields), "  tags: " + (" ".join(f"{t[0]}[1*N]" for t in tags) or "none"),
              "  other: " + (" ".join(other) or "none"),
              "  note: leaves [n, 2n) hold each value's own aggregates" + ("; tags live on the N internal nodes only" if tags else "") +
              ("; hash powers are per level (a covering node of level s has 2^s leaves)" if other else "")]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def describe(s):
    from gen_treap_algebra import DESC
    keeps = ", ".join(DESC[m] for m in s.mods)
    ups = ", ".join(UOP[u] for u in sorted(s.ups))
    return ((f"Lazy segment tree {MARK}: range updates ({ups})" if s.lazy else f"Segment tree {MARK}: point updates") +
            f" and range queries in O(logN); each node keeps {keeps} over its range. All indices 0-based, ranges inclusive "
            "[l, r]; searches return -1 when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a "
            "perfect subtree of 2^s leaves (s = its level)" +
            (", and every internal node holds its pending tags (\"applied here, not yet to my children\"): an update pushes "
             "the tags on its two boundary leaf paths, tags the covering nodes, then rebuilds both paths, each node redoing "
             "its own pending tag" + ("; a pending add or xor folds into a pending assign" if s.asgTag and (s.addTag or s.xorf) else "") +
             ("; a pending arithmetic add sits after a pending assign" if s.asgTag and s.ap else "") + "." if s.tags() else
             "; an update rewrites a leaf, then its ancestors."))


def leaf_py(s):
    """{field: Python expr of the leaf value for v}"""
    e = {"sm": "v", "mn": "v", "mx": "v", "fh": "(v + _HO) % _HP", "bh": "(v + _HO) % _HP", "pre": "v", "suf": "v", "best": "v",
         "xr": "v", "an": "v", "orr": "v", "g": "0" if s.gdiff else "v", "fv": "v", "lv": "v", "pr": "1", "sr": "1", "br": "1",
         "a00": "v", "a01": "NEG", "a10": "NEG", "a11": "-v"}
    return [(f[0], e[f[0]]) for f in s.fields()]


def leaf_cpp(s):
    e = {"sm": "S(v)", "mn": "v", "mx": "v", "fh": "hval(v)", "bh": "hval(v)", "pre": "S(v)", "suf": "S(v)", "best": "S(v)",
         "xr": "v", "an": "v", "orr": "v", "g": "T(0)" if s.gdiff else "v", "fv": "v", "lv": "v", "pr": "1", "sr": "1", "br": "1",
         "a00": "S(v)", "a01": "NEG", "a10": "NEG", "a11": "-S(v)"}
    return [(f[0], e[f[0]]) for f in s.fields()]


def clampf(tn, e):
    return ("min(H, " if "hi" in tn else "") + ("max(Lo, " if "lo" in tn else "") + e + (" + C" if "c" in tn else "") + \
        (")" if "lo" in tn else "") + (")" if "hi" in tn else "")


def bitsf(tn, e):
    return ("(" if "tO" in tn else "") + e + (" & A" if "tA" in tn else "") + (") | O" if "tO" in tn else "")


# ================================================================================================ Python

def py(s):
    F, TG = s.fields(), s.tags()
    fl, tn = [f[0] for f in F], s.tn
    names = ["n", "h"] + fl + [t[0] for t in TG] + (["PW"] if s.has("hash") else []) + (["GS"] if s.G else [])
    out = [header("#", s), "\n", wrap(describe(s), "#")]
    imports = (["import random"] if s.has("hash") else []) + (["from math import gcd"] if s.has("gcd") else [])
    out.append("\n".join(imports) + ("\n\n\n" if imports else "\n"))
    if s.has("hash"):
        out.append(PY_HASH_CONST)
    if s.clamp or s.has("alt") or s.has("min") or s.has("max"):
        out.append('INF, NEG = float("inf"), float("-inf")\n\n\n')
    if s.has("alt"):
        out.append('''def _altJoin(A, B):  # A's part, then B's: (++, +-, -+, --) = best by (start sign, end sign)
    a0, a1, a2, a3 = A
    b0, b1, b2, b3 = B
    return (max(a0, b0, a0 + b2, a1 + b0), max(a1, b1, a0 + b3, a1 + b1),
            max(a2, b2, a2 + b2, a3 + b0), max(a3, b3, a2 + b3, a3 + b1))


''')
    out.append(f"class {s.cls()}:\n" + slots_line(names) + "\n")
    init = ["    # O(N" + (" log U" if s.has("gcd") else "") + ") -- arr: the initial array (non-empty)", "    def __init__(self, arr):",
            "        n = self.n = len(arr)", "        self.h = n.bit_length()"]
    for f, e in leaf_py(s):
        init.append(f"        self.{f} = [0] * n + " + ("list(arr)" if e == "v" else f"[{e}] * n" if "v" not in e else f"[{e} for v in arr]"))
    for t in TG:
        init.append(f"        self.{t[0]} = [{t[2]}] * n")
    if s.has("hash"):
        init += ["        pw = self.PW = [_HB]  # PW[s] = B^(2^s): the hash power of a level-s node",
                 "        while len(pw) <= self.h:", "            pw.append(pw[-1] * pw[-1] % _HP)"]
        if s.G:
            init += ["        gs = self.GS = [1]  # GS[s] = 1 + B + ... + B^(2^s - 1): what a level-s node of all 1s hashes to",
                     "        for k in range(self.h):", "            gs.append((gs[k] * pw[k] + gs[k]) % _HP)"]
    init.append("        for x in range(n - 1, 0, -1):")
    if s.kPull:
        init += ["            s, y = 0, x", "            while y < n:  # (x's level: down its left edge to the leaves)", "                y <<= 1",
                 "                s += 1", "            self._pull(x, s)"]
    else:
        init.append("            self._pull(x)")
    out.append("\n".join(init) + "\n\n")
    pub = py_public(s)
    out.append("\n".join(pub[op] for op in s.ops if op in pub))
    out.append(py_internals(s))
    return "".join(out)


def py_public(s):
    pub = {}
    P = "        self._pushPath(l + n)\n        self._pushPath(r + n)\n" if s.tags() else ""
    for op, (f, typ, ident, comb) in SIMPLE.items():
        if op not in s.ops:
            continue
        if comb in ("min", "max"):
            c = "<" if comb == "min" else ">"
            acc = f'''            if lo & 1:
                if {f}[lo] {c} res:
                    res = {f}[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                if {f}[hi] {c} res:
                    res = {f}[hi]'''
            ident = "INF" if comb == "min" else "NEG"
        else:
            acc = f'''            if lo & 1:
                {comb.format(f"{f}[lo]")}
                lo += 1
            if hi & 1:
                hi -= 1
                {comb.format(f"{f}[hi]")}'''
        pub[op] = f'''    # O(logN) -- {QDOC[op]}
    def {op}(self, l, r):
        n, {f} = self.n, self.{f}
{P}        res, lo, hi = {ident}, l + n, r + n + 1
        while lo < hi:
{acc}
            lo >>= 1
            hi >>= 1
        return res
'''
    if "rangeGcd" in s.ops:
        if s.gdiff:
            pub["rangeGcd"] = f'''    # O(logN + logU) -- {QDOC["rangeGcd"]}
    def rangeGcd(self, l, r):
        g, fv, lv = self.g, self.fv, self.lv
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, last = gcd(fv[t], g[t]), lv[t]  # the first value, then every adjacent difference
        for t, _ in ns[1:]:
            res = gcd(gcd(res, fv[t] - last), g[t])
            last = lv[t]
        return res
'''
        else:
            pub["rangeGcd"] = f'''    # O(logN + logU) -- {QDOC["rangeGcd"]}
    def rangeGcd(self, l, r):
        n, g = self.n, self.g
{P}        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res = gcd(res, g[lo])
                lo += 1
            if hi & 1:
                hi -= 1
                res = gcd(res, g[hi])
            lo >>= 1
            hi >>= 1
        return res
'''
    if "maxPrefixSum" in s.ops:
        pub["maxPrefixSum"] = f'''    # O(logN) -- {QDOC["maxPrefixSum"]}
    def maxPrefixSum(self, l, r):
        sm, pre = self.sm, self.pre
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, acc = pre[t], sm[t]
        for t, _ in ns[1:]:
            if acc + pre[t] > res:
                res = acc + pre[t]
            acc += sm[t]
        return res
'''
    if "maxSuffixSum" in s.ops:
        pub["maxSuffixSum"] = f'''    # O(logN) -- {QDOC["maxSuffixSum"]}
    def maxSuffixSum(self, l, r):
        sm, suf = self.sm, self.suf
        ns = self._nodes(l, r)
        t = ns[-1][0]
        res, acc = suf[t], sm[t]
        for t, _ in reversed(ns[:-1]):
            if acc + suf[t] > res:
                res = acc + suf[t]
            acc += sm[t]
        return res
'''
    if "maxSubarraySum" in s.ops:
        pub["maxSubarraySum"] = f'''    # O(logN) -- {QDOC["maxSubarraySum"]}
    def maxSubarraySum(self, l, r):
        sm, pre, suf, best = self.sm, self.pre, self.suf, self.best
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, q = best[t], suf[t]  # (q: the best sum ending at the right edge so far)
        for t, _ in ns[1:]:
            res = max(res, best[t], q + pre[t])
            q = max(suf[t], sm[t] + q)
        return res
'''
    if s.has("hash"):
        pub["rangeHash"] = f'''    # O(logN) -- {QDOC["rangeHash"]}
    def rangeHash(self, l, r):
        fh, pw, P, res = self.fh, self.PW, _HP, 0
        for t, s in self._nodes(l, r):
            res = (res * pw[s] + fh[t]) % P
        return res
'''
        pub["rangeHashReversed"] = f'''    # O(logN) -- {QDOC["rangeHashReversed"]}
    def rangeHashReversed(self, l, r):
        bh, pw, P, res, p = self.bh, self.PW, _HP, 0, 1
        for t, s in self._nodes(l, r):  # (each node read backwards goes in front of what came before it)
            res = (bh[t] * p + res) % P
            p = p * pw[s] % P
        return res
'''
        pub["isPalindrome"] = f'''    # O(logN) -- {QDOC["isPalindrome"]}
    def isPalindrome(self, l, r):
        fh, bh, pw, P, f, b, p = self.fh, self.bh, self.PW, _HP, 0, 0, 1
        for t, s in self._nodes(l, r):
            f = (f * pw[s] + fh[t]) % P
            b = (bh[t] * p + b) % P
            p = p * pw[s] % P
        return f == b
'''
        pub["rangesEqual"] = f'''    # O(logN) -- {QDOC["rangesEqual"]}
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)
'''
    if s.has("run"):
        pub["longestEqualRun"] = f'''    # O(logN) -- {QDOC["longestEqualRun"]}
    def longestEqualRun(self, l, r):
        pr, sr, br, fv, lv = self.pr, self.sr, self.br, self.fv, self.lv
        ns = self._nodes(l, r)
        t, s = ns[0]
        p, q, res, k, last = pr[t], sr[t], br[t], 1 << s, lv[t]  # (prefix run, suffix run, best, length, last value)
        for t, s in ns[1:]:
            j = last == fv[t]
            if j and q + pr[t] > res:
                res = q + pr[t]
            if br[t] > res:
                res = br[t]
            if j and p == k:
                p += pr[t]
            q = q + sr[t] if j and sr[t] == 1 << s else sr[t]
            k += 1 << s
            last = lv[t]
        return res
'''
    if s.has("alt"):
        pub["maxAltSubseqSum"] = f'''    # O(logN) -- {QDOC["maxAltSubseqSum"]}
    def maxAltSubseqSum(self, l, r):
        a00, a01, a10, a11 = self.a00, self.a01, self.a10, self.a11
        ns = self._nodes(l, r)
        t = ns[0][0]
        c = (a00[t], a01[t], a10[t], a11[t])
        for t, _ in ns[1:]:
            c = _altJoin(c, (a00[t], a01[t], a10[t], a11[t]))
        return max(c[0], c[1])
'''
    psh = "                self._push(t, s)\n                s -= 1\n" if s.tags() and s.kPush else \
        "                self._push(t)\n" if s.tags() else ""
    for op, (side, cmp) in SEARCH.items():
        if op not in s.ops:
            continue
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        first, second, it = ("2 * t", "2 * t + 1", "self._nodes(l, r)") if side == "leftmost" else ("2 * t + 1", "2 * t", "reversed(self._nodes(l, r))")
        pub[op] = f'''    # O(logN) -- the {"first" if side == "leftmost" else "last"} i in [l, r] with a[i] {o} x, or -1 (a walk pruned by the node {"max" if f == "mx" else "min"})
    def {op}(self, l, r, x):
        n, F = self.n, self.{f}
        for t, s in {it}:
            if F[t] {o} x:  # the {"first" if side == "leftmost" else "last"} covering node with a passing value: walk down it
                while t < n:
{psh}                    t = {first} if F[{first}] {o} x else {second}
                return t - n
        return -1
'''
    for op, field, strict in (("leftmostPrefixSumGteX", "pre", False), ("leftmostPrefixSumGtX", "pre", True),
                              ("rightmostSuffixSumGteX", "suf", False), ("rightmostSuffixSumGtX", "suf", True)):
        if op not in s.ops:
            continue
        o = ">" if strict else ">="
        if field == "pre":
            doc = f"first i in [l, r] with a[l] + ... + a[i] {o} x, or -1 (a walk pruned by best prefix sums)"
            first, second, it = "2 * t", "2 * t + 1", "self._nodes(l, r)"
        else:
            doc = f"last i in [l, r] with a[i] + ... + a[r] {o} x, or -1 (a walk pruned by best suffix sums)"
            first, second, it = "2 * t + 1", "2 * t", "reversed(self._nodes(l, r))"
        pub[op] = f'''    # O(logN) -- {doc}
    def {op}(self, l, r, x):
        n, sm, P = self.n, self.sm, self.{field}
        acc = 0
        for t, s in {it}:
            if acc + P[t] {o} x:
                while t < n:
{psh}                    if acc + P[{first}] {o} x:
                        t = {first}
                    else:
                        acc += sm[{first}]
                        t = {second}
                return t - n
            acc += sm[t]
        return -1
'''
    tn = s.tn
    if s.lazy:
        calls = {"assign": ("v", ("_applyAssign", "v") if s.asgTag else ("_applyClamp", clamp_args(tn, "v", "v", "0")) if s.clamp
                            else ("_applyBits", bits_args(tn, "0", "v"))),
                 "add": ("v", ("_applyAP", "v, 0") if s.ap else ("_applyAdd", "v") if s.addTag else ("_applyClamp", clamp_args(tn, "INF", "NEG", "v"))),
                 "ap": ("start, step", ("_applyAP", "start + step * ((@ << s) - n - l), step")),
                 "chmin": ("v", ("_applyClamp", clamp_args(tn, "v", "NEG", "0"))),
                 "chmax": ("v", ("_applyClamp", clamp_args(tn, "INF", "v", "0"))),
                 "and": ("v", ("_applyBits", bits_args(tn, "v", "0"))),
                 "or": ("v", ("_applyBits", bits_args(tn, "-1", "v"))),
                 "xor": ("v", ("_applyXor", "v"))}
        for u in s.ups:
            args, (fn, a) = calls[u]
            ks = takes_s(s, fn)
            call = f"self.{fn}(@, s, {a})" if ks else f"self.{fn}(@, {a})"
            pub[UOP[u]] = f'''    # O(logN{" * logU" if s.has("gcd") else ""}) -- {UDOC[u]}
    def {UOP[u]}(self, l, r, {args}):
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi{", s" if ks else ""} = l + n, r + n + 1{", 0" if ks else ""}
        while lo < hi:
            if lo & 1:
                {call.replace("@", "lo")}
                lo += 1
            if hi & 1:
                hi -= 1
                {call.replace("@", "hi")}
            lo >>= 1
            hi >>= 1''' + ("\n            s += 1" if ks else "") + '''
        self._rebuild(l + n)
        self._rebuild(r + n)
'''
    pp = "        self._pushPath(p)\n" if s.tags() else ""
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "self._leaf(p) + v", "a[i] += v"),
                          ("pointChmax", "max(self._leaf(p), v)", "a[i] = max(a[i], v)"),
                          ("pointChmin", "min(self._leaf(p), v)", "a[i] = min(a[i], v)")):
        pub[op] = f'''    # O(logN{" * logU" if s.has("gcd") else ""}) -- {doc}
    def {op}(self, i, v):
        p = i + self.n
{pp}        self._setLeaf(p, {expr})
        self._rebuild(p)
'''
    pub["pointGet"] = f'''    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.n
{pp}        return self._leaf(p)
'''
    if s.tags():
        lvl = '''            s, y = 0, x
            while y < n:
                y <<= 1
                s += 1
            self._push(x, s)
''' if s.kPush else "            self._push(x)\n"
        pub["getAll"] = f'''    # O(N) -- the whole array, every pending tag pushed down on the way
    def getAll(self):
        n = self.n
        for x in range(1, n):  # (parents before children)
{lvl}        return [self._leaf(p) for p in range(n, 2 * n)]
'''
    else:
        pub["getAll"] = '''    # O(N) -- the whole array
    def getAll(self):
        return [self._leaf(p) for p in range(self.n, 2 * self.n)]
''' if s.vf is None else f'''    # O(N) -- the whole array
    def getAll(self):
        return self.{s.vf}[self.n:]
'''
    return pub


def clamp_args(tn, hi, lo, c):
    return ", ".join(v for n, v in (("hi", hi), ("lo", lo), ("c", c)) if n in tn)


def bits_args(tn, A, O):
    return ", ".join(v for n, v in (("tA", A), ("tO", O)) if n in tn)


def takes_s(s, fn):
    return {"_applyAssign": s.kAsg, "_setAssign": s.kAsg, "_applyAdd": s.kAdd, "_setAdd": s.kAdd, "_applyAP": True, "_setAP": True,
            "_applyXor": True, "_setXor": True}.get(fn, False)


def py_pull(s):
    fl = [f[0] for f in s.fields()]
    L = ["        a, b = 2 * x, 2 * x + 1"]
    if "sm" in fl:
        if s.ms:
            L.append("        sm = self.sm")
            if "pre" in fl:
                L.append("        self.pre[x] = max(self.pre[a], sm[a] + self.pre[b])")
            if "suf" in fl:
                L.append("        self.suf[x] = max(self.suf[b], sm[b] + self.suf[a])")
            if "best" in fl:
                L.append("        self.best[x] = max(self.best[a], self.best[b], self.suf[a] + self.pre[b])")
            L.append("        sm[x] = sm[a] + sm[b]")
        else:
            L.append("        self.sm[x] = self.sm[a] + self.sm[b]")
    for f, c in (("mn", "<"), ("mx", ">")):
        if f in fl:
            L += [f"        u, w = self.{f}[a], self.{f}[b]", f"        self.{f}[x] = u if u {c} w else w"]
    if "fh" in fl:  # concatenation: H(X + Y) = H(X) * B^|Y| + H(Y); the backward hash reads right to left
        L += ["        k = self.PW[s - 1]", "        self.fh[x] = (self.fh[a] * k + self.fh[b]) % _HP",
              "        self.bh[x] = (self.bh[b] * k + self.bh[a]) % _HP"]
    if "xr" in fl:
        L.append("        self.xr[x] = self.xr[a] ^ self.xr[b]")
    if "an" in fl:
        L.append("        self.an[x] = self.an[a] & self.an[b]")
    if "orr" in fl:
        L.append("        self.orr[x] = self.orr[a] | self.orr[b]")
    if "g" in fl:
        L.append("        self.g[x] = gcd(gcd(self.g[a], self.g[b]), self.fv[b] - self.lv[a])  # (the adjacent differences)" if s.gdiff
                 else "        self.g[x] = gcd(self.g[a], self.g[b])")
    if "pr" in fl:  # (prefix run, suffix run, best run) of two halves of 2^(s-1) values each
        L += ["        h, j = 1 << (s - 1), self.lv[a] == self.fv[b]", "        pa, sb = self.pr[a], self.sr[b]",
              "        self.br[x] = max(self.br[a], self.br[b], self.sr[a] + self.pr[b] if j else 0)",
              "        self.pr[x] = pa + self.pr[b] if j and pa == h else pa", "        self.sr[x] = sb + self.sr[a] if j and sb == h else sb"]
    if s.ends:
        L += ["        self.fv[x] = self.fv[a]", "        self.lv[x] = self.lv[b]"]
    if "a00" in fl:
        L.append("        self.a00[x], self.a01[x], self.a10[x], self.a11[x] = _altJoin((self.a00[a], self.a01[a], self.a10[a], "
                 "self.a11[a]),\n" + " " * 70 + "(self.a00[b], self.a01[b], self.a10[b], self.a11[b]))")
    tn = s.tn
    re_ = []  # redo x's own pending tags on top
    if s.asgTag:
        re_ += ["        if self.hasAsg[x]:", "            " + call_py(s, "_setAssign", "self.asg[x]")]
        if s.addTag:
            re_ += ["        elif self.add[x]:", "            " + call_py(s, "_setAdd", "self.add[x]")]
    elif s.addTag:
        re_ += ["        if self.add[x]:", "            " + call_py(s, "_setAdd", "self.add[x]")]
    if s.ap:
        re_ += ["        if self.as_[x] or self.ad[x]:", "            " + call_py(s, "_setAP", "self.as_[x], self.ad[x]")]
    if s.clamp:
        tp = [p for p in ("hi", "lo", "c") if p in tn]
        re_ += ["        if " + " or ".join({"hi": "self.hi[x] != INF", "lo": "self.lo[x] != NEG", "c": "self.c[x]"}[p] for p in tp) + ":",
                "            self._setClamp(x, " + ", ".join(f"self.{p}[x]" for p in tp) + ")"]
    if s.bits:
        tp = [p for p in ("tA", "tO") if p in tn]
        re_ += ["        if " + " or ".join({"tA": "self.tA[x] != -1", "tO": "self.tO[x]"}[p] for p in tp) + ":",
                "            self._setBits(x, " + ", ".join(f"self.{p}[x]" for p in tp) + ")"]
    # (a pending xor changes nothing above the leaves: every internal node has an even length)
    return L + re_


def call_py(s, fn, args):
    return f"self.{fn}(x, s, {args})" if takes_s(s, fn) else f"self.{fn}(x, {args})"


def py_internals(s):
    fl, tn = [f[0] for f in s.fields()], s.tn
    out = ["\n    # ---- internals ----\n"]
    out.append("\n    def _setLeaf(self, p, v):  # leaf p holds v alone\n" + "".join(f"        self.{f}[p] = {e}\n" for f, e in leaf_py(s)))
    if s.vf:
        out.append(f"\n    def _leaf(self, p):  # the value at leaf p\n        return self.{s.vf}[p]\n")
    else:
        out.append('''
    def _leaf(self, p):  # the value at leaf p, read back from its hash v + _HO
        w = (self.fh[p] - _HO) % _HP
        return w - _HP if w > _HP // 2 else w
''')
    sig = "x, s" if s.kPull else "x"
    out.append(f"\n    def _pull(self, {sig}):  # recompute node x{' (level s)' if s.kPull else ''} from its children" +
               (", then redo its own pending tags" if s.tags() else "") + "\n" + "".join(y + "\n" for y in py_pull(s)))
    rs = "        s = 0\n" if s.kPull else ""
    out.append(f'''
    def _rebuild(self, p):  # recompute every ancestor of leaf p
{rs}        while p > 1:
            p >>= 1
''' + ("            s += 1\n            self._pull(p, s)\n" if s.kPull else "            self._pull(p)\n"))
    out.append('''
    def _nodes(self, l, r):  # the O(logN) nodes covering a[l..r], left to right, each with its level
        n = self.n
''' + ("        self._pushPath(l + n)\n        self._pushPath(r + n)\n" if s.tags() else "") + '''        lo, hi, s, left, right = l + n, r + n + 1, 0, [], []
        while lo < hi:
            if lo & 1:
                left.append((lo, s))
                lo += 1
            if hi & 1:
                hi -= 1
                right.append((hi, s))
            lo >>= 1
            hi >>= 1
            s += 1
        return left + right[::-1]
''')
    if not s.tags():
        return "".join(out)
    push = []
    ksig = lambda fn: "x, s, " if takes_s(s, fn) else "x, "  # noqa: E731
    ch = lambda fn, args: (f"            self.{fn}(a, c, {args})\n            self.{fn}(b, c, {args})\n" if takes_s(s, fn)  # noqa: E731
                           else f"            self.{fn}(a, {args})\n            self.{fn}(b, {args})\n")
    if s.asgTag:
        a = (["        k = 1 << s"] if {"sm", "pre", "suf", "best", "xr", "pr", "a00"} & set(fl) else [])
        if "sm" in fl:
            a.append("        self.sm[x] = v * k")
        for f in ("mn", "mx", "an", "orr"):
            if f in fl:
                a.append(f"        self.{f}[x] = v")
        if "fh" in fl:
            a.append("        self.fh[x] = self.bh[x] = (v + _HO) % _HP * self.GS[s] % _HP")
        ms = [f for f in ("pre", "suf", "best") if f in fl]
        if ms:
            a.append("        " + " = ".join(f"self.{f}[x]" for f in ms) + " = v * k if v > 0 else v")
        if "xr" in fl:
            a.append("        self.xr[x] = v if k & 1 else 0")
        if "g" in fl:
            a.append("        self.g[x] = 0" if s.gdiff else "        self.g[x] = v  # (read through a gcd: |v|)")
        if s.ends:
            a.append("        self.fv[x] = self.lv[x] = v")
        if "pr" in fl:
            a.append("        self.pr[x] = self.sr[x] = self.br[x] = k")
        if "a00" in fl:
            a += ["        self.a00[x], self.a11[x] = v, -v", "        self.a01[x] = self.a10[x] = 0 if k > 1 else NEG"]
        out.append(f"\n    def _setAssign(self, {ksig('_setAssign')}v):  # every value under node x becomes v\n" + "".join(y + "\n" for y in a))
        t = ["            self.asg[x], self.hasAsg[x] = v, 1"] + (["            self.add[x] = 0"] if s.addTag else []) + \
            (["            self.as_[x] = self.ad[x] = 0"] if s.ap else []) + (["            self.tx[x] = 0"] if s.xorf else [])
        out.append(f"\n    def _applyAssign(self, {ksig('_applyAssign')}v):\n        {call_py(s, '_setAssign', 'v')}\n        if x < self.n:\n" +
                   "".join(y + "\n" for y in t))
        push.append("        if self.hasAsg[x]:\n            v = self.asg[x]\n" + ch("_applyAssign", "v") + "            self.hasAsg[x] = 0\n")
    if s.addTag:
        a = []
        if "sm" in fl:
            a.append("        self.sm[x] += v << s")
        for f in ("mn", "mx"):
            if f in fl:
                a.append(f"        self.{f}[x] += v")
        if "fh" in fl:
            a += ["        h = v % _HP * self.GS[s] % _HP", "        self.fh[x] = (self.fh[x] + h) % _HP", "        self.bh[x] = (self.bh[x] + h) % _HP"]
        if s.ends:
            a += ["        self.fv[x] += v", "        self.lv[x] += v"]
        out.append(f"\n    def _setAdd(self, {ksig('_setAdd')}v):  # every value under node x gains v\n" + "".join(y + "\n" for y in a))
        t = (["            if self.hasAsg[x]:", "                self.asg[x] += v  # (still an assign, of a shifted value)", "            else:",
              "                self.add[x] += v"] if s.asgTag else ["            self.add[x] += v"])
        out.append(f"\n    def _applyAdd(self, {ksig('_applyAdd')}v):\n        {call_py(s, '_setAdd', 'v')}\n        if x < self.n:\n" +
                   "".join(y + "\n" for y in t))
        push.append("        if self.add[x]:\n            v = self.add[x]\n" + ch("_applyAdd", "v") + "            self.add[x] = 0\n")
    if s.ap:
        out.append('''
    def _setAP(self, x, s, st, d):  # the k-th value under node x (k from 0) gains st + k * d
        k = 1 << s
        self.sm[x] += st * k + d * (k * (k - 1) // 2)

    def _applyAP(self, x, s, st, d):
        self._setAP(x, s, st, d)
        if x < self.n:
            self.as_[x] += st
            self.ad[x] += d
''')
        push.append('''        if self.as_[x] or self.ad[x]:
            st, d = self.as_[x], self.ad[x]
            self._applyAP(a, c, st, d)
            self._applyAP(b, c, st + d * (1 << c), d)
            self.as_[x] = self.ad[x] = 0
''')
    if s.clamp:
        params = [{"hi": "H", "lo": "Lo", "c": "C"}[p] for p in ("hi", "lo", "c") if p in tn]
        a = [f"        self.{g}[x] = {clampf(tn, f'self.{g}[x]')}" for g in ("mn", "mx") if g in fl]
        out.append(f"\n    def _setClamp(self, x, {', '.join(params)}):  # every value v under node x becomes {clampf(tn, 'v')}\n" +
                   "".join(y + "\n" for y in a))
        # compose (the old map, then this one): hi' = H(old hi), lo' = min(lo pushed through, hi'), c' = old c + C
        c = []
        if "hi" in tn:
            c.append("            h = min(H, " + ("max(Lo, " if "lo" in tn else "") + "self.hi[x]" + (" + C" if "c" in tn else "") +
                     (")" if "lo" in tn else "") + ")")
        if "lo" in tn:
            c.append("            self.lo[x] = " + ("min(" if "hi" in tn else "") + "max(Lo, self.lo[x]" + (" + C" if "c" in tn else "") + ")" +
                     (", h)" if "hi" in tn else ""))
        if "hi" in tn:
            c.append("            self.hi[x] = h")
        if "c" in tn:
            c.append("            self.c[x] += C")
        out.append(f"\n    def _applyClamp(self, x, {', '.join(params)}):\n        self._setClamp(x, {', '.join(params)})\n        if x < self.n:\n" +
                   "".join(y + "\n" for y in c))
        tp = [p for p in ("hi", "lo", "c") if p in tn]
        cond = " or ".join({"hi": "self.hi[x] != INF", "lo": "self.lo[x] != NEG", "c": "self.c[x]"}[p] for p in tp)
        args = ", ".join(f"self.{p}[x]" for p in tp)
        reset = ", ".join(f"self.{p}[x]" for p in tp) + " = " + ", ".join({"hi": "INF", "lo": "NEG", "c": "0"}[p] for p in tp)
        push.append(f"        if {cond}:\n            self._applyClamp(a, {args})\n            self._applyClamp(b, {args})\n            {reset}\n")
    if s.bits:
        TA, TO = "tA" in tn, "tO" in tn
        params = ", ".join((["A"] if TA else []) + (["O"] if TO else []))
        a = [f"        self.{g}[x] = {bitsf(tn, f'self.{g}[x]')}" for g in ("an", "orr") if g in fl]
        out.append(f"\n    def _setBits(self, x, {params}):  # every value v under node x becomes {bitsf(tn, 'v')}\n" + "".join(y + "\n" for y in a))
        c = (["            self.tA[x] &= A"] if TA else []) + ([f"            self.tO[x] = {bitsf(tn, 'self.tO[x]')}"] if TO else [])
        out.append(f"\n    def _applyBits(self, x, {params}):\n        self._setBits(x, {params})\n        if x < self.n:\n" + "".join(y + "\n" for y in c))
        cond = " or ".join((["self.tA[x] != -1"] if TA else []) + (["self.tO[x]"] if TO else []))
        args = ", ".join((["self.tA[x]"] if TA else []) + (["self.tO[x]"] if TO else []))
        reset = ", ".join((["self.tA[x]"] if TA else []) + (["self.tO[x]"] if TO else [])) + " = " + ", ".join((["-1"] if TA else []) + (["0"] if TO else []))
        push.append(f"        if {cond}:\n            self._applyBits(a, {args})\n            self._applyBits(b, {args})\n            {reset}\n")
    if s.xorf:
        out.append('''
    def _setXor(self, x, s, v):  # every value under node x is xored with v (an even count leaves the xor alone)
        if s == 0:
            self.xr[x] ^= v

    def _applyXor(self, x, s, v):
        self._setXor(x, s, v)
        if x < self.n:
''' + ("            if self.hasAsg[x]:\n                self.asg[x] ^= v\n            else:\n                self.tx[x] ^= v\n" if s.asgTag
       else "            self.tx[x] ^= v\n"))
        push.append("        if self.tx[x]:\n            v = self.tx[x]\n" + ch("_applyXor", "v") + "            self.tx[x] = 0\n")
    out.append(f"\n    def _push(self, x{', s' if s.kPush else ''}):  # hand node x's pending tags to its children\n        a, b = 2 * x, 2 * x + 1\n" +
               ("        c = s - 1  # (their level)\n" if s.kPush else "") + "".join(push))
    out.append(f'''
    def _pushPath(self, p):  # hand down every pending tag on the path from the root to leaf p
        for s in range(self.h, 0, -1):
            self._push(p >> s{", s" if s.kPush else ""})
''')
    return "".join(out)


# ================================================================================================ C++

def cpp(s):
    F, TG = s.fields(), s.tags()
    fl, tn = [f[0] for f in F], s.tn
    S_ = s.has("sum") or bool(s.ms) or s.has("alt")
    C = s.cls()
    out = [header("//", s), "\n", wrap(describe(s), "//"),
           "// T: int, long long, ..." + ("; sums are kept in S (long long for small T)." if S_ else ""), f"\ntemplate <typename T>\nstruct {C} {{\n"]
    if S_:
        out.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n")
    if s.has("hash"):
        out.append("    using U64 = unsigned long long;\n")
    if s.clamp:
        out.append("    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();\n")
    if s.has("alt"):
        out.append("    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)\n")
    out.append("    int n, h;\n")
    for f in F:
        out.append(f"    vector<{f[1]}> {f[0]};\n")
    for t in TG:
        out.append(f"    vector<{t[1]}> {t[0]};\n")
    if s.has("hash"):
        out.append("    vector<U64> PW" + (", GS" if s.G else "") + ";  // PW[s] = B^(2^s)" +
                   (", GS[s] = 1 + B + ... + B^(2^s - 1)" if s.G else "") + ": per level\n")
        out.append('''
    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
''' + CPP_HASH_HELPERS.replace(
            "    static unsigned long long hadd(unsigned long long a, unsigned long long b) { return a + b >= HP ? a + b - HP : a + b; }",
            "    static unsigned long long hadd(unsigned long long a, unsigned long long b) {\n        return a + b >= HP ? a + b - HP : a + b;\n    }"))
    init = [f"    // O(N{' log U' if s.has('gcd') else ''}) -- arr: the initial array (non-empty)",
            f"    explicit {C}(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {{"]
    for f, e in leaf_cpp(s):
        ident = next(x[3] for x in F if x[0] == f)
        init.append(f"        {f}.assign(2 * n, {ident});")
    for t in TG:
        init.append(f"        {t[0]}.assign(n, {t[3]});")
    lp = leaf_cpp(s)
    init.append("        for (int i = 0; i < n; i++) setLeaf(n + i, arr[i]);" if len(lp) > 1 or lp[0][1] != "v" else
                f"        for (int i = 0; i < n; i++) {lp[0][0]}[n + i] = arr[i];")
    if s.has("hash"):
        init += ["        PW.assign(1, HB());", "        while ((int)PW.size() <= h) PW.push_back(hmul(PW.back(), PW.back()));"]
        if s.G:
            init += ["        GS.assign(1, 1);", "        for (int k = 0; k < h; k++) GS.push_back(hadd(hmul(GS[k], PW[k]), GS[k]));"]
    if s.kPull:
        init += ["        for (int x = n - 1; x > 0; x--) {", "            int s = 0;",
                 "            for (int y = x; y < n; y <<= 1) s++;  // (x's level: down its left edge to the leaves)", "            pull(x, s);",
                 "        }"]
    else:
        init.append("        for (int x = n - 1; x > 0; x--) pull(x);")
    out.append("\n" if s.has("hash") else "")
    out.append("\n".join(init) + "\n    }\n\n")
    pub = cpp_public(s)
    out.append("\n".join(pub[op] for op in s.ops if op in pub))
    out.append(cpp_internals(s))
    out.append("};\n")
    return "".join(out)


def cpp_public(s):
    pub = {}
    P = "        pushPath(l + n), pushPath(r + n);\n" if s.tags() else ""
    for op, (f, typ, ident, comb) in SIMPLE.items():
        if op not in s.ops:
            continue
        if comb in ("min", "max"):
            ident = "numeric_limits<T>::max()" if comb == "min" else "numeric_limits<T>::lowest()"
            lo, hi = f"res = {comb}(res, {f}[lo++])", f"res = {comb}(res, {f}[--hi])"
        else:
            ident = {"0": f"{typ}(0)", "-1": "~T(0)"}[ident]
            lo, hi = comb.format(f"{f}[lo++]"), comb.format(f"{f}[--hi]")
        pub[op] = f'''    // O(logN) -- {QDOC[op]}
    {typ} {op}(int l, int r) {{
{P}        {typ} res = {ident};
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {{
            if (lo & 1) {lo};
            if (hi & 1) {hi};
        }}
        return res;
    }}
'''
    cov = "        int ns[64], ls[64], c = cover(l, r, ns, ls);\n"
    if "rangeGcd" in s.ops:
        if s.gdiff:
            pub["rangeGcd"] = f'''    // O(logN + logU) -- {QDOC["rangeGcd"]}
    T rangeGcd(int l, int r) {{
{cov}        T res = gcd(fv[ns[0]], g[ns[0]]), last = lv[ns[0]];  // the first value, then every adjacent difference
        for (int i = 1; i < c; i++) res = gcd(gcd(res, T(fv[ns[i]] - last)), g[ns[i]]), last = lv[ns[i]];
        return res;
    }}
'''
        else:
            pub["rangeGcd"] = f'''    // O(logN + logU) -- {QDOC["rangeGcd"]}
    T rangeGcd(int l, int r) {{
{P}        T res = T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {{
            if (lo & 1) res = gcd(res, g[lo++]);
            if (hi & 1) res = gcd(res, g[--hi]);
        }}
        return res;
    }}
'''
    if "maxPrefixSum" in s.ops:
        pub["maxPrefixSum"] = f'''    // O(logN) -- {QDOC["maxPrefixSum"]}
    S maxPrefixSum(int l, int r) {{
{cov}        S res = pre[ns[0]], acc = sm[ns[0]];
        for (int i = 1; i < c; i++) res = max(res, acc + pre[ns[i]]), acc += sm[ns[i]];
        return res;
    }}
'''
    if "maxSuffixSum" in s.ops:
        pub["maxSuffixSum"] = f'''    // O(logN) -- {QDOC["maxSuffixSum"]}
    S maxSuffixSum(int l, int r) {{
{cov}        S res = suf[ns[c - 1]], acc = sm[ns[c - 1]];
        for (int i = c - 2; i >= 0; i--) res = max(res, acc + suf[ns[i]]), acc += sm[ns[i]];
        return res;
    }}
'''
    if "maxSubarraySum" in s.ops:
        pub["maxSubarraySum"] = f'''    // O(logN) -- {QDOC["maxSubarraySum"]}
    S maxSubarraySum(int l, int r) {{
{cov}        S res = best[ns[0]], q = suf[ns[0]];  // (q: the best sum ending at the right edge so far)
        for (int i = 1; i < c; i++) {{
            int t = ns[i];
            res = max({{res, best[t], q + pre[t]}}), q = max(suf[t], sm[t] + q);
        }}
        return res;
    }}
'''
    if s.has("hash"):
        pub["rangeHash"] = f'''    // O(logN) -- {QDOC["rangeHash"]}
    U64 rangeHash(int l, int r) {{
{cov}        U64 res = 0;
        for (int i = 0; i < c; i++) res = hadd(hmul(res, PW[ls[i]]), fh[ns[i]]);
        return res;
    }}
'''
        pub["rangeHashReversed"] = f'''    // O(logN) -- {QDOC["rangeHashReversed"]}
    U64 rangeHashReversed(int l, int r) {{
{cov}        U64 res = 0, p = 1;
        for (int i = 0; i < c; i++) res = hadd(hmul(bh[ns[i]], p), res), p = hmul(p, PW[ls[i]]);  // (each node in front)
        return res;
    }}
'''
        pub["isPalindrome"] = f'''    // O(logN) -- {QDOC["isPalindrome"]}
    bool isPalindrome(int l, int r) {{
{cov}        U64 f = 0, b = 0, p = 1;
        for (int i = 0; i < c; i++) f = hadd(hmul(f, PW[ls[i]]), fh[ns[i]]), b = hadd(hmul(bh[ns[i]], p), b), p = hmul(p, PW[ls[i]]);
        return f == b;
    }}
'''
        pub["rangesEqual"] = f'''    // O(logN) -- {QDOC["rangesEqual"]}
    bool rangesEqual(int l1, int r1, int l2, int r2) {{
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }}
'''
    if s.has("run"):
        pub["longestEqualRun"] = f'''    // O(logN) -- {QDOC["longestEqualRun"]}
    int longestEqualRun(int l, int r) {{
{cov}        int t = ns[0], p = pr[t], q = sr[t], res = br[t], k = 1 << ls[0];  // (prefix run, suffix run, best, length)
        T last = lv[t];
        for (int i = 1; i < c; i++) {{
            t = ns[i];
            int w = 1 << ls[i];
            bool j = last == fv[t];
            res = max({{res, br[t], j ? q + pr[t] : 0}});
            if (j && p == k) p += pr[t];
            q = j && sr[t] == w ? q + sr[t] : sr[t];
            k += w, last = lv[t];
        }}
        return res;
    }}
'''
    if s.has("alt"):
        pub["maxAltSubseqSum"] = f'''    // O(logN) -- {QDOC["maxAltSubseqSum"]}
    S maxAltSubseqSum(int l, int r) {{
{cov}        array<S, 4> a{{a00[ns[0]], a01[ns[0]], a10[ns[0]], a11[ns[0]]}};
        for (int i = 1; i < c; i++) a = altJoin(a, {{a00[ns[i]], a01[ns[i]], a10[ns[i]], a11[ns[i]]}});
        return max(a[0], a[1]);
    }}
'''
    psh = "push(t, s--), " if s.tags() and s.kPush else "push(t), " if s.tags() else ""
    for op, (side, cmp) in SEARCH.items():
        if op not in s.ops:
            continue
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        first, second = ("2 * t", "2 * t + 1") if side == "leftmost" else ("2 * t + 1", "2 * t")
        loop = "for (int i = 0; i < c; i++) {" if side == "leftmost" else "for (int i = c - 1; i >= 0; i--) {"
        pub[op] = f'''    // O(logN) -- the {"first" if side == "leftmost" else "last"} i in [l, r] with a[i] {o} x, or -1 (a walk pruned by the node {"max" if f == "mx" else "min"})
    int {op}(int l, int r, T x) {{
{cov}        {loop}
            int t = ns[i]{", s = ls[i]" if psh.startswith("push(t, s") else ""};
            if (!({f}[t] {o} x)) continue;
            while (t < n) {psh}t = {f}[{first}] {o} x ? {first} : {second};  // walk down the passing node
            return t - n;
        }}
        return -1;
    }}
'''
    for op, field, strict in (("leftmostPrefixSumGteX", "pre", False), ("leftmostPrefixSumGtX", "pre", True),
                              ("rightmostSuffixSumGteX", "suf", False), ("rightmostSuffixSumGtX", "suf", True)):
        if op not in s.ops:
            continue
        o = ">" if strict else ">="
        if field == "pre":
            doc = f"first i in [l, r] with a[l] + ... + a[i] {o} x, or -1 (a walk pruned by best prefix sums)"
            first, second, loop = "2 * t", "2 * t + 1", "for (int i = 0; i < c; i++) {"
        else:
            doc = f"last i in [l, r] with a[i] + ... + a[r] {o} x, or -1 (a walk pruned by best suffix sums)"
            first, second, loop = "2 * t + 1", "2 * t", "for (int i = c - 1; i >= 0; i--) {"
        pline = " " * 20 + psh[:-2] + ";\n" if psh else ""
        pub[op] = f'''    // O(logN) -- {doc}
    int {op}(int l, int r, T x) {{
{cov}        S acc = 0;
        {loop}
            int t = ns[i]{", s = ls[i]" if psh.startswith("push(t, s") else ""};
            if (acc + {field}[t] {o} S(x)) {{
                while (t < n) {{
{pline}                    if (acc + {field}[{first}] {o} S(x)) t = {first};
                    else acc += sm[{first}], t = {second};
                }}
                return t - n;
            }}
            acc += sm[t];
        }}
        return -1;
    }}
'''
    tn = s.tn
    if s.lazy:
        calls = {"assign": ("T v", ("applyAssign", "v") if s.asgTag else ("applyClamp", clamp_args(tn, "v", "v", "T(0)")) if s.clamp
                            else ("applyBits", bits_args(tn, "T(0)", "v"))),
                 "add": ("T v", ("applyAP", "v, T(0)") if s.ap else ("applyAdd", "v") if s.addTag else ("applyClamp", clamp_args(tn, "INF", "NEG", "v"))),
                 "ap": ("T start, T step", ("applyAP", "start + step * T((X << s) - n - l), step")),
                 "chmin": ("T v", ("applyClamp", clamp_args(tn, "v", "NEG", "T(0)"))),
                 "chmax": ("T v", ("applyClamp", clamp_args(tn, "INF", "v", "T(0)"))),
                 "and": ("T v", ("applyBits", bits_args(tn, "v", "T(0)"))),
                 "or": ("T v", ("applyBits", bits_args(tn, "~T(0)", "v"))),
                 "xor": ("T v", ("applyXor", "v"))}
        for u in s.ups:
            params, (fn, a) = calls[u]
            ks = takes_s(s, "_" + fn)
            cl = lambda X, inc: f"{fn}({X}, s, {a.replace('X', X)})" if ks else f"{fn}({X}, {a})"  # noqa: E731
            pub[UOP[u]] = f'''    // O(logN{" * logU" if s.has("gcd") else ""}) -- {UDOC[u]}
    void {UOP[u]}(int l, int r, {params}) {{
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1{", s = 0" if ks else ""}; lo < hi; lo >>= 1, hi >>= 1{", s++" if ks else ""}) {{
            if (lo & 1) {cl("lo", True)}, lo++;
            if (hi & 1) hi--, {cl("hi", False)};
        }}
        rebuild(l + n), rebuild(r + n);
    }}
'''
    pp = "        pushPath(p);\n" if s.tags() else ""
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "T(leaf(p) + v)", "a[i] += v"),
                          ("pointChmax", "max(leaf(p), v)", "a[i] = max(a[i], v)"), ("pointChmin", "min(leaf(p), v)", "a[i] = min(a[i], v)")):
        pub[op] = f'''    // O(logN{" * logU" if s.has("gcd") else ""}) -- {doc}
    void {op}(int i, T v) {{
        int p = i + n;
{pp}        setLeaf(p, {expr}), rebuild(p);
    }}
'''
    pub["pointGet"] = f'''    // O(logN) -- a[i]
    T pointGet(int i) {{
        int p = i + n;
{pp}        return leaf(p);
    }}
'''
    if s.tags():
        lvl = '''        for (int x = 1; x < n; x++) {  // (parents before children)
            int s = 0;
            for (int y = x; y < n; y <<= 1) s++;
            push(x, s);
        }
''' if s.kPush else "        for (int x = 1; x < n; x++) push(x);  // (parents before children)\n"
        pub["getAll"] = f'''    // O(N) -- the whole array, every pending tag pushed down on the way
    vector<T> getAll() {{
{lvl}        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }}
'''
    else:
        pub["getAll"] = '''    // O(N) -- the whole array
    vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }
'''
    return pub


def call_cpp(s, fn, args):
    return f"{fn}(x, s, {args})" if takes_s(s, "_" + fn) else f"{fn}(x, {args})"


def cpp_pull(s):
    fl = [f[0] for f in s.fields()]
    L = ["        int a = 2 * x, b = 2 * x + 1;"]
    if "pre" in fl:
        L.append("        pre[x] = max(pre[a], sm[a] + pre[b]);")
    if "suf" in fl:
        L.append("        suf[x] = max(suf[b], sm[b] + suf[a]);")
    if "best" in fl:
        L.append("        best[x] = max({best[a], best[b], suf[a] + pre[b]});")
    if "sm" in fl:
        L.append("        sm[x] = sm[a] + sm[b];")
    if "mn" in fl:
        L.append("        mn[x] = min(mn[a], mn[b]);")
    if "mx" in fl:
        L.append("        mx[x] = max(mx[a], mx[b]);")
    if "fh" in fl:  # concatenation: H(X + Y) = H(X) * B^|Y| + H(Y); the backward hash reads right to left
        L += ["        fh[x] = hadd(hmul(fh[a], PW[s - 1]), fh[b]), bh[x] = hadd(hmul(bh[b], PW[s - 1]), bh[a]);"]
    if "xr" in fl:
        L.append("        xr[x] = xr[a] ^ xr[b];")
    if "an" in fl:
        L.append("        an[x] = an[a] & an[b];")
    if "orr" in fl:
        L.append("        orr[x] = orr[a] | orr[b];")
    if "g" in fl:
        L.append("        g[x] = gcd(gcd(g[a], g[b]), T(fv[b] - lv[a]));  // (the adjacent differences)" if s.gdiff else "        g[x] = gcd(g[a], g[b]);")
    if "pr" in fl:  # (prefix run, suffix run, best run) of two halves of 2^(s-1) values each
        L += ["        int hl = 1 << (s - 1);", "        bool j = lv[a] == fv[b];", "        br[x] = max({br[a], br[b], j ? sr[a] + pr[b] : 0});",
              "        pr[x] = j && pr[a] == hl ? pr[a] + pr[b] : pr[a];", "        sr[x] = j && sr[b] == hl ? sr[b] + sr[a] : sr[b];"]
    if s.ends:
        L.append("        fv[x] = fv[a], lv[x] = lv[b];")
    if "a00" in fl:
        L += ["        array<S, 4> c = altJoin({a00[a], a01[a], a10[a], a11[a]}, {a00[b], a01[b], a10[b], a11[b]});",
              "        a00[x] = c[0], a01[x] = c[1], a10[x] = c[2], a11[x] = c[3];"]
    tn = s.tn
    if s.asgTag:
        L.append("        if (hasAsg[x]) " + call_cpp(s, "setAssign", "asg[x]") + ";")
        if s.addTag:
            L.append("        else if (add[x] != T(0)) " + call_cpp(s, "setAdd", "add[x]") + ";")
    elif s.addTag:
        L.append("        if (add[x] != T(0)) " + call_cpp(s, "setAdd", "add[x]") + ";")
    if s.ap:
        L.append("        if (as_[x] != T(0) || ad[x] != T(0)) setAP(x, s, as_[x], ad[x]);")
    if s.clamp:
        tp = [p for p in ("hi", "lo", "c") if p in tn]
        L.append("        if (" + " || ".join({"hi": "hi[x] != INF", "lo": "lo[x] != NEG", "c": "c[x] != T(0)"}[p] for p in tp) + ") setClamp(x, " +
                 ", ".join(f"{p}[x]" for p in tp) + ");")
    if s.bits:
        tp = [p for p in ("tA", "tO") if p in tn]
        L.append("        if (" + " || ".join({"tA": "tA[x] != ~T(0)", "tO": "tO[x] != T(0)"}[p] for p in tp) + ") setBits(x, " +
                 ", ".join(f"{p}[x]" for p in tp) + ");")
    return L


def cpp_internals(s):
    fl, tn = [f[0] for f in s.fields()], s.tn
    out = ["\n    // ---- internals ----\n"]
    if "a00" in fl:
        out.append('''
    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
    }
''')
    out.append("\n    void setLeaf(int p, T v) {  // leaf p holds v alone\n        " +
               rev_line([f"{f}[p] = {e}" for f, e in leaf_cpp(s)]) + "\n    }\n")
    if s.vf:
        out.append(f"\n    T leaf(int p) const {{ return T({s.vf}[p]); }}  // the value at leaf p\n")
    else:
        out.append('''
    T leaf(int p) const {  // the value at leaf p, read back from its hash v + offset
        U64 w = hadd(fh[p], HP - hval(T(0)));
        return w > HP / 2 ? T((long long)w - (long long)HP) : T(w);
    }
''')
    sig = "int x, int s" if s.kPull else "int x"
    out.append(f"\n    void pull({sig}) {{  // recompute node x{' (level s)' if s.kPull else ''} from its children" +
               (", then redo its own pending tags" if s.tags() else "") + "\n" + "".join(y + "\n" for y in cpp_pull(s)) + "    }\n")
    out.append("\n    void rebuild(int p) {  // recompute every ancestor of leaf p\n" +
               ("        for (int s = 1; p > 1; s++) p >>= 1, pull(p, s);\n" if s.kPull else "        while (p > 1) p >>= 1, pull(p);\n") + "    }\n")
    out.append('''
    int cover(int l, int r, int* ns, int* ls) {  // the nodes covering a[l..r] left to right (ns) and their levels (ls)
''' + ("        pushPath(l + n), pushPath(r + n);\n" if s.tags() else "") + '''        int c = 0, rc = 0, rn[32], rl[32];
        for (int lo = l + n, hi = r + n + 1, s = 0; lo < hi; lo >>= 1, hi >>= 1, s++) {
            if (lo & 1) ns[c] = lo++, ls[c++] = s;
            if (hi & 1) rn[rc] = --hi, rl[rc++] = s;
        }
        while (rc) rc--, ns[c] = rn[rc], ls[c++] = rl[rc];
        return c;
    }
''')
    if not s.tags():
        return "".join(out)
    push = []
    ks = lambda fn: "int x, int s, " if takes_s(s, "_" + fn) else "int x, "  # noqa: E731
    ch = lambda fn, args: (f"{fn}(a, c, {args}), {fn}(b, c, {args})" if takes_s(s, "_" + fn) else f"{fn}(a, {args}), {fn}(b, {args})")  # noqa: E731
    if s.asgTag:
        a = (["int k = 1 << s;"] if {"sm", "pre", "suf", "best", "xr", "pr", "a00"} & set(fl) else [])
        if "sm" in fl:
            a.append("sm[x] = S(v) * k;")
        for f in ("mn", "mx", "an", "orr"):
            if f in fl:
                a.append(f"{f}[x] = v;")
        if "fh" in fl:
            a.append("fh[x] = bh[x] = hmul(hval(v), GS[s]);")
        ms = [f for f in ("pre", "suf", "best") if f in fl]
        if ms:
            a.append(" = ".join(f"{f}[x]" for f in ms) + " = v > T(0) ? S(v) * k : S(v);")
        if "xr" in fl:
            a.append("xr[x] = k & 1 ? v : T(0);")
        if "g" in fl:
            a.append("g[x] = T(0);" if s.gdiff else "g[x] = v;  // (read through a gcd: |v|)")
        if s.ends:
            a.append("fv[x] = lv[x] = v;")
        if "pr" in fl:
            a.append("pr[x] = sr[x] = br[x] = k;")
        if "a00" in fl:
            a.append("a00[x] = S(v), a11[x] = -S(v), a01[x] = a10[x] = k > 1 ? S(0) : NEG;")
        out.append(f"\n    void setAssign({ks('setAssign')}T v) {{  // every value under node x becomes v\n" + "".join(f"        {y}\n" for y in a) + "    }\n")
        t = ["asg[x] = v, hasAsg[x] = 1"] + (["add[x] = T(0)"] if s.addTag else []) + (["as_[x] = ad[x] = T(0)"] if s.ap else []) + \
            (["tx[x] = T(0)"] if s.xorf else [])
        out.append(f"\n    void applyAssign({ks('applyAssign')}T v) {{\n        {call_cpp(s, 'setAssign', 'v')};\n        if (x < n) {', '.join(t)};\n    }}\n")
        push.append(f"        if (hasAsg[x]) {ch('applyAssign', 'asg[x]')}, hasAsg[x] = 0;\n")
    if s.addTag:
        a = []
        if "sm" in fl:
            a.append("sm[x] += S(v) * (S(1) << s);")
        for f in ("mn", "mx"):
            if f in fl:
                a.append(f"{f}[x] += v;")
        if "fh" in fl:
            a += ["U64 hh = hmul(hraw(v), GS[s]);", "fh[x] = hadd(fh[x], hh), bh[x] = hadd(bh[x], hh);"]
        if s.ends:
            a.append("fv[x] += v, lv[x] += v;")
        out.append(f"\n    void setAdd({ks('setAdd')}T v) {{  // every value under node x gains v\n" + "".join(f"        {y}\n" for y in a) + "    }\n")
        t = ("if (x < n) {\n            if (hasAsg[x]) asg[x] += v;  // (still an assign, of a shifted value)\n            else add[x] += v;\n        }"
             if s.asgTag else "if (x < n) add[x] += v;")
        out.append(f"\n    void applyAdd({ks('applyAdd')}T v) {{\n        {call_cpp(s, 'setAdd', 'v')};\n        {t}\n    }}\n")
        push.append(f"        if (add[x] != T(0)) {ch('applyAdd', 'add[x]')}, add[x] = T(0);\n")
    if s.ap:
        out.append('''
    void setAP(int x, int s, T st, T d) {  // the k-th value under node x (k from 0) gains st + k * d
        S k = S(1) << s;
        sm[x] += S(st) * k + S(d) * (k * (k - 1) / 2);
    }

    void applyAP(int x, int s, T st, T d) {
        setAP(x, s, st, d);
        if (x < n) as_[x] += st, ad[x] += d;
    }
''')
        push.append('''        if (as_[x] != T(0) || ad[x] != T(0)) {
            applyAP(a, c, as_[x], ad[x]), applyAP(b, c, T(as_[x] + ad[x] * T(1 << c)), ad[x]);
            as_[x] = ad[x] = T(0);
        }
''')
    if s.clamp:
        params = [{"hi": "H", "lo": "Lo", "c": "C"}[p] for p in ("hi", "lo", "c") if p in tn]
        sig = ", ".join(f"T {p}" for p in params)
        a = [f"{g}[x] = {clampf(tn, f'{g}[x]')};" for g in ("mn", "mx") if g in fl]
        out.append(f"\n    void setClamp(int x, {sig}) {{  // every value v under node x becomes {clampf(tn, 'v')}\n" +
                   "".join(f"        {y}\n" for y in a) + "    }\n")
        # compose (the old map, then this one): hi' = H(old hi), lo' = min(lo pushed through, hi'), c' = old c + C
        c = []
        if "hi" in tn:
            oh = "(hi[x] == INF ? INF : T(hi[x] + C))" if "c" in tn else "hi[x]"
            c.append("T hh = min(H, " + (f"max(Lo, {oh})" if "lo" in tn else oh) + ");")
        if "lo" in tn:
            lo_e = "max(Lo, lo[x] == NEG ? NEG : T(lo[x] + C))" if "c" in tn else "max(Lo, lo[x])"
            c.append(f"lo[x] = {'min(' + lo_e + ', hh)' if 'hi' in tn else lo_e};")
        if "hi" in tn:
            c.append("hi[x] = hh;")
        if "c" in tn:
            c.append("c[x] += C;")
        out.append(f"\n    void applyClamp(int x, {sig}) {{\n        setClamp(x, {', '.join(params)});\n        if (x >= n) return;\n" +
                   "".join(f"        {y}\n" for y in c) + "    }\n")
        tp = [p for p in ("hi", "lo", "c") if p in tn]
        cond = " || ".join({"hi": "hi[x] != INF", "lo": "lo[x] != NEG", "c": "c[x] != T(0)"}[p] for p in tp)
        args = ", ".join(f"{p}[x]" for p in tp)
        reset = ", ".join(f"{p}[x] = " + {"hi": "INF", "lo": "NEG", "c": "T(0)"}[p] for p in tp)
        push.append(f"        if ({cond}) {{\n            applyClamp(a, {args}), applyClamp(b, {args});\n            {reset};\n        }}\n")
    if s.bits:
        TA, TO = "tA" in tn, "tO" in tn
        params = (["A"] if TA else []) + (["O"] if TO else [])
        sig = ", ".join(f"T {p}" for p in params)
        a = [f"{g}[x] = {bitsf(tn, f'{g}[x]')};" for g in ("an", "orr") if g in fl]
        out.append(f"\n    void setBits(int x, {sig}) {{  // every value v under node x becomes {bitsf(tn, 'v')}\n" + "".join(f"        {y}\n" for y in a) + "    }\n")
        c = (["tA[x] &= A"] if TA else []) + ([f"tO[x] = {bitsf(tn, 'tO[x]')}"] if TO else [])
        out.append(f"\n    void applyBits(int x, {sig}) {{\n        setBits(x, {', '.join(params)});\n        if (x < n) {', '.join(c)};\n    }}\n")
        cond = " || ".join((["tA[x] != ~T(0)"] if TA else []) + (["tO[x] != T(0)"] if TO else []))
        args = ", ".join((["tA[x]"] if TA else []) + (["tO[x]"] if TO else []))
        reset = ", ".join((["tA[x] = ~T(0)"] if TA else []) + (["tO[x] = T(0)"] if TO else []))
        push.append(f"        if ({cond}) {{\n            applyBits(a, {args}), applyBits(b, {args});\n            {reset};\n        }}\n")
    if s.xorf:
        out.append('''
    void setXor(int x, int s, T v) {  // every value under node x is xored with v (an even count leaves the xor alone)
        if (s == 0) xr[x] ^= v;
    }

    void applyXor(int x, int s, T v) {
        setXor(x, s, v);
        if (x >= n) return;
        ''' + ("if (hasAsg[x]) asg[x] ^= v;\n        else tx[x] ^= v;" if s.asgTag else "tx[x] ^= v;") + '''
    }
''')
        push.append(f"        if (tx[x] != T(0)) {ch('applyXor', 'tx[x]')}, tx[x] = T(0);\n")
    out.append(f"\n    void push(int x{', int s' if s.kPush else ''}) {{  // hand node x's pending tags to its children\n        int a = 2 * x, b = 2 * x + 1"
               + (", c = s - 1;  // (their level)\n" if s.kPush else ";\n") + "".join(push) + "    }\n")
    out.append(f'''
    void pushPath(int p) {{  // hand down every pending tag on the path from the root to leaf p
        for (int s = h; s > 0; s--) push(p >> s{", s" if s.kPush else ""});
    }}
''')
    return "".join(out)


# ================================================================================================ main

def generated(text):
    return MARK in text


def main(only=None):
    if only is None:
        for d in os.listdir(DIR):
            t = os.path.join(DIR, d, "template.py")
            if os.path.exists(t) and generated(open(t).read()):
                shutil.rmtree(os.path.join(DIR, d))
    taken = set(os.listdir(DIR))  # hand-written folders: their op set stays theirs
    seen, skipped = {}, 0
    for s in variants():
        if only is not None and not only(s):
            continue
        name = folder_name(s.ops)
        if name in taken:
            skipped += 1
            continue
        folder = name if len(name) <= 180 else s.name()
        assert folder not in seen, (folder, seen.get(folder))
        seen[folder] = s.name()
        os.makedirs(os.path.join(DIR, folder), exist_ok=True)
        write_template(os.path.join(DIR, folder, "template.py"), py(s))
        write_template(os.path.join(DIR, folder, "template.cpp"), cpp(s))
    print("wrote", len(seen), "segment trees;", skipped, "op sets already had a hand-written template")


if __name__ == "__main__":
    main()
