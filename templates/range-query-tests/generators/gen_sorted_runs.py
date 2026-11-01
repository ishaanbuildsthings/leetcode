"""Range sort (rangeSortAsc / rangeSortDesc(l, r): sort a[l..r] in place): the sorted-runs family.

    python3 gen_sorted_runs.py

The array is a sequence of sorted runs. Each run is a dynamic value seg tree over [valLo, valHi] (copies per node, plus
whatever the variant aggregates) and an up / down flag. Sorting [l, r] cuts the runs at l and r + 1 (a value tree splits
by count along one path: O(log U) new nodes) and merges every run inside into one (value trees merge node by node, and
each step of that frees a node). Nodes are only made at the start (log U per value) and by cuts (log U each, two per
operation), so all merges together cost O((N + Q) log U), and every run is merged away at most once.

Variants (every one has the point ops, rangeAssign, getAll and the two sorts):
  - aggregates: every subset of {sum, xor, min, max, or, and, hash}. sum / xor / or / and / hash are fields of the value
    trees (min / max of a run is its tree's first / last value, so they cost no field there).
  - where the runs live:
      fixed length, only sum / xor: Fenwick trees over positions (run starts; each run's sum / xor at its start)
      fixed length, any of min / max / or / and / hash: a seg tree over positions holding each run's aggregates
      sequence edits (insert / erase / reverse / rotate / move): an implicit treap of runs (expected bounds too)
Queries cut the runs at l and r + 1 too, then read whole runs, so every op is O(log N + log U) amortized.
"""
import itertools
import os
import shutil

from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
DTYPE = "sorted-runs"
AGGS = ["sum", "xor", "min", "max", "or", "and", "hash"]
BASE = ["getAll", "pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet", "rangeAssign", "rangeSortAsc",
        "rangeSortDesc"]
AGG_OPS = {"sum": ["rangeSum"], "xor": ["rangeXorQuery"], "min": ["rangeMin"], "max": ["rangeMax"],
           "or": ["rangeOrQuery"], "and": ["rangeAndQuery"],
           "hash": ["isPalindrome", "rangeHash", "rangeHashReversed", "rangesEqual"]}
SEQ = ["append", "appendLeft", "eraseRange", "insertAt", "insertCopiesAt", "moveRange", "pop", "popLeft", "rangeReverse", "rangeRotateLeft",
       "rangeRotateRight"]
VFIELDS = {"sum": ["sm"], "xor": ["xr"], "or": ["ov"], "and": ["av"], "hash": ["fh", "bh"]}  # per value-tree node
WORD = {"sum": "sum", "xor": "xor", "min": "min", "max": "max", "or": "or", "and": "and", "hash": "hashes"}


def ops_of(aggs, seq):
    return sorted(BASE + [o for a in aggs for o in AGG_OPS[a]] + (SEQ if seq else []))


def kind_of(aggs, seq):
    return "treap" if seq else "seg" if set(aggs) - {"sum", "xor"} else "fenwick"


def header(cm, aggs, seq):
    ops = ops_of(aggs, seq)
    kind = kind_of(aggs, seq)
    amort = "log(N)+log(U) amortized"
    comp = {op: amort for op in ops}
    comp["getAll"] = "N*log(U)"
    comp["pointGet"] = "log(N)+log(U) expected" if seq else "log(N)+log(U)"
    lines = [f"@operations: {' '.join(ops)}", f"@data-structure-type: {DTYPE}", "@complexities:"]
    lines += [f"  {op}: {comp[op]}" for op in ops] + ["  build: N*log(U)"]
    vt = ["Lc", "Rc", "cnt"] + [f for a in aggs for f in VFIELDS.get(a, [])]
    node = " ".join(f"{f}[1*N*log(U)]" for f in vt)
    other = []
    if kind == "treap":
        sub = {"sum": ["Ssm"], "xor": ["Sxr"], "min": ["Omn", "Smn"], "max": ["Omx", "Smx"], "or": ["Sov"], "and": ["Sav"],
               "hash": ["Sfh", "Sbh"]}
        other = [f"{x}[1*N]" for x in ["TL", "TR", "TP", "TV", "TN", "TD", "TS", "TF"] + [y for a in aggs for y in sub[a]]]
    else:
        other += [f"{x}[1*N]" for x in ["root", "len", "desc", "bc"]]
        if kind == "fenwick":
            other += [f"{x}[1*N]" for a in aggs for x in {"sum": ["bs"], "xor": ["bx"]}[a]]
        else:
            other += [f"{x}[4*N]" for a in aggs for x in {"sum": ["qs"], "xor": ["qx"], "min": ["qn"], "max": ["qm"],
                      "or": ["qo"], "and": ["qa"], "hash": ["qf", "qb", "ql"]}[a]]
    if "hash" in aggs:
        other += ["pw[1*N]", "gs[1*N]"]
    where = {"fenwick": "Fenwick trees over positions mark run starts" + (" and hold each run's " + " / ".join(WORD[a] for a in aggs) if aggs else ""),
             "seg": "a seg tree over positions holds each run's " + " / ".join(WORD[a] for a in aggs) + " at its start",
             "treap": "the runs are the nodes of an implicit treap (expected depth log N)"}[kind]
    lines += ["@memory:", "  layout: none", f"  node: {node}", "  tags: none", f"  other: {' '.join(other)}",
              f"  note: value nodes: N log U to start, plus O(log U) per cut (merges free nodes, which are reused); {where}; "
              "U = valHi - valLo + 1"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def doc(cm, aggs, seq):
    kind = kind_of(aggs, seq)
    what = ["point reads / writes", "rangeAssign"] + [{"sum": "range sums", "xor": "range xors", "min": "range mins",
            "max": "range maxes", "or": "range ors", "and": "range ands",
            "hash": "range hashes both ways (isPalindrome, rangesEqual)"}[a] for a in aggs]
    if seq:
        what.append("insert / erase / reverse / rotate / move anywhere")
    where = {"fenwick": "a Fenwick tree over positions marks where runs start" + (", others hold each run's " + " / ".join(WORD[a] for a in aggs) + " at its start" if aggs else ""),
             "seg": "a Fenwick tree over positions marks where runs start, and a seg tree over positions holds each run's " + " / ".join(WORD[a] for a in aggs) + " at its start",
             "treap": "the runs, in order, are the nodes of an implicit treap (random priorities, expected depth log N), each also keeping its subtree's length" + (" and " + " / ".join(WORD[a] for a in aggs) if aggs else "") + "; a reverse flips the order of the runs and each run's up / down flag"}[kind]
    hashes = ("\nHashes are polynomial, mod the prime 2^61 - 1, with a base and a value offset random per run: hash(x1..xk) = "
              "x1 B^(k-1) + ... + xk; a value tree keeps the hash of its values in sorted order both ways." if "hash" in aggs else "")
    text = (f"An array whose ranges you can sort in place (ascending or descending), amortized O(log N + log U) a sort, with "
            f"{', '.join(what)} and the whole array. It is kept as a sequence of sorted runs: each run is a dynamic value seg "
            f"tree over [valLo, valHi] (copies per node) and an up / down flag, and {where}. Sorting [l, r] cuts the runs at "
            "l and r + 1 and merges every run inside into one; a[i] is the k-th value of the run holding it; a query cuts at l "
            "and r + 1 too, then reads whole runs. Merges cost about as many nodes as they free and every run is merged away "
            "at most once, hence the amortized bounds" + (" (the treap's are expected as well)" if seq else "") +
            ". Indices 0-based, ranges inclusive, every index is a position in the current array." + hashes)
    import textwrap
    return "\n".join(f"{cm} {ln}" for ln in textwrap.wrap(text, 116)) + "\n"


# ================================================================================================ Python

def py_value_tree(aggs):
    vf = [f for a in aggs for f in VFIELDS.get(a, [])]
    ident = {"sm": "0", "xr": "0", "ov": "0", "av": "-1", "fh": "0", "bh": "0"}
    H = "hash" in aggs
    leaf = ["        self.cnt[x] = c"]
    if "sum" in aggs: leaf.append("        self.sm[x] = c * v")
    if "xor" in aggs: leaf.append("        self.xr[x] = v if c & 1 else 0")
    if "or" in aggs: leaf.append("        self.ov[x] = v")
    if "and" in aggs: leaf.append("        self.av[x] = v")
    if H: leaf.append("        self.fh[x] = self.bh[x] = (v + _HO) % _HP * self.gs[c] % _HP")
    pull = ["        l, r = self.Lc[x], self.Rc[x]", "        cnt = self.cnt", "        cnt[x] = cnt[l] + cnt[r]"]
    if "sum" in aggs: pull.append("        self.sm[x] = self.sm[l] + self.sm[r]")
    if "xor" in aggs: pull.append("        self.xr[x] = self.xr[l] ^ self.xr[r]")
    if "or" in aggs: pull.append("        self.ov[x] = self.ov[l] | self.ov[r]")
    if "and" in aggs: pull.append("        self.av[x] = self.av[l] & self.av[r]")
    if H:
        pull += ["        fh, bh, pw = self.fh, self.bh, self.pw",
                 "        fh[x] = (fh[l] * pw[cnt[r]] + fh[r]) % _HP",
                 "        bh[x] = (bh[r] * pw[cnt[l]] + bh[l]) % _HP"]
    grow = '''
    # hash tables up to length m: pw[k] = B^k, gs[k] = 1 + B + ... + B^(k-1)
    def _grow(self, m):
        pw, gs = self.pw, self.gs
        while len(pw) <= m:
            gs.append((gs[-1] + pw[-1]) % _HP)
            pw.append(pw[-1] * _HB % _HP)
''' if H else ""
    return f'''
    # ---- internals: value trees (node 0 = the empty tree) ----

    def _node(self):
        if self.free:
            t = self.free.pop()
            self.Lc[t] = self.Rc[t] = self.cnt[t] = 0
            return t
        self.Lc.append(0)
        self.Rc.append(0)
        self.cnt.append(0)
{"".join(f"        self.{f}.append({ident[f]}){chr(10)}" for f in vf)}        return len(self.cnt) - 1

    def _freeTree(self, t):  # hand every node of t back
        stack = [t] if t else []
        while stack:
            t = stack.pop()
            self.free.append(t)
            for c in (self.Lc[t], self.Rc[t]):
                if c:
                    stack.append(c)

    # node x holds c copies of v (a leaf, or a node with one value under it)
    def _setLeaf(self, x, v, c):
{chr(10).join(leaf)}

    def _pull(self, x):
{chr(10).join(pull)}
{grow}
    # a tree holding c copies of v: one node per level
    def _leaf(self, v, c=1):
        top = t = self._node()
        nl, nh = self.vlo, self.vhi
        while True:
            self._setLeaf(t, v, c)
            if nl == nh:
                return top
            mid = (nl + nh) >> 1
            u = self._node()
            if v <= mid:
                self.Lc[t], nh = u, mid
            else:
                self.Rc[t], nl = u, mid + 1
            t = u

    # (the k smallest of t, the rest), 0 <= k <= cnt[t]: t keeps the first part, new nodes (one path) the second
    def _split(self, t, k, nl, nh):
        cnt = self.cnt
        if k <= 0:
            return 0, t
        if k >= cnt[t]:
            return t, 0
        b = self._node()
        if nl == nh:  # one value: split its copies
            self._setLeaf(b, nl, cnt[t] - k)
            self._setLeaf(t, nl, k)
            return t, b
        mid = (nl + nh) >> 1
        cl = cnt[self.Lc[t]]
        if k <= cl:
            self.Lc[t], self.Lc[b] = self._split(self.Lc[t], k, nl, mid)
            self.Rc[b], self.Rc[t] = self.Rc[t], 0
        else:
            self.Rc[t], self.Rc[b] = self._split(self.Rc[t], k - cl, mid + 1, nh)
        self._pull(t)
        self._pull(b)
        return t, b

    # the union of a and b, overlaid node by node (b's nodes where both have one are freed)
    def _merge(self, a, b, nl, nh):
        if not a or not b:
            return a or b
        if nl == nh:
            self._setLeaf(a, nl, self.cnt[a] + self.cnt[b])
        else:
            mid = (nl + nh) >> 1
            self.Lc[a] = self._merge(self.Lc[a], self.Lc[b], nl, mid)
            self.Rc[a] = self._merge(self.Rc[a], self.Rc[b], mid + 1, nh)
            self._pull(a)
        self.free.append(b)
        return a

    # the k-th smallest value of t, 1 <= k <= cnt[t]
    def _kth(self, t, k):
        nl, nh, cnt, Lc, Rc = self.vlo, self.vhi, self.cnt, self.Lc, self.Rc
        while nl != nh:
            mid = (nl + nh) >> 1
            cl = cnt[Lc[t]]
            if k <= cl:
                t, nh = Lc[t], mid
            else:
                k -= cl
                t, nl = Rc[t], mid + 1
        return nl

    # t's values, ascending (or descending)
    def _values(self, t, desc):
        out = []
        stack = [(t, self.vlo, self.vhi)]
        while stack:  # in-order, pushed right first
            t, nl, nh = stack.pop()
            if not self.cnt[t]:
                continue
            if nl == nh:
                out += [nl] * self.cnt[t]
                continue
            mid = (nl + nh) >> 1
            stack.append((self.Rc[t], mid + 1, nh))
            stack.append((self.Lc[t], nl, mid))
        return out[::-1] if desc else out
'''


def py_value_init(aggs):
    vf = [f for a in aggs for f in VFIELDS.get(a, [])]
    ident = {"sm": "0", "xr": "0", "ov": "0", "av": "-1", "fh": "0", "bh": "0"}
    lines = ["        self.vlo, self.vhi = valLo, valHi", "        self.Lc, self.Rc, self.cnt = [0], [0], [0]  # value node 0 = the empty tree"]
    lines += [f"        self.{f} = [{ident[f]}]" for f in vf]
    lines.append("        self.free = []  # value nodes freed by merges, reused first")
    if "hash" in aggs:
        lines += ["        self.pw, self.gs = [1], [0]", "        self._grow(n)"]
    return "\n".join(lines)


PY_POINT_WRAPPERS = '''
    # O(log N + log U) amortized -- a[i] += v
    def pointAdd(self, i, v):
        self.pointAssign(i, self.pointGet(i) + v)

    # O(log N + log U) amortized -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        if v > self.pointGet(i):
            self.pointAssign(i, v)

    # O(log N + log U) amortized -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        if v < self.pointGet(i):
            self.pointAssign(i, v)
'''

QDOC = {"rangeSum": "a[l] + ... + a[r]", "rangeXorQuery": "a[l] ^ ... ^ a[r]", "rangeMin": "min of a[l..r]",
        "rangeMax": "max of a[l..r]", "rangeOrQuery": "a[l] | ... | a[r]", "rangeAndQuery": "a[l] & ... & a[r]",
        "rangeHash": "hash of a[l..r] read left to right (a[l] B^(len-1) + ... + a[r], mod 2^61 - 1; B random per run): equal ranges hash equal",
        "rangeHashReversed": "hash of a[l..r] read right to left (= rangeHash of the reversed range)",
        "isPalindrome": "is a[l..r] a palindrome?",
        "rangesEqual": "a[l1..r1] == a[l2..r2]? (equal lengths and equal hashes)"}


def py_runs(aggs):
    """Fixed-length variants: runs indexed by their start position; Fenwick or seg tree over positions."""
    kind = kind_of(aggs, False)
    S = kind == "seg"
    io = bool(aggs)
    # --- container: init / in / out / ask
    init = ["        self.root = [self._leaf(v) for v in arr]  # per run start: its value tree (every element starts as its own run)",
            "        self.len = [1] * n  # per run start: its length",
            "        self.desc = [False] * n  # per run start: sorted descending?",
            "        self.bc = [0] + [1] * n  # Fenwick: 1 at each run start",
            "        self.top = 1 << (n.bit_length() - 1) if n else 0"]
    fens = ["bc"]
    if kind == "fenwick":
        if "sum" in aggs:
            init.append("        self.bs = [0] + list(arr)  # Fenwick: each run's sum, at its start")
            fens.append("bs")
        if "xor" in aggs:
            init.append("        self.bx = [0] + list(arr)  # Fenwick (of xors): each run's xor, at its start")
    init.append("        for i in range(1, n + 1):  # O(N) Fenwick builds")
    init.append("            j = i + (i & -i)")
    init.append("            if j <= n:")
    init += [f"                self.{f}[j] += self.{f}[i]" for f in fens]
    if kind == "fenwick" and "xor" in aggs:
        init.append("                self.bx[j] ^= self.bx[i]")
    Q = {"sum": [("qs", "0")], "xor": [("qx", "0")], "min": [("qn", "INF")], "max": [("qm", "-INF")],
         "or": [("qo", "0")], "and": [("qa", "-1")], "hash": [("qf", "0"), ("qb", "0"), ("ql", "0")]}
    qarr = [x for a in aggs for x in Q[a]]
    if S:
        init.append("        size = self.size = 1 << max(0, (n - 1).bit_length())  # seg tree over positions: each run's aggregates at its start")
        init += [f"        self.{q} = [{i}] * (2 * size)" for q, i in qarr]
        init.append("        for s in range(n):")
        init.append("            self._set(s + size, s)")
        init.append("        for p in range(size - 1, 0, -1):")
        init.append("            self._up(p)")
    inout = ""
    if kind == "fenwick" and io:
        add = []
        if "sum" in aggs: add.append("        self._fen(self.bs, s, sgn * self.sm[t])")
        if "xor" in aggs: add.append("        self._fenx(s, self.xr[t])")
        inout = f'''
    # add (sgn = 1) or take out (sgn = -1) the run starting at s from the run aggregates
    def _io(self, s, sgn):
        t = self.root[s]
{chr(10).join(add)}
'''
        if "xor" in aggs:
            inout += '''
    def _fenx(self, i, v):  # xor v in at i
        f, n = self.bx, self.n
        i += 1
        while i <= n:
            f[i] ^= v
            i += i & -i
'''
    if S:
        setl = ["        t = self.root[s]"]
        for a in aggs:
            setl += {"sum": ["        self.qs[p] = self.sm[t]"], "xor": ["        self.qx[p] = self.xr[t]"],
                     "min": ["        self.qn[p] = self._kth(t, 1)"], "max": ["        self.qm[p] = self._kth(t, self.cnt[t])"],
                     "or": ["        self.qo[p] = self.ov[t]"], "and": ["        self.qa[p] = self.av[t]"],
                     "hash": ["        if self.desc[s]:", "            self.qf[p], self.qb[p] = self.bh[t], self.fh[t]",
                              "        else:", "            self.qf[p], self.qb[p] = self.fh[t], self.bh[t]",
                              "        self.ql[p] = self.len[s]"]}[a]
        clr = [f"        self.{q}[p] = {i}" for q, i in qarr]
        up = ["        l, r = 2 * p, 2 * p + 1"]
        for a in aggs:
            up += {"sum": ["        self.qs[p] = self.qs[l] + self.qs[r]"], "xor": ["        self.qx[p] = self.qx[l] ^ self.qx[r]"],
                   "min": ["        a, b = self.qn[l], self.qn[r]", "        self.qn[p] = a if a < b else b"],
                   "max": ["        a, b = self.qm[l], self.qm[r]", "        self.qm[p] = a if a > b else b"],
                   "or": ["        self.qo[p] = self.qo[l] | self.qo[r]"], "and": ["        self.qa[p] = self.qa[l] & self.qa[r]"],
                   "hash": ["        qf, qb, ql, pw = self.qf, self.qb, self.ql, self.pw",
                            "        qf[p] = (qf[l] * pw[ql[r]] + qf[r]) % _HP",
                            "        qb[p] = (qb[r] * pw[ql[l]] + qb[l]) % _HP",
                            "        ql[p] = ql[l] + ql[r]"]}[a]
        # ask: accumulate over positions [l, r]
        ainit, aleft, aright, ret = [], [], [], []
        for a in aggs:
            if a == "hash":
                ainit.append("        lf = lb = ll = rf = rb = rl = 0  # hashes of the left part and of the right part")
                aleft += ["                lf = (lf * pw[ql[l]] + qf[l]) % _HP", "                lb = (qb[l] * pw[ll] + lb) % _HP",
                          "                ll += ql[l]"]
                aright += ["                rf = (qf[r] * pw[rl] + rf) % _HP", "                rb = (rb * pw[ql[r]] + qb[r]) % _HP",
                           "                rl += ql[r]"]
                ret += ["(lf * pw[rl] + rf) % _HP", "(rb * pw[ll] + lb) % _HP"]
                continue
            v, q, idn = {"sum": ("s", "qs", "0"), "xor": ("x", "qx", "0"), "min": ("mn", "qn", "INF"), "max": ("mx", "qm", "-INF"),
                         "or": ("o", "qo", "0"), "and": ("an", "qa", "-1")}[a]
            ainit.append(f"        {v} = {idn}")
            step = {"sum": "{v} += {q}[{i}]", "xor": "{v} ^= {q}[{i}]", "min": "if {q}[{i}] < {v}:\n                    {v} = {q}[{i}]",
                    "max": "if {q}[{i}] > {v}:\n                    {v} = {q}[{i}]", "or": "{v} |= {q}[{i}]", "and": "{v} &= {q}[{i}]"}[a]
            aleft.append("                " + step.format(v=v, q=q, i="l"))
            aright.append("                " + step.format(v=v, q=q, i="r"))
            ret.append(v)
        loc = ", ".join(f"self.{q}" for q, _ in qarr)
        names = ", ".join(q for q, _ in qarr)
        inout = f'''
    # leaf p of the position tree <- the aggregates of the run starting at s
    def _set(self, p, s):
{chr(10).join(setl).replace("[p]", "[p]")}

    def _up(self, p):
{chr(10).join(up)}

    # add (sgn = 1) or take out (sgn = -1) the run starting at s from the position tree
    def _io(self, s, sgn):
        p = s + self.size
        if sgn > 0:
            self._set(p, s)
        else:
{chr(10).join("    " + c for c in clr)}
        p >>= 1
        while p:
            self._up(p)
            p >>= 1

    # the aggregates of positions l..r ({", ".join(ret)})
    def _ask(self, l, r):
        {names} = {loc}
{"        pw = self.pw" + chr(10) if "hash" in aggs else ""}{chr(10).join(ainit)}
        l += self.size
        r += self.size + 1
        while l < r:
            if l & 1:
{chr(10).join(aleft)}
                l += 1
            if r & 1:
                r -= 1
{chr(10).join(aright)}
            l >>= 1
            r >>= 1
        return {", ".join(ret)}
'''
    IO = (lambda s, sgn: f"self._io({s}, {sgn})") if io else None

    def call(s, sgn, ind):
        return f"{ind}{IO(s, sgn)}\n" if io else ""
    # --- queries
    queries = ""
    order = [o for a in aggs for o in (["f", "b"] if a == "hash" else [a])]
    for a in aggs:
        for op in AGG_OPS[a]:
            if kind == "fenwick":
                body = {"rangeSum": "return self._pre(self.bs, r + 1) - self._pre(self.bs, l)",
                        "rangeXorQuery": "return self._prex(r + 1) ^ self._prex(l)"}[op]
                queries += f'''
    # O(log N + log U) amortized -- {QDOC[op]}
    def {op}(self, l, r):
        self._cutAt(l)
        self._cutAt(r + 1)
        {body}
'''
                continue
            if op == "rangesEqual":
                queries += f'''
    # O(log N + log U) amortized -- {QDOC[op]}
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)
'''
                continue
            idx = {"rangeSum": order.index("sum") if "sum" in order else 0, "rangeXorQuery": order.index("xor") if "xor" in order else 0,
                   "rangeMin": order.index("min") if "min" in order else 0, "rangeMax": order.index("max") if "max" in order else 0,
                   "rangeOrQuery": order.index("or") if "or" in order else 0, "rangeAndQuery": order.index("and") if "and" in order else 0,
                   "rangeHash": order.index("f") if "f" in order else 0, "rangeHashReversed": order.index("b") if "b" in order else 0}
            if op == "isPalindrome":
                body = f"res = self._ask(l, r)\n        return res[{order.index('f')}] == res[{order.index('b')}]" if len(order) > 1 else ""
            else:
                body = f"return self._ask(l, r){'' if len(order) == 1 else f'[{idx[op]}]'}"
            queries += f'''
    # O(log N + log U) amortized -- {QDOC[op]}
    def {op}(self, l, r):
        self._cutAt(l)
        self._cutAt(r + 1)
        {body}
'''
    prex = '''
    def _prex(self, i):  # xor of positions 0..i-1
        f, s = self.bx, 0
        while i > 0:
            s ^= f[i]
            i &= i - 1
        return s
''' if kind == "fenwick" and "xor" in aggs else ""
    return f'''
    # O(N log U) -- arr: the initial array; every value a[i] ever holds must lie in [valLo, valHi] (U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        n = self.n = len(arr)
{py_value_init(aggs)}
{chr(10).join(init)}

    # O(log N + log U) -- a[i]
    def pointGet(self, i):
        s = self._startOf(i)
        k = i - s
        return self._kth(self.root[s], self.len[s] - k if self.desc[s] else k + 1)

    # O(log N + log U) amortized -- a[i] = v
    def pointAssign(self, i, v):
        self._cutAt(i)
        self._cutAt(i + 1)
{call("i", -1, "        ")}        self._freeTree(self.root[i])
        self.root[i] = self._leaf(v)
{call("i", 1, "        ")}{PY_POINT_WRAPPERS}
    # O(log N + log U) amortized -- sort a[l..r] ascending
    def rangeSortAsc(self, l, r):
        self._sort(l, r, False, None)

    # O(log N + log U) amortized -- sort a[l..r] descending
    def rangeSortDesc(self, l, r):
        self._sort(l, r, True, None)

    # O(log N + log U) amortized -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        self._sort(l, r, False, v)
{queries}
    # O(N log U) -- the whole current array
    def getAll(self):
        out, s = [], 0
        while s < self.n:
            out += self._values(self.root[s], self.desc[s])
            s += self.len[s]
        return out

    # ---- internals: runs ----

    # cut at l and r + 1, then turn a[l..r] into one run: every run inside merged (v is None) or thrown away for a run
    # of r - l + 1 copies of v
    def _sort(self, l, r, desc, v):
        self._cutAt(l)
        self._cutAt(r + 1)
{call("l", -1, "        ")}        t, s = self.root[l], l + self.len[l]
        if v is not None:
            self._freeTree(t)
        while s <= r:  # every run inside goes
            b, nxt = self.root[s], s + self.len[s]
{call("s", -1, "            ")}            self._fen(self.bc, s, -1)
            if v is None:
                t = self._merge(t, b, self.vlo, self.vhi)
            else:
                self._freeTree(b)
            s = nxt
        self.root[l] = t if v is None else self._leaf(v, r - l + 1)
        self.len[l], self.desc[l] = r - l + 1, desc
{call("l", 1, "        ")}
    # make a run start at p (0 < p < n): split the run holding it by count
    def _cutAt(self, p):
        if p <= 0 or p >= self.n:
            return
        s = self._startOf(p)
        if s == p:
            return
{call("s", -1, "        ")}        t, k, ln = self.root[s], p - s, self.len[s]
        if self.desc[s]:  # the first k are the k largest
            b, a = self._split(t, ln - k, self.vlo, self.vhi)
        else:
            a, b = self._split(t, k, self.vlo, self.vhi)
        self.root[s], self.len[s] = a, k
        self.root[p], self.len[p], self.desc[p] = b, ln - k, self.desc[s]
        self._fen(self.bc, p, 1)
{call("s", 1, "        ")}{call("p", 1, "        ")}
    # the start of the run holding i: the (# of starts <= i)-th start, by binary lifting
    def _startOf(self, i):
        k, bc, pos, step = self._pre(self.bc, i + 1), self.bc, 0, self.top
        while step:
            nxt = pos + step
            if nxt <= self.n and bc[nxt] < k:
                pos = nxt
                k -= bc[nxt]
            step >>= 1
        return pos

    def _fen(self, f, i, v):
        n = self.n
        i += 1
        while i <= n:
            f[i] += v
            i += i & -i

    @staticmethod
    def _pre(f, i):  # f's total over positions 0..i-1
        s = 0
        while i > 0:
            s += f[i]
            i &= i - 1
        return s
{prex}{inout}{py_value_tree(aggs)}'''


def py_treap(aggs):
    """Sequence variants: the runs are the nodes of an implicit treap."""
    H = "hash" in aggs
    sub = {"sum": [("Ssm", "0")], "xor": [("Sxr", "0")], "min": [("Omn", "INF"), ("Smn", "INF")],
           "max": [("Omx", "-INF"), ("Smx", "-INF")], "or": [("Sov", "0")], "and": [("Sav", "-1")],
           "hash": [("Sfh", "0"), ("Sbh", "0")]}
    arrs = [("TL", "0"), ("TR", "0"), ("TP", "0"), ("TV", "0"), ("TN", "0"), ("TD", "False"), ("TS", "0"), ("TF", "False")]
    arrs += [x for a in aggs for x in sub[a]]
    init = ["        # treap of runs (node 0 = empty): children TL / TR, priority TP, value tree TV, length TN, descending TD,",
            "        # subtree length TS, pending reverse TF" + (", subtree " + " / ".join(WORD[a] for a in aggs) if aggs else "") +
            (" (O: the run's own min / max)" if {"min", "max"} & set(aggs) else "")]
    init += [f"        self.{a} = [{i}]" for a, i in arrs]
    init.append("        self.tfree = []")
    def own(t):  # the run's own min / max, read off its value tree t
        out = []
        if "min" in aggs: out.append(f"        self.Omn[x] = self._kth({t}, 1)")
        if "max" in aggs: out.append(f"        self.Omx[x] = self._kth({t}, self.cnt[{t}])")
        return "".join(ln + "\n" for ln in out)
    tpull = ["        L, R = self.TL[x], self.TR[x]", "        t = self.TV[x]", "        TS = self.TS", "        TS[x] = TS[L] + self.TN[x] + TS[R]"]
    for a in aggs:
        tpull += {"sum": ["        self.Ssm[x] = self.Ssm[L] + self.sm[t] + self.Ssm[R]"],
                  "xor": ["        self.Sxr[x] = self.Sxr[L] ^ self.xr[t] ^ self.Sxr[R]"],
                  "min": ["        m = self.Omn[x]", "        if self.Smn[L] < m:", "            m = self.Smn[L]",
                          "        if self.Smn[R] < m:", "            m = self.Smn[R]", "        self.Smn[x] = m"],
                  "max": ["        m = self.Omx[x]", "        if self.Smx[L] > m:", "            m = self.Smx[L]",
                          "        if self.Smx[R] > m:", "            m = self.Smx[R]", "        self.Smx[x] = m"],
                  "or": ["        self.Sov[x] = self.Sov[L] | self.ov[t] | self.Sov[R]"],
                  "and": ["        self.Sav[x] = self.Sav[L] & self.av[t] & self.Sav[R]"],
                  "hash": ["        pw, Sfh, Sbh = self.pw, self.Sfh, self.Sbh",
                           "        f, b = (self.bh[t], self.fh[t]) if self.TD[x] else (self.fh[t], self.bh[t])  # the run, read left to right / right to left",
                           "        m = self.TN[x]",
                           "        Sfh[x] = ((Sfh[L] * pw[m] + f) * pw[TS[R]] + Sfh[R]) % _HP",
                           "        Sbh[x] = ((Sbh[R] * pw[m] + b) * pw[TS[L]] + Sbh[L]) % _HP"]}[a]
    rev = ["        self.TL[x], self.TR[x] = self.TR[x], self.TL[x]", "        self.TD[x] = not self.TD[x]"]
    if H: rev.append("        self.Sfh[x], self.Sbh[x] = self.Sbh[x], self.Sfh[x]")
    rev.append("        self.TF[x] = not self.TF[x]")
    newn = ["        if self.tfree:", "            x = self.tfree.pop()", "            self.TL[x] = self.TR[x] = 0", "            self.TF[x] = False",
            "        else:", "            x = len(self.TS)"]
    newn += [f"            self.{a}.append({i})" for a, i in arrs]
    newn += ["        self.TP[x] = random.getrandbits(62)", "        self.TV[x], self.TN[x], self.TD[x] = t, ln, desc"]
    queries = ""
    for a in aggs:
        for op in AGG_OPS[a]:
            if op == "rangesEqual":
                queries += f'''
    # O(log N + log U) amortized -- {QDOC[op]}
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)
'''
                continue
            read = {"rangeSum": "self.Ssm[B]", "rangeXorQuery": "self.Sxr[B]", "rangeMin": "self.Smn[B]", "rangeMax": "self.Smx[B]",
                    "rangeOrQuery": "self.Sov[B]", "rangeAndQuery": "self.Sav[B]", "rangeHash": "self.Sfh[B]",
                    "rangeHashReversed": "self.Sbh[B]", "isPalindrome": "self.Sfh[B] == self.Sbh[B]"}[op]
            queries += f'''
    # O(log N + log U) amortized -- {QDOC[op]}
    def {op}(self, l, r):
        A, B, C = self._extract(l, r)
        res = {read}
        self._join(A, B, C)
        return res
'''
    return f'''
    # O(N log U) -- arr: the initial array (may be empty); every value a[i] ever holds must lie in [valLo, valHi]
    # (U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        n = self.n = len(arr)
{py_value_init(aggs)}
{chr(10).join(init)}
        stack = []  # O(N) build: the treap's right spine
        for v in arr:
            x, last = self._run(self._leaf(v), 1, False), 0
            while stack and self.TP[stack[-1]] < self.TP[x]:
                last = stack.pop()
                self._tpull(last)
            self.TL[x] = last
            if stack:
                self.TR[stack[-1]] = x
            stack.append(x)
        for x in reversed(stack):
            self._tpull(x)
        self.top = stack[0] if stack else 0

    # O(1) -- the current length
    def size(self):
        return self.n

    # O(log N + log U) expected -- a[i]
    def pointGet(self, i):
        x = self.top
        while True:
            self._push(x)
            ls = self.TS[self.TL[x]]
            if i < ls:
                x = self.TL[x]
            elif i < ls + self.TN[x]:
                k = i - ls
                return self._kth(self.TV[x], self.TN[x] - k if self.TD[x] else k + 1)
            else:
                i -= ls + self.TN[x]
                x = self.TR[x]

    # O(log N + log U) amortized -- a[i] = v
    def pointAssign(self, i, v):
        self.rangeAssign(i, i, v)
{PY_POINT_WRAPPERS}
    # O(log N + log U) amortized -- sort a[l..r] ascending
    def rangeSortAsc(self, l, r):
        self._sort(l, r, False)

    # O(log N + log U) amortized -- sort a[l..r] descending
    def rangeSortDesc(self, l, r):
        self._sort(l, r, True)

    # O(log N + log U) amortized -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        A, B, C = self._extract(l, r)
        self._drop(B)
        self._join(A, self._run(self._leaf(v, r - l + 1), r - l + 1, False), C)

    # O(log N + log U) amortized -- reverse a[l..r]
    def rangeReverse(self, l, r):
        A, B, C = self._extract(l, r)
        self._rev(B)
        self._join(A, B, C)

    # O(log N + log U) amortized -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        self.insertCopiesAt(i, v, 1)

    # O(log N + log U) amortized -- insert k copies of v starting at index i (0 <= i <= size(); k <= 0 does nothing)
    def insertCopiesAt(self, i, v, k):
        if k <= 0:
            return
        self.n += k
{"        self._grow(self.n)" + chr(10) if H else ""}        A, C = self._tsplit(self.top, i)
        self.top = self._tmerge(self._tmerge(A, self._run(self._leaf(v, k), k, False)), C)

    # O(log N + log U) amortized -- append v
    def append(self, v):
        self.insertCopiesAt(self.n, v, 1)

    # O(log N + log U) amortized -- insert v at the front (it becomes a[0])
    def appendLeft(self, v):
        self.insertCopiesAt(0, v, 1)

    # O(log N + log U) amortized -- remove a[i] and return it
    def pop(self, i):
        v = self.pointGet(i)
        self.eraseRange(i, i)
        return v

    # O(log N + log U) amortized -- remove a[0] and return it
    def popLeft(self):
        return self.pop(0)

    # O(log N + log U) amortized -- remove a[l..r]
    def eraseRange(self, l, r):
        A, B, C = self._extract(l, r)
        self._drop(B)
        self.n -= r - l + 1
        self.top = self._tmerge(A, C)

    # O(log N + log U) amortized -- rotate a[l..r] left by k (a[l + k] comes first; any k, negative = right)
    def rangeRotateLeft(self, l, r, k):
        k %= r - l + 1
        if k:
            A, B, C = self._extract(l, r)
            X, Y = self._tsplit(B, k)
            self._join(A, self._tmerge(Y, X), C)

    # O(log N + log U) amortized -- rotate a[l..r] right by k (any k, negative = left)
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)

    # O(log N + log U) amortized -- cut a[l..r] out and paste it so it starts at index i of what is left
    # (0 <= i <= size() - (r - l + 1))
    def moveRange(self, l, r, i):
        A, B, C = self._extract(l, r)
        X, Y = self._tsplit(self._tmerge(A, C), i)
        self.top = self._tmerge(self._tmerge(X, B), Y)
{queries}
    # O(N log U) -- the whole current array
    def getAll(self):
        out, stack, x = [], [], self.top
        while stack or x:
            while x:
                self._push(x)
                stack.append(x)
                x = self.TL[x]
            x = stack.pop()
            out += self._values(self.TV[x], self.TD[x])
            x = self.TR[x]
        return out

    # ---- internals: the treap of runs ----

    # a new run node: value tree t, length ln, descending?
    def _run(self, t, ln, desc):
{chr(10).join(newn)}
{own("t")}        self._tpull(x)
        return x

    def _tpull(self, x):
{chr(10).join(tpull)}

    def _rev(self, x):  # reverse x's subtree: swap its children (and below, lazily), flip its run
        if not x:
            return
{chr(10).join(rev)}

    def _push(self, x):
        if self.TF[x]:
            self._rev(self.TL[x])
            self._rev(self.TR[x])
            self.TF[x] = False

    # (the first k elements, the rest), cutting the run that straddles k
    def _tsplit(self, x, k):
        if not x or k <= 0:
            return 0, x
        if k >= self.TS[x]:
            return x, 0
        self._push(x)
        L = self.TL[x]
        ls = self.TS[L]
        if k <= ls:
            a, b = self._tsplit(L, k)
            self.TL[x] = b
            self._tpull(x)
            return a, x
        if k >= ls + self.TN[x]:
            a, b = self._tsplit(self.TR[x], k - ls - self.TN[x])
            self.TR[x] = a
            self._tpull(x)
            return x, b
        k -= ls  # cut this run: x keeps its first k elements, a new node the rest
        t, ln = self.TV[x], self.TN[x]
        if self.TD[x]:  # the first k are the k largest
            b, a = self._split(t, ln - k, self.vlo, self.vhi)
        else:
            a, b = self._split(t, k, self.vlo, self.vhi)
        self.TV[x], self.TN[x] = a, k
{own("a")}        u = self._run(b, ln - k, self.TD[x])
        R = self.TR[x]
        self.TR[x] = 0
        self._tpull(x)
        return x, self._tmerge(u, R)

    def _tmerge(self, a, b):
        if not a or not b:
            return a or b
        if self.TP[a] > self.TP[b]:
            self._push(a)
            self.TR[a] = self._tmerge(self.TR[a], b)
            self._tpull(a)
            return a
        self._push(b)
        self.TL[b] = self._tmerge(a, self.TL[b])
        self._tpull(b)
        return b

    # (before l, a[l..r], after r) as three treaps
    def _extract(self, l, r):
        A, B = self._tsplit(self.top, l)
        B, C = self._tsplit(B, r - l + 1)
        return A, B, C

    def _join(self, A, B, C):
        self.top = self._tmerge(self._tmerge(A, B), C)

    def _nodes(self, x):  # every run node of x's treap
        out, stack = [], [x] if x else []
        while stack:
            x = stack.pop()
            out.append(x)
            for c in (self.TL[x], self.TR[x]):
                if c:
                    stack.append(c)
        return out

    def _drop(self, x):  # free every run of x (value trees and treap nodes)
        for y in self._nodes(x):
            self._freeTree(self.TV[y])
            self.tfree.append(y)

    # a[l..r] becomes one sorted run: every run inside merges into one
    def _sort(self, l, r, desc):
        A, B, C = self._extract(l, r)
        t = 0
        for y in self._nodes(B):
            t = self._merge(t, self.TV[y], self.vlo, self.vhi)
            self.tfree.append(y)
        self._join(A, self._run(t, r - l + 1, desc), C)
{py_value_tree(aggs)}'''


PY_HASH = '''_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)
'''


def class_name(aggs, seq):
    return "SortedRuns" + "".join(a.capitalize() for a in aggs) + ("Seq" if seq else "")


def python(aggs, seq):
    pre = []
    if seq or "hash" in aggs:
        pre.append("import random")
    if {"min", "max"} & set(aggs):
        pre.append('INF = float("inf")')
    body = (header("#", aggs, seq) + "\n" + doc("#", aggs, seq) + "\n" + ("\n".join(pre) + "\n" if pre else "") +
            (PY_HASH if "hash" in aggs else "") + f"\n\nclass {class_name(aggs, seq)}:" +
            (py_treap(aggs) if seq else py_runs(aggs)))
    return body


# ================================================================================================ write

def variants():
    for k in range(len(AGGS) + 1):
        for aggs in itertools.combinations(AGGS, k):
            for seq in (False, True):
                yield list(aggs), seq


def folder_for(aggs, seq):
    name = folder_name(ops_of(aggs, seq))
    if len(name) <= 180:
        return name
    return DTYPE + "".join("-" + a for a in aggs) + ("-seq" if seq else "")


def main(langs=("py", "cpp")):
    for d in os.listdir(DIR):  # every sorted-runs folder is regenerated (names follow the op lists)
        t = os.path.join(DIR, d, "template.py")
        if os.path.exists(t) and f"@data-structure-type: {DTYPE}" in open(t).read():
            shutil.rmtree(os.path.join(DIR, d))
    count = 0
    for aggs, seq in variants():
        folder = os.path.join(DIR, folder_for(aggs, seq))
        os.makedirs(folder, exist_ok=True)
        if "py" in langs:
            write_template(os.path.join(folder, "template.py"), python(aggs, seq))
        if "cpp" in langs:
            from gen_sorted_runs_cpp import cpp  # noqa: E402
            write_template(os.path.join(folder, "template.cpp"), cpp(aggs, seq))
        count += 1
    print("wrote", count, "sorted-runs templates")


if __name__ == "__main__":
    import sys
    main(("py",) if "--py" in sys.argv else ("py", "cpp"))
