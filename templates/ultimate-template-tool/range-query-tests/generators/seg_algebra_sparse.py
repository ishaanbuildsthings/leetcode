"""Sparse versions of gen_seg_algebra.py's trees: sparse.py + sparse.cpp, over any index range [lo, hi], every position
starting at 0 (called from gen_seg_algebra.main).

The root covers 2^D >= hi - lo + 1 positions from lo (the ones past hi are zeros nobody reads), so a node still covers
2^s positions at level s and the per-level hash tables, the in-order folds and every combine / tag function of the
dense tree carry over; only where nodes live changes. A node's children are created on demand, as blocks of zeros,
right before anything descends past it (queries push like the dense tree does, so they may create nodes too).
Updates recurse top-down instead of looping bottom-up, so a node's own pending tag never needs redoing on a pull: a
node is pushed before anything below it changes.
  Python: per-field lists that grow by one entry per node; L / R hold the children (0: none yet).
  C++:    the same as vectors the tree owns.
"""
import re

from gen_treap import CPP_HASH_HELPERS, PY_HASH_CONST, wrap
from gen_treap_algebra import PREFIX_SEARCHES, QDOC, SEARCH, CMP, UDOC, UOP, rev_line
from gen_treap_more import slots_line

SPARSE_NOTE = "built from nothing: every position of [lo, hi] starts at 0"
PY_TAKE = ["_setLeaf", "_leaf", "_pull", "_setAssign", "_applyAssign", "_setAdd", "_applyAdd", "_setAP", "_applyAP", "_setClamp",
           "_applyClamp", "_setBits", "_applyBits", "_setXor", "_applyXor", "_push"]
CPP_TAKE = ["setLeaf", "leaf", "pull", "setAssign", "applyAssign", "setAdd", "applyAdd", "setAP", "applyAP", "setClamp",
            "applyClamp", "setBits", "applyBits", "setXor", "applyXor", "push"]
FOLD_OPS = ["rangeGcd", "maxPrefixSum", "maxSuffixSum", "minPrefixSum", "minSuffixSum", "maxSubarraySum", "minSubarraySum",
            "rangeHash", "rangeHashReversed", "isPalindrome", "rangesEqual", "longestEqualRun", "maxAltSubseqSum"]


def fit_call(line, ind=8):
    """an update(..., lambda) call on one line, or with the lambda's body on a line of its own past 120 columns"""
    if ind + len(line) <= 120:
        return line
    head, body = line.split(" { ", 1)
    return head + " {\n" + " " * (ind + 4) + body[:-len(" });")] + "\n" + " " * ind + "});"


def sparse_cost(dense_cost):
    c = dense_cost.replace("log(N)+log(U)", "log(U)").replace("log(N)", "log(U)")
    return "1" if c in ("N", "N*log(U) ?") else c


def header(cm, s, dense_header):
    """the dense header with getAll gone, every N a U (the index range), build 1 and the per-update node memory"""
    lines = []
    for ln in dense_header.rstrip("\n").split("\n"):
        body = ln[len(cm) + 1:]
        if body.startswith("@operations:"):
            ln = f"{cm} @operations: " + " ".join(o for o in body.split()[1:] if o != "getAll")
        elif body.startswith("  getAll:"):
            continue
        elif body.startswith("  build:"):
            ln = f"{cm}   build: 1"
        elif body.startswith("  layout:"):
            ln = f"{cm}   layout: sparse"
        elif body.startswith("  node:") or body.startswith("  tags:"):
            ln = re.sub(r"\[\d\*N\]", "[4*log(U)]", ln)
        elif body.startswith("  other:"):
            other = [x for x in re.findall(r"\w+\[[^\]]*\]", body)]
            other = [re.sub(r"\[.*\]", "[1*log(U)]", x) for x in other] + ["children[8*log(U)]"]
            if s.has("hash") and not any(x.startswith("GS") for x in other):
                other.insert(1, "GS[1*log(U)]")
            ln = f"{cm}   other: " + " ".join(other)
        elif body.startswith("  note:"):
            ln = (f"{cm}   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates)" +
                  (", amortized for the shrink walks" if s.shrink else "") + "; node data per field, children L / R")
        elif re.match(r"  \w+: ", body):
            op, c = body.strip().split(": ", 1)
            ln = f"{cm}   {op}: {sparse_cost(c)}"
        lines.append(ln)
    return "\n".join(lines) + "\n"


def blocks(text, names, kind):
    """the methods named in names out of an emitted class body (each a blank-line-separated block)"""
    out = {}
    for b in text.split("\n\n"):
        m = re.search(r"^    def (\w+)\(" if kind == "py" else r"^    (?:static )?[\w<>, :]+? (\w+)\(", b, re.M)
        if m and m.group(1) in names:
            out[m.group(1)] = b.strip("\n")
    return out


def dedent_py_tag_blocks(b):
    """the dense tree's `if x < self.n:` (tags only on internal nodes) gone: every sparse node may hold tags"""
    lines, out, k = b.split("\n"), [], 0
    while k < len(lines):
        if lines[k] == "        if x < self.n:":
            k += 1
            while k < len(lines) and lines[k].startswith("            "):
                out.append(lines[k][4:])
                k += 1
            continue
        out.append(lines[k])
        k += 1
    return "\n".join(out)


def py_methods(s, dense_internals):
    got = blocks(dense_internals, PY_TAKE, "py")
    out = []
    for name in PY_TAKE:
        if name not in got:
            continue
        b = got[name].replace("a, b = 2 * x, 2 * x + 1", "a, b = self.L[x], self.R[x]")
        b = dedent_py_tag_blocks(b)
        if name == "_pull":  # (no own tag to redo: a node is pushed before anything below it changes)
            lines = b.split("\n")
            cut = next((i for i, ln in enumerate(lines) if re.match(r"        (el)?if self\.", ln)), len(lines))
            b = "\n".join(lines[:cut]).replace(", then redo its own pending tags", "")
        out.append(b)
    return out


def cpp_methods(s, dense_internals):
    got = blocks(dense_internals, CPP_TAKE, "cpp")
    out = []
    for name in CPP_TAKE:
        if name not in got:
            continue
        b = got[name].replace("int a = 2 * x, b = 2 * x + 1", "int a = L[x], b = R[x]")
        b = b.replace("        if (x < n) {\n            if (hasAsg[x]) asg[x] += v;  // (still an assign, of a shifted value)\n"
                      "            else add[x] += v;\n        }",
                      "        if (hasAsg[x]) asg[x] += v;  // (still an assign, of a shifted value)\n        else add[x] += v;")
        b = b.replace("if (x < n) ", "").replace("        if (x >= n) return;\n", "")
        if name == "pull":
            lines = b.split("\n")
            cut = next((i for i, ln in enumerate(lines) if re.match(r"        (else )?if \(", ln)), len(lines) - 1)
            b = "\n".join(lines[:cut] + ["    }"]).replace(", then redo its own pending tags", "")
        out.append(b)
    return out


def zero_py(s):
    """_newZero's appends: a block of 2^s zeros (assign 0 at level s)"""
    fl = [f[0] for f in s.fields()]
    z = {"sm": "0", "mn": "0", "mx": "0", "fh": "h", "bh": "h", "pre": "0", "suf": "0", "best": "0",
         "npre": "0", "nsuf": "0", "nbest": "0", "xr": "0", "an": "0",
         "orr": "0", "g": "0", "fv": "0", "lv": "0", "pr": "1 << s", "sr": "1 << s", "br": "1 << s", "a00": "0",
         "a01": "0 if s else NEG", "a10": "0 if s else NEG", "a11": "0"}
    L = (["        h = _HO * self.GS[s] % _HP  # (0 hashes as _HO)"] if "fh" in fl else [])
    L += ["        self.L.append(0)", "        self.R.append(0)"] + [f"        self.{f}.append({z[f]})" for f in fl]
    L += [f"        self.{t[0]}.append({t[2]})" for t in s.tags()]
    return L


def zero_cpp(s):
    fl = [f[0] for f in s.fields()]
    z = {"sm": "S(0)", "mn": "T(0)", "mx": "T(0)", "fh": "h", "bh": "h", "pre": "S(0)", "suf": "S(0)", "best": "S(0)",
         "npre": "S(0)", "nsuf": "S(0)", "nbest": "S(0)", "xr": "T(0)",
         "an": "T(0)", "orr": "T(0)", "g": "T(0)", "fv": "T(0)", "lv": "T(0)", "pr": "1 << s", "sr": "1 << s", "br": "1 << s",
         "a00": "S(0)", "a01": "s ? S(0) : NEG", "a10": "s ? S(0) : NEG", "a11": "S(0)"}
    parts = ["L.push_back(0)", "R.push_back(0)"] + [f"{f}.push_back({z[f]})" for f in fl] + [f"{t[0]}.push_back({t[3]})" for t in s.tags()]
    pre = ["        U64 h = hmul(hval(T(0)), GS[s]);"] if "fh" in fl else []
    return pre + ["        " + rev_line(parts)]


def describe(s, dense_desc):
    from gen_treap_algebra import DESC
    keeps = ", ".join(DESC[m] for m in s.mods)
    ups = ", ".join(UOP[u] for u in sorted(s.ups))
    kind = "Shrink segment tree" if s.shrink else "Lazy segment tree" if s.lazy else "Segment tree"
    return (f"{kind} with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every "
            "position starting at 0; " + (f"range updates ({ups})" if ups else "point updates") + " and range queries in "
            f"O(logU), U = hi - lo + 1; each node keeps {keeps} over its range. Ranges inclusive [l, r]; searches return "
            "lo - 1 when nothing qualifies. The root covers 2^D >= U positions from lo (the ones past hi are zeros nobody "
            "reads), so a node of level s covers 2^s positions; children are created on demand as blocks of zeros, right "
            "before anything descends past a node" + (", and a node's pending tags (\"applied here, not yet to my "
            "children\") go down as it is passed" if s.tags() else "") + (". mod / floor div / floor sqrt walk down every "
            "node whose max still changes" if s.shrink else "") + ".")


# ================================================================================================ Python

def py(s, dense_py, dense_internals, dense_desc):
    from gen_seg_algebra import py_public  # (the dense ops that fold the covering nodes in order work as they are)
    fl = [f[0] for f in s.fields()]
    TG = s.tags()
    cls = "Sparse" + s.cls()
    hdr = header("#", s, dense_py[:dense_py.index("\n\n")] + "\n")
    names = ["first", "last", "D", "L", "R"] + fl + [t[0] for t in TG] + (["PW", "GS"] if s.has("hash") else [])
    out = [hdr, "\n", wrap(describe(s, dense_desc), "#")]
    imports = (["import random"] if s.has("hash") else []) + (["from math import gcd"] if s.has("gcd") else []) + \
        (["from math import isqrt"] if s.shrink else [])
    out.append("\n".join(imports) + ("\n\n\n" if imports else "\n"))
    if s.has("hash"):
        out.append(PY_HASH_CONST)
    if s.clamp or s.has("alt") or s.has("min") or s.has("max"):
        out.append('INF, NEG = float("inf"), float("-inf")\n\n\n')
    if s.has("alt"):
        m = re.search(r"^def _altJoin.*?\n\n\n", dense_py, re.M | re.S)
        out.append(m.group(0))
    out.append(f"class {cls}:\n" + slots_line(names) + "\n")
    init = ["    # O(1) -- all zeros over [lo, hi]; any range of integers works (lo <= hi)", "    def __init__(self, lo, hi):",
            "        self.first, self.last = lo, hi  # (the index range: lo / hi are the clamp tags' names)",
            "        self.D = (hi - lo).bit_length()  # the root's level: 2^D >= hi - lo + 1",
            "        self.L, self.R = [0], [0]  # node 0: none (node 1 is the root)"]
    init += [f"        self.{f[0]} = [{f[2]}]" for f in s.fields()] + [f"        self.{t[0]} = [{t[2]}]" for t in TG]
    if s.has("hash"):
        init += ["        pw = self.PW = [_HB]  # PW[s] = B^(2^s), GS[s] = 1 + B + ... + B^(2^s - 1): per level", "        gs = self.GS = [1]",
                 "        for k in range(self.D):", "            gs.append((gs[k] * pw[k] + gs[k]) % _HP)", "            pw.append(pw[k] * pw[k] % _HP)"]
    init.append("        self._newZero(self.D)")
    out.append("\n".join(init) + "\n\n")
    pub = py_public(s)
    pub = {op: pub[op] for op in FOLD_OPS if op in pub}
    pub.update(py_sparse_public(s))
    out.append("\n".join(pub[op] for op in s.ops if op in pub))
    out.append("\n    # ---- internals ----\n\n")
    internals = [f'''    def _newZero(self, s):  # a new node: a block of 2^s zeros
''' + "\n".join(zero_py(s)) + "\n        return len(self.L) - 1", '''    def _kids(self, x, s):  # create node x's children (blocks of zeros) if it has none yet
        if not self.L[x]:
            a = self._newZero(s - 1)
            self.L[x], self.R[x] = a, self._newZero(s - 1)''', f'''    def _cover(self, l, r):  # the nodes covering a[l..r], left to right, as (node, level, first index)
        out = []
        self._collect(1, self.D, self.first, l, r, out)
        return out''', f'''    def _collect(self, x, s, tl, l, r, out):
        if l <= tl and tl + (1 << s) - 1 <= r:
            out.append((x, s, tl))
            return
        self._kids(x, s)
{push_py(s, "x")}        m = tl + (1 << (s - 1))
        if l < m:
            self._collect(self.L[x], s - 1, tl, l, r, out)
        if r >= m:
            self._collect(self.R[x], s - 1, m, l, r, out)''', '''    def _nodes(self, l, r):  # the covering nodes left to right, each with its level
        return [(x, s) for x, s, _ in self._cover(l, r)]''']
    if s.lazy:
        internals.append(f'''    def _update(self, x, s, tl, l, r, f):  # f(node, level, first index) on every node covering a[l..r], then pull up
        if l <= tl and tl + (1 << s) - 1 <= r:
            f(x, s, tl)
            return
        self._kids(x, s)
{push_py(s, "x")}        m = tl + (1 << (s - 1))
        if l < m:
            self._update(self.L[x], s - 1, tl, l, r, f)
        if r >= m:
            self._update(self.R[x], s - 1, m, l, r, f)
        {pull_py(s, "x", "s")}''')
    internals.append(f'''    def _leafOf(self, i):  # (the leaf holding a[i], the nodes above it top-down), every tag on the way pushed
        x, s, tl, path = 1, self.D, self.first, []
        while s:
            self._kids(x, s)
{push_py(s, "x", 12)}            path.append(x)
            s -= 1
            if i >= tl + (1 << s):
                tl += 1 << s
                x = self.R[x]
            else:
                x = self.L[x]
        return x, path''')
    internals.append(f'''    def _up(self, path):  # recompute the nodes of path, deepest first (path[k] has level D - k)
        for k in range(len(path) - 1, -1, -1):
            {pull_py(s, "path[k]", "self.D - k")}''')
    if s.shrink:
        asg = (f'''        if self.mn[x] == self.mx[x]:  # all equal: one assign
            self.{"_applyAssign(x, s, " if s.kAsg else "_applyAssign(x, "}f(self.mx[x]))
            return
''' if s.asgTag else "")
        internals.append(f'''    def _shrink(self, x, s, lim, f):  # every value v >= lim under node x (level s) becomes f(v) (the rest are fixed)
        if self.mx[x] < lim:
            return
        if s == 0:
            self._setLeaf(x, f(self.mx[x]))
            return
{asg}        self._kids(x, s)
{push_py(s, "x")}        self._shrink(self.L[x], s - 1, lim, f)
        self._shrink(self.R[x], s - 1, lim, f)
        {pull_py(s, "x", "s")}''')
    internals += py_methods(s, dense_internals)
    out.append("\n\n".join(internals) + "\n")
    return "".join(out).replace("self._setLeaf(p, ", "self._setLeaf(x, ")


def push_py(s, x, ind=8):
    if not s.tags():
        return ""
    return " " * ind + (f"self._push({x}, s)\n" if s.kPush else f"self._push({x})\n")


def pull_py(s, x, lvl):
    return f"self._pull({x}, {lvl})" if s.kPull else f"self._pull({x})"


def py_sparse_public(s):
    pub = {}
    for op, f, ident, comb in (("rangeSum", "sm", "0", "res += {}"), ("rangeXorQuery", "xr", "0", "res ^= {}"),
                               ("rangeAndQuery", "an", "-1", "res &= {}"), ("rangeOrQuery", "orr", "0", "res |= {}"),
                               ("rangeMin", "mn", "INF", "min"), ("rangeMax", "mx", "NEG", "max")):
        if op not in s.ops:
            continue
        if comb in ("min", "max"):
            c = "<" if comb == "min" else ">"
            body = f"            if {f}[t] {c} res:\n                res = {f}[t]"
        else:
            body = "            " + comb.format(f"{f}[t]")
        pub[op] = f'''    # O(logU) -- {QDOC[op]}
    def {op}(self, l, r):
        {f}, res = self.{f}, {ident}
        for t, _ in self._nodes(l, r):
{body}
        return res
'''
    if "rangeGcd" in s.ops and not s.gdiff:
        pub["rangeGcd"] = f'''    # O(logU + logU) -- {QDOC["rangeGcd"]}
    def rangeGcd(self, l, r):
        g, res = self.g, 0
        for t, _ in self._nodes(l, r):
            res = gcd(res, g[t])
        return res
'''
    psh = ("                    self._push(t, s)\n" if s.kPush else "                    self._push(t)\n") if s.tags() else ""
    for op, (side, cmp) in SEARCH.items():
        if op not in s.ops:
            continue
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        left = side == "leftmost"
        it = "self._cover(l, r)" if left else "reversed(self._cover(l, r))"
        step = ('''                    if F[L[t]] {o} x:
                        t = L[t]
                    else:
                        t, tl = R[t], tl + (1 << s)''' if left else '''                    if F[R[t]] {o} x:
                        t, tl = R[t], tl + (1 << s)
                    else:
                        t = L[t]''').format(o=o)
        pub[op] = f'''    # O(logU) -- the {"first" if left else "last"} i in [l, r] with a[i] {o} x, or lo - 1 (a walk pruned by the node {"max" if f == "mx" else "min"})
    def {op}(self, l, r, x):
        F, L, R = self.{f}, self.L, self.R
        for t, s, tl in {it}:
            if F[t] {o} x:  # the {"first" if left else "last"} covering node with a passing value: walk down it
                while s:
                    self._kids(t, s)
{psh}                    s -= 1
{step}
                return tl
        return self.first - 1
'''
    for op, field, strict in PREFIX_SEARCHES:
        if op not in s.ops:
            continue
        o = (">" if strict else ">=") if field in ("pre", "suf") else ("<" if strict else "<=")
        kind = "best" if field in ("pre", "suf") else "min"
        left = field in ("pre", "npre")
        doc = (f"first i in [l, r] with a[l] + ... + a[i] {o} x, or lo - 1 (a walk pruned by {kind} prefix sums)" if left else
               f"last i in [l, r] with a[i] + ... + a[r] {o} x, or lo - 1 (a walk pruned by {kind} suffix sums)")
        it = "self._cover(l, r)" if left else "reversed(self._cover(l, r))"
        near, far = ("L", "R") if left else ("R", "L")
        go_far = "t, tl = R[t], tl + (1 << s)" if left else "t = L[t]"
        go_near = "t = L[t]" if left else "t, tl = R[t], tl + (1 << s)"
        pub[op] = f'''    # O(logU) -- {doc}
    def {op}(self, l, r, x):
        sm, P, L, R = self.sm, self.{field}, self.L, self.R
        acc = 0
        for t, s, tl in {it}:
            if acc + P[t] {o} x:
                while s:
                    self._kids(t, s)
{psh}                    s -= 1
                    if acc + P[{near}[t]] {o} x:
                        {go_near}
                    else:
                        acc += sm[{near}[t]]
                        {go_far}
                return tl
            acc += sm[t]
        return self.first - 1
'''
    tn = s.tn
    if s.lazy:
        from gen_seg_algebra import clamp_args, bits_args, takes_s
        calls = {"assign": ("v", ("_applyAssign", "v") if s.asgTag else ("_applyClamp", clamp_args(tn, "v", "v", "0")) if s.clamp
                            else ("_applyBits", bits_args(tn, "0", "v"))),
                 "add": ("v", ("_applyAP", "v, 0") if s.ap else ("_applyAdd", "v") if s.addTag else ("_applyClamp", clamp_args(tn, "INF", "NEG", "v"))),
                 "ap": ("start, step", ("_applyAP", "start + step * (tl - l), step")),
                 "chmin": ("v", ("_applyClamp", clamp_args(tn, "v", "NEG", "0"))),
                 "chmax": ("v", ("_applyClamp", clamp_args(tn, "INF", "v", "0"))),
                 "and": ("v", ("_applyBits", bits_args(tn, "v", "0"))),
                 "or": ("v", ("_applyBits", bits_args(tn, "-1", "v"))),
                 "xor": ("v", ("_applyXor", "v"))}
        shr = {"mod": ("x", "x >= 1", "x", "lambda v: v % x", "logU * logU"),
               "div": ("x", "x >= 2", "1", "lambda v: v // x", "logU * logU"),
               "sqrt": ("", "", "2", "isqrt", "logU * loglogU")}
        for u in s.ups:
            if u in shr:
                args, cond, lim, f, c = shr[u]
                call = f"self._update(1, self.D, self.first, l, r, lambda t, s, tl: self._shrink(t, s, {lim}, {f}))"
                pub[UOP[u]] = f'''    # amortized O({c}) -- {UDOC[u]}
    def {UOP[u]}(self, l, r{", " + args if args else ""}):
''' + (f"        if {cond}:\n            {call}\n" if cond else f"        {call}\n")
                continue
            args, (fn, a) = calls[u]
            fcall = f"self.{fn}(t, s, {a})" if takes_s(s, fn) else f"self.{fn}(t, {a})"
            pub[UOP[u]] = f'''    # O(logU{" * logU" if s.has("gcd") else ""}) -- {UDOC[u]}
    def {UOP[u]}(self, l, r, {args}):
        self._update(1, self.D, self.first, l, r, lambda t, s, tl: {fcall})
'''
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "self._leaf(x) + v", "a[i] += v"),
                          ("pointChmax", "max(self._leaf(x), v)", "a[i] = max(a[i], v)"),
                          ("pointChmin", "min(self._leaf(x), v)", "a[i] = min(a[i], v)")):
        pub[op] = f'''    # O(logU{" * logU" if s.has("gcd") else ""}) -- {doc}
    def {op}(self, i, v):
        x, path = self._leafOf(i)
        self._setLeaf(x, {expr})
        self._up(path)
'''
    pub["pointGet"] = '''    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._leaf(self._leafOf(i)[0])
'''
    return pub


# ================================================================================================ C++

def cpp(s, dense_cpp, dense_internals, dense_desc):
    from gen_seg_algebra import cpp_public
    fl = [f[0] for f in s.fields()]
    TG = s.tags()
    cls = "Sparse" + s.cls()
    S_ = s.has("sum") or bool(s.ms) or s.has("alt")
    hdr = header("//", s, dense_cpp[:dense_cpp.index("\n\n")] + "\n")
    out = [hdr, "\n", wrap(describe(s, dense_desc), "//"),
           "// T: int, long long, ..." + ("; sums are kept in S (long long for small T)." if S_ else ""), f"\ntemplate <typename T>\nstruct {cls} {{\n"]
    if S_:
        out.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n")
    if s.has("hash"):
        out.append("    using U64 = unsigned long long;\n")
    if s.clamp:
        out.append("    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();\n")
    if s.has("alt"):
        out.append("    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)\n")
    out.append("    long long first, last;  // the index range [lo, hi]\n    int D;  // the root's level: 2^D >= hi - lo + 1\n    vector<int> L{0}, R{0};  // children (node 0: none; node 1 is the root)\n")
    for f in s.fields():  # (run lengths can pass 2^31 over a huge range)
        out.append(f"    vector<{'long long' if f[1] == 'int' else f[1]}> {f[0]}{{{f[3]}}};\n")
    for t in TG:
        out.append(f"    vector<{t[1]}> {t[0]}{{{t[3]}}};\n")
    if s.has("hash"):
        out.append("    vector<U64> PW, GS;  // PW[s] = B^(2^s), GS[s] = 1 + B + ... + B^(2^s - 1): per level\n")
        out.append('''
    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
''' + CPP_HASH_HELPERS.replace(
            "    static unsigned long long hadd(unsigned long long a, unsigned long long b) { return a + b >= HP ? a + b - HP : a + b; }",
            "    static unsigned long long hadd(unsigned long long a, unsigned long long b) {\n        return a + b >= HP ? a + b - HP : a + b;\n    }"))
    else:
        out.append("\n")
    init = ["    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)",
            f"    {cls}(long long lo, long long hi) : first(lo), last(hi), D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {{"]
    if s.has("hash"):
        init += ["        PW.assign(1, HB()), GS.assign(1, 1);",
                 "        for (int k = 0; k < D; k++) GS.push_back(hadd(hmul(GS[k], PW[k]), GS[k])), PW.push_back(hmul(PW[k], PW[k]));"]
    init += ["        newZero(D);", "    }"]
    out.append("\n".join(init) + "\n\n")
    pub = cpp_public(s)
    pub = {op: pub[op].replace("(int l, int r)", "(long long l, long long r)").replace("(int l1, int r1, int l2, int r2)",
                                                                                        "(long long l1, long long r1, long long l2, long long r2)")
           .replace("int ns[64]{}, ls[64]{}", "int ns[128]{}, ls[128]{}") for op in FOLD_OPS if op in pub}
    pub.update(cpp_sparse_public(s))
    out.append("\n".join(pub[op] for op in s.ops if op in pub))
    out.append("\n    // ---- internals ----\n\n")
    internals = []
    if "a00" in fl:
        m = re.search(r"    // A's part, then B's.*?\n    }\n", dense_internals, re.S)
        internals.append(m.group(0).rstrip("\n"))
    internals += ["    int newZero(int s) {  // a new node: a block of 2^s zeros\n" + "\n".join(zero_cpp(s)) + "\n        return (int)L.size() - 1;\n    }",
                  '''    void kids(int x, int s) {  // create node x's children (blocks of zeros) if it has none yet
        if (L[x]) return;
        int a = newZero(s - 1), b = newZero(s - 1);
        L[x] = a, R[x] = b;
    }''', f'''    // the nodes covering a[l..r] left to right: ns, their levels ls, their first indices ts
    int cover(long long l, long long r, int* ns, int* ls, long long* ts) {{
        int c = 0;
        collect(1, D, first, l, r, ns, ls, ts, c);
        return c;
    }}''', '''    int cover(long long l, long long r, int* ns, int* ls) {
        long long ts[128];
        return cover(l, r, ns, ls, ts);
    }''', f'''    void collect(int x, int s, long long tl, long long l, long long r, int* ns, int* ls, long long* ts, int& c) {{
        if (l <= tl && tl + (1LL << s) - 1 <= r) {{
            ns[c] = x, ls[c] = s, ts[c++] = tl;
            return;
        }}
        kids(x, s);
{push_cpp(s, "x")}        long long m = tl + (1LL << (s - 1));
        if (l < m) collect(L[x], s - 1, tl, l, r, ns, ls, ts, c);
        if (r >= m) collect(R[x], s - 1, m, l, r, ns, ls, ts, c);
    }}''']
    if s.lazy:
        internals.append(f'''    template <class F>  // f(node, level, first index) on every node covering a[l..r], then pull up
    void update(int x, int s, long long tl, long long l, long long r, const F& f) {{
        if (l <= tl && tl + (1LL << s) - 1 <= r) {{
            f(x, s, tl);
            return;
        }}
        kids(x, s);
{push_cpp(s, "x")}        long long m = tl + (1LL << (s - 1));
        if (l < m) update(L[x], s - 1, tl, l, r, f);
        if (r >= m) update(R[x], s - 1, m, l, r, f);
        {pull_cpp(s, "x", "s")};
    }}''')
    internals.append(f'''    int leafOf(long long i, int* path) {{  // the leaf holding a[i]; path: the nodes above it top-down, every tag pushed
        int x = 1;
        long long tl = first;
        for (int s = D; s > 0; s--) {{
            kids(x, s);
{push_cpp(s, "x", 12)}            path[D - s] = x;
            if (i >= tl + (1LL << (s - 1))) tl += 1LL << (s - 1), x = R[x];
            else x = L[x];
        }}
        return x;
    }}''')
    internals.append(f'''    void up(const int* path) {{  // recompute the nodes of path, deepest first (path[k] has level D - k)
        for (int k = D - 1; k >= 0; k--) {pull_cpp(s, "path[k]", "D - k")};
    }}''')
    if s.shrink:
        internals.append('''    // floor(sqrt(v)) for v >= 0, exact for every 64-bit value
    static T isqrtT(T v) {
        T r = (T)sqrtl((long double)v);
        while (r > 0 && (__int128)r * r > v) r--;
        while ((__int128)(r + 1) * (r + 1) <= v) r++;
        return r;
    }''')
        asg = (f"        if (mn[x] == mx[x]) {{ {'applyAssign(x, s, ' if s.kAsg else 'applyAssign(x, '}f(mx[x])); return; }}  // all equal: one assign\n"
               if s.asgTag else "")
        internals.append(f'''    template <class F>
    void shrink(int x, int s, T lim, const F& f) {{  // every value v >= lim under node x (level s) becomes f(v)
        if (mx[x] < lim) return;
        if (s == 0) {{ setLeaf(x, f(mx[x])); return; }}
{asg}        kids(x, s);
{push_cpp(s, "x")}        shrink(L[x], s - 1, lim, f), shrink(R[x], s - 1, lim, f);
        {pull_cpp(s, "x", "s")};
    }}''')
    internals += cpp_methods(s, dense_internals)
    out.append("\n\n".join(internals) + "\n};\n")
    return long_runs("".join(out))


def long_runs(text):  # the dense tree's int lengths (n < 2^31) as long long: a sparse range can be huge
    for old, new in (("    int longestEqualRun(", "    long long longestEqualRun("),
                     ("int t = ns[0], p = pr[t], q = sr[t], res = br[t], k = 1 << ls[0];",
                      "int t = ns[0];\n        long long p = pr[t], q = sr[t], res = br[t], k = 1LL << ls[0];"),
                     ("int w = 1 << ls[i];", "long long w = 1LL << ls[i];"), ("int hl = 1 << (s - 1);", "long long hl = 1LL << (s - 1);"),
                     ("push_back(1 << s)", "push_back(1LL << s)"),
                     ("res = max({res, br[t], j ? q + pr[t] : 0});", "res = max({res, br[t], j ? q + pr[t] : 0LL});"),
                     ("br[x] = max({br[a], br[b], j ? sr[a] + pr[b] : 0});", "br[x] = max({br[a], br[b], j ? sr[a] + pr[b] : 0LL});")):
        text = text.replace(old, new)
    return text.replace("        int k = 1 << s;\n", "        long long k = 1LL << s;\n")  # (levels pass 31 here)


def push_cpp(s, x, ind=8):
    if not s.tags():
        return ""
    return " " * ind + (f"push({x}, s);\n" if s.kPush else f"push({x});\n")


def pull_cpp(s, x, lvl):
    return f"pull({x}, {lvl})" if s.kPull else f"pull({x})"


def cpp_sparse_public(s):
    pub = {}
    cov = "        int ns[128], ls[128], c = cover(l, r, ns, ls);\n"
    for op, f, typ, ident, comb in (("rangeSum", "sm", "S", "S(0)", "res += {}"), ("rangeXorQuery", "xr", "T", "T(0)", "res ^= {}"),
                                    ("rangeAndQuery", "an", "T", "~T(0)", "res &= {}"), ("rangeOrQuery", "orr", "T", "T(0)", "res |= {}"),
                                    ("rangeMin", "mn", "T", "numeric_limits<T>::max()", "res = min(res, {})"),
                                    ("rangeMax", "mx", "T", "numeric_limits<T>::lowest()", "res = max(res, {})")):
        if op not in s.ops:
            continue
        pub[op] = f'''    // O(logU) -- {QDOC[op]}
    {typ} {op}(long long l, long long r) {{
{cov}        {typ} res = {ident};
        for (int i = 0; i < c; i++) {comb.format(f"{f}[ns[i]]")};
        return res;
    }}
'''
    if "rangeGcd" in s.ops and not s.gdiff:
        pub["rangeGcd"] = f'''    // O(logU + logU) -- {QDOC["rangeGcd"]}
    T rangeGcd(long long l, long long r) {{
{cov}        T res = T(0);
        for (int i = 0; i < c; i++) res = gcd(res, g[ns[i]]);
        return res;
    }}
'''
    psh = ("                kids(t, s), push(t, s);\n" if s.kPush else "                kids(t, s), push(t);\n") if s.tags() else "                kids(t, s);\n"
    cov3 = "        int ns[128], ls[128];\n        long long ts[128];\n        int c = cover(l, r, ns, ls, ts);\n"
    for op, (side, cmp) in SEARCH.items():
        if op not in s.ops:
            continue
        f, o = ("mx" if cmp.startswith("G") else "mn"), CMP[cmp]
        left = side == "leftmost"
        loop = "for (int i = 0; i < c; i++) {" if left else "for (int i = c - 1; i >= 0; i--) {"
        step = (f"                if ({f}[L[t]] {o} x) t = L[t];\n                else t = R[t], tl += 1LL << s;" if left else
                f"                if ({f}[R[t]] {o} x) t = R[t], tl += 1LL << s;\n                else t = L[t];")
        pub[op] = f'''    // O(logU) -- the {"first" if left else "last"} i in [l, r] with a[i] {o} x, or lo - 1 (a walk pruned by the node {"max" if f == "mx" else "min"})
    long long {op}(long long l, long long r, T x) {{
{cov3}        {loop}
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!({f}[t] {o} x)) continue;
            while (s) {{  // walk down the passing node
{psh}                s--;
{step}
            }}
            return tl;
        }}
        return first - 1;
    }}
'''
    for op, field, strict in PREFIX_SEARCHES:
        if op not in s.ops:
            continue
        o = (">" if strict else ">=") if field in ("pre", "suf") else ("<" if strict else "<=")
        kind = "best" if field in ("pre", "suf") else "min"
        left = field in ("pre", "npre")
        doc = (f"first i in [l, r] with a[l] + ... + a[i] {o} x, or lo - 1 (a walk pruned by {kind} prefix sums)" if left else
               f"last i in [l, r] with a[i] + ... + a[r] {o} x, or lo - 1 (a walk pruned by {kind} suffix sums)")
        loop = "for (int i = 0; i < c; i++) {" if left else "for (int i = c - 1; i >= 0; i--) {"
        near = "L" if left else "R"
        go_near = "t = L[t]" if left else "t = R[t], tl += 1LL << s"
        go_far = "t = R[t], tl += 1LL << s" if left else "t = L[t]"
        pub[op] = f'''    // O(logU) -- {doc}
    long long {op}(long long l, long long r, T x) {{
{cov3}        S acc = 0;
        {loop}
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + {field}[t] {o} S(x)) {{
                while (s) {{
    {psh}                    s--;
                    if (acc + {field}[{near}[t]] {o} S(x)) {go_near};
                    else acc += sm[{near}[t]], {go_far};
                }}
                return tl;
            }}
            acc += sm[t];
        }}
        return first - 1;
    }}
'''
    tn = s.tn
    if s.lazy:
        from gen_seg_algebra import clamp_args, bits_args, takes_s
        calls = {"assign": ("T v", ("applyAssign", "v") if s.asgTag else ("applyClamp", clamp_args(tn, "v", "v", "T(0)")) if s.clamp
                            else ("applyBits", bits_args(tn, "T(0)", "v"))),
                 "add": ("T v", ("applyAP", "v, T(0)") if s.ap else ("applyAdd", "v") if s.addTag else ("applyClamp", clamp_args(tn, "INF", "NEG", "v"))),
                 "ap": ("T start, T step", ("applyAP", "T(start + step * T(tl - l)), step")),
                 "chmin": ("T v", ("applyClamp", clamp_args(tn, "v", "NEG", "T(0)"))),
                 "chmax": ("T v", ("applyClamp", clamp_args(tn, "INF", "v", "T(0)"))),
                 "and": ("T v", ("applyBits", bits_args(tn, "v", "T(0)"))),
                 "or": ("T v", ("applyBits", bits_args(tn, "~T(0)", "v"))),
                 "xor": ("T v", ("applyXor", "v"))}
        shr = {"mod": ("T x", "x >= 1", "x", "[x](T v) { return T(v % x); }", "logU * logU"),
               "div": ("T x", "x >= 2", "T(1)", "[x](T v) { return T(v / x); }", "logU * logU"),
               "sqrt": ("", "", "T(2)", "isqrtT", "logU * loglogU")}
        for u in s.ups:
            if u in shr:
                params, cond, lim, f, c = shr[u]
                ind = "            " if cond else "        "
                call = (f"update(1, D, first, l, r, [&](int t, int s, long long) {{\n{ind}    shrink(t, s, {lim}, {f});\n{ind}}});")
                pub[UOP[u]] = f'''    // amortized O({c}) -- {UDOC[u]}
    void {UOP[u]}(long long l, long long r{", " + params if params else ""}) {{
        {"if (" + cond + ")" + chr(10) + ind if cond else ""}{call}
    }}
'''
                continue
            params, (fn, a) = calls[u]
            fcall = f"{fn}(t, s, {a})" if takes_s(s, "_" + fn) else f"{fn}(t, {a})"
            uses = [n for n in ("s", "tl") if re.search(rf"\b{n}\b", fcall)]
            lam = f"[&](int t, int{' s' if 's' in uses else ''}, long long{' tl' if 'tl' in uses else ''})"
            pub[UOP[u]] = f'''    // O(logU{" * logU" if s.has("gcd") else ""}) -- {UDOC[u]}
    void {UOP[u]}(long long l, long long r, {params}) {{
        {fit_call(f"update(1, D, first, l, r, {lam} {{ {fcall}; }});")}
    }}
'''
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "T(leaf(x) + v)", "a[i] += v"),
                          ("pointChmax", "max(leaf(x), v)", "a[i] = max(a[i], v)"), ("pointChmin", "min(leaf(x), v)", "a[i] = min(a[i], v)")):
        pub[op] = f'''    // O(logU{" * logU" if s.has("gcd") else ""}) -- {doc}
    void {op}(long long i, T v) {{
        int path[64], x = leafOf(i, path);
        setLeaf(x, {expr}), up(path);
    }}
'''
    pub["pointGet"] = '''    // O(logU) -- a[i]
    T pointGet(long long i) {
        int path[64];
        return leaf(leafOf(i, path));
    }
'''
    return pub
