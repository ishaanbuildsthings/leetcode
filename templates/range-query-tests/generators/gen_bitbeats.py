"""Bitwise segment tree beats (range and= / or=), one template per set of extra aggregates it keeps.

    python3 gen_bitbeats.py      (then python3 sparse_beats.py for the sparse versions)

andAll / orAll are always kept (the beats rule needs them, and they answer rangeAndQuery / rangeOrQuery); max, min
and sum each cost one more array, so every subset of {rangeMax, rangeMin, rangeSum} gets its own template and you
never pay for an aggregate you don't use. Sums need each node's length, which the recursion already knows
(tr - tl + 1), so no size array is stored.
"""
import itertools
import os

from note_lang import write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
BASE = ["rangeAndApply", "rangeAndQuery", "rangeOrApply", "rangeOrQuery"]
ORIGINAL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/range-AndApply-OrApply-Min-Max-Sum-AndQuery-OrQuery-pointSet"

DOC = r'''
"""
HOW DO POTENTIALS WORK? (bitwise beats)

THE POTENTIAL IS PER BIT, NOT PER VALUE. This is what makes this template different from the
chmin/chmax beats ones, where the potential counts distinct values.

Call a bit MIXED in a node when the node's values do not all agree on it. Since the node stores
the AND and the OR of everything under it, the mixed bits are exactly andAll ^ orAll -- one
&-and-^ gives you the whole set in O(1), which is the only reason this is affordable.

Give each node a score equal to how many of its K bits are mixed, and sum that over all nodes.
A node's score is at most K, and there are O(n) nodes over logN levels, so the whole tree starts
at O(n * K * logN).

WHY THIS IS THE RIGHT THING TO COUNT: an AND / OR is uniform across a node exactly when it
leaves every mixed bit alone. If it touches only bits the node already agrees on, then every value
changes by the SAME delta -- which is why max, min AND sum all survive the O(1) apply here, not
just max. And if it does touch a mixed bit, then after the operation that bit is no longer mixed
(an AND forces it to 0 everywhere, an OR forces it to 1 everywhere), so the score drops.

So the three cases are:
  1) the op cannot change anything here                  -> return, free
  2) fully covered and no mixed bit is touched           -> O(1) apply, no potential spent, which
                                                            is exactly why we must NOT descend
  3) a mixed bit is touched                              -> descend, and that bit becomes uniform
                                                            in the nodes below, paying for the visit
Same shape as chmin beats: we can only descend when potential actually drops.

WHY THERE IS NO RANGE XOR: xor flips a bit everywhere, so a mixed bit stays mixed. A fully covered
node whose mixed bits xor touches can't take the O(1) apply (its values would move by different
amounts), and descending spends no potential, so one xor over a range of distinct values walks the
whole tree: O(N) per op, every time. For xor with sums use BitCountTree, which counts set bits per
node instead and handles xor in O(logN * K) without beats.

Pushing a tag to the children costs O(K) of potential and there are logN of them per op, so q ops
add O(q * K * logN). Total O((n + q) * K * logN).

THE TAG IS TWO MASKS, (tagAnd, tagXor), meaning  v -> (v & tagAnd) ^ tagXor.
Every per-bit function you can build out of AND / OR / XOR is one of four things -- keep, force 0,
force 1, flip -- and all four fit:
    keep     a=1 x=0        force 0  a=0 x=0
    force 1  a=0 x=1        flip     a=1 x=1
so the three operations are just
    AND x  ->  (a, x) = (x,  0)
    OR  x  ->  (a, x) = (~x, x)
    XOR x  ->  (a, x) = (~0, x)
and two tags compose into one:
    a = a1 & a2,   x = (x1 & a2) ^ x2

WHY A PUSHED TAG IS ALWAYS LEGAL:
_apply has a precondition -- mixed <= a and mixed & x == 0 -- that nothing in the code checks.
It holds because a tag is only ever created at a node that satisfied it, the operation does not
change that node's mixed set (it only touches uniform bits), and composing two tags that both
respect a mixed set gives a tag that still respects it. A child's mixed bits are a subset of its
parent's, so a tag legal for the parent is legal for the child.

WHY THE PRUNE NEEDS ALL THREE CHECKS (_noEffect):
nothing changes iff for every value v in the node, (v & a) ^ x == v. Per bit:
  flip bits    (a=1,x=1) always change something         -> a & x must be 0
  force-0 bits (a=0,x=0) need the bit already 0 for all  -> ~a & ~x & orAll must be 0
  force-1 bits (a=0,x=1) need the bit already 1 for all  -> ~a & x & ~andAll must be 0
Dropping the last two costs real time -- a pure OR would never prune.
"""
'''

# (field, op, python combine of a / b, C++ combine, out-of-range identity in C++)
AGGS = [("mx", "rangeMax", "a if a > b else b", "max(a, b)", "S(0)"),
        ("mn", "rangeMin", "a if a < b else b", "min(a, b)", "S(FULL)"),
        ("tot", "rangeSum", "a + b", "a + b", "S(0)"),
        ("andAll", "rangeAndQuery", "a & b", "a & b", "S(FULL)"),
        ("orAll", "rangeOrQuery", "a | b", "a | b", "S(0)")]
DESC = {"rangeMax": "max of a[l..r]", "rangeMin": "min of a[l..r]", "rangeSum": "a[l] + ... + a[r]",
        "rangeAndQuery": "a[l] & ... & a[r]", "rangeOrQuery": "a[l] | ... | a[r]"}


def header(cm, ops, fields):
    comp = {op: "log(N)" for op in ops}
    comp.update({op: "log(N) amortized" for op in ("pointAdd", "pointAssign", "pointChmax", "pointChmin")})
    comp.update({"rangeAndApply": "log(N)*log(U) amortized", "rangeOrApply": "log(N)*log(U) amortized"})
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: beats", "@complexities:"]
    lines += [f"  {op}: {comp[op]}" for op in ops] + ["  build: N", "@memory:", "  layout: 4n-recursive",
              "  node: " + " ".join(f"{f}[4*N]" for f in fields), "  tags: tagAnd[4*N] tagXor[4*N]", "  other: none",
              "  note: the and/or tags compose into one (and, xor) pair per node (or X is the pair (~X, X)); no range xor, "
              "see BitCountTree", f"@original-file-url: {ORIGINAL}.{'py' if cm == '#' else 'cpp'}"]
    return "\n".join(f"{cm} {ln}" for ln in lines) + "\n"


def python(ops, aggs):
    fields = [f for f, *_ in aggs]
    S = "tot" in fields
    shift = [f for f in fields if f in ("mx", "mn", "tot")]
    k = ", k" if S else ""
    leaf = " = ".join(f"self.{f}[i]" for f in fields) + " = v"
    lines = [f"# O(logN):  {op}(l, r)" + " " * (14 - len(op)) + f"-- {DESC[op]}" for _, op, *_ in AGGS if op in ops]
    out = header("#", ops, fields) + f'''
# ========================
# COMPLEXITIES
#
# O(n) build
# seg = BitBeats_PERFORMANT(arr, 20)   # second arg is the bit width
#
# K = bit width (20 for values < 2^20)
# AMORTIZED O(logN * K):  rangeAndApply(l, r, x)      -- a[i] &= x
# AMORTIZED O(logN * K):  rangeOrApply(l, r, x)       -- a[i] |= x
# AMORTIZED O(logN):      pointAssign(pos, newVal)
#
{chr(10).join(lines)}
# O(logN):  pointGet(pos)
# O(n) space
#
# Whole thing is O((n + q) * K * logN). Values must be NON-NEGATIVE and below 2^K. Python ints cannot overflow.
#
# ========================
#
{DOC.strip()}

# ========================


class BitBeats_PERFORMANT:
    def __init__(self, arr, bits=20):
        self.n = n = len(arr)
        self.FULL = FULL = (1 << bits) - 1
        size = 4 * max(1, n)
{"".join(f"        self.{f} = [0] * size{chr(10)}" for f in shift)}        self.andAll = [FULL] * size
        self.orAll = [0] * size
        self.tagAnd = [FULL] * size
        self.tagXor = [0] * size
        if n:
            self._build(1, 0, n - 1, arr)

    def _build(self, i, tl, tr, arr):
        self.tagAnd[i] = self.FULL; self.tagXor[i] = 0
        if tl == tr:
            v = arr[tl]
            {leaf}
            return
        tm = (tl + tr) // 2
        self._build(2 * i, tl, tm, arr)
        self._build(2 * i + 1, tm + 1, tr, arr)
        self._pull(i)

    def _pull(self, i):
        l = 2 * i; r = l + 1
{"        mx = self.mx" + chr(10) + "        self.mx[i] = mx[l] if mx[l] > mx[r] else mx[r]" + chr(10) if "mx" in fields else ""}{"        mn = self.mn" + chr(10) + "        self.mn[i] = mn[l] if mn[l] < mn[r] else mn[r]" + chr(10) if "mn" in fields else ""}{"        self.tot[i] = self.tot[l] + self.tot[r]" + chr(10) if S else ""}        self.andAll[i] = self.andAll[l] & self.andAll[r]
        self.orAll[i] = self.orAll[l] | self.orAll[r]
        self.tagAnd[i] = self.FULL; self.tagXor[i] = 0

    # legal only when every bit the node disagrees on is kept: mixed <= a and mixed & x == 0.
    # then every value changes by the SAME delta{", so " + " / ".join(f for f in shift) + " just shift" if shift else ""}{" (k = the node's length)" if S else ""}.
    def _apply(self, i, a, x{k}):
        FULL = self.FULL
{f"""        keep = (a ^ x) & FULL
        delta = ((~self.orAll[i]) & x & FULL) - (self.andAll[i] & ~keep & FULL)
""" if shift else ""}{"        self.mx[i] += delta" + chr(10) if "mx" in fields else ""}{"        self.mn[i] += delta" + chr(10) if "mn" in fields else ""}{"        self.tot[i] += delta * k" + chr(10) if S else ""}        self.andAll[i] = ((self.andAll[i] & a) ^ x) & FULL
        self.orAll[i] = ((self.orAll[i] & a) ^ x) & FULL
        self.tagAnd[i] = self.tagAnd[i] & a & FULL
        self.tagXor[i] = ((self.tagXor[i] & a) ^ x) & FULL

    def _push(self, i, tl, tr):
        if tl == tr:
            return
        a = self.tagAnd[i]; x = self.tagXor[i]
        if a == self.FULL and x == 0:
            return
{"        tm = (tl + tr) // 2" + chr(10) if S else ""}        self._apply(2 * i, a, x{", tm - tl + 1" if S else ""})
        self._apply(2 * i + 1, a, x{", tr - tm" if S else ""})
        self.tagAnd[i] = self.FULL; self.tagXor[i] = 0

    # nothing changes iff for every value v in the node, (v & a) ^ x == v.
    # per bit: keep (a=1,x=0) always fine; flip (a=1,x=1) always changes;
    # force-0 (a=0,x=0) fine only if already 0 everywhere; force-1 fine only if already 1 everywhere.
    def _noEffect(self, i, a, x):
        FULL = self.FULL
        if a & x & FULL: return False
        if ~a & ~x & self.orAll[i] & FULL: return False
        if ~a & x & ~self.andAll[i] & FULL: return False
        return True

    def _upd(self, i, tl, tr, ql, qr, a, x):
        if qr < tl or ql > tr:
            return
        if self._noEffect(i, a, x):
            return
        mixed = (self.andAll[i] ^ self.orAll[i]) & self.FULL
        if ql <= tl and qr >= tr and (mixed & (~a | x) & self.FULL) == 0:
            self._apply(i, a, x{", tr - tl + 1" if S else ""})
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        self._upd(2 * i, tl, tm, ql, qr, a, x)
        self._upd(2 * i + 1, tm + 1, tr, ql, qr, a, x)
        self._pull(i)

    ################ PUBLIC METHODS START HERE ################

    # O(logN logU) -- a[i] &= X for i in [l, r]
    def rangeAndApply(self, l, r, X):
        if l <= r and self.n: self._upd(1, 0, self.n - 1, l, r, X & self.FULL, 0)

    # O(logN logU) -- a[i] |= X for i in [l, r]
    def rangeOrApply(self, l, r, X):
        if l <= r and self.n: self._upd(1, 0, self.n - 1, l, r, ~X & self.FULL, X & self.FULL)

    def _set(self, i, tl, tr, p, v):
        if tl == tr:
            {leaf}
            self.tagAnd[i] = self.FULL; self.tagXor[i] = 0
            return
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        if p <= tm: self._set(2 * i, tl, tm, p, v)
        else: self._set(2 * i + 1, tm + 1, tr, p, v)
        self._pull(i)

    # O(logN) -- a[p] = v
    def pointAssign(self, p, v):
        if self.n: self._set(1, 0, self.n - 1, p, v & self.FULL)

    def _q(self, i, tl, tr, ql, qr, kind):
        if qr < tl or ql > tr:
            return None
        if ql <= tl and qr >= tr:
            return ({", ".join(f"self.{f}" for f in fields)})[kind][i]
        self._push(i, tl, tr)
        tm = (tl + tr) // 2
        a = self._q(2 * i, tl, tm, ql, qr, kind)
        b = self._q(2 * i + 1, tm + 1, tr, ql, qr, kind)
        if a is None: return b
        if b is None: return a
'''
    for j, (f, op, pyc, _, _) in enumerate(aggs):
        out += f"        return {pyc}\n" if j == len(aggs) - 1 else f"        if kind == {j}: return {pyc}\n"
    out += "\n"
    empty = {"rangeMax": "None", "rangeMin": "None", "rangeSum": "0", "rangeAndQuery": "self.FULL", "rangeOrQuery": "0"}
    for j, (f, op, *_ ) in enumerate(aggs):
        out += (f"    # O(logN) -- {DESC[op]}\n    def {op}(self, l, r): return {empty[op]} if (l > r or not self.n) else "
                f"self._q(1, 0, self.n-1, l, r, {j})\n")
    out += '''    # O(logN) -- a[p]
    def pointGet(self, p): return self.rangeAndQuery(p, p)

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)
'''
    return out


def cpp(ops, aggs):
    fields = [f for f, *_ in aggs]
    S = "tot" in fields
    shift = [f for f in fields if f in ("mx", "mn", "tot")]
    tfields = [f for f in fields if f != "tot"] + ["tagAnd", "tagXor"]
    init = {"mx": "mx(4 * max(1, n))", "mn": "mn(4 * max(1, n))", "andAll": "andAll(4 * max(1, n), FULL)",
            "orAll": "orAll(4 * max(1, n))", "tagAnd": "tagAnd(4 * max(1, n), FULL)", "tagXor": "tagXor(4 * max(1, n))",
            "tot": "tot(4 * max(1, n))"}
    inits = ", ".join(init[f] for f in tfields + (["tot"] if S else []))
    leaf = " = ".join(f"{f}[i]" for f in fields if f != "tot") + " = v" + (", tot[i] = v" if S else "")
    names = {"mx": "max", "mn": "min", "tot": "sum", "andAll": "and", "orAll": "or"}
    shifts = ", ".join(f"{f}[i] += delta" if f != "tot" else "tot[i] += S(delta) * k" for f in shift)
    out = header("//", ops, fields) + f'''
// Bitwise segment tree beats: range and= / or=, range {" / ".join(names[f] for f in fields)}, point ops.
// All indices 0-based, ranges inclusive. Values live in [0, 2^bits). Every update is the map v -> (v & a) ^ x:
//   and X -> (X, 0)   or X -> (~X, X)
// and those compose into one (and, xor) tag. A tag may only be applied to a whole node when every bit the node's
// values DISAGREE on is merely kept (mixed & (~a | x) == 0){": then every value moves by the same delta, so " + " / ".join(names[f] for f in shift) + " just shift" if shift else ""}.
// Otherwise recurse; each recursion makes a mixed bit uniform, which pays for it.
// No range xor: xor flips a mixed bit without making it uniform, so it could recurse to every leaf, O(N) per op.
// For xor with sums use BitCountTree (per-bit counts), which needs no beats at all.
// T: int, long long, ...{"; sums accumulate in S (long long for small T)" if S else ""}.
template <typename T>
struct BitBeats {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    T FULL;
    vector<T> {", ".join(tfields)};
{"    vector<S> tot;" + chr(10) if S else ""}
    // O(N)
    explicit BitBeats(const vector<T>& a, int bits = 20)
        : n((int)a.size()), FULL(T((T(1) << bits) - 1)), {inits} {{
        if (n) build(1, 0, n - 1, a);
    }}

    void setLeaf(int i, T v) {{
        {leaf};
        tagAnd[i] = FULL, tagXor[i] = 0;
    }}

    void build(int i, int tl, int tr, const vector<T>& a) {{
        if (tl == tr) {{ setLeaf(i, a[tl]); return; }}
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }}

    void pull(int i) {{
        int l = 2 * i, r = l + 1;
{"        mx[i] = max(mx[l], mx[r]);" + chr(10) if "mx" in fields else ""}{"        mn[i] = min(mn[l], mn[r]);" + chr(10) if "mn" in fields else ""}{"        tot[i] = tot[l] + tot[r];" + chr(10) if S else ""}        andAll[i] = andAll[l] & andAll[r], orAll[i] = orAll[l] | orAll[r];
        tagAnd[i] = FULL, tagXor[i] = 0;
    }}

    // only legal when the node's mixed bits are all kept{", so every value shifts by the same delta" if shift else ""}{" (k = the node's length)" if S else ""}
    void apply(int i, T a, T x{", long long k" if S else ""}) {{
{f"""        T keep = (a ^ x) & FULL;
        T delta = (~orAll[i] & x & FULL) - (andAll[i] & ~keep & FULL);
        {shifts};
""" if shift else ""}        andAll[i] = ((andAll[i] & a) ^ x) & FULL, orAll[i] = ((orAll[i] & a) ^ x) & FULL;
        tagAnd[i] = tagAnd[i] & a & FULL, tagXor[i] = ((tagXor[i] & a) ^ x) & FULL;
    }}

    void push(int i, int tl, int tr) {{
        if (tl == tr || (tagAnd[i] == FULL && tagXor[i] == 0)) return;
{"        int tm = (tl + tr) / 2;" + chr(10) if S else ""}        apply(2 * i, tagAnd[i], tagXor[i]{", tm - tl + 1" if S else ""}), apply(2 * i + 1, tagAnd[i], tagXor[i]{", tr - tm" if S else ""});
        tagAnd[i] = FULL, tagXor[i] = 0;
    }}

    // (v & a) ^ x == v for every v in the node? keep bits are fine, flip bits never are, force-0 needs all 0,
    // force-1 needs all 1
    bool noEffect(int i, T a, T x) const {{
        if (a & x & FULL) return false;
        if (~a & ~x & orAll[i] & FULL) return false;
        if (~a & x & ~andAll[i] & FULL) return false;
        return true;
    }}

    void upd(int i, int tl, int tr, int ql, int qr, T a, T x) {{
        if (qr < tl || ql > tr || noEffect(i, a, x)) return;
        T mixed = (andAll[i] ^ orAll[i]) & FULL;
        if (ql <= tl && tr <= qr && (mixed & (~a | x) & FULL) == 0) {{ apply(i, a, x{", tr - tl + 1" if S else ""}); return; }}
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        upd(2 * i, tl, tm, ql, qr, a, x), upd(2 * i + 1, tm + 1, tr, ql, qr, a, x);
        pull(i);
    }}

    void set(int i, int tl, int tr, int p, T v) {{
        if (tl == tr) {{ setLeaf(i, v); return; }}
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        if (p <= tm) set(2 * i, tl, tm, p, v);
        else set(2 * i + 1, tm + 1, tr, p, v);
        pull(i);
    }}

    // kind: {", ".join(f"{j} {names[f]}" for j, f in enumerate(fields))}; identities are valid because every value is in [0, FULL]
    S query(int i, int tl, int tr, int ql, int qr, int kind) {{
        if (qr < tl || ql > tr) {{
            switch (kind) {{
'''
    for j, (f, op, _, cc, ident) in enumerate(aggs):
        out += f"                {'default' if j == len(aggs) - 1 else f'case {j}'}: return {ident};\n"
    out += '''            }
        }
        if (ql <= tl && tr <= qr) {
            switch (kind) {
'''
    for j, (f, *_ ) in enumerate(aggs):
        out += f"                {'default' if j == len(aggs) - 1 else f'case {j}'}: return {f}[i];\n"
    out += '''            }
        }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        S a = query(2 * i, tl, tm, ql, qr, kind), b = query(2 * i + 1, tm + 1, tr, ql, qr, kind);
        switch (kind) {
'''
    for j, (f, op, _, cc, _) in enumerate(aggs):
        out += f"            {'default' if j == len(aggs) - 1 else f'case {j}'}: return {cc};\n"
    out += '''        }
    }

    // amortized O(logN logU) -- a[i] &= X for i in [l, r]
    void rangeAndApply(int l, int r, T X) { if (l <= r && n) upd(1, 0, n - 1, l, r, X & FULL, 0); }

    // amortized O(logN logU) -- a[i] |= X for i in [l, r]
    void rangeOrApply(int l, int r, T X) { if (l <= r && n) upd(1, 0, n - 1, l, r, ~X & FULL, X & FULL); }
'''
    pub = {"rangeMax": "T rangeMax(int l, int r) {{ return T(query(1, 0, n - 1, l, r, {j})); }}",
           "rangeMin": "T rangeMin(int l, int r) {{ return T(query(1, 0, n - 1, l, r, {j})); }}",
           "rangeSum": "S rangeSum(int l, int r) {{ return l > r || !n ? S(0) : query(1, 0, n - 1, l, r, {j}); }}",
           "rangeAndQuery": "T rangeAndQuery(int l, int r) {{ return l > r || !n ? FULL : T(query(1, 0, n - 1, l, r, {j})); }}",
           "rangeOrQuery": "T rangeOrQuery(int l, int r) {{ return l > r || !n ? T(0) : T(query(1, 0, n - 1, l, r, {j})); }}"}
    for j, (f, op, *_ ) in enumerate(aggs):
        out += f"\n    // O(logN) -- {DESC[op]}\n    " + pub[op].format(j=j) + "\n"
    out += '''
    // O(logN) -- a[i] = v & FULL
    void pointAssign(int i, T v) { if (n) set(1, 0, n - 1, i, v & FULL); }

    // O(logN) -- a[i]
    T pointGet(int i) { return rangeAndQuery(i, i); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = (a[i] + delta) & FULL
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }
};
'''
    return out


def main():
    for r in range(4):
        for extra in itertools.combinations(["rangeMax", "rangeMin", "rangeSum"], r):
            ops = sorted(POINT + BASE + list(extra))
            aggs = [a for a in AGGS if a[1] in BASE or a[1] in extra]
            folder = os.path.join(DIR, "-".join(ops))
            os.makedirs(folder, exist_ok=True)
            write_template(os.path.join(folder, "template.py"), python(ops, aggs))
            write_template(os.path.join(folder, "template.cpp"), cpp(ops, aggs))
            print("wrote", os.path.basename(folder))


if __name__ == "__main__":
    main()
