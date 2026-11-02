"""copy(l, r): a[l..r] as a treap of its own in O(log N) however long it is (the original is unchanged), alongside the
sequence edits; paste it anywhere (paste(i, t.copy(l, r)) inserts a copy of a range). Lengths are long long: copies
pasted into themselves double, so an array can pass 2^31 (or 10^18) values with few nodes.

    python3 gen_persistent_treap.py

A persistent implicit treap: no node is ever changed after it is made; an update copies the O(log N) nodes on its paths
and the rest is shared, so a copied range is just a pointer to the same nodes. Pending reverses are pushed into fresh
copies of the children. With nodes shared, fixed random priorities would no longer be independent, so merge picks its
root at random weighted by subtree size (a is the root with probability |a| / (|a| + |b|)), which keeps every tree a
random one: O(log N) expected depth. Queries don't change the root at all. Memory grows by O(log N) nodes per update
(nothing is freed). Four templates: with or without rangeSum, with or without rangeReverse (without it no node keeps a
reverse flag and the walks need no flip bookkeeping).
"""
import os

import shutil

from gen_treap_algebra import POOL_NOTE, piece_example
from gen_treap import wrap
from gen_treap_more import slots_line
from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
DTYPE = "persistent-treap"
BASE = ["append", "appendLeft", "copy", "cut", "getAll", "insertAt", "merge", "paste", "pointAssign",
        "pointGet", "split", "trisect"]


def header(cm, ops, sums):
    lines = [f"@operations: {' '.join(ops)}", f"@data-structure-type: {DTYPE}", "@complexities:"]
    lines += [f"  {op}: {'N' if op == 'getAll' else 'log(N) expected'}" for op in ops] + ["  build: N", "@memory:", "  layout: none",
              "  node: " + " ".join(f"{f}[1*N*log(N)]" for f in ["val", "sz", "L", "R"] + (["sm"] if sums else [])),
              "  tags: " + ("rev[1*N*log(N)]" if "rangeReverse" in ops else "none"), "  other: none",
              "  note: nodes are never changed or freed: each update copies O(log N) of them (N here counts updates too), "
              "and copies share every node they don't change; log(N) is of the length, which can be huge (long long)"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def desc(rv):
    return ("Persistent implicit treap: an array you can insert into anywhere, cut pieces out of (that is how to erase) and "
            "paste them back" + (", reverse," if rv else "") +
            " and copy (copy(l, r): a[l..r] as a treap of its own, O(logN) however long, since the copy shares the same "
            "nodes; this one is unchanged), each in O(logN) expected. No node changes after it is made: updates copy the "
            "nodes on their paths, so a copy and its original never affect each other. Merge picks its root at random "
            "weighted by size, so shared nodes need no priorities. Lengths and indices are long long (copies pasted into "
            "each other double). All indices 0-based, ranges inclusive, always positions in the CURRENT array.")


def python(ops, sums):
    S, RV = sums, "rangeReverse" in ops
    slots = ["root", "val", "sz", "L", "R"] + (["rev"] if RV else []) + (["sm"] if S else [])
    opn = (lambda t: f"self._open({t})") if RV else (lambda t: f"self.val[{t}], self.L[{t}], self.R[{t}]")
    return header("#", ops, S) + "\n" + wrap(desc(RV), "#") + f'''import random


class PersistentTreap:
''' + wrap(POOL_NOTE.format(cls="PersistentTreap"), "    #") + "".join(f"    {n} = [0]\n" for n in slots[1:]) + '''    __slots__ = ("root",)

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self.root = self._build(list(arr), 0, len(arr))

    def _empty(self):  # a new, empty PersistentTreap (on the same pool, like every one)
        return PersistentTreap()

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(logN) expected -- a[l..r] (leave out l and r: the whole array, O(1)) as a PersistentTreap of its own; this one
    # is unchanged. The copy shares this one's nodes, so it costs O(logN) however long it is
    def copy(self, l=0, r=None):
        if r is None:
            r = self.size() - 1
        piece = self._empty()
        piece.root = self.root if l == 0 and r == self.size() - 1 else self._cut(self.root, l, r)[1]
        return piece

    # O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        x, y = self._split(self.root, i)
        self.root = self._merge(self._merge(x, self._new(v, 0, 0)), y)

    # O(logN) expected -- append v to the end
    def append(self, v):
        self.root = self._merge(self.root, self._new(v, 0, 0))

    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
    def cut(self, l, r):
        a, b, c = self._cut(self.root, l, r)
        self.root = self._merge(a, c)
        piece = self._empty()
        piece.root = b
        return piece

    # O(logN) expected -- insert all of other (any PersistentTreap, e.g. a cut piece) so it starts at a[i]
    # (0 <= i <= size()); other is left empty
    def paste(self, i, other):
        x, y = self._split(self.root, i)
        self.root = self._merge(self._merge(x, other.root), y)
        other.root = 0

    # O(logN) expected -- append all of other at the end, leaving it empty (it must share this treap's nodes)
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(logN) expected -- (a[0..k-1], a[k..]) as two PersistentTreaps of their own; this one is left empty
    def split(self, k):
        left, right = self._empty(), self._empty()
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right

    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PersistentTreaps of their own; this one is left empty
    def trisect(self, l, r):
        left, mid, right = self._empty(), self._empty(), self._empty()
        left.root, mid.root, right.root = self._cut(self.root, l, r)
        self.root = 0
        return left, mid, right
''' + ('''
    # O(logN) expected -- reverse a[l..r] in place
    def rangeReverse(self, l, r):
        a, b, c = self._cut(self.root, l, r)
        self.root = self._merge(self._merge(a, self._flip(b)), c)
''' if RV else "") + '''
    # O(logN) expected -- a[i] = v
    def pointAssign(self, i, v):
        a, b, c = self._cut(self.root, i, i)
        self.root = self._merge(self._merge(a, self._new(v, 0, 0)), c)
''' + ('''
    # O(logN) expected -- a[i] (a read-only walk: pending reverses only swap which child is which)
    def pointGet(self, i):
        L, R, sz, rev, val = self.L, self.R, self.sz, self.rev, self.val
        t, flip = self.root, False
        while True:
            lt, rt = (R[t], L[t]) if flip else (L[t], R[t])
            flip ^= bool(rev[t])
            if i < sz[lt]:
                t = lt
            elif i == sz[lt]:
                return val[t]
            else:
                i -= sz[lt] + 1
                t = rt
''' if RV else '''
    # O(logN) expected -- a[i] (a read-only walk)
    def pointGet(self, i):
        L, R, sz, val = self.L, self.R, self.sz, self.val
        t = self.root
        while True:
            lt = L[t]
            if i < sz[lt]:
                t = lt
            elif i == sz[lt]:
                return val[t]
            else:
                i -= sz[lt] + 1
                t = R[t]
''') + ('''
    # O(logN) expected -- a[l] + ... + a[r] (the root doesn't change)
    def rangeSum(self, l, r):
        return self.sm[self._cut(self.root, l, r)[1]]
''' if S else "") + ('''
    # O(N) -- the whole current array
    def getAll(self):
        L, R, rev, val = self.L, self.R, self.rev, self.val
        out, stack, t, flip = [], [], self.root, False
        while stack or t:
            while t:  # (a subtree's flip: whether its children are swapped, from the reverses pending above it)
                stack.append((t, flip))
                lt = R[t] if flip else L[t]
                flip ^= bool(rev[t])
                t = lt
            t, flip = stack.pop()
            out.append(val[t])
            rt = L[t] if flip else R[t]
            flip ^= bool(rev[t])
            t = rt
        return out
''' if RV else '''
    # O(N) -- the whole current array
    def getAll(self):
        L, R, val = self.L, self.R, self.val
        out, stack, t = [], [], self.root
        while stack or t:
            while t:
                stack.append(t)
                t = L[t]
            t = stack.pop()
            out.append(val[t])
            t = R[t]
        return out
''') + '''
    # ---- internals: every function returns new nodes and leaves its arguments as they were ----
''' + ('''
    def _new(self, v, l, r, rv=0):
        self.val.append(v), self.L.append(l), self.R.append(r), self.rev.append(rv)
''' if RV else '''
    def _new(self, v, l, r):
        self.val.append(v), self.L.append(l), self.R.append(r)
''') + '''        self.sz.append(self.sz[l] + self.sz[r] + 1)
''' + ("        self.sm.append(self.sm[l] + v + self.sm[r])\n" if S else "") + '''        return len(self.val) - 1
''' + ('''
    def _flip(self, t):  # t reversed: a copy with its children swapped and a pending reverse for them
        return self._new(self.val[t], self.R[t], self.L[t], self.rev[t] ^ 1) if t else 0

    def _open(self, t):  # (value, left, right) of t with its pending reverse handed to (copies of) the children
        if self.rev[t]:
            return self.val[t], self._flip(self.L[t]), self._flip(self.R[t])
        return self.val[t], self.L[t], self.R[t]
''' if RV else "") + f'''
    def _build(self, arr, lo, hi):  # a balanced tree of arr[lo:hi]
        if lo >= hi:
            return 0
        mid = (lo + hi) // 2
        return self._new(arr[mid], self._build(arr, lo, mid), self._build(arr, mid + 1, hi))

    def _split(self, t, k):  # (first k of t, the rest)
        if not t:
            return 0, 0
        v, l, r = {opn("t")}
        if self.sz[l] >= k:
            a, b = self._split(l, k)
            return a, self._new(v, b, r)
        a, b = self._split(r, k - self.sz[l] - 1)
        return self._new(v, l, a), b

    def _merge(self, a, b):  # a's elements, then b's; the root is a with probability |a| / (|a| + |b|)
        if not a or not b:
            return a or b
        if random.randrange(self.sz[a] + self.sz[b]) < self.sz[a]:
            v, l, r = {opn("a")}
            return self._new(v, l, self._merge(r, b))
        v, l, r = {opn("b")}
        return self._new(v, self._merge(a, l), r)

    def _cut(self, t, l, r):  # (a[0..l-1], a[l..r], a[r+1..])
        a, b = self._split(t, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c
'''


def cpp(ops, sums):
    S, RV = sums, "rangeReverse" in ops
    opn = (lambda t: f"open({t}, v, l, r)") if RV else (lambda t: f"v = val[{t}], l = L[{t}], r = R[{t}]")
    return header("//", ops, S) + "\n" + wrap(desc(RV), "//") + (
        "// T: int, long long, ...; sums are kept in S (long long for small T)." if S else "// T: int, long long, ...") + '''
template <typename T>
struct PersistentTreap {
''' + ("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n" if S else "") + '''''' + (wrap(POOL_NOTE.format(cls="PersistentTreap<T>"), "    //") + "    static inline vector<T> val{T(0)};\n    static inline vector<long long> sz{0};  // (long long: copies make long arrays)\n"
                                                                          "    static inline vector<int> L{0}, R{0};\n" +
       ("    static inline vector<char> rev{0};\n" if RV else "") + ("    static inline vector<S> sm{S(0)};\n" if S else "")) + '''    int root = 0;

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit PersistentTreap(const vector<T>& arr = {}) { root = build(arr, 0, (int)arr.size()); }

    PersistentTreap makeEmpty() const { return PersistentTreap(); }  // (a new, empty one: same pool, like every one)

    // O(1) -- the current length of the array
    long long size() const { return sz[root]; }

    // O(1) -- the whole array as a PersistentTreap of its own; this one is unchanged (they share nodes)
    PersistentTreap copy() const { return *this; }

    // O(logN) expected -- a[l..r] as a PersistentTreap of its own; this one is unchanged. The copy shares this one's
    // nodes, so it costs O(logN) however long it is
    PersistentTreap copy(long long l, long long r) {
        int a, b, c;
        cut(root, l, r, a, b, c);
        PersistentTreap piece = makeEmpty();
        piece.root = b;
        return piece;
    }

    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(long long i, T v) {
        int x, y;
        split(root, i, x, y);
        root = merge(merge(x, make(v, 0, 0)), y);
    }

    // O(logN) expected -- append v to the end
    void append(T v) { root = merge(root, make(v, 0, 0)); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
    PersistentTreap cut(long long l, long long r) {
        int a, b, c;
        cut(root, l, r, a, b, c);
        root = merge(a, c);
        PersistentTreap piece = makeEmpty();
        piece.root = b;
        return piece;
    }

    // O(logN) expected -- insert all of other (any PersistentTreap, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(long long i, PersistentTreap& other) {
        int x, y;
        split(root, i, x, y);
        root = merge(merge(x, other.root), y), other.root = 0;
    }
    void paste(long long i, PersistentTreap&& other) { paste(i, other); }  // (a temporary: paste(i, t.copy(l, r)))

    // O(logN) expected -- append all of other at the end, leaving it empty (it must share this treap's nodes)
    void merge(PersistentTreap& other) { root = merge(root, other.root), other.root = 0; }
    void merge(PersistentTreap&& other) { merge(other); }  // (a temporary: merge(t.copy()))

    // O(logN) expected -- (a[0..k-1], a[k..]) as two PersistentTreaps of their own; this one is left empty
    pair<PersistentTreap, PersistentTreap> split(long long k) {
        PersistentTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PersistentTreaps of their own; this one is left empty
    tuple<PersistentTreap, PersistentTreap, PersistentTreap> trisect(long long l, long long r) {
        PersistentTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cut(root, l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }
''' + ('''
    // O(logN) expected -- reverse a[l..r] in place
    void rangeReverse(long long l, long long r) {
        int a, b, c;
        cut(root, l, r, a, b, c);
        root = merge(merge(a, flip(b)), c);
    }
''' if RV else "") + '''
    // O(logN) expected -- a[i] = v
    void pointAssign(long long i, T v) {
        int a, b, c;
        cut(root, i, i, a, b, c);
        root = merge(merge(a, make(v, 0, 0)), c);
    }
''' + ('''
    // O(logN) expected -- a[i] (a read-only walk: pending reverses only swap which child is which)
    T pointGet(long long i) const {
        int t = root;
        bool f = false;
        while (true) {
            int lt = f ? R[t] : L[t], rt = f ? L[t] : R[t];
            f ^= rev[t];
            if (i < sz[lt]) t = lt;
            else if (i == sz[lt]) return val[t];
            else i -= sz[lt] + 1, t = rt;
        }
    }
''' if RV else '''
    // O(logN) expected -- a[i] (a read-only walk)
    T pointGet(long long i) const {
        int t = root;
        while (true) {
            int lt = L[t];
            if (i < sz[lt]) t = lt;
            else if (i == sz[lt]) return val[t];
            else i -= sz[lt] + 1, t = R[t];
        }
    }
''') + ('''
    // O(logN) expected -- a[l] + ... + a[r] (the root doesn't change)
    S rangeSum(long long l, long long r) {
        int a, b, c;
        cut(root, l, r, a, b, c);
        return sm[b];
    }
''' if S else "") + ('''
    // O(N) -- the whole current array
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(size());
        vector<pair<int, bool>> st;  // (node, whether its children are swapped by the reverses pending above it)
        int t = root;
        bool f = false;
        while (!st.empty() || t) {
            while (t) {
                st.push_back({t, f});
                int lt = f ? R[t] : L[t];
                f ^= rev[t];
                t = lt;
            }
            tie(t, f) = st.back();
            st.pop_back();
            out.push_back(val[t]);
            int rt = f ? L[t] : R[t];
            f ^= rev[t];
            t = rt;
        }
        return out;
    }
''' if RV else '''
    // O(N) -- the whole current array
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(size());
        vector<int> st;
        int t = root;
        while (!st.empty() || t) {
            while (t) st.push_back(t), t = L[t];
            t = st.back(), st.pop_back();
            out.push_back(val[t]);
            t = R[t];
        }
        return out;
    }
''') + '''
    // ---- internals: every function returns new nodes and leaves its arguments as they were ----
''' + ('''
    int make(T v, int l, int r, char rv = 0) {
        val.push_back(v), L.push_back(l), R.push_back(r), rev.push_back(rv), sz.push_back(sz[l] + sz[r] + 1);
''' if RV else '''
    int make(T v, int l, int r) {
        val.push_back(v), L.push_back(l), R.push_back(r), sz.push_back(sz[l] + sz[r] + 1);
''') + ("        sm.push_back(sm[l] + S(v) + sm[r]);\n" if S else "") + '''        return (int)val.size() - 1;
    }
''' + ('''
    // t reversed: a copy with its children swapped and a pending reverse for them
    int flip(int t) { return t ? make(val[t], R[t], L[t], rev[t] ^ 1) : 0; }

    // value, left, right of t with its pending reverse handed to (copies of) the children
    void open(int t, T& v, int& l, int& r) {
        v = val[t];
        if (rev[t]) l = flip(L[t]), r = flip(R[t]);
        else l = L[t], r = R[t];
    }
''' if RV else "") + f'''
    int build(const vector<T>& arr, int lo, int hi) {{  // a balanced tree of arr[lo, hi)
        if (lo >= hi) return 0;
        int mid = (lo + hi) / 2, l = build(arr, lo, mid), r = build(arr, mid + 1, hi);
        return make(arr[mid], l, r);
    }}

    void split(int t, long long k, int& a, int& b) {{  // a = first k of t, b = the rest
        if (!t) {{ a = b = 0; return; }}
        T v;
        int l, r, x, y;
        {opn("t")};
        if (sz[l] >= k) split(l, k, x, y), a = x, b = make(v, y, r);
        else split(r, k - sz[l] - 1, x, y), a = make(v, l, x), b = y;
    }}

    int merge(int a, int b) {{  // a's elements, then b's; the root is a with probability |a| / (|a| + |b|)
        if (!a || !b) return a ? a : b;
        T v;
        int l, r;
        if (rnd() % (unsigned long long)(sz[a] + sz[b]) < (unsigned long long)sz[a]) {{
            {opn("a")};
            int m = merge(r, b);
            return make(v, l, m);
        }}
        {opn("b")};
        int m = merge(a, l);
        return make(v, m, r);
    }}

    void cut(int t, long long l, long long r, int& a, int& b, int& c) {{  // a[0..l-1], a[l..r], a[r+1..]
        split(t, l, a, b);
        split(b, r - l + 1, b, c);
    }}
}};
'''


def main():
    for d in os.listdir(DIR):  # (folder names follow the op lists)
        t = os.path.join(DIR, d, "template.py")
        if os.path.exists(t) and f"@data-structure-type: {DTYPE}" in open(t).read():
            shutil.rmtree(os.path.join(DIR, d))
    for sums in (False, True):
        for rev in (False, True):
            ops = sorted(BASE + (["rangeSum"] if sums else []) + (["rangeReverse"] if rev else []))
            folder = os.path.join(DIR, folder_name(ops))
            os.makedirs(folder, exist_ok=True)
            write_template(os.path.join(folder, "template.py"), python(ops, sums).rstrip("\n") + "\n" +
                           piece_example("py", "PersistentTreap([1, 2, 3, 4, 5])", list("12345")))
            write_template(os.path.join(folder, "template.cpp"), cpp(ops, sums) +
                           piece_example("cpp", "PersistentTreap<int> t({1, 2, 3, 4, 5})", list("12345")))
            print("wrote", os.path.basename(folder))


if __name__ == "__main__":
    raise SystemExit("retired: gen_persistent_algebra.py writes every persistent treap now (a superset of these); run that instead")
