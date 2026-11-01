"""xor / OR / AND of the values in a value range inside a[l..r], WITH point updates: a segment tree over positions whose
every node is a dynamic value seg tree over [valLo, valHi] keeping, per value node, how many copies are below it and
the OR / AND (and xor) of the values present. OR and AND can't be undone, so a BIT's prefix difference (as in
gen_dynamic_order.py, which covers xor alone) doesn't work: a query combines the O(log N) segment nodes covering [l, r],
each answering its value range in O(log U).

    python3 gen_seg_of_trees.py

One template per set of kept aggregates with OR or AND in it (xor alone is the BIT of value trees, lighter).
"""
import itertools
import os

from gen_wavelet import BIT_SUFFIXES
from note_lang import add_get_all, folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
DTYPE = "seg-of-trees"
WORD = {"xor": "xor", "or": "OR", "and": "AND"}
FIELD = {"xor": "X", "or": "O", "and": "A"}
OPC = {"xor": "^", "or": "|", "and": "&"}
ID_PY = {"xor": "0", "or": "0", "and": "-1"}
ID_CPP = {"xor": "T(0)", "or": "T(0)", "and": "~T(0)"}
WHAT = {"LtX": "the values < x", "LteX": "the values <= x", "GtX": "the values > x", "GteX": "the values >= x",
        "InValRange": "the a[i] with lowVal <= a[i] <= highVal"}


def header(cm, ops, aggs):
    q = "log(N)*log(U)"
    lines = [f"@operations: {' '.join(ops)}", f"@data-structure-type: {DTYPE}", "@complexities:"]
    lines += [f"  {op}: {'1' if op == 'pointGet' else 'N' if op == 'getAll' else q}" for op in ops] + ["  build: N*log(N)*log(U)"]
    per = "1*N*log(N)*log(U)"
    node = " ".join(f"{f}[{per}]" for f in ["L", "R", "C"] + [FIELD[a] for a in aggs])
    lines += ["@memory:", "  layout: none", f"  node: {node}", "  tags: none", "  other: root[2*N] arr[1*N]",
              "  note: segment tree over positions (2N nodes, bottom-up), each node a dynamic value seg tree over [valLo, "
              "valHi] (U = its size); value nodes are never freed, so each point update adds up to 2 log N log U of them"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def _doc(agg, suf):
    empty = ID_PY[agg] + (" (every bit)" if agg == "and" else "")
    return f"{WORD[agg]} of {WHAT[suf]} in a[l..r]" + (" (copies count)" if agg == "xor" else "") + f"; {empty} if there are none"


# ------------------------------------------------------------------------------------------------ Python

def python(ops, aggs):
    slots = ["arr", "n", "vlo", "vhi", "root", "L", "R", "C"] + [FIELD[a] for a in aggs]
    p = ['''# xor / OR / AND of the values in a value range inside a[l..r], with point updates. A segment tree over positions
# (bottom-up: node p >= n is a[p - n], node p < n covers its children's positions); every node keeps a dynamic value
# seg tree over [valLo, valHi] of the values at its positions: per value node, the copies below it''' +
         "".join(f", the {WORD[a]}" for a in aggs) + '''
# of the values present. a[l..r] is O(log N) segment nodes, and each answers a value range in O(log U).
# Values are integers; query arguments (x, lowVal, ...) can be anything.


class SegOfValueTrees:
''' + f"    __slots__ = ({', '.join(repr(s) for s in slots)})\n\n" + '''    # O(N log N log U) -- arr: the initial array (a list), 0-indexed; every value a[i] ever holds must lie in
    # [valLo, valHi] (any integers, negative is fine; U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        self.arr = list(arr)
        self.n = n = len(arr)
        self.vlo, self.vhi = valLo, valHi
        self.root = [0] * (2 * n)  # segment node p's value tree (0: empty)
        self.L, self.R, self.C = [0], [0], [0]  # value node 0 = the empty tree
''' + "".join(f"        self.{FIELD[a]} = [{ID_PY[a]}]  # {WORD[a]} of the values present below\n" for a in aggs) + '''        for i, v in enumerate(arr):
            self._add(i, v, 1)

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]

    # O(logN logU) -- a[i] = v
    def pointAssign(self, i, v):
        old = self.arr[i]
        if v != old:
            self._add(i, old, -1)
            self._add(i, v, 1)
            self.arr[i] = v

    # O(logN logU) -- a[i] += v
    def pointAdd(self, i, v):
        self.pointAssign(i, self.arr[i] + v)

    # O(logN logU) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        self.pointAssign(i, max(self.arr[i], v))

    # O(logN logU) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        self.pointAssign(i, min(self.arr[i], v))
''']
    for a in aggs:
        for suf in BIT_SUFFIXES:
            args = "lowVal, highVal" if suf == "InValRange" else "x"
            rng = {"LtX": "self.vlo, x - 1", "LteX": "self.vlo, x", "GtX": "x + 1, self.vhi", "GteX": "x, self.vhi",
                   "InValRange": "lowVal, highVal"}[suf]
            p.append(f'''
    # O(logN logU) -- {_doc(a, suf)}
    def {a}{suf}(self, l, r, {args}):
        return self._{a}(l, r, {rng})
''')
    new = ["        self.L.append(0), self.R.append(0), self.C.append(0)"] + [f"        self.{FIELD[a]}.append({ID_PY[a]})" for a in aggs]
    bitwise = [a for a in aggs if a != "xor"]
    p.append('''
    # ---- internals ----

    # a[i] = v gains d copies in every segment node over i
    def _add(self, i, v, d):
        root, p = self.root, i + self.n
        while p:
            root[p] = self._ins(root[p], v, d)
            p >>= 1

    def _newNode(self):
''' + "\n".join(new) + '''
        return len(self.C) - 1

    # value tree t (0: a new one) with d more copies of v
    def _ins(self, t, v, d):
        L, R, C = self.L, self.R, self.C
''' + ("        X = self.X\n" if "xor" in aggs else "") + '''        if not t:
            t = self._newNode()
        top, nl, nh = t, self.vlo, self.vhi
''' + ("        path = []\n" if bitwise else "") + '''        while True:
            C[t] += d
''' + ("            if d & 1:\n                X[t] ^= v\n" if "xor" in aggs else "") + ("            path.append(t)\n" if bitwise else "") + '''            if nl == nh:
                break
            mid = (nl + nh) >> 1
            if v <= mid:
                if not L[t]:
                    L[t] = self._newNode()
                t, nh = L[t], mid
            else:
                if not R[t]:
                    R[t] = self._newNode()
                t, nl = R[t], mid + 1
''' + ('''        c = C[t]
        if not c or c == d:  # v appeared or disappeared here: OR / AND again up the path
''' + "".join(f"            {FIELD[a]} = self.{FIELD[a]}\n            {FIELD[a]}[t] = v if c else {ID_PY[a]}\n" for a in bitwise) + '''            for u in reversed(path[:-1]):
''' + "".join(f"                {FIELD[a]}[u] = {FIELD[a]}[L[u]] {OPC[a]} {FIELD[a]}[R[u]]\n" for a in bitwise) if bitwise else "") + '''        return top
''')
    for a in aggs:
        f, op, ident = FIELD[a], OPC[a], ID_PY[a]
        p.append(f'''
    # {WORD[a]} of the values in [lo, hi] over a[l..r]: the segment nodes covering [l, r], each a value range walk
    def _{a}(self, l, r, lo, hi):
        res = {ident}
        if lo > hi:
            return res
        root, l, r = self.root, l + self.n, r + self.n + 1
        while l < r:
            if l & 1:
                res {op}= self._{a}In(root[l], lo, hi)
                l += 1
            if r & 1:
                r -= 1
                res {op}= self._{a}In(root[r], lo, hi)
            l >>= 1
            r >>= 1
        return res

    # {WORD[a]} of value tree t's values in [lo, hi]: whole value nodes inside it, at most 4 a level
    def _{a}In(self, t, lo, hi):
        L, R, F, res = self.L, self.R, self.{f}, {ident}
        stack = [(t, self.vlo, self.vhi)]
        while stack:
            t, nl, nh = stack.pop()
            if not t or nh < lo or hi < nl:
                continue
            if lo <= nl and nh <= hi:
                res {op}= F[t]
                continue
            mid = (nl + nh) >> 1
            stack.append((L[t], nl, mid))
            stack.append((R[t], mid + 1, nh))
        return res
''')
    return "".join(p)


# ------------------------------------------------------------------------------------------------ C++

def cpp(ops, aggs):
    bitwise = [a for a in aggs if a != "xor"]
    c = ['''// xor / OR / AND of the values in a value range inside a[l..r], with point updates. A segment tree over positions
// (bottom-up: node p >= n is a[p - n], node p < n covers its children's positions); every node keeps a dynamic value
// seg tree over [valLo, valHi] of the values at its positions: per value node, the copies below it''' +
         "".join(f", the {WORD[a]}" for a in aggs) + '''
// of the values present. a[l..r] is O(log N) segment nodes, and each answers a value range in O(log U).
// Values are integers; query arguments (x, lowVal, ...) can be anything. T: int, long long, ...
template <typename T>
struct SegOfValueTrees {
    int n;
    long long vlo, vhi;
    vector<T> arr;
    vector<int> root, L, R, C;  // root[p]: segment node p's value tree; value node 0 = the empty tree
''' + "".join(f"    vector<T> {FIELD[a]};  // {WORD[a]} of the values present below\n" for a in aggs) + '''
    // O(N log N log U) -- arr: the initial array, 0-indexed; every value a[i] ever holds must lie in [valLo, valHi]
    // (any integers, negative is fine; U = valHi - valLo + 1)
    SegOfValueTrees(const vector<T>& a, long long valLo, long long valHi)
        : n((int)a.size()), vlo(valLo), vhi(valHi), arr(a), root(2 * n, 0), L(1, 0), R(1, 0), C(1, 0)''' +
         "".join(f", {FIELD[a]}(1, {ID_CPP[a]})" for a in aggs) + ''' {
        for (int i = 0; i < n; i++) add(i, a[i], 1);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }

    // O(logN logU) -- a[i] = v
    void pointAssign(int i, T v) {
        if (v == arr[i]) return;
        add(i, arr[i], -1), add(i, v, 1), arr[i] = v;
    }

    // O(logN logU) -- a[i] += v
    void pointAdd(int i, T v) { pointAssign(i, arr[i] + v); }

    // O(logN logU) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { pointAssign(i, max(arr[i], v)); }

    // O(logN logU) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { pointAssign(i, min(arr[i], v)); }
''']
    for a in aggs:
        for suf in BIT_SUFFIXES:
            params = "T lowVal, T highVal" if suf == "InValRange" else "T x"
            rng = {"LtX": "vlo, (long long)x - 1", "LteX": "vlo, (long long)x", "GtX": "(long long)x + 1, vhi",
                   "GteX": "(long long)x, vhi", "InValRange": "(long long)lowVal, (long long)highVal"}[suf]
            c.append(f'''
    // O(logN logU) -- {_doc(a, suf)}
    T {a}{suf}(int l, int r, {params}) const {{ return {a}Range(l, r, {rng}); }}
''')
    c.append('''
    // ---- internals ----

    // a[i] = v gains d copies in every segment node over i
    void add(int i, T v, int d) {
        for (int p = i + n; p; p >>= 1) {
            int t = ins(root[p], v, d);
            root[p] = t;
        }
    }

    int newNode() {
        L.push_back(0), R.push_back(0), C.push_back(0);
''' + "".join(f"        {FIELD[a]}.push_back({ID_CPP[a]});\n" for a in aggs) + '''        return (int)C.size() - 1;
    }

    // value tree t (0: a new one) with d more copies of v
    int ins(int t, T v, int d) {
        if (!t) t = newNode();
        int top = t;
        long long nl = vlo, nh = vhi;
''' + ("        int path[130], dep = 0;\n" if bitwise else "") + '''        while (true) {
            C[t] += d;
''' + ("            if (d & 1) X[t] ^= v;\n" if "xor" in aggs else "") + ("            path[dep++] = t;\n" if bitwise else "") + '''            if (nl == nh) break;
            long long mid = nl + (nh - nl) / 2;
            if (v <= mid) {
                if (!L[t]) { int x = newNode(); L[t] = x; }
                t = L[t], nh = mid;
            } else {
                if (!R[t]) { int x = newNode(); R[t] = x; }
                t = R[t], nl = mid + 1;
            }
        }
''' + (('''        if (!C[t] || C[t] == d) {  // v appeared or disappeared here: OR / AND again up the path
''' + "".join(f"            {FIELD[a]}[t] = C[t] ? v : {ID_CPP[a]};\n" for a in bitwise) + '''            for (int k = dep - 2; k >= 0; k--) {
                int u = path[k];
''' + "".join(f"                {FIELD[a]}[u] = {FIELD[a]}[L[u]] {OPC[a]} {FIELD[a]}[R[u]];\n" for a in bitwise) + '''            }
        }
''') if bitwise else "") + '''        return top;
    }
''')
    for a in aggs:
        f, op, ident = FIELD[a], OPC[a], ID_CPP[a]
        c.append(f'''
    // {WORD[a]} of the values in [lo, hi] over a[l..r]: the segment nodes covering [l, r], each a value range walk
    T {a}Range(int l, int r, long long lo, long long hi) const {{
        T res = {ident};
        if (lo > hi) return res;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {{
            if (l & 1) res {op}= {a}In(root[l++], lo, hi);
            if (r & 1) res {op}= {a}In(root[--r], lo, hi);
        }}
        return res;
    }}

    // {WORD[a]} of value tree t's values in [lo, hi]: whole value nodes inside it, at most 4 a level
    T {a}In(int t, long long lo, long long hi) const {{
        T res = {ident};
        array<long long, 3> st[260];
        int sp = 0;
        st[sp++] = {{t, vlo, vhi}};
        while (sp) {{
            auto [u, nl, nh] = st[--sp];
            if (!u || nh < lo || hi < nl) continue;
            if (lo <= nl && nh <= hi) {{
                res {op}= {f}[u];
                continue;
            }}
            long long mid = nl + (nh - nl) / 2;
            st[sp++] = {{L[u], nl, mid}};
            st[sp++] = {{R[u], mid + 1, nh}};
        }}
        return res;
    }}
''')
    c.append("};\n")
    return "".join(c)


def main():
    for xr in (False, True):
        for bits in (("or",), ("and",), ("or", "and")):
            aggs = (("xor",) if xr else ()) + bits
            ops = sorted(POINT + [a + s for a in aggs for s in BIT_SUFFIXES] + ["getAll"])
            name = folder_name(ops)  # (the site names folders by their ops unless the list is too long for a folder name)
            folder = os.path.join(DIR, name if len(name) <= 180 else f"{DTYPE}-" + "-".join(aggs))
            os.makedirs(folder, exist_ok=True)
            write_template(os.path.join(folder, "template.py"), header("#", ops, aggs) + "\n" + add_get_all(python(ops, aggs), "py"))
            write_template(os.path.join(folder, "template.cpp"), header("//", ops, aggs) + "\n" + add_get_all(cpp(ops, aggs), "cpp"))
            print("wrote", os.path.basename(folder))


if __name__ == "__main__":
    main()
