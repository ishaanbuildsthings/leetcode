"""Segment tree beats for range chmin / chmax with range sums: every combination, each paying only for what it has.

    python3 gen_beats.py      (then python3 sparse_beats.py for the sparse versions, then gen_letters.py)

One design for all (the one BeatsGcd uses): a node keeps, for the side(s) it supports,
  chmin: mx, mx2 (strict second max), cntMx      chmax: mn, mn2 (strict second min), cntMn
plus the sum tot, and an add tag only if the variant has rangeAdd. No chmin / chmax tags: a node's own mx / mn ARE its
pending clamp (push clamps each child to them), and no assign tag: a node whose values are all equal (mn == mx, or
no second max / min on a one-sided tree) pushes that value down as an assign. Variants:
  side:  chmin, chmax, or both
  add:   with or without rangeAdd (its tag; and chmin / chmax become log^2 N amortized with it)
  extra: (one-sided) also keep the other extreme plainly, for rangeMin (chmin side) / rangeMax (chmax side)
Every variant has rangeAssign (free, see above), rangeSum, the extreme(s) it keeps as queries, point ops and getAll.
Without rangeSum a chmin / chmax tree is not beats at all: the lazy clamp trees (gen_lazy_family.py) do it in 2N.
"""
import itertools
import os

from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
NAME = "ChminChmaxBeats"
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]


def spec(side, add, extra):
    CN, CX = side in ("chmin", "both"), side in ("chmax", "both")
    MX = CN or (extra and side == "chmax")  # mx kept (with mx2 / cntMx only on the chmin side)
    MN = CX or (extra and side == "chmin")
    ops = sorted(POINT + ["getAll", "rangeAssign", "rangeSum"] + (["rangeChmin"] if CN else []) + (["rangeChmax"] if CX else []) +
                 (["rangeAdd"] if add else []) + (["rangeMax"] if MX else []) + (["rangeMin"] if MN else []))
    fields = (["mx", "mx2", "cntMx"] if CN else ["mx"] if MX else []) + (["mn", "mn2", "cntMn"] if CX else ["mn"] if MN else []) + ["tot"]
    return CN, CX, MX, MN, ops, fields


def header(cm, side, add, extra):
    CN, CX, MX, MN, ops, fields = spec(side, add, extra)
    upd = "log^2(N) amortized" if add else "log(N) amortized"
    comp = {op: upd for op in ops}
    comp.update({"rangeSum": "log(N)", "rangeMax": "log(N)", "rangeMin": "log(N)", "pointGet": "log(N)", "getAll": "N"})
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: beats", "@complexities:"]
    lines += [f"  {op}: {comp[op]}" for op in ops] + ["  build: N", "@memory:", "  layout: 4n-recursive",
              "  node: " + " ".join(f"{f}[4*N]" for f in fields), "  tags: " + ("addTag[4*N]" if add else "none"), "  other: none",
              "  note: no chmin / chmax / assign tags: a node's own " + " / ".join((["mx"] if CN else []) + (["mn"] if CX else [])) +
              " is its pending clamp, and a node whose values are all equal pushes that value as an assign"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def doc(cm, side, add, extra):
    import textwrap
    CN, CX, MX, MN, ops, fields = spec(side, add, extra)
    what = " and ".join((["chmin (a[i] = min(a[i], x))"] if CN else []) + (["chmax (a[i] = max(a[i], x))"] if CX else []))
    kept = " / ".join((["max"] if MX else []) + (["min"] if MN else []))
    own = " / ".join((["mx"] if CN else []) + (["mn"] if CX else []))
    text = ("Segment tree beats: range " + what + (", range add" if add else "") + " and range assign, with range sums and the "
            "range " + kept + ", plus point ops. All indices 0-based, ranges inclusive. How it works: ")
    if CN:
        text += ("a chmin only changes the max values of a node it covers, so a node keeps its max, its strict second max "
                 "and how many copies of the max it has; a chmin x with mx2 < x < mx moves just those copies (the sum drops "
                 "by (mx - x) * cntMx) and stops there, and only x <= mx2 has to go further down. ")
    if CX:
        text += ("a chmax is the same with the min: mn, mn2 and cntMn. " if CN else
                 "a chmax only changes the min values of a node it covers, so a node keeps its min, its strict second min "
                 "and how many copies of the min it has; a chmax x with mn < x < mn2 moves just those copies (the sum rises "
                 "by (x - mn) * cntMn) and stops there, and only x >= mn2 has to go further down. ")
    text += ("A node's own " + own + " doubles as its pending clamp: push clamps each child to it, so there is no chmin / "
             "chmax tag. There is no assign tag either: when all of a node's values are equal (" +
             ("mn == mx" if CN and CX else "no second max" if CN else "no second min") +
             "), push hands that value to both children as an assign. ")
    if add:
        text += "An add shifts everything a node keeps and goes in the one add tag. "
    text += ("Amortized O(log^2 N) per update with range add, O(log N) without it" if add else "Amortized O(log N) per update") + \
        " (beats: every extra descent removes a distinct value)."
    return "\n".join(f"{cm} {ln}" for ln in textwrap.wrap(text, 116)) + "\n"


# ------------------------------------------------------------------------------------------------ Python

def python(side, add, extra):
    CN, CX, MX, MN, ops, fields = spec(side, add, extra)
    init = {"mx": "0", "mx2": "NEG_INF", "cntMx": "0", "mn": "0", "mn2": "POS_INF", "cntMn": "0", "tot": "0", "addTag": "0"}
    F = fields + (["addTag"] if add else [])
    uni = "self.mn[i] == self.mx[i]" if CN and CX else "self.mx2[i] == NEG_INF" if CN else "self.mn2[i] == POS_INF"
    val = "self.mx[i]" if MX else "self.mn[i]"
    leaf = []
    if CN: leaf.append("self.mx[i] = v; self.mx2[i] = NEG_INF; self.cntMx[i] = 1")
    elif MX: leaf.append("self.mx[i] = v")
    if CX: leaf.append("self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = 1")
    elif MN: leaf.append("self.mn[i] = v")
    leaf.append("self.tot[i] = v" + ("; self.addTag[i] = 0" if add else ""))
    pull = ["        l = 2 * i; r = l + 1", "        self.tot[i] = self.tot[l] + self.tot[r]"]
    if CN:
        pull += ["        mx = self.mx; mx2 = self.mx2; cntMx = self.cntMx", "        if mx[l] > mx[r]:",
                 "            mx[i] = mx[l]; cntMx[i] = cntMx[l]", "            mx2[i] = mx2[l] if mx2[l] > mx[r] else mx[r]",
                 "        elif mx[l] < mx[r]:", "            mx[i] = mx[r]; cntMx[i] = cntMx[r]",
                 "            mx2[i] = mx2[r] if mx2[r] > mx[l] else mx[l]", "        else:",
                 "            mx[i] = mx[l]; cntMx[i] = cntMx[l] + cntMx[r]", "            mx2[i] = mx2[l] if mx2[l] > mx2[r] else mx2[r]"]
    elif MX:
        pull += ["        a = self.mx[l]; b = self.mx[r]", "        self.mx[i] = a if a > b else b"]
    if CX:
        pull += ["        mn = self.mn; mn2 = self.mn2; cntMn = self.cntMn", "        if mn[l] < mn[r]:",
                 "            mn[i] = mn[l]; cntMn[i] = cntMn[l]", "            mn2[i] = mn2[l] if mn2[l] < mn[r] else mn[r]",
                 "        elif mn[l] > mn[r]:", "            mn[i] = mn[r]; cntMn[i] = cntMn[r]",
                 "            mn2[i] = mn2[r] if mn2[r] < mn[l] else mn[l]", "        else:",
                 "            mn[i] = mn[l]; cntMn[i] = cntMn[l] + cntMn[r]", "            mn2[i] = mn2[l] if mn2[l] < mn2[r] else mn2[r]"]
    elif MN:
        pull += ["        a = self.mn[l]; b = self.mn[r]", "        self.mn[i] = a if a < b else b"]
    if add:
        pull.append("        self.addTag[i] = 0")
    asg = []
    if CN: asg.append("self.mx[i] = v; self.mx2[i] = NEG_INF; self.cntMx[i] = sz")
    elif MX: asg.append("self.mx[i] = v")
    if CX: asg.append("self.mn[i] = v; self.mn2[i] = POS_INF; self.cntMn[i] = sz")
    elif MN: asg.append("self.mn[i] = v")
    asg.append("self.tot[i] = v * sz" + ("; self.addTag[i] = 0" if add else ""))
    out = [header("#", side, add, extra), "\n", doc("#", side, add, extra), "\nNEG_INF = float('-inf')\nPOS_INF = float('inf')\n\n\n"]
    out.append(f'''class {NAME}:
    # O(N)
    def __init__(self, arr):
        self.n = n = len(arr)
        size = 4 * max(1, n)
{"".join(f"        self.{f} = [{init[f]}] * size{chr(10)}" for f in F)}        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        if tl == tr:
            v = arr[tl]
{"".join(f"            {x}{chr(10)}" for x in leaf)}            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
{chr(10).join(pull)}

    # every value under node i (sz of them) becomes v
    def _applyAssign(self, i, sz, v):
{"".join(f"        {x}{chr(10)}" for x in asg)}''')
    if add:
        sh = []
        if CN: sh += ["        self.mx[i] += v", "        if self.mx2[i] != NEG_INF: self.mx2[i] += v"]
        elif MX: sh.append("        self.mx[i] += v")
        if CX: sh += ["        self.mn[i] += v", "        if self.mn2[i] != POS_INF: self.mn2[i] += v"]
        elif MN: sh.append("        self.mn[i] += v")
        out.append(f'''
    # every value under node i gains v
    def _applyAdd(self, i, sz, v):
        if {uni}:
            self._applyAssign(i, sz, {val} + v); return
{chr(10).join(sh)}
        self.tot[i] += sz * v
        self.addTag[i] += v
''')
    if CN:
        body = ["        if self.mn[i] >= v:", "            self._applyAssign(i, sz, v); return"] if CX else []
        body += ["        if self.mx[i] > v:"] + (["            if self.mn2[i] == self.mx[i]: self.mn2[i] = v"] if CX else []) + [
            "            self.tot[i] -= (self.mx[i] - v) * self.cntMx[i]", "            self.mx[i] = v"]
        if MN and not CX:
            body += ["            if self.mn[i] > v: self.mn[i] = v"]
        out.append(f'''
    # chmin by v on node i, with mx2 < v: only the copies of the max move
    def _applyChmin(self, i, sz, v):
{chr(10).join(body)}
''')
    if CX:
        body = ["        if self.mx[i] <= v:", "            self._applyAssign(i, sz, v); return"] if CN else []
        body += ["        if self.mn[i] < v:"] + (["            if self.mx2[i] == self.mn[i]: self.mx2[i] = v"] if CN else []) + [
            "            self.tot[i] += (v - self.mn[i]) * self.cntMn[i]", "            self.mn[i] = v"]
        if MX and not CN:
            body += ["            if self.mx[i] < v: self.mx[i] = v"]
        out.append(f'''
    # chmax by v on node i, with v < mn2: only the copies of the min move
    def _applyChmax(self, i, sz, v):
{chr(10).join(body)}
''')
    push = [f"        if {uni}:", f"            v = {val}", "            self._applyAssign(l, lsz, v); self._applyAssign(r, rsz, v)", "            return"]
    if add:
        push += ["        a = self.addTag[i]", "        if a:", "            self._applyAdd(l, lsz, a); self._applyAdd(r, rsz, a)", "            self.addTag[i] = 0"]
    if CN:
        push.append("        self._applyChmin(l, lsz, self.mx[i]); self._applyChmin(r, rsz, self.mx[i])")
    if CX:
        push.append("        self._applyChmax(l, lsz, self.mn[i]); self._applyChmax(r, rsz, self.mn[i])")
    out.append(f'''
    # hand node i's pending changes to its children: all one value (an assign), else the add, then its own clamp
    def _push(self, i, tl, tr):
        if tl == tr: return
        tm = (tl + tr) // 2
        lsz = tm - tl + 1; rsz = tr - tm
        l = 2 * i; r = l + 1
{chr(10).join(push)}
''')
    cost = "log^2 N" if add else "logN"
    if CN:
        out.append(f'''
    def _chmin(self, i, tl, tr, ql, qr, x):
        if qr < tl or ql > tr or x >= self.mx[i]: return
        if ql <= tl and qr >= tr and x > self.mx2[i]:
            self._applyChmin(i, tr - tl + 1, x); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._chmin(2 * i, tl, tm, ql, qr, x)
        self._chmin(2 * i + 1, tm + 1, tr, ql, qr, x)
        self._pull(i)

    # amortized O({cost}) -- a[i] = min(a[i], x) for i in [l, r]
    def rangeChmin(self, l, r, x):
        if l <= r and self.n: self._chmin(1, 0, self.n - 1, l, r, x)
''')
    if CX:
        out.append(f'''
    def _chmax(self, i, tl, tr, ql, qr, x):
        if qr < tl or ql > tr or x <= self.mn[i]: return
        if ql <= tl and qr >= tr and x < self.mn2[i]:
            self._applyChmax(i, tr - tl + 1, x); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._chmax(2 * i, tl, tm, ql, qr, x)
        self._chmax(2 * i + 1, tm + 1, tr, ql, qr, x)
        self._pull(i)

    # amortized O({cost}) -- a[i] = max(a[i], x) for i in [l, r]
    def rangeChmax(self, l, r, x):
        if l <= r and self.n: self._chmax(1, 0, self.n - 1, l, r, x)
''')
    if add:
        out.append(f'''
    def _add(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr: return
        if ql <= tl and qr >= tr:
            self._applyAdd(i, tr - tl + 1, v); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._add(2 * i, tl, tm, ql, qr, v)
        self._add(2 * i + 1, tm + 1, tr, ql, qr, v)
        self._pull(i)

    # amortized O({cost}) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        if l <= r and self.n: self._add(1, 0, self.n - 1, l, r, v)
''')
    out.append(f'''
    def _assign(self, i, tl, tr, ql, qr, v):
        if qr < tl or ql > tr: return
        if ql <= tl and qr >= tr:
            self._applyAssign(i, tr - tl + 1, v); return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._assign(2 * i, tl, tm, ql, qr, v)
        self._assign(2 * i + 1, tm + 1, tr, ql, qr, v)
        self._pull(i)

    # amortized O({cost}) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        if l <= r and self.n: self._assign(1, 0, self.n - 1, l, r, v)

    def _sum(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return 0
        if ql <= tl and qr >= tr: return self.tot[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        return self._sum(2 * i, tl, tm, ql, qr) + self._sum(2 * i + 1, tm + 1, tr, ql, qr)

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return 0 if (l > r or not self.n) else self._sum(1, 0, self.n - 1, l, r)
''')
    if MX:
        out.append('''
    def _qmax(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return NEG_INF
        if ql <= tl and qr >= tr: return self.mx[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._qmax(2 * i, tl, tm, ql, qr)
        b = self._qmax(2 * i + 1, tm + 1, tr, ql, qr)
        return a if a > b else b

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        return NEG_INF if (l > r or not self.n) else self._qmax(1, 0, self.n - 1, l, r)
''')
    if MN:
        out.append('''
    def _qmin(self, i, tl, tr, ql, qr):
        if qr < tl or ql > tr: return POS_INF
        if ql <= tl and qr >= tr: return self.mn[i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._qmin(2 * i, tl, tm, ql, qr)
        b = self._qmin(2 * i + 1, tm + 1, tr, ql, qr)
        return a if a < b else b

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        return POS_INF if (l > r or not self.n) else self._qmin(1, 0, self.n - 1, l, r)
''')
    get = "self.rangeMax(p, p)" if MX else "self.rangeMin(p, p)"
    leafv = "self.mx[i]" if MX else "self.mn[i]"
    out.append(f'''
    # O(logN) -- a[p]
    def pointGet(self, p):
        return {get}

    def _getAllRec(self, i, tl, tr, out):
        if tl == tr:
            out.append({leafv})
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._getAllRec(2 * i, tl, tm, out)
        self._getAllRec(2 * i + 1, tm + 1, tr, out)

    # O(N) -- the whole array: one DFS that pushes every tag down and reads the leaves left to right
    def getAll(self):
        out = []
        if self.n:
            self._getAllRec(1, 0, self.n - 1, out)
        return out

    # amortized O({cost}) -- a[p] = v
    def pointAssign(self, p, v):
        self.rangeAssign(p, p, v)

    # amortized O({cost}) -- a[i] += v
    def pointAdd(self, i, v):
        {"self.rangeAdd(i, i, v)" if add else "self.rangeAssign(i, i, self.pointGet(i) + v)"}

    # amortized O({cost}) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        {"self.rangeChmax(i, i, v)" if CX else "if v > self.pointGet(i): self.rangeAssign(i, i, v)"}

    # amortized O({cost}) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        {"self.rangeChmin(i, i, v)" if CN else "if v < self.pointGet(i): self.rangeAssign(i, i, v)"}
''')
    return "".join(out)


# ------------------------------------------------------------------------------------------------ C++

def cpp(side, add, extra):
    CN, CX, MX, MN, ops, fields = spec(side, add, extra)
    uni = "mn[i] == mx[i]" if CN and CX else "mx2[i] == NEG_INF" if CN else "mn2[i] == POS_INF"
    val = "mx[i]" if MX else "mn[i]"
    tf = [f for f in fields if f in ("mx", "mx2", "mn", "mn2")] + (["addTag"] if add else [])
    cf = [f for f in fields if f.startswith("cnt")]
    F = tf + cf + ["tot"]
    inits = ", ".join(f"{f}(4 * max(1, n){', NEG_INF' if f == 'mx2' else ', POS_INF' if f == 'mn2' else ''})" for f in F)
    leaf = []
    if CN: leaf.append("mx[i] = a[tl], mx2[i] = NEG_INF, cntMx[i] = 1")
    elif MX: leaf.append("mx[i] = a[tl]")
    if CX: leaf.append("mn[i] = a[tl], mn2[i] = POS_INF, cntMn[i] = 1")
    elif MN: leaf.append("mn[i] = a[tl]")
    leaf.append("tot[i] = a[tl]")
    pull = ["        int l = 2 * i, r = l + 1;", "        tot[i] = tot[l] + tot[r];"]
    if CN:
        pull += ["        if (mx[l] > mx[r]) mx[i] = mx[l], cntMx[i] = cntMx[l], mx2[i] = max(mx2[l], mx[r]);",
                 "        else if (mx[l] < mx[r]) mx[i] = mx[r], cntMx[i] = cntMx[r], mx2[i] = max(mx2[r], mx[l]);",
                 "        else mx[i] = mx[l], cntMx[i] = cntMx[l] + cntMx[r], mx2[i] = max(mx2[l], mx2[r]);"]
    elif MX:
        pull.append("        mx[i] = max(mx[l], mx[r]);")
    if CX:
        pull += ["        if (mn[l] < mn[r]) mn[i] = mn[l], cntMn[i] = cntMn[l], mn2[i] = min(mn2[l], mn[r]);",
                 "        else if (mn[l] > mn[r]) mn[i] = mn[r], cntMn[i] = cntMn[r], mn2[i] = min(mn2[r], mn[l]);",
                 "        else mn[i] = mn[l], cntMn[i] = cntMn[l] + cntMn[r], mn2[i] = min(mn2[l], mn2[r]);"]
    elif MN:
        pull.append("        mn[i] = min(mn[l], mn[r]);")
    if add:
        pull.append("        addTag[i] = 0;")
    asg = []
    if CN: asg.append("mx[i] = v, mx2[i] = NEG_INF, cntMx[i] = sz")
    elif MX: asg.append("mx[i] = v")
    if CX: asg.append("mn[i] = v, mn2[i] = POS_INF, cntMn[i] = sz")
    elif MN: asg.append("mn[i] = v")
    asg.append("tot[i] = S(v) * sz" + (", addTag[i] = 0" if add else ""))
    cost = "log^2 N" if add else "logN"
    tdecl = f"    vector<T> {', '.join(tf)};" if tf else ""
    out = [header("//", side, add, extra), "\n", doc("//", side, add, extra),
           "// T: int, long long, ...; sums are kept in S (long long for small T).\n",
           f'''template <typename T>
struct {NAME} {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NEG_INF = numeric_limits<T>::lowest(), POS_INF = numeric_limits<T>::max();
    int n;
{tdecl}
{f"    vector<int> {', '.join(cf)};" + chr(10) if cf else ""}    vector<S> tot;

    // O(N)
    explicit {NAME}(const vector<T>& a) : n((int)a.size()), {inits} {{
        if (n) build(1, 0, n - 1, a);
    }}

    void build(int i, int tl, int tr, const vector<T>& a) {{
        if (tl == tr) {{ {", ".join(leaf)}; return; }}
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }}

    void pull(int i) {{
{chr(10).join(pull)}
    }}

    // every value under node i (sz of them) becomes v
    void applyAssign(int i, long long sz, T v) {{ {", ".join(asg)}; }}
''']
    if add:
        sh = []
        if CN: sh += ["        mx[i] += v;", "        if (mx2[i] != NEG_INF) mx2[i] += v;"]
        elif MX: sh.append("        mx[i] += v;")
        if CX: sh += ["        mn[i] += v;", "        if (mn2[i] != POS_INF) mn2[i] += v;"]
        elif MN: sh.append("        mn[i] += v;")
        out.append(f'''
    // every value under node i gains v
    void applyAdd(int i, long long sz, T v) {{
        if ({uni}) {{ applyAssign(i, sz, {val} + v); return; }}
{chr(10).join(sh)}
        tot[i] += S(v) * sz, addTag[i] += v;
    }}
''')
    if CN:
        body = ["        if (mn[i] >= v) { applyAssign(i, sz, v); return; }"] if CX else []
        inner = (["if (mn2[i] == mx[i]) mn2[i] = v;"] if CX else []) + ["tot[i] -= S(mx[i] - v) * cntMx[i];", "mx[i] = v;"] + (
            ["if (mn[i] > v) mn[i] = v;"] if MN and not CX else [])
        body += ["        if (mx[i] > v) {"] + [f"            {x}" for x in inner] + ["        }"]
        out.append(f'''
    // chmin by v on node i, with mx2 < v: only the copies of the max move
    void applyChmin(int i, long long sz, T v) {{
{chr(10).join(body)}{"" if CX else chr(10) + "        (void)sz;"}
    }}
''')
    if CX:
        body = ["        if (mx[i] <= v) { applyAssign(i, sz, v); return; }"] if CN else []
        inner = (["if (mx2[i] == mn[i]) mx2[i] = v;"] if CN else []) + ["tot[i] += S(v - mn[i]) * cntMn[i];", "mn[i] = v;"] + (
            ["if (mx[i] < v) mx[i] = v;"] if MX and not CN else [])
        body += ["        if (mn[i] < v) {"] + [f"            {x}" for x in inner] + ["        }"]
        out.append(f'''
    // chmax by v on node i, with v < mn2: only the copies of the min move
    void applyChmax(int i, long long sz, T v) {{
{chr(10).join(body)}{"" if CN else chr(10) + "        (void)sz;"}
    }}
''')
    push = [f"        if ({uni}) {{ applyAssign(l, lsz, {val}), applyAssign(r, rsz, {val}); return; }}"]
    if add:
        push.append("        if (T a = addTag[i]) applyAdd(l, lsz, a), applyAdd(r, rsz, a), addTag[i] = 0;")
    if CN:
        push.append("        applyChmin(l, lsz, mx[i]), applyChmin(r, rsz, mx[i]);")
    if CX:
        push.append("        applyChmax(l, lsz, mn[i]), applyChmax(r, rsz, mn[i]);")
    out.append(f'''
    // hand node i's pending changes to its children: all one value (an assign), else the add, then its own clamp
    void push(int i, int tl, int tr) {{
        if (tl == tr) return;
        int tm = (tl + tr) / 2, l = 2 * i, r = l + 1;
        long long lsz = tm - tl + 1, rsz = tr - tm;
{chr(10).join(push)}
    }}
''')
    if CN:
        out.append('''
    void chmin(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || x >= mx[i]) return;
        if (ql <= tl && tr <= qr && x > mx2[i]) { applyChmin(i, tr - tl + 1, x); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        chmin(2 * i, tl, tm, ql, qr, x), chmin(2 * i + 1, tm + 1, tr, ql, qr, x);
        pull(i);
    }
''')
    if CX:
        out.append('''
    void chmax(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || x <= mn[i]) return;
        if (ql <= tl && tr <= qr && x < mn2[i]) { applyChmax(i, tr - tl + 1, x); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        chmax(2 * i, tl, tm, ql, qr, x), chmax(2 * i + 1, tm + 1, tr, ql, qr, x);
        pull(i);
    }
''')
    if add:
        out.append('''
    void add(int i, int tl, int tr, int ql, int qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAdd(i, tr - tl + 1, v); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        add(2 * i, tl, tm, ql, qr, v), add(2 * i + 1, tm + 1, tr, ql, qr, v);
        pull(i);
    }
''')
    out.append('''
    void assign(int i, int tl, int tr, int ql, int qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAssign(i, tr - tl + 1, v); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        assign(2 * i, tl, tm, ql, qr, v), assign(2 * i + 1, tm + 1, tr, ql, qr, v);
        pull(i);
    }

    S qsum(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && tr <= qr) return tot[i];
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return qsum(2 * i, tl, tm, ql, qr) + qsum(2 * i + 1, tm + 1, tr, ql, qr);
    }
''')
    if MX:
        out.append('''
    T qmax(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return NEG_INF;
        if (ql <= tl && tr <= qr) return mx[i];
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return max(qmax(2 * i, tl, tm, ql, qr), qmax(2 * i + 1, tm + 1, tr, ql, qr));
    }
''')
    if MN:
        out.append('''
    T qmin(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return POS_INF;
        if (ql <= tl && tr <= qr) return mn[i];
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return min(qmin(2 * i, tl, tm, ql, qr), qmin(2 * i + 1, tm + 1, tr, ql, qr));
    }
''')
    pubs = []
    if CN: pubs.append(f"    // amortized O({cost}) -- a[i] = min(a[i], x) for i in [l, r]\n    void rangeChmin(int l, int r, T x) {{ if (l <= r && n) chmin(1, 0, n - 1, l, r, x); }}\n")
    if CX: pubs.append(f"    // amortized O({cost}) -- a[i] = max(a[i], x) for i in [l, r]\n    void rangeChmax(int l, int r, T x) {{ if (l <= r && n) chmax(1, 0, n - 1, l, r, x); }}\n")
    if add: pubs.append(f"    // amortized O({cost}) -- a[i] += x for i in [l, r]\n    void rangeAdd(int l, int r, T x) {{ if (l <= r && n) add(1, 0, n - 1, l, r, x); }}\n")
    pubs.append(f"    // amortized O({cost}) -- a[i] = x for i in [l, r]\n    void rangeAssign(int l, int r, T x) {{ if (l <= r && n) assign(1, 0, n - 1, l, r, x); }}\n")
    pubs.append("    // O(logN) -- a[l] + ... + a[r]\n    S rangeSum(int l, int r) { return l > r || !n ? S(0) : qsum(1, 0, n - 1, l, r); }\n")
    if MX: pubs.append("    // O(logN) -- max of a[l..r]\n    T rangeMax(int l, int r) { return l > r || !n ? NEG_INF : qmax(1, 0, n - 1, l, r); }\n")
    if MN: pubs.append("    // O(logN) -- min of a[l..r]\n    T rangeMin(int l, int r) { return l > r || !n ? POS_INF : qmin(1, 0, n - 1, l, r); }\n")
    get = "rangeMax(i, i)" if MX else "rangeMin(i, i)"
    leafv = "mx[i]" if MX else "mn[i]"
    pubs.append(f"    // O(logN) -- a[i]\n    T pointGet(int i) {{ return {get}; }}\n")
    pubs.append(f'''    void getAllRec(int i, int tl, int tr, vector<T>& out) {{
        if (tl == tr) {{ out.push_back({leafv}); return; }}
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        getAllRec(2 * i, tl, tm, out), getAllRec(2 * i + 1, tm + 1, tr, out);
    }}

    // O(N) -- the whole array: one DFS that pushes every tag down and reads the leaves left to right
    vector<T> getAll() {{
        vector<T> out;
        out.reserve(n);
        if (n) getAllRec(1, 0, n - 1, out);
        return out;
    }}
''')
    pubs.append(f"    // amortized O({cost}) -- a[i] = v\n    void pointAssign(int i, T v) {{ rangeAssign(i, i, v); }}\n")
    pubs.append(f"    // amortized O({cost}) -- a[i] += v\n    void pointAdd(int i, T v) {{ " + ("rangeAdd(i, i, v); }\n" if add else "rangeAssign(i, i, pointGet(i) + v); }\n"))
    pubs.append(f"    // amortized O({cost}) -- a[i] = max(a[i], v)\n    void pointChmax(int i, T v) {{ " + ("rangeChmax(i, i, v); }\n" if CX else "if (v > pointGet(i)) rangeAssign(i, i, v); }\n"))
    pubs.append(f"    // amortized O({cost}) -- a[i] = min(a[i], v)\n    void pointChmin(int i, T v) {{ " + ("rangeChmin(i, i, v); }\n" if CN else "if (v < pointGet(i)) rangeAssign(i, i, v); }\n"))
    out.append("\n" + "\n".join(pubs) + "};\n")
    return "".join(out)


def variants():
    for side in ("chmin", "chmax", "both"):
        for add in (False, True):
            for extra in ((False, True) if side != "both" else (False,)):
                yield side, add, extra


def main():
    for side, add, extra in variants():
        ops = spec(side, add, extra)[4]
        folder = os.path.join(DIR, folder_name(ops))
        os.makedirs(folder, exist_ok=True)
        for f in ("sparse.py", "sparse.cpp", "letters.py", "letters.cpp"):  # (re-made by sparse_beats.py / gen_letters.py)
            if os.path.exists(os.path.join(folder, f)):
                os.remove(os.path.join(folder, f))
        write_template(os.path.join(folder, "template.py"), python(side, add, extra))
        write_template(os.path.join(folder, "template.cpp"), cpp(side, add, extra))
        print("wrote", os.path.basename(folder))


if __name__ == "__main__":
    main()
