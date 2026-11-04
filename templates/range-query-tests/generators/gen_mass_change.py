"""Mass change: rangeReplace(l, r, x, y) turns every a[i] == x with l <= i <= r into y (CF 911G), in every structure
that can do it well. Each family is on the Pareto frontier for some mix of ops / value ranges:

    python3 gen_mass_change.py

  position trees   one seg tree over the positions per distinct value (any values, hashed): a change splits x's
                   tree at [l, r] and merges the cut part into y's; every merge frees nodes, so O(log N) amortized.
                   Options: countOccurrences (a count per node), pointGet / pointAssign (a parent per node).
"""
import os
import re
import shutil

from gen_sqrt_seq import pick
from gen_treap import wrap
from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
MARKS = ("One seg tree over the positions per value", "Lazy seg tree whose tag is a value map",
         "Implicit treap whose lazy tag is a value map",
         "Blocks whose values form a union-find of classes")


# ================================================================================================ position trees

PT_MARK = MARKS[0]
PT_FIND = ["leftmostIndexOf", "leftmostIndexOfInRange", "rightmostIndexOf", "rightmostIndexOfInRange"]


def pt_variants():
    return [(cnt, point) for cnt in (False, True) for point in (False, True)]


def pt_ops(cnt, point):
    return sorted(["getAll", "rangeReplace"] + PT_FIND + (["countOccurrences"] if cnt else []) +
                  (["pointAssign", "pointGet"] if point else []))


def pt_header(cm, cnt, point):
    cost = {"getAll": "N*log(N)", "rangeReplace": "log(N) amortized", "countOccurrences": "log(N)", "pointGet": "log(N)",
            "pointAssign": "log(N) amortized", **{op: "log(N)" for op in PT_FIND}}
    ops = pt_ops(cnt, point)
    node = ["L[1*N*log(N)]", "R[1*N*log(N)]"] + (["C[1*N*log(N)]"] if cnt else []) + (
        ["P[1*N*log(N)]", "W[1*N*log(N)]"] if point else [])
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: position-trees", "@complexities:"]
    lines += [f"  {op}: {cost[op]}" for op in ops] + ["  build: N*log(N)", "@memory:", "  layout: none",
                                                     f"  node: {' '.join(node)}", "  tags: none",
                                                     "  other: roots[1*N] vals[1*N]" + (" leaf[1*N]" if point else ""),
                                                     "  note: one dynamic seg tree over the positions per distinct value; at "
                                                     "most about N log N nodes live at once (freed nodes are reused); values "
                                                     "are hashed, so any values work"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def pt_describe(cnt, point):
    return (f"{PT_MARK} (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r] into y in O(log N) "
            "amortized, for any values. Each distinct value keeps a seg tree over 0..n-1 holding the positions where it "
            "is; a change splits x's tree at [l, r] (O(log N) new nodes) and merges the cut part into y's tree (each "
            "step of a merge frees a node, so merges cost O(log N) amortized over the whole run). Also: where x first / "
            "last appears (in a range)" + (", how many times x appears in a range" if cnt else "") +
            (", a[i] and a[i] = v" if point else "") + ". All indices 0-based, ranges inclusive [l, r]; searches return "
            "-1 when nothing qualifies.")


PT_PY = '''
class PositionTrees:
    # node 0 = the empty tree; L / R: children@C@, C: how many positions below@P@, P: parent, W: which value (at roots)
    __slots__ = ("n", "L", "R"@C@, "C"@P@, "P", "W", "leaf", "ids", "vals", "roots", "free")

    # O(N log N) -- arr: the initial array (a list)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.L, self.R = [0], [0]
@C@        self.C = [0]
@P@        self.P, self.W, self.leaf = [0], [0], [0] * n
        self.ids, self.vals, self.roots, self.free = {}, [], [], []
        for i, v in enumerate(arr):
            k = self._id(v)
            self.roots[k] = self._insert(self.roots[k], i)
@P@        for k, t in enumerate(self.roots):
@P@            self.W[t] = k

    # O(1) -- the length of the array
    def size(self):
        return self.n

    # O(logN) amortized -- every a[i] == x with l <= i <= r becomes y
    def rangeReplace(self, l, r, x, y):
        k = self.ids.get(x)
        if k is not None and x != y:
            self._move(k, l, r, y)

@C@    # O(logN) -- # of i in [l, r] with a[i] == x
@C@    def countOccurrences(self, l, r, x):
@C@        k = self.ids.get(x)
@C@        return self._count(self.roots[k], 0, self.n - 1, l, r) if k is not None else 0
@C@
    # O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        k = self.ids.get(x)
        t = self.roots[k] if k is not None else 0
        if not t:
            return -1
        L, R, lo, hi = self.L, self.R, 0, self.n - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            if L[t]:
                t, hi = L[t], mid
            else:
                t, lo = R[t], mid + 1
        return lo

    # O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        k = self.ids.get(x)
        t = self.roots[k] if k is not None else 0
        if not t:
            return -1
        L, R, lo, hi = self.L, self.R, 0, self.n - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            if R[t]:
                t, lo = R[t], mid + 1
            else:
                t, hi = L[t], mid
        return lo

    # O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none
    def leftmostIndexOfInRange(self, l, r, x):
        k = self.ids.get(x)
        return self._first(self.roots[k], 0, self.n - 1, l, r, True) if k is not None else -1

    # O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none
    def rightmostIndexOfInRange(self, l, r, x):
        k = self.ids.get(x)
        return self._first(self.roots[k], 0, self.n - 1, l, r, False) if k is not None else -1

@P@    # O(logN) -- a[i]
@P@    def pointGet(self, i):
@P@        return self.vals[self._owner(i)]
@P@
@P@    # O(logN) amortized -- a[i] = v
@P@    def pointAssign(self, i, v):
@P@        k = self._owner(i)
@P@        if self.vals[k] != v:
@P@            self._move(k, i, i, v)
@P@
    # O(N log N) -- the whole current array
    def getAll(self):
        out, L, R = [None] * self.n, self.L, self.R
        for k, t in enumerate(self.roots):
            if not t:
                continue
            v, stack = self.vals[k], [(t, 0, self.n - 1)]
            while stack:
                t, lo, hi = stack.pop()
                if lo == hi:
                    out[lo] = v
                    continue
                mid = (lo + hi) >> 1
                if L[t]:
                    stack.append((L[t], lo, mid))
                if R[t]:
                    stack.append((R[t], mid + 1, hi))
        return out

    # ---- internals ----

    def _id(self, v):  # v's index into vals / roots (a new one, with an empty tree, the first time v is seen)
        k = self.ids.get(v)
        if k is None:
            k = self.ids[v] = len(self.vals)
            self.vals.append(v)
            self.roots.append(0)
        return k

    def _new(self):  # an empty node (a freed one if there is one)
        if self.free:
            x = self.free.pop()
            self.L[x] = self.R[x] = 0
            return x
        self.L.append(0)
        self.R.append(0)
@C@        self.C.append(0)
@P@        self.P.append(0)
@P@        self.W.append(0)
        return len(self.L) - 1

    def _pull(self, x):  # recompute x from its children
@CP@        l, r = self.L[x], self.R[x]
@C@        self.C[x] = self.C[l] + self.C[r]
@P@        self.P[l] = self.P[r] = x
        return x

    def _insert(self, t, i):  # t's tree with position i (not in it) added; returns the root
        root = t = t or self._new()
        L, R, lo, hi = self.L, self.R, 0, self.n - 1
        while True:
@C@            self.C[t] += 1
            if lo == hi:
@P@                self.leaf[i] = t
                return root
            mid = (lo + hi) >> 1
            if i <= mid:
                if not L[t]:
                    c = self._new()
                    L[t] = c
@P@                    self.P[c] = t
                t, hi = L[t], mid
            else:
                if not R[t]:
                    c = self._new()
                    R[t] = c
@P@                    self.P[c] = t
                t, lo = R[t], mid + 1

    def _split(self, t, lo, hi, l, r):  # (t without the positions in [l, r], a tree of just those); no empty nodes left
        if not t or r < lo or hi < l:
            return t, 0
        if l <= lo and hi <= r:
            return 0, t
        L, R, mid = self.L, self.R, (lo + hi) >> 1
        a1, b1 = self._split(L[t], lo, mid, l, r)
        a2, b2 = self._split(R[t], mid + 1, hi, l, r)
        cut = 0
        if b1 or b2:
            cut = self._new()
            L[cut], R[cut] = b1, b2
            self._pull(cut)
        if a1 or a2:
            L[t], R[t] = a1, a2
            return self._pull(t), cut
        self.free.append(t)
        return 0, cut

    def _merge(self, a, b):  # the union of two trees over disjoint positions; b's nodes that overlap a's are freed
        if not a or not b:
            return a or b
        L, R = self.L, self.R
        L[a] = self._merge(L[a], L[b])
        R[a] = self._merge(R[a], R[b])
        self.free.append(b)
        return self._pull(a)

    def _move(self, k, l, r, y):  # the positions in [l, r] of vals[k]'s tree go to y's
        keep, cut = self._split(self.roots[k], 0, self.n - 1, l, r)
        self.roots[k] = keep
        if cut:
            ky = self._id(y)
            t = self.roots[ky] = self._merge(self.roots[ky], cut)
@P@            self.P[t], self.W[t] = 0, ky

@C@    def _count(self, t, lo, hi, l, r):
@C@        if not t or r < lo or hi < l:
@C@            return 0
@C@        if l <= lo and hi <= r:
@C@            return self.C[t]
@C@        mid = (lo + hi) >> 1
@C@        return self._count(self.L[t], lo, mid, l, r) + self._count(self.R[t], mid + 1, hi, l, r)
@C@
    def _first(self, t, lo, hi, l, r, left):  # the first (left) / last position of t's tree in [l, r], or -1
        if not t or r < lo or hi < l:
            return -1
        if lo == hi:
            return lo
        mid = (lo + hi) >> 1
        a, b = (self.L[t], self.R[t]) if left else (self.R[t], self.L[t])
        alo, ahi, blo, bhi = (lo, mid, mid + 1, hi) if left else (mid + 1, hi, lo, mid)
        res = self._first(a, alo, ahi, l, r, left)
        return res if res != -1 else self._first(b, blo, bhi, l, r, left)
@P@
@P@    def _owner(self, i):  # the index into vals of a[i]'s value: up from i's leaf to its tree's root
@P@        P, t = self.P, self.leaf[i]
@P@        while P[t]:
@P@            t = P[t]
@P@        return self.W[t]
'''

PT_CPP = '''
template <typename T>
struct PositionTrees {
    struct SafeHash {  // splitmix64 with a seed random per run (the default hash of an integer is easy to attack)
        size_t operator()(const T& x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    // node 0 = the empty tree; L / R: children@C@, C: how many positions below@P@, P: parent, W: which value (at roots)
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int L = 0, R = 0;
@C@        int C = 0;
@P@        int P = 0, W = 0;
    };
    int n;
    vector<Node> nd;
    vector<int> roots, freeList;
@P@    vector<int> leaf;
    vector<T> vals;
    unordered_map<T, int, SafeHash> ids;

    // O(N log N) -- arr: the initial array
    PositionTrees(const vector<T>& arr) : n((int)arr.size()), nd(1) {
        nd.reserve(2 * n + 2);
@P@        leaf.assign(n, 0);
        for (int i = 0; i < n; i++) {
            int k = id(arr[i]);
            roots[k] = insert(roots[k], i);
        }
@P@        for (int k = 0; k < (int)roots.size(); k++) nd[roots[k]].W = k;
    }

    // O(1) -- the length of the array
    int size() const { return n; }

    // O(logN) amortized -- every a[i] == x with l <= i <= r becomes y
    void rangeReplace(int l, int r, const T& x, const T& y) {
        auto it = ids.find(x);
        if (it != ids.end() && x != y) moveTo(it->second, l, r, y);
    }

@C@    // O(logN) -- # of i in [l, r] with a[i] == x
@C@    int countOccurrences(int l, int r, const T& x) const {
@C@        auto it = ids.find(x);
@C@        return it == ids.end() ? 0 : countIn(roots[it->second], 0, n - 1, l, r);
@C@    }
@C@
    // O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    int leftmostIndexOf(const T& x) const { return edgeOf(x, true); }

    // O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    int rightmostIndexOf(const T& x) const { return edgeOf(x, false); }

    // O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none
    int leftmostIndexOfInRange(int l, int r, const T& x) const {
        auto it = ids.find(x);
        return it == ids.end() ? -1 : firstIn(roots[it->second], 0, n - 1, l, r, true);
    }

    // O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none
    int rightmostIndexOfInRange(int l, int r, const T& x) const {
        auto it = ids.find(x);
        return it == ids.end() ? -1 : firstIn(roots[it->second], 0, n - 1, l, r, false);
    }

@P@    // O(logN) -- a[i]
@P@    T pointGet(int i) const { return vals[owner(i)]; }
@P@
@P@    // O(logN) amortized -- a[i] = v
@P@    void pointAssign(int i, const T& v) {
@P@        int k = owner(i);
@P@        if (vals[k] != v) moveTo(k, i, i, v);
@P@    }
@P@
    // O(N log N) -- the whole current array
    vector<T> getAll() const {
        vector<T> out(n);
        vector<array<int, 3>> st;
        for (int k = 0; k < (int)roots.size(); k++) {
            if (!roots[k]) continue;
            st.push_back({roots[k], 0, n - 1});
            while (!st.empty()) {
                auto [t, lo, hi] = st.back();
                st.pop_back();
                if (lo == hi) {
                    out[lo] = vals[k];
                    continue;
                }
                int mid = (lo + hi) >> 1;
                if (nd[t].L) st.push_back({nd[t].L, lo, mid});
                if (nd[t].R) st.push_back({nd[t].R, mid + 1, hi});
            }
        }
        return out;
    }

    // ---- internals ----

    int id(const T& v) {  // v's index into vals / roots (a new one, with an empty tree, the first time v is seen)
        auto [it, fresh] = ids.try_emplace(v, (int)vals.size());
        if (fresh) vals.push_back(v), roots.push_back(0);
        return it->second;
    }

    int newNode() {  // an empty node (a freed one if there is one)
        if (!freeList.empty()) {
            int x = freeList.back();
            freeList.pop_back();
            nd[x] = Node();
            return x;
        }
        nd.emplace_back();
        return (int)nd.size() - 1;
    }

    int pull(int x) {  // recompute x from its children
@CP@        int l = nd[x].L, r = nd[x].R;
@C@        nd[x].C = nd[l].C + nd[r].C;
@P@        nd[l].P = nd[r].P = x;
        return x;
    }

    int insert(int t, int i) {  // t's tree with position i (not in it) added; returns the root
        if (!t) t = newNode();
        int root = t, lo = 0, hi = n - 1;
        while (true) {
@C@            nd[t].C++;
            if (lo == hi) {
@P@                leaf[i] = t;
                return root;
            }
            int mid = (lo + hi) >> 1;
            bool left = i <= mid;
            if (!(left ? nd[t].L : nd[t].R)) {
                int c = newNode();
                (left ? nd[t].L : nd[t].R) = c;
@P@                nd[c].P = t;
            }
            t = left ? nd[t].L : nd[t].R;
            (left ? hi : lo) = left ? mid : mid + 1;
        }
    }

    // (t without the positions in [l, r], a tree of just those); no empty nodes are left behind
    pair<int, int> split(int t, int lo, int hi, int l, int r) {
        if (!t || r < lo || hi < l) return {t, 0};
        if (l <= lo && hi <= r) return {0, t};
        int mid = (lo + hi) >> 1;
        auto [a1, b1] = split(nd[t].L, lo, mid, l, r);
        auto [a2, b2] = split(nd[t].R, mid + 1, hi, l, r);
        int cut = 0;
        if (b1 || b2) {
            cut = newNode();
            nd[cut].L = b1, nd[cut].R = b2;
            pull(cut);
        }
        if (a1 || a2) {
            nd[t].L = a1, nd[t].R = a2;
            return {pull(t), cut};
        }
        freeList.push_back(t);
        return {0, cut};
    }

    int merge(int a, int b) {  // the union of two trees over disjoint positions; b's nodes that overlap a's are freed
        if (!a || !b) return a ? a : b;
        int l = merge(nd[a].L, nd[b].L);
        int r = merge(nd[a].R, nd[b].R);
        nd[a].L = l, nd[a].R = r;
        freeList.push_back(b);
        return pull(a);
    }

    void moveTo(int k, int l, int r, const T& y) {  // the positions in [l, r] of vals[k]'s tree go to y's
        auto [keep, cut] = split(roots[k], 0, n - 1, l, r);
        roots[k] = keep;
        if (!cut) return;
        int ky = id(y);
        int t = roots[ky] = merge(roots[ky], cut);
@P@        nd[t].P = 0, nd[t].W = ky;
@!P@        (void)t;
    }

@C@    int countIn(int t, int lo, int hi, int l, int r) const {
@C@        if (!t || r < lo || hi < l) return 0;
@C@        if (l <= lo && hi <= r) return nd[t].C;
@C@        int mid = (lo + hi) >> 1;
@C@        return countIn(nd[t].L, lo, mid, l, r) + countIn(nd[t].R, mid + 1, hi, l, r);
@C@    }
@C@
    int edgeOf(const T& x, bool left) const {  // the first (left) / last position of x, or -1
        auto it = ids.find(x);
        int t = it == ids.end() ? 0 : roots[it->second];
        if (!t) return -1;
        int lo = 0, hi = n - 1;
        while (lo < hi) {
            int mid = (lo + hi) >> 1;
            if (left ? nd[t].L : !nd[t].R) t = nd[t].L, hi = mid;
            else t = nd[t].R, lo = mid + 1;
        }
        return lo;
    }

    int firstIn(int t, int lo, int hi, int l, int r, bool left) const {  // the first (left) / last position in [l, r], or -1
        if (!t || r < lo || hi < l) return -1;
        if (lo == hi) return lo;
        int mid = (lo + hi) >> 1;
        int res = left ? firstIn(nd[t].L, lo, mid, l, r, left) : firstIn(nd[t].R, mid + 1, hi, l, r, left);
        if (res != -1) return res;
        return left ? firstIn(nd[t].R, mid + 1, hi, l, r, left) : firstIn(nd[t].L, lo, mid, l, r, left);
    }
@P@
@P@    int owner(int i) const {  // the index into vals of a[i]'s value: up from i's leaf to its tree's root
@P@        int t = leaf[i];
@P@        while (nd[t].P) t = nd[t].P;
@P@        return nd[t].W;
@P@    }
};
'''


def pt_flags(cnt, point):
    return {"C": cnt, "P": point}


def pt_py(cnt, point):
    body = PT_PY.replace('"R"@C@, "C"@P@, "P", "W", "leaf",', '"R"' + (', "C"' if cnt else '') + (', "P", "W", "leaf"' if point else '') + ",")
    body = body.replace("children@C@, C: how many positions below@P@, P: parent, W: which value (at roots)",
                        "children" + (", C: how many positions below" if cnt else "") + (", P: parent, W: which value (at roots)" if point else ""))
    return pt_header("#", cnt, point) + "\n" + wrap(pt_describe(cnt, point), "#") + pick(body, pt_flags(cnt, point))


def pt_cpp(cnt, point):
    body = PT_CPP.replace("children@C@, C: how many positions below@P@, P: parent, W: which value (at roots)",
                          "children" + (", C: how many positions below" if cnt else "") + (", P: parent, W: which value (at roots)" if point else ""))
    return (pt_header("//", cnt, point) + "\n" + wrap(pt_describe(cnt, point), "//") +
            "// T: any type with a hash (int, long long, char, ...)\n" + pick(body, pt_flags(cnt, point)))


# ================================================================================================ value-map seg tree

VM_MARK = "Lazy seg tree whose tag is a value map"
VM_FIND = PT_FIND


def vm_variants():
    return [(False, False), (True, False), (True, True)]


def vm_ops(cnt, sm):
    return sorted(["getAll", "pointAssign", "pointGet", "rangeAssign", "rangeReplace"] + (["countOccurrences"] + VM_FIND if cnt else []) +
                  (["rangeSum"] if sm else []))


def vm_header(cm, cnt, sm):
    ops = vm_ops(cnt, sm)
    cost = {op: "U*log(N)" for op in ops}
    cost.update(pointGet="log(N)", getAll="N*log(N)")
    node = ["t[4*N]"] + (["cnt[2*N*U]"] if cnt else []) + (["sm[4*N]"] if sm else [])
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: lazy-seg-tree", "@complexities:"]
    lines += [f"  {op}: {cost[op]}" for op in ops] + ["  build: N*U", "@memory:", "  layout: pow2-iterative",
                                                     f"  node: {' '.join(node)}", "  tags: mp[2*N*U]",
                                                     "  other: none",
                                                     "  note: U = valHi - valLo + 1 (every value ever in the array is in "
                                                     "[valLo, valHi]); each tag is a whole map old value -> new value, so a "
                                                     "push costs O(U); a map is kept only while pending (handed down, its "
                                                     "memory is reused), so mp is far below 2*N*U in practice"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def vm_describe(cnt, sm):
    return (f"{VM_MARK} (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r] into y, and "
            "rangeAssign(l, r, v) sets a[l..r] = v, in O(U log N), U = valHi - valLo + 1: good when the values are few "
            "(911G: 1..100). A pending tag is a map old value -> new value for the whole segment, so any mix of changes "
            "composes into one map." + (" Each node also keeps how many times each value appears below it" +
                                        (" and its sum" if sm else "") + ", for countOccurrences / where x first / last "
                                        "appears" + (" / rangeSum" if sm else "") + "." if cnt else "") +
            " All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies.")


VM_PY = '''
class ValueMapSeg:
    # leaves t[cap + i] hold a[i] - valLo (-1: padding past n); mp[k]: node k's pending map for its children (None: none)
@C@    # cnt[k][v]: how many leaves below internal node k hold v (its own map already applied)
    __slots__ = ("n", "cap", "U", "valLo", "t", "mp"@C@, "cnt"@S@, "sm")

    # O(N*U) -- arr: the initial array (a list); every value it will ever hold must be in [valLo, valHi]
    def __init__(self, arr, valLo, valHi):
        n = self.n = len(arr)
        self.valLo, self.U = valLo, valHi - valLo + 1
        cap = self.cap = 1 << max(0, (n - 1).bit_length())
        self.t = [-1] * (2 * cap)
        for i, v in enumerate(arr):
            self.t[cap + i] = self._off(v)
        self.mp = [None] * cap
@C@        self.cnt = [None] * cap
@S@        self.sm = [0] * (2 * cap)
@S@        for i in range(n):
@S@            self.sm[cap + i] = self.t[cap + i] + self.valLo
@CS@        for k in range(cap - 1, 0, -1):
@CS@            self._pull(k)

    # O(1) -- the length of the array
    def size(self):
        return self.n

    # O(logN) -- a[i]
    def pointGet(self, i):
        k = self.cap + i
        v = self.t[k]
        k >>= 1
        while k:  # (a map higher up is newer: apply them bottom-up)
            if self.mp[k] is not None:
                v = self.mp[k][v]
            k >>= 1
        return v + self.valLo

    # O(U*logN) -- a[i] = v; needs valLo <= v <= valHi
    def pointAssign(self, i, v):
        o, k = self._off(v), self.cap + i
        for h in range(self.cap.bit_length() - 1, 0, -1):
            self._push(k >> h)
        self.t[k] = o
@S@        self.sm[k] = o + self.valLo
@CS@        k >>= 1
@CS@        while k:
@CS@            self._pull(k)
@CS@            k >>= 1

    # O(U*logN) -- every a[i] == x with l <= i <= r becomes y; needs valLo <= y <= valHi
    def rangeReplace(self, l, r, x, y):
        b = self._off(y)
        a = x - self.valLo
        if 0 <= a < self.U and a != b:
            self._update(l, r, lambda k: self._applyRep(k, a, b))

    # O(U*logN) -- a[l..r] = v; needs valLo <= v <= valHi
    def rangeAssign(self, l, r, v):
        o = self._off(v)
        self._update(l, r, lambda k: self._applyMap(k, [o] * self.U))

    # O(N log N) -- the whole current array
    def getAll(self):
        return [self.pointGet(i) for i in range(self.n)]
@C@
@C@    # O(U*logN) -- # of i in [l, r] with a[i] == x
@C@    def countOccurrences(self, l, r, x):
@C@        a = x - self.valLo
@C@        if not 0 <= a < self.U:
@C@            return 0
@C@        res = 0
@C@        for k in self._cover(l, r):
@C@            res += self._count(k, a)
@C@        return res
@C@
@C@    # O(U*logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
@C@    def leftmostIndexOf(self, x):
@C@        return self._find(x, 0, self.n - 1, True)
@C@
@C@    # O(U*logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
@C@    def rightmostIndexOf(self, x):
@C@        return self._find(x, 0, self.n - 1, False)
@C@
@C@    # O(U*logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none
@C@    def leftmostIndexOfInRange(self, l, r, x):
@C@        return self._find(x, l, r, True)
@C@
@C@    # O(U*logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none
@C@    def rightmostIndexOfInRange(self, l, r, x):
@C@        return self._find(x, l, r, False)
@S@
@S@    # O(U*logN) -- a[l] + ... + a[r]
@S@    def rangeSum(self, l, r):
@S@        return sum(self.sm[k] for k in self._cover(l, r))

    # ---- internals ----

    def _off(self, v):  # v's index into a map
        o = v - self.valLo
        if not 0 <= o < self.U:
            raise ValueError(f"value {v} is outside [valLo, valHi]")
        return o

    def _applyMap(self, k, g):  # node k's segment goes through map g (newer than anything below k)
        if k >= self.cap:
            if self.t[k] >= 0:
                self.t[k] = g[self.t[k]]
@S@                self.sm[k] = self.t[k] + self.valLo
            return
        m = self.mp[k]
        self.mp[k] = g[:] if m is None else [g[v] for v in m]
@C@        c, new = self.cnt[k], [0] * self.U
@C@        for v in range(self.U):
@C@            if c[v]:
@C@                new[g[v]] += c[v]
@C@        self.cnt[k] = new
@S@        lo = self.valLo
@S@        self.sm[k] = sum((v + lo) * w for v, w in enumerate(new) if w)

    def _applyRep(self, k, a, b):  # every a in node k's segment becomes b
        if k >= self.cap:
            if self.t[k] == a:
                self.t[k] = b
@S@                self.sm[k] = b + self.valLo
            return
        m = self.mp[k]
        if m is None:
            m = self.mp[k] = list(range(self.U))
        self.mp[k] = [b if v == a else v for v in m]
@C@        c = self.cnt[k]
@S@        self.sm[k] += (b - a) * c[a]
@C@        c[b] += c[a]
@C@        c[a] = 0

    def _push(self, k):  # hand node k's pending map to its children
        g = self.mp[k]
        if g is not None:
            self._applyMap(2 * k, g)
            self._applyMap(2 * k + 1, g)
            self.mp[k] = None
@CS@
@CS@    def _pull(self, k):  # recompute internal node k from its children (k has no pending map)
@C@        if 2 * k >= self.cap:
@C@            c = [0] * self.U
@C@            for j in (2 * k, 2 * k + 1):
@C@                if self.t[j] >= 0:
@C@                    c[self.t[j]] += 1
@C@            self.cnt[k] = c
@C@        else:
@C@            self.cnt[k] = [p + q for p, q in zip(self.cnt[2 * k], self.cnt[2 * k + 1])]
@S@        self.sm[k] = self.sm[2 * k] + self.sm[2 * k + 1]

    def _pushAbove(self, l, r):  # push every map above the leaves l..r - 1 (offset by cap) down to them
        for h in range(self.cap.bit_length() - 1, 0, -1):
            if (l >> h) << h != l:
                self._push(l >> h)
            if (r >> h) << h != r:
                self._push((r - 1) >> h)

    def _cover(self, l, r):  # the nodes that exactly cover a[l..r], every map above them pushed
        l, r = l + self.cap, r + self.cap + 1
        self._pushAbove(l, r)
        out = []
        while l < r:
            if l & 1:
                out.append(l)
                l += 1
            if r & 1:
                r -= 1
                out.append(r)
            l >>= 1
            r >>= 1
        return out

    def _update(self, l, r, apply):
        l, r = l + self.cap, r + self.cap + 1
        self._pushAbove(l, r)
        a, b = l, r
        while a < b:
            if a & 1:
                apply(a)
                a += 1
            if b & 1:
                b -= 1
                apply(b)
            a >>= 1
            b >>= 1
@CS@        for h in range(1, self.cap.bit_length()):
@CS@            if (l >> h) << h != l:
@CS@                self._pull(l >> h)
@CS@            if (r >> h) << h != r:
@CS@                self._pull((r - 1) >> h)
@C@
@C@    def _count(self, k, a):  # how many a's in node k's segment (its own map applied)
@C@        return int(self.t[k] == a) if k >= self.cap else self.cnt[k][a]
@C@
@C@    def _find(self, x, l, r, left):  # the first (left) / last i in [l, r] with a[i] == x, or -1
@C@        a = x - self.valLo
@C@        if not 0 <= a < self.U:
@C@            return -1
@C@        return self._walk(1, 0, self.cap - 1, l, r, a, left)
@C@
@C@    def _walk(self, k, nl, nr, l, r, a, left):
@C@        if r < nl or nr < l or not self._count(k, a):
@C@            return -1
@C@        if k >= self.cap:
@C@            return nl
@C@        self._push(k)
@C@        m = (nl + nr) >> 1
@C@        kids = ((2 * k, nl, m), (2 * k + 1, m + 1, nr))
@C@        for c, cl, cr in (kids if left else kids[::-1]):
@C@            res = self._walk(c, cl, cr, l, r, a, left)
@C@            if res != -1:
@C@                return res
@C@        return -1
'''

VM_CPP = '''
template <typename T>
struct ValueMapSeg {
@S@    using S = long long;  // sums
    // leaves t[cap + i] hold a[i] - valLo (-1: padding past n); node k's pending map for its children is
    // rows[row[k] * U ..] (row[k] = -1: none). A map row exists only while pending: pushed down, it is reused
@C@    // cnt[k * U + v]: how many leaves below internal node k hold v (its own map already applied)
    int n, cap, lg, U;
    T valLo;
    vector<int> t, row, rows, freeRows, gbuf, tmp;
@C@    vector<int> cnt;
@S@    vector<S> sm;

    // O(N*U) -- arr: the initial array; every value it will ever hold must be in [valLo, valHi]
    ValueMapSeg(const vector<T>& arr, T valLo, T valHi) : n((int)arr.size()), cap(1), lg(0), U(int(valHi - valLo) + 1), valLo(valLo) {
        while (cap < n) cap <<= 1, lg++;
        t.assign(2 * cap, -1), row.assign(cap, -1), tmp.assign(U, 0);
@C@        cnt.assign((size_t)cap * U, 0);
@S@        sm.assign(2 * cap, 0);
        for (int i = 0; i < n; i++) {
            t[cap + i] = off(arr[i]);
@S@            sm[cap + i] = S(arr[i]);
        }
@CS@        for (int k = cap - 1; k >= 1; k--) pull(k);
    }

    // O(1) -- the length of the array
    int size() const { return n; }

    // O(logN) -- a[i]
    T pointGet(int i) const {
        int k = cap + i, v = t[k];
        for (k >>= 1; k; k >>= 1)  // (a map higher up is newer: apply them bottom-up)
            if (row[k] >= 0) v = rows[(size_t)row[k] * U + v];
        return T(v + valLo);
    }

    // O(U*logN) -- a[i] = v; needs valLo <= v <= valHi
    void pointAssign(int i, const T& v) {
        int o = off(v), k = cap + i;
        for (int h = lg; h >= 1; h--) push(k >> h);
        t[k] = o;
@S@        sm[k] = S(v);
@CS@        for (k >>= 1; k; k >>= 1) pull(k);
    }

    // O(U*logN) -- every a[i] == x with l <= i <= r becomes y; needs valLo <= y <= valHi
    void rangeReplace(int l, int r, const T& x, const T& y) {
        int b = off(y);
        long long a = (long long)x - (long long)valLo;
        if (a < 0 || a >= U || a == b) return;
        update(l, r, [&](int k) { applyRep(k, (int)a, b); });
    }

    // O(U*logN) -- a[l..r] = v; needs valLo <= v <= valHi
    void rangeAssign(int l, int r, const T& v) {
        vector<int> g(U, off(v));
        update(l, r, [&](int k) { applyMap(k, g.data()); });
    }

    // O(N log N) -- the whole current array
    vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = pointGet(i);
        return out;
    }
@C@
@C@    // O(U*logN) -- # of i in [l, r] with a[i] == x
@C@    int countOccurrences(int l, int r, const T& x) {
@C@        long long a = (long long)x - (long long)valLo;
@C@        if (a < 0 || a >= U) return 0;
@C@        int res = 0;
@C@        cover(l, r, [&](int k) { res += countOf(k, (int)a); });
@C@        return res;
@C@    }
@C@
@C@    // O(U*logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
@C@    int leftmostIndexOf(const T& x) { return find(x, 0, n - 1, true); }
@C@
@C@    // O(U*logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
@C@    int rightmostIndexOf(const T& x) { return find(x, 0, n - 1, false); }
@C@
@C@    // O(U*logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none
@C@    int leftmostIndexOfInRange(int l, int r, const T& x) { return find(x, l, r, true); }
@C@
@C@    // O(U*logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none
@C@    int rightmostIndexOfInRange(int l, int r, const T& x) { return find(x, l, r, false); }
@S@
@S@    // O(U*logN) -- a[l] + ... + a[r]
@S@    S rangeSum(int l, int r) {
@S@        S res = 0;
@S@        cover(l, r, [&](int k) { res += sm[k]; });
@S@        return res;
@S@    }

    // ---- internals ----

    int off(const T& v) const {  // v's index into a map
        long long o = (long long)v - (long long)valLo;
        if (o < 0 || o >= U) throw invalid_argument("value outside [valLo, valHi]");
        return (int)o;
    }

    void applyMap(int k, const int* g) {  // node k's segment goes through map g (newer than anything below k)
        if (k >= cap) {
            if (t[k] >= 0) {
                t[k] = g[t[k]];
@S@                sm[k] = S(t[k] + valLo);
            }
            return;
        }
        if (row[k] < 0) {
            row[k] = newRow();
            std::copy(g, g + U, &rows[(size_t)row[k] * U]);
        } else {
            int* m = &rows[(size_t)row[k] * U];
            for (int v = 0; v < U; v++) m[v] = g[m[v]];
        }
@C@        int* c = &cnt[(size_t)k * U];
@C@        fill(tmp.begin(), tmp.end(), 0);
@C@        for (int v = 0; v < U; v++) if (c[v]) tmp[g[v]] += c[v];
@C@        copy(tmp.begin(), tmp.end(), c);
@S@        sm[k] = 0;
@S@        for (int v = 0; v < U; v++) if (c[v]) sm[k] += S(c[v]) * S(v + valLo);
    }

    void applyRep(int k, int a, int b) {  // every a in node k's segment becomes b
        if (k >= cap) {
            if (t[k] == a) {
                t[k] = b;
@S@                sm[k] = S(b + valLo);
            }
            return;
        }
        if (row[k] < 0) {
            row[k] = newRow();
            iota(&rows[(size_t)row[k] * U], &rows[(size_t)row[k] * U] + U, 0);
        }
        int* m = &rows[(size_t)row[k] * U];
        for (int v = 0; v < U; v++) if (m[v] == a) m[v] = b;
@C@        int* c = &cnt[(size_t)k * U];
@S@        sm[k] += S(b - a) * S(c[a]);
@C@        c[b] += c[a], c[a] = 0;
    }

    void push(int k) {  // hand node k's pending map to its children (its row is free again)
        if (row[k] < 0) return;
        gbuf.assign(rows.begin() + (size_t)row[k] * U, rows.begin() + (size_t)(row[k] + 1) * U);
        freeRows.push_back(row[k]), row[k] = -1;
        applyMap(2 * k, gbuf.data()), applyMap(2 * k + 1, gbuf.data());
    }

    int newRow() {  // a map row (a freed one if there is one)
        if (!freeRows.empty()) {
            int r = freeRows.back();
            freeRows.pop_back();
            return r;
        }
        rows.resize(rows.size() + U);
        return int(rows.size() / U) - 1;
    }
@CS@
@CS@    void pull(int k) {  // recompute internal node k from its children (k has no pending map)
@C@        int* c = &cnt[(size_t)k * U];
@C@        if (2 * k >= cap) {
@C@            fill(c, c + U, 0);
@C@            for (int j = 2 * k; j <= 2 * k + 1; j++) if (t[j] >= 0) c[t[j]]++;
@C@        } else {
@C@            const int* p = &cnt[(size_t)(2 * k) * U];
@C@            const int* q = &cnt[(size_t)(2 * k + 1) * U];
@C@            for (int v = 0; v < U; v++) c[v] = p[v] + q[v];
@C@        }
@S@        sm[k] = sm[2 * k] + sm[2 * k + 1];
@CS@    }

    void pushAbove(int l, int r) {  // push every map above the leaves l..r - 1 (offset by cap) down to them
        for (int h = lg; h >= 1; h--) {
            if (((l >> h) << h) != l) push(l >> h);
            if (((r >> h) << h) != r) push((r - 1) >> h);
        }
    }

    template <class F>
    void update(int l, int r, F apply) {
        l += cap, r += cap + 1;
        pushAbove(l, r);
        for (int a = l, b = r; a < b; a >>= 1, b >>= 1) {
            if (a & 1) apply(a++);
            if (b & 1) apply(--b);
        }
@CS@        for (int h = 1; h <= lg; h++) {
@CS@            if (((l >> h) << h) != l) pull(l >> h);
@CS@            if (((r >> h) << h) != r) pull((r - 1) >> h);
@CS@        }
    }
@CS@
@CS@    template <class F>
@CS@    void cover(int l, int r, F visit) {  // visit the nodes that exactly cover a[l..r], every map above them pushed
@CS@        l += cap, r += cap + 1;
@CS@        pushAbove(l, r);
@CS@        for (; l < r; l >>= 1, r >>= 1) {
@CS@            if (l & 1) visit(l++);
@CS@            if (r & 1) visit(--r);
@CS@        }
@CS@    }
@C@
@C@    int countOf(int k, int a) const { return k >= cap ? int(t[k] == a) : cnt[(size_t)k * U + a]; }
@C@
@C@    int find(const T& x, int l, int r, bool left) {  // the first (left) / last i in [l, r] with a[i] == x, or -1
@C@        long long a = (long long)x - (long long)valLo;
@C@        return a < 0 || a >= U ? -1 : walk(1, 0, cap - 1, l, r, (int)a, left);
@C@    }
@C@
@C@    int walk(int k, int nl, int nr, int l, int r, int a, bool left) {
@C@        if (r < nl || nr < l || !countOf(k, a)) return -1;
@C@        if (k >= cap) return nl;
@C@        push(k);
@C@        int m = (nl + nr) >> 1;
@C@        int res = left ? walk(2 * k, nl, m, l, r, a, left) : walk(2 * k + 1, m + 1, nr, l, r, a, left);
@C@        if (res != -1) return res;
@C@        return left ? walk(2 * k + 1, m + 1, nr, l, r, a, left) : walk(2 * k, nl, m, l, r, a, left);
@C@    }
};
'''


def vm_flags(cnt, sm):
    return {"C": cnt, "S": sm}


def vm_py(cnt, sm):
    body = VM_PY.replace('"mp"@C@, "cnt"@S@, "sm")', '"mp"' + (', "cnt"' if cnt else '') + (', "sm"' if sm else '') + ")")
    return vm_header("#", cnt, sm) + "\n" + wrap(vm_describe(cnt, sm), "#") + pick(body, vm_flags(cnt, sm))


def vm_cpp(cnt, sm):
    return (vm_header("//", cnt, sm) + "\n" + wrap(vm_describe(cnt, sm), "//") +
            "// T: int, long long, char, ...: the values; valLo / valHi bound every value the array will ever hold\n" +
            pick(VM_CPP, vm_flags(cnt, sm)))


# ================================================================================================ value-map treaps

VT_MARK = "Implicit treap whose lazy tag is a value map"
VT_SEQ = ["append", "appendLeft", "cut", "getAll", "insertAt", "insertCopiesAt", "merge", "paste", "rangeRotateLeft",
          "rangeRotateRight", "split", "trisect"]


def vt_variants():
    return [(rev, cnt, sm, pers) for pers in (False, True) for rev in (False, True)
            for cnt, sm in ((False, False), (True, False), (True, True))]


def vt_ops(rev, cnt, sm, pers):
    return sorted(VT_SEQ + ["pointAssign", "pointGet", "rangeAssign", "rangeReplace"] + (["rangeReverse"] if rev else []) +
                  (["countOccurrences"] + PT_FIND if cnt else []) + (["rangeSum"] if sm else []) + (["copy"] if pers else []))


def vt_header(cm, rev, cnt, sm, pers):
    ops = vt_ops(rev, cnt, sm, pers)
    cost = {op: "U*log(N) expected" for op in ops}
    cost.update(pointGet="log(N) expected", getAll="N*log(N) expected")
    if cnt:  # (read-only walks: a whole subtree's count under the maps above it costs O(U))
        cost.update({op: "U*log(N) expected" for op in ["countOccurrences"] + PT_FIND})
    m = "1*N*log(N)" if pers else "1*N"  # (persistent: each op copies the O(log N) nodes on its paths)
    node = [f"val[{m}]", f"L[{m}]", f"R[{m}]", f"sz[{m}]"] + ([] if pers else ["pri[1*N]"]) + (
        [f"cnt[{m}*U]"] if cnt else []) + ([f"sm[{m}]"] if sm else [])
    tags = [f"mp[{m}*U]"] + ([f"rev[{m}]"] if rev else [])
    cls = vt_cls(pers)
    note = ("nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and copies "
            "share every node they don't change; " if pers else "N = every value ever inserted (nodes are never freed); ")
    note += (f"U = valHi - valLo + 1; every {cls} shares one node pool" +
             (" and so one value range [valLo, valHi] (C++: the last constructor's)" if cm == "//" else "") +
             "; a pending tag is a whole map old value -> new value, so a push costs O(U)")
    lines = [f"@operations: {' '.join(ops)}", f"@data-structure-type: {'persistent-treap' if pers else 'treap'}",
             "@complexities:"]
    lines += [f"  {op}: {cost[op]}" for op in ops] + ["  build: N*U" if cnt else "  build: N", "@memory:", "  layout: none",
                                                     f"  node: {' '.join(node)}", f"  tags: {' '.join(tags)}",
                                                     "  other: none", f"  note: {note}"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def vt_folder(rev, cnt, sm, pers):
    name = folder_name(vt_ops(rev, cnt, sm, pers))
    return name if len(name) <= 180 else ("persistent-treap" if pers else "treap") + "-value-map" + ("-rev" if rev else "") + (
        "-counts" if cnt else "") + ("-sums" if sm else "")


def vt_cls(pers):
    return "PersistentValueMapTreap" if pers else "ValueMapTreap"


def vt_describe(rev, cnt, sm, pers):
    return (f"{VT_MARK} (mass change, CF 911G, with sequence edits): an array you can insert into anywhere, " +
            ("reverse, " if rev else "") + "rotate, cut pieces out of (that is how to erase) and paste them back" +
            (", and copy (copy(l, r): a[l..r] as a treap of its own in O(log N) however long; every op copies the nodes "
             "it changes, so copies never affect each other)" if pers else "") +
            "; plus rangeReplace(l, r, x, y) (every x in a[l..r] becomes y) and rangeAssign, in O(U log N) expected, "
            "U = valHi - valLo + 1: good when the values are few. A pending tag is a map old value -> new value, so "
            "any mix of changes composes into one map." +
            (" Each node also keeps how many times each value appears in its subtree" + (" and its sum" if sm else "") +
             " (countOccurrences, where x first / last appears" + (", rangeSum" if sm else "") + "; read without "
             "changing anything)." if cnt else "") +
            " All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches "
            "return -1 when nothing qualifies.")


VT_PY = '''import random


class @CLS@:
    # one node pool shared by every @CLS@: pieces move between them (node 0 = the empty tree); nodes are never
    # freed. val[x]: x's value - valLo (every map that reached x already applied); mp[x]: the map x still owes its
    # children (None: none)
    val = [0]
@!P@    pri = [0]
    L = [0]
    R = [0]
    sz = [0]
@R@    rev = [0]
    mp = [None]
@C@    cnt = [None]
@S@    sm = [0]
    __slots__ = ("root", "valLo", "U")

    # O(N@C@*U@) -- arr: the initial array (a list); every value it will ever hold must be in [valLo, valHi]
    def __init__(self, arr, valLo, valHi):
        self.valLo, self.U = valLo, valHi - valLo + 1
        self.root = self._build([self._off(v) for v in arr])

    def _empty(self):  # a new, empty one (same pool, same value range)
        piece = @CLS@.__new__(@CLS@)
        piece.root, piece.valLo, piece.U = 0, self.valLo, self.U
        return piece

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

    # O(U*logN) expected -- append v to the end; needs valLo <= v <= valHi
    def append(self, v):
        self.root = self._merge(self.root, self._new(self._off(v)))

    # O(U*logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(U*logN) expected -- insert v so it becomes a[i]; needs valLo <= v <= valHi
    def insertAt(self, i, v):
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, self._new(self._off(v))), c)

    # O(k@C@*U@ + U*logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    def insertCopiesAt(self, i, v, k):
        if k > 0:
            o = self._off(v)
            a, c = self._split(self.root, i)
            self.root = self._merge(self._merge(a, self._build([o] * k)), c)
@P@
@P@    # O(U*logN) expected -- a[l..r] (leave out l and r: the whole array, O(1)) as a @CLS@ of its own; this
@P@    # one is unchanged. The copy shares this one's nodes, so it costs O(U*logN) however long it is
@P@    def copy(self, l=0, r=None):
@P@        n = self.size()
@P@        if r is None:
@P@            r = n - 1
@P@        whole = l == 0 and r == n - 1  # (an empty treap's whole copy too)
@P@        if not whole and not 0 <= l <= r < n:
@P@            raise IndexError(f"copy: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {n}")
@P@        piece = self._empty()
@P@        piece.root = self.root if whole else self._cut(l, r)[1]
@P@        return piece

    # O(U*logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
    def cut(self, l, r):
        a, b, c = self._cut(l, r)
        self.root = self._merge(a, c)
        piece = self._empty()
        piece.root = b
        return piece

    # O(U*logN) expected -- insert all of other (e.g. a cut piece) so it starts at a[i]; other is left empty
    def paste(self, i, other):
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, other.root), c)
        other.root = 0

    # O(U*logN) expected -- append all of other at the end; other is left empty
    def merge(self, other):
        self.root = self._merge(self.root, other.root)
        other.root = 0

    # O(U*logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    def split(self, k):
        left, right = self._empty(), self._empty()
        left.root, right.root = self._split(self.root, k)
        self.root = 0
        return left, right

    # O(U*logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    def trisect(self, l, r):
        left, mid, right = self._empty(), self._empty(), self._empty()
        left.root, mid.root, right.root = self._cut(l, r)
        self.root = 0
        return left, mid, right

    # O(U*logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
    # taken mod the length (negative shifts right)
    def rangeRotateLeft(self, l, r, k):
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = self._split(b, k)
            b = self._merge(b2, b1)
        self._join(a, b, c)

    # O(U*logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    # (negative shifts left)
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)
@R@
@R@    # O(U*logN) expected -- reverse a[l..r] in place
@R@    def rangeReverse(self, l, r):
@R@        a, b, c = self._cut(l, r)
@R@        self._applyRev(b)
@R@        self._join(a, b, c)

    # O(logN) expected -- a[i]
    def pointGet(self, i):
        L, R, sz, t, f, path = self.L, self.R, self.sz, self.root, 0, []
        while True:
            lt, rt = (R[t], L[t]) if f else (L[t], R[t])
            ls = sz[lt]
            if i == ls:
                break
            path.append(t)
@R@            f ^= self.rev[t]
            if i < ls:
                t = lt
            else:
                i -= ls + 1
                t = rt
        v = self.val[t]
        for y in reversed(path):  # (a map higher up is newer: apply them bottom-up)
            m = self.mp[y]
            if m is not None:
                v = m[v]
        return v + self.valLo

    # O(U*logN) expected -- a[i] = v; needs valLo <= v <= valHi
    def pointAssign(self, i, v):
        o = self._off(v)
        a, b, c = self._cut(i, i)
        self.val[b] = o
        self._pull(b)
        self._join(a, b, c)

    # O(U*logN) expected -- every a[i] == x with l <= i <= r becomes y; needs valLo <= y <= valHi
    def rangeReplace(self, l, r, x, y):
        b = self._off(y)
        a = x - self.valLo
        if 0 <= a < self.U and a != b:
            p, q, s = self._cut(l, r)
            self._applyRep(q, a, b)
            self._join(p, q, s)

    # O(U*logN) expected -- a[l..r] = v; needs valLo <= v <= valHi
    def rangeAssign(self, l, r, v):
        o = self._off(v)
        a, b, c = self._cut(l, r)
        self._applyMap(b, [o] * self.U)
        self._join(a, b, c)

    # O(N logN) expected -- the whole current array (read without changing anything)
    def getAll(self):
        L, R, val, mp, lo, out, path = self.L, self.R, self.val, self.mp, self.valLo, [], []

        def go(t, f):
            if not t:
                return
            lt, rt = (R[t], L[t]) if f else (L[t], R[t])
@R@            f ^= self.rev[t]
            path.append(t)
            go(lt, f)
            path.pop()
            v = val[t]
            for y in reversed(path):
                if mp[y] is not None:
                    v = mp[y][v]
            out.append(v + lo)
            path.append(t)
            go(rt, f)
            path.pop()
        go(self.root, 0)
        return out
@C@
@C@    # O(U*logN) expected -- # of i in [l, r] with a[i] == x
@C@    def countOccurrences(self, l, r, x):
@C@        a = x - self.valLo
@C@        if not 0 <= a < self.U:
@C@            return 0
@C@        return self._fold(self.root, l, r, None, 0, lambda t, g: self._countWhole(t, a, g), lambda v: v == a)
@C@
@C@    # O(U*logN) expected -- the smallest i with a[i] == x, or -1 if x isn't in the array
@C@    def leftmostIndexOf(self, x):
@C@        return self._findIn(0, self.size() - 1, x, True)
@C@
@C@    # O(U*logN) expected -- the largest i with a[i] == x, or -1 if x isn't in the array
@C@    def rightmostIndexOf(self, x):
@C@        return self._findIn(0, self.size() - 1, x, False)
@C@
@C@    # O(U*logN) expected -- the smallest i in [l, r] with a[i] == x, or -1 if there is none
@C@    def leftmostIndexOfInRange(self, l, r, x):
@C@        return self._findIn(l, r, x, True)
@C@
@C@    # O(U*logN) expected -- the largest i in [l, r] with a[i] == x, or -1 if there is none
@C@    def rightmostIndexOfInRange(self, l, r, x):
@C@        return self._findIn(l, r, x, False)
@S@
@S@    # O(U*logN) expected -- a[l] + ... + a[r]
@S@    def rangeSum(self, l, r):
@S@        lo = self.valLo
@S@        return self._fold(self.root, l, r, None, 0, self._sumWhole, lambda v: v + lo)

    # ---- internals ----

    def _off(self, v):  # v's index into a map
        o = v - self.valLo
        if not 0 <= o < self.U:
            raise ValueError(f"value {v} is outside [valLo, valHi]")
        return o

    def _new(self, o):  # a node holding offset o
        x = len(self.val)
        self.val.append(o)
@!P@        self.pri.append(random.getrandbits(62))
        self.L.append(0)
        self.R.append(0)
        self.sz.append(1)
@R@        self.rev.append(0)
        self.mp.append(None)
@C@        c = [0] * self.U
@C@        c[o] = 1
@C@        self.cnt.append(c)
@S@        self.sm.append(o + self.valLo)
        return x
@P@
@P@    def _clone(self, x):  # a new copy of node x (sharing its children; maps are never changed in place, so shared too)
@P@        y = len(self.val)
@P@        for arr in (self.val, self.L, self.R, self.sz@R@, self.rev@@, self.mp@S@, self.sm@@):
@P@            arr.append(arr[x])
@C@        self.cnt.append(self.cnt[x][:])
@P@        return y
@!P@
@!P@    def _build(self, offs):  # a treap of new nodes holding offs in order: a Cartesian tree in one pass, O(len)
@!P@        pri, L, R = self.pri, self.L, self.R
@!P@        stack = []
@!P@        for o in offs:
@!P@            x, last = self._new(o), 0
@!P@            while stack and pri[stack[-1]] < pri[x]:
@!P@                last = stack.pop()
@!P@            L[x] = last
@!P@            if stack:
@!P@                R[stack[-1]] = x
@!P@            stack.append(x)
@!P@        root = stack[0] if stack else 0
@!P@        order, todo = [], ([root] if root else [])
@!P@        while todo:
@!P@            x = todo.pop()
@!P@            order.append(x)
@!P@            if L[x]:
@!P@                todo.append(L[x])
@!P@            if R[x]:
@!P@                todo.append(R[x])
@!P@        for x in reversed(order):
@!P@            self._pull(x)
@!P@        return root
@P@
@P@    def _build(self, offs, lo=0, hi=None):  # a balanced treap of new nodes holding offs[lo:hi] in order
@P@        if hi is None:
@P@            hi = len(offs)
@P@        if lo >= hi:
@P@            return 0
@P@        mid = (lo + hi) >> 1
@P@        x = self._new(offs[mid])
@P@        self.L[x] = self._build(offs, lo, mid)
@P@        self.R[x] = self._build(offs, mid + 1, hi)
@P@        self._pull(x)
@P@        return x

    def _pull(self, x):  # recompute x from its children
        l, r = self.L[x], self.R[x]
        self.sz[x] = self.sz[l] + self.sz[r] + 1
@C@        c = [0] * self.U
@C@        for y in (l, r):
@C@            if y:
@C@                c = [p + q for p, q in zip(c, self.cnt[y])]
@C@        c[self.val[x]] += 1
@C@        self.cnt[x] = c
@S@        self.sm[x] = self.sm[l] + self.sm[r] + self.val[x] + self.valLo

    def _applyMap(self, x, g):  # x's subtree goes through map g (newer than anything already in it)
        if not x:
            return
        self.val[x] = g[self.val[x]]
        m = self.mp[x]
        self.mp[x] = g[:] if m is None else [g[v] for v in m]
@C@        c, new = self.cnt[x], [0] * self.U
@C@        for v in range(self.U):
@C@            if c[v]:
@C@                new[g[v]] += c[v]
@C@        self.cnt[x] = new
@S@        lo = self.valLo
@S@        self.sm[x] = sum((v + lo) * w for v, w in enumerate(new) if w)

    def _applyRep(self, x, a, b):  # every a in x's subtree becomes b
        if not x:
            return
        if self.val[x] == a:
            self.val[x] = b
        m = self.mp[x]
        self.mp[x] = [b if v == a else v for v in (m if m is not None else range(self.U))]
@C@        c = self.cnt[x]
@S@        self.sm[x] += (b - a) * c[a]
@C@        c[b] += c[a]
@C@        c[a] = 0
@R@
@R@    def _applyRev(self, x):  # reverse x's subtree
@R@        if x:
@R@            self.L[x], self.R[x] = self.R[x], self.L[x]
@R@            self.rev[x] ^= 1

    def _push(self, x):  # hand x's pending tags to its children@P@ (fresh copies of them: x is a copy only this tree has)
        g = self.mp[x]
@R@        if not self.rev[x] and g is None:
@!R@        if g is None:
            return
@P@        if self.L[x]:
@P@            self.L[x] = self._clone(self.L[x])
@P@        if self.R[x]:
@P@            self.R[x] = self._clone(self.R[x])
@R@        if self.rev[x]:
@R@            self._applyRev(self.L[x])
@R@            self._applyRev(self.R[x])
@R@            self.rev[x] = 0
        if g is not None:
            self._applyMap(self.L[x], g)
            self._applyMap(self.R[x], g)
            self.mp[x] = None
@!P@
@!P@    def _split(self, t, k):  # (first k of t, the rest)
@!P@        if not t:
@!P@            return 0, 0
@!P@        self._push(t)
@!P@        L, R = self.L, self.R
@!P@        if self.sz[L[t]] >= k:
@!P@            a, L[t] = self._split(L[t], k)
@!P@            self._pull(t)
@!P@            return a, t
@!P@        R[t], b = self._split(R[t], k - self.sz[L[t]] - 1)
@!P@        self._pull(t)
@!P@        return t, b
@!P@
@!P@    def _merge(self, a, b):  # a's elements, then b's
@!P@        if not a or not b:
@!P@            return a or b
@!P@        if self.pri[a] > self.pri[b]:
@!P@            self._push(a)
@!P@            self.R[a] = self._merge(self.R[a], b)
@!P@            self._pull(a)
@!P@            return a
@!P@        self._push(b)
@!P@        self.L[b] = self._merge(a, self.L[b])
@!P@        self._pull(b)
@!P@        return b
@P@
@P@    def _split(self, t, k):  # (first k of t, the rest), as new nodes (t's are left as they were)
@P@        if not t:
@P@            return 0, 0
@P@        t = self._clone(t)
@P@        self._push(t)
@P@        if self.sz[self.L[t]] >= k:
@P@            a, b = self._split(self.L[t], k)  # (locals: the copies made below may grow the lists)
@P@            self.L[t] = b
@P@            self._pull(t)
@P@            return a, t
@P@        a, b = self._split(self.R[t], k - self.sz[self.L[t]] - 1)
@P@        self.R[t] = a
@P@        self._pull(t)
@P@        return t, b
@P@
@P@    def _merge(self, a, b):  # a's elements, then b's, as new nodes; the root is a with probability |a| / (|a| + |b|)
@P@        if not a or not b:
@P@            return a or b
@P@        if random.randrange(self.sz[a] + self.sz[b]) < self.sz[a]:
@P@            a = self._clone(a)
@P@            self._push(a)
@P@            self.R[a] = self._merge(self.R[a], b)
@P@            self._pull(a)
@P@            return a
@P@        b = self._clone(b)
@P@        self._push(b)
@P@        self.L[b] = self._merge(a, self.L[b])
@P@        self._pull(b)
@P@        return b

    def _cut(self, l, r):  # (a[0..l-1], a[l..r], a[r+1..])
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    def _join(self, a, b, c):
        self.root = self._merge(self._merge(a, b), c)
@C@
@C@    def _compose(self, g, m):  # the map "m, then g" (None: no map)
@C@        if m is None:
@C@            return g
@C@        return m if g is None else [g[v] for v in m]
@C@
@C@    def _countWhole(self, t, a, g):  # how many values in t's subtree are a once map g (None: none) is applied
@C@        c = self.cnt[t]
@C@        return c[a] if g is None else sum(c[v] for v in range(self.U) if g[v] == a)
@S@
@S@    def _sumWhole(self, t, g):  # the sum of t's subtree once map g (None: none) is applied
@S@        if g is None:
@S@            return self.sm[t]
@S@        c, lo = self.cnt[t], self.valLo
@S@        return sum((g[v] + lo) * c[v] for v in range(self.U) if c[v])
@C@
@C@    # whole(subtree, map) summed over the subtrees inside a[l..r] of t's, plus one(value) for each node only partly
@C@    # inside; g: the maps above t not yet handed down, f: a reverse above t not yet handed down (changes nothing)
@C@    def _fold(self, t, l, r, g, f, whole, one):
@C@        sz = self.sz
@C@        if not t or r < 0 or l >= sz[t]:
@C@            return 0
@C@        if l <= 0 and sz[t] - 1 <= r:
@C@            return whole(t, g)
@C@        lt, rt = (self.R[t], self.L[t]) if f else (self.L[t], self.R[t])
@C&R@        f ^= self.rev[t]
@C@        h, ls, v = self._compose(g, self.mp[t]), sz[lt], self.val[t]
@C@        res = self._fold(lt, l, r, h, f, whole, one) + self._fold(rt, l - ls - 1, r - ls - 1, h, f, whole, one)
@C@        return res + one(g[v] if g is not None else v) if l <= ls <= r else res
@C@
@C@    def _findIn(self, l, r, x, left):
@C@        a = x - self.valLo
@C@        return self._find(self.root, l, r, a, None, 0, left) if 0 <= a < self.U else -1
@C@
@C@    def _find(self, t, l, r, a, g, f, left):  # the first (left) / last index in [l, r] of t's subtree holding a, or -1
@C@        sz = self.sz
@C@        if not t or r < 0 or l >= sz[t] or l <= 0 and sz[t] - 1 <= r and not self._countWhole(t, a, g):
@C@            return -1
@C@        lt, rt = (self.R[t], self.L[t]) if f else (self.L[t], self.R[t])
@C&R@        f ^= self.rev[t]
@C@        h, ls, v = self._compose(g, self.mp[t]), sz[lt], self.val[t]
@C@        parts = ((lt, 0), (-1, ls), (rt, ls + 1))
@C@        for c, off in (parts if left else parts[::-1]):
@C@            if c == -1:
@C@                if l <= ls <= r and (g[v] if g is not None else v) == a:
@C@                    return ls
@C@                continue
@C@            res = self._find(c, l - off, r - off, a, h, f, left)
@C@            if res != -1:
@C@                return res + off
@C@        return -1
'''


def vt_py(rev, cnt, sm, pers):
    f = {"R": rev, "C": cnt, "S": sm, "P": pers}
    body = VT_PY.replace("@CLS@", vt_cls(pers)).replace("O(N@C@*U@)", "O(N*U)" if cnt else "O(N)").replace(
        "O(k@C@*U@ + U*logN)", "O(k*U + U*logN)" if cnt else "O(k + U*logN)")
    body = body.replace("self.sz@R@, self.rev@@, self.mp@S@, self.sm@@", "self.sz" + (", self.rev" if rev else "") + ", self.mp" +
                        (", self.sm" if sm else ""))
    body = body.replace("children@P@ (fresh copies", "children (fresh copies" if pers else "children@DROP@ (fresh copies")
    body = body.replace("@DROP@ (fresh copies of them: x is a copy only this tree has)", "")
    body = body.replace("@C@        self.cnt.append(self.cnt[x][:])\n@P@        return y", "@C@        self.cnt.append(self.cnt[x][:])\n        return y") if pers else body
    text = pick(body, f)
    head, sep, rest = text.partition("\n\n\nclass ")
    return vt_header("#", rev, cnt, sm, pers) + "\n" + head + "\n\n" + wrap(vt_describe(rev, cnt, sm, pers), "#") + "class " + rest

VT_CPP = '''
template <typename T>
struct @CLS@ {
@S@    using S = long long;  // sums
    using Z = @Z@;  // lengths, indices and counts@P@ (long long: copies can make the array huge)
    // one node pool shared by every @CLS@<T>: pieces move between them (node 0 = the empty tree). Nodes are never
    // freed, so there is nothing to reset between test cases; every one shares the value range too (the last
    // constructor's [valLo, valHi]). val: the node's value - valLo (every map that reached it already applied); the
    // map it still owes its children is rows[row * U ..] (row = -1: none). A map row exists only while pending:
    // handed down, it is reused
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
@!P@        unsigned long long pri = 0;
        int val = 0, L = 0, R = 0;
        Z sz = 0;
@R@        char rev = 0;
        int row = -1;
@S@        S sm = 0;
    };
    static inline vector<Node> nd{Node{}};
    static inline vector<int> rows, freeRows, gbuf;  // U entries per map row
@C@    static inline vector<Z> cnt, tmp;  // U entries per node: how many of each value in its subtree
    static inline int U = 0;
    static inline T valLo = T(0);
    int root = 0;

    @CLS@() {}  // (an empty one, on the current value range)

    // O(N@C@*U@) -- arr: the initial array; every value it will ever hold must be in [valLo, valHi]
    @CLS@(const vector<T>& arr, T lo, T hi) {
        setRange(lo, hi);
        vector<int> offs;
        offs.reserve(arr.size());
        for (const T& v : arr) offs.push_back(off(v));
        root = build(offs);
    }

    @CLS@ makeEmpty() const { return @CLS@(); }

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(1) -- the current length of the array
    @Z@ size() const { return nd[root].sz; }

    // O(U*logN) expected -- append v to the end; needs valLo <= v <= valHi
    void append(T v) { root = mergeNodes(root, newNode(off(v))); }

    // O(U*logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(U*logN) expected -- insert v so it becomes a[i]; needs valLo <= v <= valHi
    void insertAt(Z i, T v) {
        int o = off(v), a, c;
        splitNodes(root, i, a, c);
        root = mergeNodes(mergeNodes(a, newNode(o)), c);
    }

    // O(k@C@*U@ + U*logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(Z i, T v, Z k) {
        if (k <= 0) return;
        int o = off(v), a, c;
        splitNodes(root, i, a, c);
        root = mergeNodes(mergeNodes(a, build(vector<int>(k, o))), c);
    }
@P@
@P@    // O(1) -- the whole array as a @CLS@ of its own; this one is unchanged (they share every node)
@P@    @CLS@ copy() const { return *this; }
@P@
@P@    // O(U*logN) expected -- a[l..r] as a @CLS@ of its own; this one is unchanged. The copy shares this one's
@P@    // nodes, so it costs O(U*logN) however long it is
@P@    @CLS@ copy(Z l, Z r) {
@P@        int a, b, c;
@P@        cutNodes(l, r, a, b, c);
@P@        @CLS@ piece = makeEmpty();
@P@        piece.root = b;
@P@        return piece;
@P@    }

    // O(U*logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
    @CLS@ cut(Z l, Z r) {
        int a, b, c;
        cutNodes(l, r, a, b, c);
        root = mergeNodes(a, c);
        @CLS@ piece = makeEmpty();
        piece.root = b;
        return piece;
    }

    // O(U*logN) expected -- insert all of other (e.g. a cut piece) so it starts at a[i]; other is left empty
    void paste(Z i, @CLS@& other) {
        int a, c;
        splitNodes(root, i, a, c);
        root = mergeNodes(mergeNodes(a, other.root), c);
        other.root = 0;
    }
    void paste(Z i, @CLS@&& other) { paste(i, other); }  // (a temporary@P@: paste(i, t.copy(l, r))@@)

    // O(U*logN) expected -- append all of other at the end; other is left empty
    void merge(@CLS@& other) {
        root = mergeNodes(root, other.root);
        other.root = 0;
    }
    void merge(@CLS@&& other) { merge(other); }  // (a temporary@P@: merge(t.copy())@@)

    // O(U*logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    pair<@CLS@, @CLS@> split(Z k) {
        @CLS@ left = makeEmpty(), right = makeEmpty();
        splitNodes(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(U*logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    tuple<@CLS@, @CLS@, @CLS@> trisect(Z l, Z r) {
        @CLS@ left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cutNodes(l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // O(U*logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
    // taken mod the length (negative shifts right)
    void rangeRotateLeft(Z l, Z r, long long k) {
        int a, b, c;
        cutNodes(l, r, a, b, c);
        long long m = r - l + 1;
        k = (k % m + m) % m;
        if (k) {
            int b1, b2;
            splitNodes(b, k, b1, b2);
            b = mergeNodes(b2, b1);
        }
        root = mergeNodes(mergeNodes(a, b), c);
    }

    // O(U*logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    // (negative shifts left)
    void rangeRotateRight(Z l, Z r, long long k) {
        long long m = r - l + 1;
        rangeRotateLeft(l, r, m - (k % m + m) % m);
    }
@R@
@R@    // O(U*logN) expected -- reverse a[l..r] in place
@R@    void rangeReverse(Z l, Z r) {
@R@        int a, b, c;
@R@        cutNodes(l, r, a, b, c);
@R@        applyRev(b);
@R@        root = mergeNodes(mergeNodes(a, b), c);
@R@    }

    // O(logN) expected -- a[i]
    T pointGet(Z i) const {
        int t = root;
        bool f = false;
        vector<int> path;
        while (true) {
            int lt = f ? nd[t].R : nd[t].L, rt = f ? nd[t].L : nd[t].R;
            Z ls = nd[lt].sz;
            if (i == ls) break;
            path.push_back(t);
@R@            f ^= nd[t].rev;
            if (i < ls) t = lt;
            else i -= ls + 1, t = rt;
        }
        int v = nd[t].val;
        for (int k = (int)path.size() - 1; k >= 0; k--)  // (a map higher up is newer: apply them bottom-up)
            if (nd[path[k]].row >= 0) v = rows[(size_t)nd[path[k]].row * U + v];
        return T(v + valLo);
    }

    // O(U*logN) expected -- a[i] = v; needs valLo <= v <= valHi
    void pointAssign(Z i, const T& v) {
        int o = off(v), a, b, c;
        cutNodes(i, i, a, b, c);
        nd[b].val = o;
        pull(b);
        root = mergeNodes(mergeNodes(a, b), c);
    }

    // O(U*logN) expected -- every a[i] == x with l <= i <= r becomes y; needs valLo <= y <= valHi
    void rangeReplace(Z l, Z r, const T& x, const T& y) {
        int to = off(y);
        long long from = (long long)x - (long long)valLo;
        if (from < 0 || from >= U || from == to) return;
        int a, b, c;
        cutNodes(l, r, a, b, c);
        applyRep(b, (int)from, to);
        root = mergeNodes(mergeNodes(a, b), c);
    }

    // O(U*logN) expected -- a[l..r] = v; needs valLo <= v <= valHi
    void rangeAssign(Z l, Z r, const T& v) {
        vector<int> g(U, off(v));
        int a, b, c;
        cutNodes(l, r, a, b, c);
        applyMap(b, g.data());
        root = mergeNodes(mergeNodes(a, b), c);
    }

    // O(N logN) expected -- the whole current array (read without changing anything)
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(size());
        vector<int> path;
        auto go = [&](auto&& self, int t, bool f) -> void {
            if (!t) return;
            int lt = f ? nd[t].R : nd[t].L, rt = f ? nd[t].L : nd[t].R;
@R@            f ^= nd[t].rev;
            path.push_back(t);
            self(self, lt, f);
            path.pop_back();
            int v = nd[t].val;
            for (int k = (int)path.size() - 1; k >= 0; k--)
                if (nd[path[k]].row >= 0) v = rows[(size_t)nd[path[k]].row * U + v];
            out.push_back(T(v + valLo));
            path.push_back(t);
            self(self, rt, f);
            path.pop_back();
        };
        go(go, root, false);
        return out;
    }
@C@
@C@    // O(U*logN) expected -- # of i in [l, r] with a[i] == x
@C@    Z countOccurrences(Z l, Z r, const T& x) const {
@C@        long long a = (long long)x - (long long)valLo;
@C@        if (a < 0 || a >= U) return 0;
@C@        return fold(root, l, r, nullptr, false, [&](int t, const int* g) { return countWhole(t, (int)a, g); },
@C@                    [&](int v) { return Z(v == a); });
@C@    }
@C@
@C@    // O(U*logN) expected -- the smallest i with a[i] == x, or -1 if x isn't in the array
@C@    Z leftmostIndexOf(const T& x) const { return findIn(0, size() - 1, x, true); }
@C@
@C@    // O(U*logN) expected -- the largest i with a[i] == x, or -1 if x isn't in the array
@C@    Z rightmostIndexOf(const T& x) const { return findIn(0, size() - 1, x, false); }
@C@
@C@    // O(U*logN) expected -- the smallest i in [l, r] with a[i] == x, or -1 if there is none
@C@    Z leftmostIndexOfInRange(Z l, Z r, const T& x) const { return findIn(l, r, x, true); }
@C@
@C@    // O(U*logN) expected -- the largest i in [l, r] with a[i] == x, or -1 if there is none
@C@    Z rightmostIndexOfInRange(Z l, Z r, const T& x) const { return findIn(l, r, x, false); }
@S@
@S@    // O(U*logN) expected -- a[l] + ... + a[r]
@S@    S rangeSum(Z l, Z r) const {
@S@        return fold(root, l, r, nullptr, false, [&](int t, const int* g) { return sumWhole(t, g); },
@S@                    [&](int v) { return S(v) + S(valLo); });
@S@    }

    // ---- internals ----

    static void setRange(T lo, T hi) {
        int u = int(hi - lo) + 1;
        if (u != U) {  // (a new value range: the pool's map rows change length, so it starts over)
            U = u;
            nd.assign(1, Node{});
            rows.clear(), freeRows.clear();
@C@            cnt.assign(U, 0), tmp.assign(U, 0);
        }
        valLo = lo;
    }

    static int off(const T& v) {  // v's index into a map
        long long o = (long long)v - (long long)valLo;
        if (o < 0 || o >= U) throw invalid_argument("value outside [valLo, valHi]");
        return (int)o;
    }

    static int newNode(int o) {  // a node holding offset o
        Node x;
@!P@        x.pri = rnd();
        x.val = o, x.sz = 1;
@S@        x.sm = S(o) + S(valLo);
        nd.push_back(x);
@C@        cnt.resize(cnt.size() + U);
@C@        cnt[(nd.size() - 1) * U + o] = 1;
        return (int)nd.size() - 1;
    }
@P@
@P@    static int clone(int x) {  // a new copy of node x (sharing its children)
@P@        Node y = nd[x];
@P@        if (y.row >= 0) {
@P@            y.row = newRow();
@P@            std::copy(rows.begin() + (size_t)nd[x].row * U, rows.begin() + (size_t)(nd[x].row + 1) * U,
@P@                      rows.begin() + (size_t)y.row * U);
@P@        }
@P@        nd.push_back(y);
@C&P@        cnt.resize(cnt.size() + U);
@C&P@        std::copy(cnt.begin() + (size_t)x * U, cnt.begin() + (size_t)(x + 1) * U, cnt.end() - U);
@P@        return (int)nd.size() - 1;
@P@    }
@!P@
@!P@    static int build(const vector<int>& offs) {  // a treap of new nodes holding offs in order: a Cartesian tree, O(len)
@!P@        vector<int> st, order;
@!P@        for (int o : offs) {
@!P@            int x = newNode(o), last = 0;
@!P@            while (!st.empty() && nd[st.back()].pri < nd[x].pri) last = st.back(), st.pop_back();
@!P@            nd[x].L = last;
@!P@            if (!st.empty()) nd[st.back()].R = x;
@!P@            st.push_back(x);
@!P@        }
@!P@        int root = st.empty() ? 0 : st[0];
@!P@        vector<int> todo;
@!P@        if (root) todo.push_back(root);
@!P@        while (!todo.empty()) {
@!P@            int x = todo.back();
@!P@            todo.pop_back();
@!P@            order.push_back(x);
@!P@            if (nd[x].L) todo.push_back(nd[x].L);
@!P@            if (nd[x].R) todo.push_back(nd[x].R);
@!P@        }
@!P@        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
@!P@        return root;
@!P@    }
@P@
@P@    static int build(const vector<int>& offs, size_t lo = 0, size_t hi = SIZE_MAX) {  // balanced, offs[lo..hi) in order
@P@        if (hi == SIZE_MAX) hi = offs.size();
@P@        if (lo >= hi) return 0;
@P@        size_t mid = (lo + hi) / 2;
@P@        int x = newNode(offs[mid]);
@P@        int l = build(offs, lo, mid), r = build(offs, mid + 1, hi);
@P@        nd[x].L = l, nd[x].R = r;
@P@        pull(x);
@P@        return x;
@P@    }

    static void pull(int x) {  // recompute x from its children
        int l = nd[x].L, r = nd[x].R;
        nd[x].sz = nd[l].sz + nd[r].sz + 1;
@C@        Z* c = &cnt[(size_t)x * U];
@C@        const Z* p = &cnt[(size_t)l * U];
@C@        const Z* q = &cnt[(size_t)r * U];
@C@        for (int v = 0; v < U; v++) c[v] = p[v] + q[v];
@C@        c[nd[x].val]++;
@S@        nd[x].sm = nd[l].sm + nd[r].sm + S(nd[x].val) + S(valLo);
    }

    static void applyMap(int x, const int* g) {  // x's subtree goes through map g (newer than anything already in it)
        if (!x) return;
        nd[x].val = g[nd[x].val];
        if (nd[x].row < 0) {
            int r = newRow();
            nd[x].row = r;
            std::copy(g, g + U, &rows[(size_t)r * U]);
        } else {
            int* m = &rows[(size_t)nd[x].row * U];
            for (int v = 0; v < U; v++) m[v] = g[m[v]];
        }
@C@        Z* c = &cnt[(size_t)x * U];
@C@        std::fill(tmp.begin(), tmp.end(), 0);
@C@        for (int v = 0; v < U; v++) if (c[v]) tmp[g[v]] += c[v];
@C@        std::copy(tmp.begin(), tmp.end(), c);
@S@        nd[x].sm = 0;
@S@        for (int v = 0; v < U; v++) if (c[v]) nd[x].sm += S(c[v]) * (S(v) + S(valLo));
    }

    static void applyRep(int x, int a, int b) {  // every a in x's subtree becomes b
        if (!x) return;
        if (nd[x].val == a) nd[x].val = b;
        if (nd[x].row < 0) {
            int r = newRow();
            nd[x].row = r;
            std::iota(&rows[(size_t)r * U], &rows[(size_t)r * U] + U, 0);
        }
        int* m = &rows[(size_t)nd[x].row * U];
        for (int v = 0; v < U; v++) if (m[v] == a) m[v] = b;
@C@        Z* c = &cnt[(size_t)x * U];
@S@        nd[x].sm += S(b - a) * S(c[a]);
@C@        c[b] += c[a], c[a] = 0;
    }
@R@
@R@    static void applyRev(int x) {  // reverse x's subtree
@R@        if (x) swap(nd[x].L, nd[x].R), nd[x].rev ^= 1;
@R@    }

    static void push(int x) {  // hand x's pending tags to its children@P@ (fresh copies of them: x is a copy only this tree has)@@
@R@        if (!nd[x].rev && nd[x].row < 0) return;
@!R@        if (nd[x].row < 0) return;
@P@        if (nd[x].L) {
@P@            int c = clone(nd[x].L);
@P@            nd[x].L = c;
@P@        }
@P@        if (nd[x].R) {
@P@            int c = clone(nd[x].R);
@P@            nd[x].R = c;
@P@        }
@R@        if (nd[x].rev) applyRev(nd[x].L), applyRev(nd[x].R), nd[x].rev = 0;
        if (nd[x].row >= 0) {
            gbuf.assign(rows.begin() + (size_t)nd[x].row * U, rows.begin() + (size_t)(nd[x].row + 1) * U);
            freeRows.push_back(nd[x].row), nd[x].row = -1;
            applyMap(nd[x].L, gbuf.data()), applyMap(nd[x].R, gbuf.data());
        }
    }

    static int newRow() {  // a map row (a freed one if there is one)
        if (!freeRows.empty()) {
            int r = freeRows.back();
            freeRows.pop_back();
            return r;
        }
        rows.resize(rows.size() + U);
        return int(rows.size() / U) - 1;
    }

    // (first k of t, the rest)@P@, as new nodes (t's are left as they were)@@
    static void splitNodes(int t, Z k, int& a, int& b) {
        if (!t) {
            a = b = 0;
            return;
        }
@P@        t = clone(t);
        push(t);
        int x, y;  // (locals: @!P@pushes never move nd, but keep it simple@@@P@the copies made below may move nd@@)
        if (nd[nd[t].L].sz >= k) {
            splitNodes(nd[t].L, k, x, y);
            nd[t].L = y, a = x, b = t;
        } else {
            splitNodes(nd[t].R, k - nd[nd[t].L].sz - 1, x, y);
            nd[t].R = x, a = t, b = y;
        }
        pull(t);
    }

    // a's elements, then b's@P@, as new nodes; the root is a with probability |a| / (|a| + |b|)@@
    static int mergeNodes(int a, int b) {
        if (!a || !b) return a ? a : b;
@!P@        if (nd[a].pri > nd[b].pri) {
@P@        if ((Z)(rnd() % (unsigned long long)(nd[a].sz + nd[b].sz)) < nd[a].sz) {
@P@            a = clone(a);
            push(a);
            int r = mergeNodes(nd[a].R, b);
            nd[a].R = r;
            pull(a);
            return a;
        }
@P@        b = clone(b);
        push(b);
        int l = mergeNodes(a, nd[b].L);
        nd[b].L = l;
        pull(b);
        return b;
    }

    void cutNodes(Z l, Z r, int& a, int& b, int& c) const {  // (a[0..l-1], a[l..r], a[r+1..])
        int bc;
        splitNodes(root, l, a, bc);
        splitNodes(bc, r - l + 1, b, c);
    }
@C@
@C@    static const int* composeAt(const int* g, int t, vector<int>& buf) {  // the map "t's pending map, then g"
@C@        if (nd[t].row < 0) return g;
@C@        const int* m = &rows[(size_t)nd[t].row * U];
@C@        if (!g) return m;
@C@        buf.resize(U);
@C@        for (int v = 0; v < U; v++) buf[v] = g[m[v]];
@C@        return buf.data();
@C@    }
@C@
@C@    static Z countWhole(int t, int a, const int* g) {  // how many a's in t's subtree once map g (null: none) is applied
@C@        const Z* c = &cnt[(size_t)t * U];
@C@        if (!g) return c[a];
@C@        Z res = 0;
@C@        for (int v = 0; v < U; v++) if (g[v] == a) res += c[v];
@C@        return res;
@C@    }
@S@
@S@    static S sumWhole(int t, const int* g) {  // the sum of t's subtree once map g (null: none) is applied
@S@        if (!g) return nd[t].sm;
@S@        const Z* c = &cnt[(size_t)t * U];
@S@        S res = 0;
@S@        for (int v = 0; v < U; v++) if (c[v]) res += S(c[v]) * (S(g[v]) + S(valLo));
@S@        return res;
@S@    }
@C@
@C@    // whole(subtree, map) summed over the subtrees inside a[l..r] of t's, plus one(value) for each node only partly
@C@    // inside; g: the maps above t not yet handed down, f: a reverse above t not yet handed down (changes nothing)
@C@    template <class W, class O>
@C@    static auto fold(int t, Z l, Z r, const int* g, bool f, W whole, O one) -> decltype(whole(t, g)) {
@C@        using R = decltype(whole(t, g));
@C@        if (!t || r < 0 || l >= nd[t].sz) return R(0);
@C@        if (l <= 0 && nd[t].sz - 1 <= r) return whole(t, g);
@C@        int lt = f ? nd[t].R : nd[t].L, rt = f ? nd[t].L : nd[t].R;
@C&R@        f ^= nd[t].rev;
@C@        vector<int> buf;
@C@        const int* h = composeAt(g, t, buf);
@C@        Z ls = nd[lt].sz;
@C@        R res = fold(lt, l, r, h, f, whole, one) + fold(rt, l - ls - 1, r - ls - 1, h, f, whole, one);
@C@        if (l <= ls && ls <= r) res += one(g ? g[nd[t].val] : nd[t].val);
@C@        return res;
@C@    }
@C@
@C@    Z findIn(Z l, Z r, const T& x, bool left) const {
@C@        long long a = (long long)x - (long long)valLo;
@C@        return a < 0 || a >= U ? -1 : findNode(root, l, r, (int)a, nullptr, false, left);
@C@    }
@C@
@C@    // the first (left) / last index in [l, r] of t's subtree holding a, or -1
@C@    static Z findNode(int t, Z l, Z r, int a, const int* g, bool f, bool left) {
@C@        if (!t || r < 0 || l >= nd[t].sz || (l <= 0 && nd[t].sz - 1 <= r && !countWhole(t, a, g))) return -1;
@C@        int lt = f ? nd[t].R : nd[t].L, rt = f ? nd[t].L : nd[t].R;
@C&R@        f ^= nd[t].rev;
@C@        vector<int> buf;
@C@        const int* h = composeAt(g, t, buf);
@C@        Z ls = nd[lt].sz;
@C@        int v = g ? g[nd[t].val] : nd[t].val;
@C@        Z res;
@C@        if (left) {
@C@            if ((res = findNode(lt, l, r, a, h, f, left)) != -1) return res;
@C@            if (l <= ls && ls <= r && v == a) return ls;
@C@            return (res = findNode(rt, l - ls - 1, r - ls - 1, a, h, f, left)) != -1 ? res + ls + 1 : -1;
@C@        }
@C@        if ((res = findNode(rt, l - ls - 1, r - ls - 1, a, h, f, left)) != -1) return res + ls + 1;
@C@        if (l <= ls && ls <= r && v == a) return ls;
@C@        return findNode(lt, l, r, a, h, f, left);
@C@    }
};
'''


def vt_cpp(rev, cnt, sm, pers):
    f = {"R": rev, "C": cnt, "S": sm, "P": pers}
    body = VT_CPP.replace("@CLS@", vt_cls(pers)).replace("@Z@", "long long" if pers else "int")
    body = body.replace("O(N@C@*U@)", "O(N*U)" if cnt else "O(N)").replace(
        "O(k@C@*U@ + U*logN)", "O(k*U + U*logN)" if cnt else "O(k + U*logN)")
    for a, b in (("indices and counts@P@ (long long: copies can make the array huge)", " (long long: copies can make the array huge)"),
                 ("(a temporary@P@: paste(i, t.copy(l, r))@@)", ": paste(i, t.copy(l, r))"),
                 ("(a temporary@P@: merge(t.copy())@@)", ": merge(t.copy())"),
                 ("children@P@ (fresh copies of them: x is a copy only this tree has)@@", " (fresh copies of them: x is a copy only this tree has)"),
                 ("rest)@P@, as new nodes (t's are left as they were)@@", ", as new nodes (t's are left as they were)"),
                 ("b's@P@, as new nodes; the root is a with probability |a| / (|a| + |b|)@@", ", as new nodes; the root is a with probability |a| / (|a| + |b|)")):
        head = a.split("@P@")[0]
        body = body.replace(a, head + (b if pers else ""))
    body = body.replace("(locals: @!P@pushes never move nd, but keep it simple@@@P@the copies made below may move nd@@)",
                        "(locals: the copies made below may move nd)" if pers else "(locals, not nd fields: simpler)")
    body = body.replace("indices and counts (long", "indices and counts (long")
    return (vt_header("//", rev, cnt, sm, pers) + "\n" + wrap(vt_describe(rev, cnt, sm, pers), "//") +
            "// T: int, long long, char, ...: the values; valLo / valHi bound every value the array will ever hold\n" +
            pick(body, f))


# ================================================================================================ sqrt blocks

SQ_MARK = "Blocks whose values form a union-find of classes"


def sq_variants():
    return [(False, False), (True, False), (True, True)]  # (sequence edits, rangeReverse)


def sq_ops(seq, rev):
    return sorted(set(["countOccurrences", "getAll", "pointAssign", "pointGet", "rangeAssign", "rangeReplace"] + PT_FIND +
                      (VT_SEQ if seq else []) + (["rangeReverse"] if rev else [])))


def sq_header(cm, seq, rev):
    ops = sq_ops(seq, rev)
    cost = {op: "sqrt(N) amortized" if seq else "sqrt(N)" for op in ops}
    cost.update(getAll="N")
    if not seq:
        cost.update(pointGet="1 amortized", pointAssign="1 amortized", rangeReplace="sqrt(N) amortized",
                    rangeAssign="sqrt(N) amortized")
    else:
        cost.update(pointGet="sqrt(N)")
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: sqrt", "@complexities:"]
    lines += [f"  {op}: {cost[op]}" for op in ops] + ["  build: N", "@memory:", "  layout: none",
                                                     "  node: cls[1*N] par[2*N] val[2*N] cnt[2*N] where[1*N]",
                                                     "  tags: " + ("rev[1*sqrt(N)]" if rev else "none"), "  other: none",
                                                     "  note: blocks of about sqrt(N) values; each block's values are "
                                                     "classes joined by a union-find (union by size, path halving: "
                                                     "O(alpha), counted as O(1)); where maps each value in the block to "
                                                     "its class; values are hashed, so any values work"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def sq_describe(seq, rev):
    return (f"{SQ_MARK} (mass change, CF 911G, in O(sqrt N)" + (", with sequence edits" if seq else "") + "): the "
            "array is cut into blocks of about sqrt(N) values. Inside a block equal values form a class, and the classes "
            "are joined by a union-find: rangeReplace(l, r, x, y) on a whole block renames x's class to y, or joins it "
            "into y's, in O(1); rangeAssign joins every class. Only the (at most two) partly covered blocks are touched "
            "value by value. Any values work (each block hashes them)." +
            (" The blocks form a list you can insert into anywhere, " + ("reverse, " if rev else "") + "rotate, cut "
             "pieces out of (that is how to erase) and paste back; a[i] then walks the list (O(sqrt N))." if seq else
             " a[i] and a[i] = v are O(1) amortized.") +
            " All indices 0-based, ranges inclusive [l, r]" + (", an index always the position in the CURRENT array" if seq else "") +
            "; searches return -1 when nothing qualifies.")


SQ_PY = '''from math import isqrt


class _Block:
    # a run of the array: cls[k] is the class of its k-th value@R@ (read backwards when rev)@@. Classes form a union-find (par);
    # a root class holds its value (val) and how many of the block's values are in it (cnt). where: value -> root class
    __slots__ = ("cls", "par", "val", "cnt", "where"@R@, "rev"@@)

    def __init__(self, vals):
        self.build(vals)

    def build(self, vals):  # O(len) -- the classes from scratch
        where, par, val, cnt, cls = {}, [], [], [], []
        for v in vals:
            c = where.get(v)
            if c is None:
                c = where[v] = len(par)
                par.append(c)
                val.append(v)
                cnt.append(0)
            cnt[c] += 1
            cls.append(c)
        self.cls, self.par, self.val, self.cnt, self.where = cls, par, val, cnt, where
@R@        self.rev = False

    def __len__(self):
        return len(self.cls)

    def find(self, c):  # c's root class (path halving)
        par = self.par
        while par[c] != c:
            par[c] = par[par[c]]
            c = par[c]
        return c

    def get(self, k):  # the k-th value
@R@        if self.rev:
@R@            k = len(self.cls) - 1 - k
        return self.val[self.find(self.cls[k])]

    def values(self):  # every value, in order
        out = [self.val[self.find(c)] for c in self.cls]
@R@        if self.rev:
@R@            out.reverse()
        return out

    def count(self, x):  # how many x's
        c = self.where.get(x)
        return self.cnt[c] if c is not None else 0

    def replace(self, x, y):  # O(1) -- every x becomes y: x's class is renamed, or joined to y's
        cx = self.where.pop(x, None)
        if cx is None:
            return
        cy = self.where.get(y)
        if cy is None:
            self.val[cx] = y
            self.where[y] = cx
            return
        if self.cnt[cx] > self.cnt[cy]:  # (union by size)
            cx, cy = cy, cx
        self.par[cx] = cy
        self.cnt[cy] += self.cnt[cx]
        self.val[cy] = y
        self.where[y] = cy

    def assignAll(self, v):  # every value becomes v: every class joined into one (O(1) amortized: each join removes one)
        roots = list(self.where.values())
        r = max(roots, key=lambda c: self.cnt[c])
        for c in roots:
            if c != r:
                self.par[c] = r
                self.cnt[r] += self.cnt[c]
        self.val[r] = v
        self.where = {v: r}

    def assign(self, k, v):  # O(1) amortized -- the k-th value becomes v (a class of its own if v is new here)
@R@        if self.rev:
@R@            k = len(self.cls) - 1 - k
        c = self.find(self.cls[k])
        old = self.val[c]
        if old == v:
            return
        self.cnt[c] -= 1
        if not self.cnt[c]:
            del self.where[old]
        d = self.where.get(v)
        if d is None:
            d = self.where[v] = len(self.par)
            self.par.append(d)
            self.val.append(v)
            self.cnt.append(0)
        self.cnt[d] += 1
        self.cls[k] = d
        if len(self.par) > 2 * len(self.cls) + 8:  # (many dead classes: start over, paid for by the assigns)
            self.build(self.values())


class SqrtReplace:
@Q@    # pieces (cut / split / trisect) are SqrtReplaces of their own: paste / merge move their blocks over
    __slots__ = ("blocks", "n", "B")

    # O(N) -- arr: the initial array (a list@Q@; leave it out to start empty@@)
@Q@    def __init__(self, arr=()):
@!Q@    def __init__(self, arr):
        self._fill(list(arr))

    # O(1) -- the @Q@current @@length of the array
    def size(self):
        return self.n

    # O(N) -- the whole current array
    def getAll(self):
        out = []
        for b in self.blocks:
            out += b.values()
        return out

    # O(@Q@sqrt(N)@@@!Q@1) amortized@@) -- a[i]
    def pointGet(self, i):
        b, k = self._locate(i)
        return b.get(k)

    # O(@Q@sqrt(N)@@@!Q@1) amortized@@) -- a[i] = v
    def pointAssign(self, i, v):
        b, k = self._locate(i)
        b.assign(k, v)

    # O(sqrt(N)) amortized -- every a[i] == x with l <= i <= r becomes y
    def rangeReplace(self, l, r, x, y):
        if x == y:
            return
        for b, lo, hi, full, _ in self._span(l, r):
            if full:
                b.replace(x, y)
            else:
                for k in range(lo, hi + 1):
                    if b.get(k) == x:
                        b.assign(k, y)

    # O(sqrt(N)) amortized -- a[l..r] = v
    def rangeAssign(self, l, r, v):
        for b, lo, hi, full, _ in self._span(l, r):
            if full:
                b.assignAll(v)
            else:
                for k in range(lo, hi + 1):
                    b.assign(k, v)

    # O(sqrt(N)) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        res = 0
        for b, lo, hi, full, _ in self._span(l, r):
            res += b.count(x) if full else sum(b.get(k) == x for k in range(lo, hi + 1))
        return res

    # O(sqrt(N)) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        return self._find(0, self.n - 1, x, True)

    # O(sqrt(N)) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        return self._find(0, self.n - 1, x, False)

    # O(sqrt(N)) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none
    def leftmostIndexOfInRange(self, l, r, x):
        return self._find(l, r, x, True)

    # O(sqrt(N)) -- the largest i in [l, r] with a[i] == x, or -1 if there is none
    def rightmostIndexOfInRange(self, l, r, x):
        return self._find(l, r, x, False)
@Q@
@Q@    # O(sqrt(N)) amortized -- insert v so it becomes a[i]
@Q@    def insertAt(self, i, v):
@Q@        j, k = self._at(i)
@Q@        if j == len(self.blocks):  # (the end: onto the last block)
@Q@            if not j or len(self.blocks[-1]) >= 2 * self.B:
@Q@                self.blocks.append(_Block([v]))
@Q@                self.n += 1
@Q@                return
@Q@            j, k = j - 1, len(self.blocks[-1])
@Q@        vals = self.blocks[j].values()
@Q@        vals.insert(k, v)
@Q@        if len(vals) > 2 * self.B:  # (too long: two blocks)
@Q@            h = len(vals) // 2
@Q@            self.blocks[j:j + 1] = [_Block(vals[:h]), _Block(vals[h:])]
@Q@        else:
@Q@            self.blocks[j].build(vals)
@Q@        self.n += 1
@Q@        if self._idealB(self.n) > 2 * self.B:  # (grown a lot: bigger blocks)
@Q@            self._fill(self.getAll())
@Q@
@Q@    # O(sqrt(N)) amortized -- append v to the end
@Q@    def append(self, v):
@Q@        self.insertAt(self.n, v)
@Q@
@Q@    # O(sqrt(N)) amortized -- insert v at the front (it becomes a[0]; everything else shifts right by one)
@Q@    def appendLeft(self, v):
@Q@        self.insertAt(0, v)
@Q@
@Q@    # O(k + sqrt(N)) amortized -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
@Q@    def insertCopiesAt(self, i, v, k):
@Q@        if k <= 0:
@Q@            return
@Q@        j = self._splitAt(i)
@Q@        self.blocks[j:j] = [_Block([v] * min(self.B, k - s)) for s in range(0, k, self.B)]
@Q@        self.n += k
@Q@        self._tidy()
@R@
@R@    # O(sqrt(N)) amortized -- reverse a[l..r] in place
@R@    def rangeReverse(self, l, r):
@R@        j1 = self._splitAt(l)
@R@        j2 = self._splitAt(r + 1)
@R@        seg = self.blocks[j1:j2][::-1]
@R@        for b in seg:
@R@            b.rev = not b.rev
@R@        self.blocks[j1:j2] = seg
@R@        self._tidy()
@Q@
@Q@    # O(sqrt(N)) amortized -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
@Q@    # taken mod the length (negative shifts right)
@Q@    def rangeRotateLeft(self, l, r, k):
@Q@        k %= r - l + 1
@Q@        if k:
@Q@            j1 = self._splitAt(l)
@Q@            j2 = self._splitAt(l + k)
@Q@            j3 = self._splitAt(r + 1)
@Q@            self.blocks[j1:j3] = self.blocks[j2:j3] + self.blocks[j1:j2]
@Q@            self._tidy()
@Q@
@Q@    # O(sqrt(N)) amortized -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
@Q@    # (negative shifts left)
@Q@    def rangeRotateRight(self, l, r, k):
@Q@        self.rangeRotateLeft(l, r, -k)
@Q@
@Q@    # O(sqrt(N)) amortized -- remove a[l..r] and return it as a SqrtReplace of its own (indices from 0)
@Q@    def cut(self, l, r):
@Q@        j1 = self._splitAt(l)
@Q@        j2 = self._splitAt(r + 1)
@Q@        piece = SqrtReplace()
@Q@        piece.blocks, piece.n, piece.B = self.blocks[j1:j2], r - l + 1, self.B
@Q@        del self.blocks[j1:j2]
@Q@        self.n -= r - l + 1
@Q@        self._tidy()
@Q@        piece._tidy()
@Q@        return piece
@Q@
@Q@    # O(sqrt(N)) amortized -- insert all of other (any SqrtReplace, e.g. a cut piece) so it starts at a[i]; other is
@Q@    # left empty
@Q@    def paste(self, i, other):
@Q@        j = self._splitAt(i)
@Q@        self.blocks[j:j] = other.blocks
@Q@        self.n += other.n
@Q@        other.blocks, other.n = [], 0
@Q@        self._tidy()
@Q@
@Q@    # O(sqrt(N)) amortized -- append all of other at the end; other is left empty
@Q@    def merge(self, other):
@Q@        self.paste(self.n, other)
@Q@
@Q@    # O(sqrt(N)) amortized -- (a[0..k-1], a[k..]) as two SqrtReplaces of their own; this one is left empty
@Q@    def split(self, k):
@Q@        left = SqrtReplace()
@Q@        left.blocks, left.n, left.B = self.blocks, self.n, self.B
@Q@        self.blocks, self.n = [], 0
@Q@        right = left.cut(k, left.n - 1) if k < left.n else SqrtReplace()
@Q@        return left, right
@Q@
@Q@    # O(sqrt(N)) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three SqrtReplaces of their own; this one is left
@Q@    # empty
@Q@    def trisect(self, l, r):
@Q@        left, right = self.split(r + 1)
@Q@        left, mid = left.split(l)
@Q@        return left, mid, right

    # ---- internals ----

    @staticmethod
    def _idealB(n):
        return max(@Q@16@@@!Q@1@@, isqrt(n))

    def _fill(self, vals):  # blocks of about _idealB values holding vals
        n = self.n = len(vals)
        B = self.B = self._idealB(n)
        self.blocks = [_Block(vals[s:s + B]) for s in range(0, n, B)]
@!Q@
@!Q@    def _locate(self, i):  # (block, position in it) of a[i]
@!Q@        return self.blocks[i // self.B], i % self.B
@!Q@
@!Q@    def _span(self, l, r):  # (block, lo, hi, whole, start) for each block meeting a[l..r]: positions lo..hi of it,
@!Q@        B = self.B  # whether that is all of it, and the index of its first value
@!Q@        for j in range(l // B, r // B + 1):
@!Q@            b, start = self.blocks[j], j * B
@!Q@            lo, hi = max(l - start, 0), min(r - start, len(b) - 1)
@!Q@            yield b, lo, hi, lo == 0 and hi == len(b) - 1, start
@Q@
@Q@    # O(N / B + B) amortized -- merge each run of neighbours that fit in one block (each merge is paid for by the
@Q@    # split that made it); when the array has grown so much that B is too small, rebuild into even blocks
@Q@    def _tidy(self):
@Q@        if self._idealB(self.n) > 2 * self.B:
@Q@            return self._fill(self.getAll())
@Q@        out, B = [], self.B
@Q@        for b in self.blocks:
@Q@            if not len(b):
@Q@                continue
@Q@            if out and len(out[-1]) + len(b) <= B:
@Q@                b = _Block(out.pop().values() + b.values())
@Q@            out.append(b)
@Q@        self.blocks = out
@Q@
@Q@    def _at(self, i):  # (block index, position in it) of a[i]; i == size() gives (number of blocks, 0)
@Q@        for j, b in enumerate(self.blocks):
@Q@            m = len(b)
@Q@            if i < m:
@Q@                return j, i
@Q@            i -= m
@Q@        return len(self.blocks), 0
@Q@
@Q@    def _locate(self, i):  # (block, position in it) of a[i]
@Q@        j, k = self._at(i)
@Q@        return self.blocks[j], k
@Q@
@Q@    def _splitAt(self, i):  # make a block start at a[i] (0 <= i <= size()): that block's index
@Q@        j, k = self._at(i)
@Q@        if k:
@Q@            vals = self.blocks[j].values()
@Q@            self.blocks[j:j + 1] = [_Block(vals[:k]), _Block(vals[k:])]
@Q@            return j + 1
@Q@        return j
@Q@
@Q@    def _span(self, l, r):  # (block, lo, hi, whole, start) for each block meeting a[l..r]: positions lo..hi of it,
@Q@        i = 0  # whether that is all of it, and the index of its first value
@Q@        for b in self.blocks:
@Q@            m = len(b)
@Q@            if i + m > l:
@Q@                lo, hi = max(l - i, 0), min(r - i, m - 1)
@Q@                yield b, lo, hi, lo == 0 and hi == m - 1, i
@Q@                if i + m > r:
@Q@                    return
@Q@            i += m

    def _find(self, l, r, x, left):  # the first (left) / last i in [l, r] with a[i] == x, or -1
        spans = list(self._span(l, r)) if l <= r else []
        for b, lo, hi, full, start in (spans if left else reversed(spans)):
            if full and not b.count(x):
                continue
            for k in (range(lo, hi + 1) if left else range(hi, lo - 1, -1)):
                if b.get(k) == x:
                    return start + k
        return -1
'''

SQ_CPP = '''
template <typename T>
struct SqrtReplace {
    struct SafeHash {  // splitmix64 with a seed random per run (the default hash of an integer is easy to attack)
        size_t operator()(const T& x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    // a run of the array: cls[k] is the class of its k-th value@R@ (read backwards when rev)@@. Classes form a union-find
    // (par); a root class holds its value (val) and how many of the block's values are in it (cnt). where: value -> root
    struct Block {
        vector<int> cls, par, cnt;
        vector<T> val;
        unordered_map<T, int, SafeHash> where;
@R@        bool rev = false;

        Block() {}
        explicit Block(const vector<T>& vals) { build(vals); }

        void build(const vector<T>& vals) {  // O(len) -- the classes from scratch
            cls.clear(), par.clear(), cnt.clear(), val.clear(), where.clear();
@R@            rev = false;
            for (const T& v : vals) {
                auto [it, fresh] = where.try_emplace(v, (int)par.size());
                if (fresh) par.push_back(it->second), val.push_back(v), cnt.push_back(0);
                cnt[it->second]++;
                cls.push_back(it->second);
            }
        }

        int size() const { return (int)cls.size(); }

        int find(int c) {  // c's root class (path halving)
            while (par[c] != c) c = par[c] = par[par[c]];
            return c;
        }

        T get(int k) {  // the k-th value
@R@            if (rev) k = size() - 1 - k;
            return val[find(cls[k])];
        }

        vector<T> values() {  // every value, in order
            vector<T> out;
            out.reserve(cls.size());
            for (int c : cls) out.push_back(val[find(c)]);
@R@            if (rev) reverse(out.begin(), out.end());
            return out;
        }

        int count(const T& x) const {  // how many x's
            auto it = where.find(x);
            return it == where.end() ? 0 : cnt[it->second];
        }

        void replace(const T& x, const T& y) {  // O(1) -- every x becomes y: x's class is renamed, or joined to y's
            auto it = where.find(x);
            if (it == where.end()) return;
            int cx = it->second;
            where.erase(it);
            auto jt = where.find(y);
            if (jt == where.end()) {
                val[cx] = y, where[y] = cx;
                return;
            }
            int cy = jt->second;
            if (cnt[cx] > cnt[cy]) swap(cx, cy);  // (union by size)
            par[cx] = cy, cnt[cy] += cnt[cx], val[cy] = y, jt->second = cy;
        }

        // every value becomes v: every class joined into one (O(1) amortized: each join removes one)
        void assignAll(const T& v) {
            int r = -1;
            for (auto& [x, c] : where)
                if (r == -1 || cnt[c] > cnt[r]) r = c;
            for (auto& [x, c] : where)
                if (c != r) par[c] = r, cnt[r] += cnt[c];
            val[r] = v;
            where.clear();
            where[v] = r;
        }

        void assign(int k, const T& v) {  // O(1) amortized -- the k-th value becomes v (a class of its own if v is new here)
@R@            if (rev) k = size() - 1 - k;
            int c = find(cls[k]);
            if (val[c] == v) return;
            if (!--cnt[c]) where.erase(val[c]);
            auto [it, fresh] = where.try_emplace(v, (int)par.size());
            if (fresh) par.push_back(it->second), val.push_back(v), cnt.push_back(0);
            cnt[it->second]++;
            cls[k] = it->second;
            if ((int)par.size() > 2 * size() + 8) build(values());  // (many dead classes: start over, paid for by the assigns)
        }
    };

    vector<Block> blocks;
    int n = 0, B = 1;

@Q@    SqrtReplace() {}  // (an empty one)
@Q@
    // O(N) -- arr: the initial array
    explicit SqrtReplace(const vector<T>& arr) { fill(arr); }

    // O(1) -- the @Q@current @@length of the array
    int size() const { return n; }

    // O(N) -- the whole current array
    vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        for (Block& b : blocks) {
            vector<T> v = b.values();
            out.insert(out.end(), v.begin(), v.end());
        }
        return out;
    }

    // O(@Q@sqrt(N)@@@!Q@1) amortized@@) -- a[i]
    T pointGet(int i) {
        auto [j, k] = locate(i);
        return blocks[j].get(k);
    }

    // O(@Q@sqrt(N)@@@!Q@1) amortized@@) -- a[i] = v
    void pointAssign(int i, const T& v) {
        auto [j, k] = locate(i);
        blocks[j].assign(k, v);
    }

    // O(sqrt(N)) amortized -- every a[i] == x with l <= i <= r becomes y
    void rangeReplace(int l, int r, const T& x, const T& y) {
        if (x == y) return;
        span(l, r, [&](Block& b, int lo, int hi, bool whole, int) {
            if (whole) b.replace(x, y);
            else
                for (int k = lo; k <= hi; k++)
                    if (b.get(k) == x) b.assign(k, y);
            return false;
        });
    }

    // O(sqrt(N)) amortized -- a[l..r] = v
    void rangeAssign(int l, int r, const T& v) {
        span(l, r, [&](Block& b, int lo, int hi, bool whole, int) {
            if (whole) b.assignAll(v);
            else
                for (int k = lo; k <= hi; k++) b.assign(k, v);
            return false;
        });
    }

    // O(sqrt(N)) -- # of i in [l, r] with a[i] == x
    int countOccurrences(int l, int r, const T& x) {
        int res = 0;
        span(l, r, [&](Block& b, int lo, int hi, bool whole, int) {
            if (whole) res += b.count(x);
            else
                for (int k = lo; k <= hi; k++) res += b.get(k) == x;
            return false;
        });
        return res;
    }

    // O(sqrt(N)) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    int leftmostIndexOf(const T& x) { return findIn(0, n - 1, x, true); }

    // O(sqrt(N)) -- the largest i with a[i] == x, or -1 if x isn't in the array
    int rightmostIndexOf(const T& x) { return findIn(0, n - 1, x, false); }

    // O(sqrt(N)) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none
    int leftmostIndexOfInRange(int l, int r, const T& x) { return findIn(l, r, x, true); }

    // O(sqrt(N)) -- the largest i in [l, r] with a[i] == x, or -1 if there is none
    int rightmostIndexOfInRange(int l, int r, const T& x) { return findIn(l, r, x, false); }
@Q@
@Q@    // O(sqrt(N)) amortized -- insert v so it becomes a[i]
@Q@    void insertAt(int i, const T& v) {
@Q@        auto [j, k] = at(i);
@Q@        if (j == (int)blocks.size()) {  // (the end: onto the last block)
@Q@            if (!j || blocks.back().size() >= 2 * B) {
@Q@                blocks.emplace_back(vector<T>{v});
@Q@                n++;
@Q@                return;
@Q@            }
@Q@            j--, k = blocks.back().size();
@Q@        }
@Q@        vector<T> vals = blocks[j].values();
@Q@        vals.insert(vals.begin() + k, v);
@Q@        if ((int)vals.size() > 2 * B) {  // (too long: two blocks)
@Q@            int h = (int)vals.size() / 2;
@Q@            blocks[j] = Block(vector<T>(vals.begin(), vals.begin() + h));
@Q@            blocks.insert(blocks.begin() + j + 1, Block(vector<T>(vals.begin() + h, vals.end())));
@Q@        } else {
@Q@            blocks[j].build(vals);
@Q@        }
@Q@        n++;
@Q@        if (idealB(n) > 2 * B) fill(getAll());  // (grown a lot: bigger blocks)
@Q@    }
@Q@
@Q@    // O(sqrt(N)) amortized -- append v to the end
@Q@    void append(const T& v) { insertAt(n, v); }
@Q@
@Q@    // O(sqrt(N)) amortized -- insert v at the front (it becomes a[0]; everything else shifts right by one)
@Q@    void appendLeft(const T& v) { insertAt(0, v); }
@Q@
@Q@    // O(k + sqrt(N)) amortized -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
@Q@    void insertCopiesAt(int i, const T& v, int k) {
@Q@        if (k <= 0) return;
@Q@        int j = splitAt(i);
@Q@        vector<Block> add;
@Q@        for (int s = 0; s < k; s += B) add.emplace_back(vector<T>(min(B, k - s), v));
@Q@        blocks.insert(blocks.begin() + j, make_move_iterator(add.begin()), make_move_iterator(add.end()));
@Q@        n += k;
@Q@        tidy();
@Q@    }
@R@
@R@    // O(sqrt(N)) amortized -- reverse a[l..r] in place
@R@    void rangeReverse(int l, int r) {
@R@        int j1 = splitAt(l), j2 = splitAt(r + 1);
@R@        reverse(blocks.begin() + j1, blocks.begin() + j2);
@R@        for (int j = j1; j < j2; j++) blocks[j].rev = !blocks[j].rev;
@R@        tidy();
@R@    }
@Q@
@Q@    // O(sqrt(N)) amortized -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
@Q@    // taken mod the length (negative shifts right)
@Q@    void rangeRotateLeft(int l, int r, long long k) {
@Q@        long long m = r - l + 1;
@Q@        k = (k % m + m) % m;
@Q@        if (!k) return;
@Q@        int j1 = splitAt(l), j2 = splitAt(l + (int)k), j3 = splitAt(r + 1);
@Q@        rotate(blocks.begin() + j1, blocks.begin() + j2, blocks.begin() + j3);
@Q@        tidy();
@Q@    }
@Q@
@Q@    // O(sqrt(N)) amortized -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
@Q@    // (negative shifts left)
@Q@    void rangeRotateRight(int l, int r, long long k) {
@Q@        long long m = r - l + 1;
@Q@        rangeRotateLeft(l, r, m - (k % m + m) % m);
@Q@    }
@Q@
@Q@    // O(sqrt(N)) amortized -- remove a[l..r] and return it as a SqrtReplace of its own (indices from 0)
@Q@    SqrtReplace cut(int l, int r) {
@Q@        int j1 = splitAt(l), j2 = splitAt(r + 1);
@Q@        SqrtReplace piece;
@Q@        piece.blocks.assign(make_move_iterator(blocks.begin() + j1), make_move_iterator(blocks.begin() + j2));
@Q@        piece.n = r - l + 1, piece.B = B;
@Q@        blocks.erase(blocks.begin() + j1, blocks.begin() + j2);
@Q@        n -= r - l + 1;
@Q@        tidy(), piece.tidy();
@Q@        return piece;
@Q@    }
@Q@
@Q@    // O(sqrt(N)) amortized -- insert all of other (any SqrtReplace, e.g. a cut piece) so it starts at a[i]; other is
@Q@    // left empty
@Q@    void paste(int i, SqrtReplace& other) {
@Q@        int j = splitAt(i);
@Q@        blocks.insert(blocks.begin() + j, make_move_iterator(other.blocks.begin()), make_move_iterator(other.blocks.end()));
@Q@        n += other.n;
@Q@        other.blocks.clear(), other.n = 0;
@Q@        tidy();
@Q@    }
@Q@    void paste(int i, SqrtReplace&& other) { paste(i, other); }
@Q@
@Q@    // O(sqrt(N)) amortized -- append all of other at the end; other is left empty
@Q@    void merge(SqrtReplace& other) { paste(n, other); }
@Q@    void merge(SqrtReplace&& other) { paste(n, other); }
@Q@
@Q@    // O(sqrt(N)) amortized -- (a[0..k-1], a[k..]) as two SqrtReplaces of their own; this one is left empty
@Q@    pair<SqrtReplace, SqrtReplace> split(int k) {
@Q@        SqrtReplace left;
@Q@        swap(left.blocks, blocks), left.n = n, left.B = B, n = 0;
@Q@        SqrtReplace right = k < left.n ? left.cut(k, left.n - 1) : SqrtReplace();
@Q@        return {std::move(left), std::move(right)};
@Q@    }
@Q@
@Q@    // O(sqrt(N)) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three SqrtReplaces of their own; this one is left
@Q@    // empty
@Q@    tuple<SqrtReplace, SqrtReplace, SqrtReplace> trisect(int l, int r) {
@Q@        auto [left, right] = split(r + 1);
@Q@        auto [first, mid] = left.split(l);
@Q@        return {std::move(first), std::move(mid), std::move(right)};
@Q@    }

    // ---- internals ----

    static int idealB(int m) { return max(@Q@16@@@!Q@1@@, (int)sqrt((double)m)); }

    void fill(const vector<T>& vals) {  // blocks of about idealB values holding vals
        n = (int)vals.size(), B = idealB(n);
        blocks.clear();
        for (int s = 0; s < n; s += B) blocks.emplace_back(vector<T>(vals.begin() + s, vals.begin() + min(n, s + B)));
    }
@!Q@
@!Q@    pair<int, int> locate(int i) const { return {i / B, i % B}; }  // (block index, position in it) of a[i]
@!Q@
@!Q@    // f(block, lo, hi, whole, start) for each block meeting a[l..r] (positions lo..hi of it, whether that is all of
@!Q@    // it, the index of its first value), until f returns true
@!Q@    template <class F>
@!Q@    void span(int l, int r, F f) {
@!Q@        for (int j = l / B; j <= r / B; j++) {
@!Q@            int start = j * B, m = blocks[j].size(), lo = max(l - start, 0), hi = min(r - start, m - 1);
@!Q@            if (f(blocks[j], lo, hi, lo == 0 && hi == m - 1, start)) return;
@!Q@        }
@!Q@    }
@Q@
@Q@    // O(N / B + B) amortized -- merge each run of neighbours that fit in one block (each merge is paid for by the
@Q@    // split that made it); when the array has grown so much that B is too small, rebuild into even blocks
@Q@    void tidy() {
@Q@        if (idealB(n) > 2 * B) return fill(getAll());
@Q@        vector<Block> out;
@Q@        for (Block& b : blocks) {
@Q@            if (!b.size()) continue;
@Q@            if (!out.empty() && out.back().size() + b.size() <= B) {
@Q@                vector<T> vals = out.back().values(), more = b.values();
@Q@                vals.insert(vals.end(), more.begin(), more.end());
@Q@                out.back().build(vals);
@Q@            } else {
@Q@                out.push_back(std::move(b));
@Q@            }
@Q@        }
@Q@        blocks = std::move(out);
@Q@    }
@Q@
@Q@    pair<int, int> at(int i) const {  // (block index, position in it) of a[i]; i == size() gives (number of blocks, 0)
@Q@        for (int j = 0; j < (int)blocks.size(); j++) {
@Q@            if (i < blocks[j].size()) return {j, i};
@Q@            i -= blocks[j].size();
@Q@        }
@Q@        return {(int)blocks.size(), 0};
@Q@    }
@Q@
@Q@    pair<int, int> locate(int i) const { return at(i); }
@Q@
@Q@    int splitAt(int i) {  // make a block start at a[i] (0 <= i <= size()): that block's index
@Q@        auto [j, k] = at(i);
@Q@        if (!k) return j;
@Q@        vector<T> vals = blocks[j].values();
@Q@        blocks[j].build(vector<T>(vals.begin(), vals.begin() + k));
@Q@        blocks.insert(blocks.begin() + j + 1, Block(vector<T>(vals.begin() + k, vals.end())));
@Q@        return j + 1;
@Q@    }
@Q@
@Q@    // f(block, lo, hi, whole, start) for each block meeting a[l..r] (positions lo..hi of it, whether that is all of
@Q@    // it, the index of its first value), until f returns true
@Q@    template <class F>
@Q@    void span(int l, int r, F f) {
@Q@        int i = 0;
@Q@        for (Block& b : blocks) {
@Q@            int m = b.size();
@Q@            if (i + m > l) {
@Q@                int lo = max(l - i, 0), hi = min(r - i, m - 1);
@Q@                if (f(b, lo, hi, lo == 0 && hi == m - 1, i) || i + m > r) return;
@Q@            }
@Q@            i += m;
@Q@        }
@Q@    }

    int findIn(int l, int r, const T& x, bool left) {  // the first (left) / last i in [l, r] with a[i] == x, or -1
        if (l > r) return -1;
        vector<tuple<Block*, int, int, bool, int>> parts;
        span(l, r, [&](Block& b, int lo, int hi, bool whole, int start) {
            parts.emplace_back(&b, lo, hi, whole, start);
            return false;
        });
        if (!left) reverse(parts.begin(), parts.end());
        for (auto& [b, lo, hi, whole, start] : parts) {
            if (whole && !b->count(x)) continue;
            for (int k = left ? lo : hi; left ? k <= hi : k >= lo; k += left ? 1 : -1)
                if (b->get(k) == x) return start + k;
        }
        return -1;
    }
};
'''


def sq_inline(text, f):  # @X@..@@ inside a line: kept only when flag X is on (@!X@: off)
    return re.sub(r"(?<!\n)@(!?)([A-Z])@(.*?)@@", lambda m: m.group(3) if f[m.group(2)] != (m.group(1) == "!") else "", text)


def sq_py(seq, rev):
    f = {"Q": seq, "R": rev}
    text = pick(sq_inline(SQ_PY, f), f)
    head, sep, rest = text.partition("\n\n\nclass _Block")
    return sq_header("#", seq, rev) + "\n" + head + "\n\n" + wrap(sq_describe(seq, rev), "#") + "class _Block" + rest


def sq_cpp(seq, rev):
    f = {"Q": seq, "R": rev}
    return (sq_header("//", seq, rev) + "\n" + wrap(sq_describe(seq, rev), "//") +
            "// T: any type with a hash (int, long long, char, ...)\n" + pick(sq_inline(SQ_CPP, f), f))


def sq_folder(seq, rev):
    name = folder_name(sq_ops(seq, rev)) + "__sqrt"  # (the same ops as a value-map seg tree's)
    return name if len(name) <= 180 else "sqrt-replace" + ("-seq" if seq else "") + ("-rev" if rev else "")


# ================================================================================================ main

def write(folder, py_text, cpp_text, seen):
    assert folder not in seen, folder
    seen.add(folder)
    os.makedirs(os.path.join(DIR, folder), exist_ok=True)
    write_template(os.path.join(DIR, folder, "template.py"), py_text)
    write_template(os.path.join(DIR, folder, "template.cpp"), cpp_text)


def main():
    for d in os.listdir(DIR):
        t = os.path.join(DIR, d, "template.py")
        if os.path.exists(t) and any(m in " ".join(open(t).read().replace("#", " ").split()) for m in MARKS):
            shutil.rmtree(os.path.join(DIR, d))
    seen = set()
    for cnt, point in pt_variants():
        write(folder_name(pt_ops(cnt, point)), pt_py(cnt, point), pt_cpp(cnt, point), seen)
    for cnt, sm in vm_variants():
        write(folder_name(vm_ops(cnt, sm)), vm_py(cnt, sm), vm_cpp(cnt, sm), seen)
    for v in vt_variants():
        write(vt_folder(*v), vt_py(*v), vt_cpp(*v), seen)
    for seq, rev in sq_variants():
        write(sq_folder(seq, rev), sq_py(seq, rev), sq_cpp(seq, rev), seen)
    print("wrote", len(seen), "mass change templates")


if __name__ == "__main__":
    main()
