"""Sparse (dynamic) versions of the value-tracking templates: sparse.py + sparse.cpp per folder.

    python3 sparse_more.py

Every position of [lo, hi] starts at 0, so 0 is special: only positions holding a nonzero value are stored, and a
query adds in the untouched / zero positions from the range length (e.g. a range with a zero in it has one more
distinct value; a range of length k with c nonzero positions holds k - c zeros).
"""
import os

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
PLAIN = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]


def header(cm, ops, dtype, comp, mem, note):
    lines = [f"{cm} @operations: {' '.join(ops)}", f"{cm} @data-structure-type: {dtype}", f"{cm} @complexities:"]
    lines += [f"{cm}   {o}: {comp.get(o, 'log(U)')}" for o in ops] + [f"{cm}   build: 1"]
    node, tags, other = mem
    lines += [f"{cm} @memory:", f"{cm}   layout: sparse", f"{cm}   node: {node}", f"{cm}   tags: {tags}",
              f"{cm}   other: {other}", f"{cm}   note: {note}"]
    return "\n".join(lines) + "\n"


def write(ops, dtype, comp, mem, note, py, cpp):
    ops = sorted(ops)
    folder = "-".join(ops)
    path = os.path.join(DIR, folder)
    assert os.path.isdir(path), folder
    open(os.path.join(path, "sparse.py"), "w").write(header("#", ops, dtype, comp, mem, note) + py)
    open(os.path.join(path, "sparse.cpp"), "w").write(header("//", ops, dtype, comp, mem, note) + cpp)
    print("wrote", folder)


def sorted_list_src():
    """The bucketed SortedList the dense templates embed (one copy of the code, read from there)."""
    src = open(os.path.join(DIR, "countDistinct-pointAdd-pointAssign-pointChmax-pointChmin-pointGet", "template.py")).read()
    return src[src.index("class SortedList:"):].rstrip() + "\n"


PY_POINTS = '''
    # O(1) -- a[i]
    def pointGet(self, i):
        return self.vals.get(i, 0)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
'''

CPP_POINTS = '''
    // O(1) expected -- a[i]
    T pointGet(long long i) const {
        auto it = vals.find(i);
        return it == vals.end() ? T(0) : it->second;
    }

    // a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
'''

# a dynamic prefix tree over [lo, hi] in a shared pool: add(i, v) adds v at i, prefix(i) = sum over [lo, i]
CPP_PREFIX_POOL = '''    struct Node {{ {ftype} f; int l, r; }};  // f: total of the stored changes under the node
    static inline vector<Node> pool{{Node{{}}}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root = 0;

    // O(1) -- forget every node of every {name}<T>; call between test cases, then build new trees
    static void resetPool() {{ pool.resize(1); }}

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) {{ pool.reserve(nodes); }}

    static int make() {{
        pool.push_back(Node{{}});
        return (int)pool.size() - 1;
    }}

    // O(logU) -- the change v at position i, added into every node on its root path
    void add(long long i, {ftype} v) {{
        if (!root) root = make();
        int y = root;
        long long a = lo, b = hi;
        while (true) {{
            pool[y].f {op}= v;
            if (a == b) return;
            long long m = a + (b - a) / 2;
            bool right = i > m;
            int c = right ? pool[y].r : pool[y].l;
            if (!c) {{
                c = make();
                (right ? pool[y].r : pool[y].l) = c;
            }}
            y = c;
            if (right) a = m + 1;
            else b = m;
        }}
    }}

    // O(logU) -- total of the changes at positions lo..i (0 for i < lo)
    {ftype} prefix(long long i) const {{
        {ftype} s = 0;
        int y = i < lo ? 0 : root;
        long long a = lo, b = hi;
        while (y) {{
            if (b <= i) {{ s {op}= pool[y].f; break; }}
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else s {op}= pool[pool[y].l].f, y = pool[y].r, a = m + 1;
        }}
        return s;
    }}
'''

PY_FENWICK = '''
    # O(logU) -- the change v at position i, into the Fenwick tree over offsets
    def _add(self, i, v):
        d, n = self.d, self.n
        x = i - self.lo + 1
        while x <= n:
            d[x] = d.get(x, 0) {op} v
            x += x & -x

    # O(logU) -- total of the changes at positions lo..i (0 for i < lo)
    def _prefix(self, i):
        d = self.d
        s = 0
        x = i - self.lo + 1
        while x > 0:
            s {op}= d.get(x, 0)
            x &= x - 1
        return s
'''

# ------------------------------------------------------------------------------------------------ all even (xor hashing)

write(PLAIN + ["doAllElementsAppearEvenFrequency"], "BIT", {"pointGet": "1"},
      ("h[1*log(U)]", "none", "links[2*log(U)] vals[1] tag[1]"),
      "per point write, the O(logU) entries above it; every value has a random 64-bit tag and position i stores "
      "tag(a[i]) ^ tag(0), so untouched positions store nothing and a range adds tag(0) once per odd length. Python: "
      "a Fenwick tree in a dict; C++: a dynamic prefix-xor tree in one shared node pool, call resetPool() between "
      "test cases", '''
import random

# Range "does every value appear an even number of times?" via xor hashing, with point updates, over any index
# range [lo, hi] (huge or negative is fine); every position starts at 0. Each distinct value gets a random 64-bit
# tag; xor over a range cancels tags in pairs, so an all-even range hashes to 0 (false positives ~q / 2^64).
# Sparse: position i stores tag(a[i]) ^ tag(0) in a dict Fenwick tree (0 for the untouched), so the xor of the
# real tags over [l, r] is the stored xor, plus tag(0) when the length is odd.


class SparseXorEven:
    __slots__ = ("lo", "hi", "n", "d", "vals", "tag", "zero")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}
        self.vals = {}  # i -> a[i], nonzero values only
        self.tag = {}
        self.zero = self._tagOf(0)

    # O(1) -- random tag for a value, minted on first sight
    def _tagOf(self, v):
        t = self.tag.get(v)
        if t is None:
            t = self.tag[v] = random.getrandbits(64)
        return t
''' + PY_FENWICK.format(op="^") + '''
    # O(logU) -- True iff every value in a[l..r] appears an even number of times
    def doAllElementsAppearEvenFrequency(self, l, r):
        h = self._prefix(r) ^ self._prefix(l - 1)
        if (r - l + 1) & 1:
            h ^= self.zero
        return h == 0

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        d = self._tagOf(self.vals.get(i, 0)) ^ self._tagOf(val)
        if val:
            self.vals[i] = val
        else:
            self.vals.pop(i, None)
        if d:
            self._add(i, d)
''' + PY_POINTS, '''
// Range "does every value appear an even number of times?" via xor hashing, with point updates, over any index
// range [lo, hi] (huge or negative is fine); every position starts at 0. Each distinct value gets a random 64-bit
// tag; xor over a range cancels tags in pairs, so an all-even range hashes to 0 (false positives ~q / 2^64).
// Sparse: position i stores tag(a[i]) ^ tag(0) in a dynamic prefix-xor tree (nothing for the untouched), so the xor
// of the real tags over [l, r] is the stored xor, plus tag(0) when the length is odd. Nodes live in one pool shared
// by every SparseXorEven<T>. T: any hashable type with == (0 must be a value).
template <typename T>
struct SparseXorEven {
    using U64 = unsigned long long;
''' + CPP_PREFIX_POOL.format(ftype="U64", op="^", name="SparseXorEven") + '''
    unordered_map<long long, T> vals;  // nonzero values only
    unordered_map<T, U64> tag;
    mt19937_64 rng;
    U64 zero;

    // O(1) -- all zeros over [lo, hi]. Seeded from the clock: a fixed seed is hackable.
    SparseXorEven(long long lo, long long hi) : lo(lo), hi(hi), rng(chrono::steady_clock::now().time_since_epoch().count()) {
        zero = tagOf(T(0));
    }

    // O(1) amortized -- random tag for a value, minted on first sight
    U64 tagOf(const T& v) {
        auto it = tag.find(v);
        if (it != tag.end()) return it->second;
        return tag[v] = rng();
    }

    // O(logU) -- true iff every value in a[l..r] appears an even number of times
    bool doAllElementsAppearEvenFrequency(long long l, long long r) const {
        U64 h = prefix(r) ^ prefix(l - 1);
        if ((r - l + 1) & 1) h ^= zero;
        return h == 0;
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        U64 d = tagOf(pointGet(i)) ^ tagOf(v);
        if (v != T(0)) vals[i] = v;
        else vals.erase(i);
        if (d) add(i, d);
    }
''' + CPP_POINTS + "};\n")

# ------------------------------------------------------------------------------------------------ count / k-th occurrence of one value

write(PLAIN + ["countValue", "kthOccurrence"], "BIT", {"pointGet": "1"},
      ("cnt[1*log(U)]", "none", "links[2*log(U)] vals[1]"),
      "per point write, the O(logU) entries above it; position i stores [a[i] == number] - [0 == number], so the "
      "untouched store nothing; kthOccurrence descends / binary-lifts. Python: a Fenwick tree in a dict; C++: a "
      "dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases", '''
# Count / find the k-th occurrence of one value (fixed at build time) in a range, with point updates, over any index
# range [lo, hi] (huge or negative is fine); every position starts at 0. An index counts if a[i] == number; untouched
# positions count iff number == 0 (z below), so position i stores [a[i] == number] - z in a dict Fenwick tree and a
# count over k positions is z * k plus the stored sum. kthOccurrence binary-lifts over the tree.


class SparseCountValueBIT:
    __slots__ = ("lo", "hi", "n", "d", "vals", "number", "z")

    # O(1)
    def __init__(self, lo, hi, number):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}
        self.vals = {}  # i -> a[i], nonzero values only
        self.number = number
        self.z = int(number == 0)
''' + PY_FENWICK.format(op="+") + '''
    # O(logU) -- how many i in [lo, i] have a[i] == number
    def _count(self, i):
        return self.z * (i - self.lo + 1) + self._prefix(i)

    # O(logU) -- how many i in [l, r] have a[i] == number
    def countValue(self, l, r):
        return self._count(r) - self._count(l - 1) if l <= r else 0

    # O(logU) -- index of the k-th (1-indexed) i in [l, r] with a[i] == number, or lo - 1
    def kthOccurrence(self, l, r, k):
        if k <= 0 or k > self.countValue(l, r):
            return self.lo - 1
        target = self._count(l - 1) + k
        d, n, z = self.d, self.n, self.z
        pos = acc = 0
        step = 1 << (n.bit_length() - 1)
        while step:
            nxt = pos + step
            if nxt <= n:  # Fenwick node nxt covers the step offsets after pos
                v = acc + d.get(nxt, 0) + z * step
                if v < target:
                    pos, acc = nxt, v
            step >>= 1
        return self.lo + pos

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        old = self.vals.get(i, 0)
        diff = (val == self.number) - (old == self.number)
        if val:
            self.vals[i] = val
        else:
            self.vals.pop(i, None)
        if diff:
            self._add(i, diff)
''' + PY_POINTS, '''
// Count / find the k-th occurrence of one value (fixed at build time) in a range, with point updates, over any index
// range [lo, hi] (huge or negative is fine); every position starts at 0. An index counts if a[i] == number; untouched
// positions count iff number == 0 (z below), so position i stores [a[i] == number] - z in a dynamic prefix-sum tree
// and a count over k positions is z * k plus the stored sum. kthOccurrence descends the tree. Nodes live in one pool
// shared by every SparseCountValueBIT<T>. T: any type with ==.
template <typename T>
struct SparseCountValueBIT {
''' + CPP_PREFIX_POOL.format(ftype="long long", op="+", name="SparseCountValueBIT") + '''
    T number;
    long long z;
    unordered_map<long long, T> vals;  // nonzero values only

    // O(1) -- all zeros over [lo, hi]
    SparseCountValueBIT(long long lo, long long hi, T number) : lo(lo), hi(hi), number(number), z(number == T(0)) {}

    // O(logU) -- how many i in [lo, i] have a[i] == number
    long long count(long long i) const { return z * (i - lo + 1) + prefix(i); }

    // O(logU) -- how many i in [l, r] have a[i] == number
    long long countValue(long long l, long long r) const { return l <= r ? count(r) - count(l - 1) : 0; }

    // O(logU) -- index of the k-th (1-indexed) i in [l, r] with a[i] == number, or lo - 1
    long long kthOccurrence(long long l, long long r, long long k) const {
        if (k <= 0 || k > countValue(l, r)) return lo - 1;
        long long target = count(l - 1) + k, acc = 0, a = lo, b = hi;
        int y = root;
        while (a < b) {  // node 0 is a block of untouched positions: z per position
            long long m = a + (b - a) / 2, c = acc + z * (m - a + 1) + pool[pool[y].l].f;
            if (c >= target) y = pool[y].l, b = m;
            else acc = c, y = pool[y].r, a = m + 1;
        }
        return a;
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        long long diff = (long long)(v == number) - (long long)(pointGet(i) == number);
        if (v != T(0)) vals[i] = v;
        else vals.erase(i);
        if (diff) add(i, diff);
    }
''' + CPP_POINTS + "};\n")

# ------------------------------------------------------------------------------------------------ count occurrences of x

SL = sorted_list_src()
write(PLAIN + ["countOccurrences"], "positions", {"pointGet": "1"},
      ("pos[2]", "none", "vals[1]"),
      "per point write, one index in its value's sorted list and one in the list of nonzero positions (C++: "
      "order-statistics trees; Python: bucketed SortedLists, below); zeros are counted as the range length minus the "
      "nonzero positions in it. No shared pool: every tree owns its memory", f'''
from bisect import bisect_left, bisect_right, insort

# "How many times does x appear in a[l..r]?" with point updates, over any index range [lo, hi] (huge or negative is
# fine); every position starts at 0. Each nonzero value keeps its sorted indices, and so does "any nonzero value";
# x != 0 is two rank queries in x's list, and x == 0 is the range length minus the nonzero positions in it.


class SparseOccurrenceLists:
    __slots__ = ("lo", "hi", "vals", "pos", "nz")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.vals = {{}}  # i -> a[i], nonzero values only
        self.pos = {{}}  # value -> SortedList of its indices (nonzero values only)
        self.nz = SortedList()  # indices holding a nonzero value

    # O(logU) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        if l > r:
            return 0
        if x == 0:
            nz = self.nz
            return (r - l + 1) - (nz.countLess(r + 1) - nz.countLess(l))
        s = self.pos.get(x)
        return 0 if s is None else s.countLess(r + 1) - s.countLess(l)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        old = self.vals.get(i, 0)
        if old == val:
            return
        if old:
            s = self.pos[old]
            s.remove(i)
            if not len(s):
                del self.pos[old]
        else:
            self.nz.add(i)
        if val:
            s = self.pos.get(val)
            if s is None:
                s = self.pos[val] = SortedList()
            s.add(i)
            self.vals[i] = val
        else:
            self.nz.remove(i)
            del self.vals[i]
''' + PY_POINTS + "\n\n" + SL, '''
// "How many times does x appear in a[l..r]?" with point updates, over any index range [lo, hi] (huge or negative is
// fine); every position starts at 0. Each nonzero value keeps its indices in an order-statistics tree (GCC pb_ds),
// and so does "any nonzero value"; x != 0 is two order_of_key calls, x == 0 is the range length minus the nonzero
// positions in it. T: any type usable as a std::map key (0 must be a value).
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

template <typename T>
struct SparseOccurrenceLists {
    using IndexSet = __gnu_pbds::tree<long long, __gnu_pbds::null_type, less<long long>, __gnu_pbds::rb_tree_tag,
                                      __gnu_pbds::tree_order_statistics_node_update>;
    long long lo, hi;
    unordered_map<long long, T> vals;  // nonzero values only
    map<T, IndexSet> pos;              // nonzero values only
    IndexSet nz;                       // indices holding a nonzero value

    // O(1) -- all zeros over [lo, hi]
    SparseOccurrenceLists(long long lo, long long hi) : lo(lo), hi(hi) {}

    // O(logU) -- # of i in [l, r] with a[i] == x
    long long countOccurrences(long long l, long long r, const T& x) const {
        if (l > r) return 0;
        if (x == T(0)) return (r - l + 1) - (long long)(nz.order_of_key(r + 1) - nz.order_of_key(l));
        auto it = pos.find(x);
        if (it == pos.end()) return 0;
        return (long long)(it->second.order_of_key(r + 1) - it->second.order_of_key(l));
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        T old = pointGet(i);
        if (old == v) return;
        if (old != T(0)) {
            auto it = pos.find(old);
            it->second.erase(i);
            if (it->second.empty()) pos.erase(it);
        } else {
            nz.insert(i);
        }
        if (v != T(0)) {
            pos[v].insert(i);
            vals[i] = v;
        } else {
            nz.erase(i);
            vals.erase(i);
        }
    }
''' + CPP_POINTS + "};\n")

# ------------------------------------------------------------------------------------------------ all distinct

write(PLAIN + ["allDistinct"], "seg-tree", {"pointGet": "1"},
      ("mn[3*log(U)] cnt[3*log(U)]", "none", "links[6*log(U)] chains[1] vals[1]"),
      "per point write, at most 3 root paths (i, its old and new predecessor); each node keeps the min nxt and the "
      "number of nonzero positions below it; chains maps each nonzero value to its sorted positions (C++: std::set; "
      "Python: a bucketed SortedList, below). C++: one shared node pool (node 0 = untouched), call resetPool() between "
      "test cases; Python: dicts keyed by heap index", f'''
from bisect import bisect_left, bisect_right, insort

# "Are all values in a[l..r] distinct?" with point updates, over any index range [lo, hi] (huge or negative is fine);
# every position starts at 0. Two zeros repeat, so a range with >= 2 positions holding 0 is not distinct. Among the
# nonzero positions, nxt[i] = the next position with the same value (none: INF), and they are distinct iff
# min(nxt[l..r]) > r. Sparse: dicts keyed by heap index over a power-of-two cover of [lo, hi] keep, per node, the
# min nxt (missing: INF) and the number of nonzero positions (missing: 0).

INF = float("inf")


class SparseDistinctTree:
    __slots__ = ("lo", "hi", "size", "mn", "cnt", "vals", "chains")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of i is size + (i - lo)
        self.mn = {{}}
        self.cnt = {{}}
        self.vals = {{}}  # i -> a[i], nonzero values only
        self.chains = {{}}  # nonzero value -> SortedList of its positions

    # O(logU) -- position i now has nxt[i] = v and is nonzero (c = 1) or zero (c = 0, v = INF)
    def _set(self, i, v, c):
        mn, cnt = self.mn, self.cnt
        p = self.size + i - self.lo
        mn[p], cnt[p] = v, c
        p >>= 1
        while p:
            a, b = mn.get(2 * p, INF), mn.get(2 * p + 1, INF)
            mn[p] = a if a < b else b
            cnt[p] = cnt.get(2 * p, 0) + cnt.get(2 * p + 1, 0)
            p >>= 1

    # O(logU) -- True iff no value repeats inside a[l..r]
    def allDistinct(self, l, r):
        mn, cnt = self.mn, self.cnt
        lo_, hi_ = l + self.size - self.lo, r + self.size - self.lo + 1
        best, c = INF, 0
        while lo_ < hi_:
            if lo_ & 1:
                best = min(best, mn.get(lo_, INF))
                c += cnt.get(lo_, 0)
                lo_ += 1
            if hi_ & 1:
                hi_ -= 1
                best = min(best, mn.get(hi_, INF))
                c += cnt.get(hi_, 0)
            lo_ >>= 1
            hi_ >>= 1
        return (r - l + 1) - c < 2 and best > r

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        old = self.vals.get(i, 0)
        if old == val:
            return
        if old:
            s = self.chains[old]
            p, nx = s.pred(i), s.succ(i)
            if p is not None:
                self._set(p, INF if nx is None else nx, 1)
            s.remove(i)
            if not len(s):
                del self.chains[old]
        if val:
            s = self.chains.get(val)
            if s is None:
                s = self.chains[val] = SortedList()
            s.add(i)
            p, nx = s.pred(i), s.succ(i)
            self._set(i, INF if nx is None else nx, 1)
            if p is not None:
                self._set(p, i, 1)
            self.vals[i] = val
        else:
            self._set(i, INF, 0)
            del self.vals[i]
''' + PY_POINTS + "\n\n" + SL, '''
// "Are all values in a[l..r] distinct?" with point updates, over any index range [lo, hi] (huge or negative is fine);
// every position starts at 0. Two zeros repeat, so a range with >= 2 positions holding 0 is not distinct. Among the
// nonzero positions, nxt[i] = the next position with the same value (none: INF), and they are distinct iff
// min(nxt[l..r]) > r. Sparse: a dynamic tree keeps, per node, the min nxt and the number of nonzero positions; nodes
// live in one pool shared by every SparseDistinctTree<T>, node 0 is the untouched block. T: a std::map key type.
template <typename T>
struct SparseDistinctTree {
    static constexpr long long INF = numeric_limits<long long>::max();
    struct Node { long long mn, cnt; int l, r; };
    static inline vector<Node> pool{Node{INF, 0, 0, 0}};  // node 0: untouched (no nxt, no nonzero), children itself
    long long lo, hi;
    int root = 0;
    unordered_map<long long, T> vals;  // nonzero values only
    map<T, set<long long>> chains;     // nonzero value -> sorted positions

    // O(1) -- all zeros over [lo, hi]
    SparseDistinctTree(long long lo, long long hi) : lo(lo), hi(hi) {}

    // O(1) -- forget every node of every SparseDistinctTree<T>; call between test cases, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{INF, 0, 0, 0});
        return (int)pool.size() - 1;
    }

    // O(logU) -- position i now has nxt[i] = v and is nonzero (c = 1) or zero (c = 0, v = INF)
    void setLeaf(long long i, long long v, long long c) {
        if (!root) root = make();
        int path[130], d = 0, y = root;
        long long a = lo, b = hi;
        while (a < b) {
            path[d++] = y;
            long long m = a + (b - a) / 2;
            bool right = i > m;
            int ch = right ? pool[y].r : pool[y].l;
            if (!ch) {
                ch = make();
                (right ? pool[y].r : pool[y].l) = ch;
            }
            y = ch;
            if (right) a = m + 1;
            else b = m;
        }
        pool[y].mn = v, pool[y].cnt = c;
        while (d--) {
            Node& p = pool[path[d]];
            p.mn = min(pool[p.l].mn, pool[p.r].mn);
            p.cnt = pool[p.l].cnt + pool[p.r].cnt;
        }
    }

    // (min nxt, # nonzero) over [max(l, a), min(r, b)] under node x
    pair<long long, long long> query(int x, long long a, long long b, long long l, long long r) const {
        if (!x) return {INF, 0};
        if (l <= a && b <= r) return {pool[x].mn, pool[x].cnt};
        long long m = a + (b - a) / 2;
        pair<long long, long long> res{INF, 0};
        if (l <= m) res = query(pool[x].l, a, m, l, r);
        if (r > m) {
            auto q = query(pool[x].r, m + 1, b, l, r);
            res = {min(res.first, q.first), res.second + q.second};
        }
        return res;
    }

    // O(logU) -- true iff no value repeats inside a[l..r]
    bool allDistinct(long long l, long long r) const {
        auto [mn, c] = query(root, lo, hi, l, r);
        return (r - l + 1) - c < 2 && mn > r;
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        T old = pointGet(i);
        if (old == v) return;
        if (old != T(0)) {
            auto oldIt = chains.find(old);
            set<long long>& from = oldIt->second;
            auto it = from.find(i);
            if (it != from.begin()) {
                auto nx = next(it);
                setLeaf(*prev(it), nx == from.end() ? INF : *nx, 1);
            }
            from.erase(it);
            if (from.empty()) chains.erase(oldIt);
        }
        if (v != T(0)) {
            set<long long>& to = chains[v];
            auto jt = to.insert(i).first;
            auto nx = next(jt);
            setLeaf(i, nx == to.end() ? INF : *nx, 1);
            if (jt != to.begin()) setLeaf(*prev(jt), i, 1);
            vals[i] = v;
        } else {
            setLeaf(i, INF, 0);
            vals.erase(i);
        }
    }
''' + CPP_POINTS + "};\n")

# ------------------------------------------------------------------------------------------------ count distinct

L2 = "log(U)*log(U)"
write(PLAIN + ["countDistinct"], "BIT", {"countDistinct": L2, "pointAdd": L2, "pointAssign": L2, "pointChmax": L2,
                                          "pointChmin": L2, "pointGet": "1"},
      ("sets[3*log(U)] last[3*log(U)]", "none", "nxt[1] chains[1] vals[1]"),
      "per point write, at most 3 nxt changes, each touching the O(logU) Fenwick nodes above its position; node j "
      "keeps an ordered set of the nxt values below it (C++: pb_ds trees in a hash map; Python: bucketed SortedLists, "
      "below, in a dict). No shared pool: every tree owns its memory", f'''
from bisect import bisect_left, bisect_right, insort

# Range count distinct with point updates in O(log^2 U), online, over any index range [lo, hi] (huge or negative is
# fine); every position starts at 0. Only nonzero positions are tracked: nxt[i] = the next position with the same
# value (none: NONE = hi + 1), and the distinct nonzero values in [l, r] are #{{i in [l, r] : nxt[i] > r}}, a 2D count
# on a Fenwick tree (in a dict, over offsets) whose node j keeps an ordered set of the nxt values < NONE below it,
# plus a plain count of the NONE ones. 0 is one more distinct value when the range has fewer nonzero positions than
# its length. An assign changes at most 3 nxt values, in an order that never lets two positions share an nxt value.


class SparseDistinctBIT:
    __slots__ = ("lo", "hi", "n", "none", "vals", "nxt", "last", "sets", "chains")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.none = hi + 1
        self.vals = {{}}  # i -> a[i], nonzero values only
        self.nxt = {{}}  # nonzero position -> nxt
        self.last = {{}}  # Fenwick tree counting positions with nxt == NONE
        self.sets = {{}}  # Fenwick tree of SortedLists of nxt values < NONE
        self.chains = {{}}  # nonzero value -> SortedList of its positions

    def _lastAdd(self, i, d):
        last, n = self.last, self.n
        j = i - self.lo + 1
        while j <= n:
            last[j] = last.get(j, 0) + d
            j += j & -j

    # how many tracked positions p <= x have nxt[p] > r (0 for x < lo)
    def _countPast(self, x, r):
        last, sets = self.last, self.sets
        res = 0
        j = x - self.lo + 1
        while j > 0:
            res += last.get(j, 0)
            s = sets.get(j)
            if s is not None:
                res += len(s) - s.countLess(r + 1)
            j &= j - 1
        return res

    # O(log^2 U) -- nxt[i] = v (None: i is not tracked, it holds 0)
    def _setNxt(self, i, v):
        old = self.nxt.get(i)
        if old == v:
            return
        n, sets = self.n, self.sets
        if old == self.none:
            self._lastAdd(i, -1)
        elif old is not None:
            j = i - self.lo + 1
            while j <= n:
                s = sets[j]
                s.remove(old)
                if not len(s):
                    del sets[j]
                j += j & -j
        if v == self.none:
            self._lastAdd(i, 1)
        elif v is not None:
            j = i - self.lo + 1
            while j <= n:
                s = sets.get(j)
                if s is None:
                    s = sets[j] = SortedList()
                s.add(v)
                j += j & -j
        if v is None:
            del self.nxt[i]
        else:
            self.nxt[i] = v

    # O(log^2 U) -- # of distinct values in a[l..r]
    def countDistinct(self, l, r):
        if l > r:
            return 0
        lo1 = self.lo - 1  # every nxt is > lo - 1, so this counts the tracked positions
        nonzero = self._countPast(r, lo1) - self._countPast(l - 1, lo1)
        return self._countPast(r, r) - self._countPast(l - 1, r) + (nonzero < r - l + 1)

    # O(log^2 U) -- a[i] = val; rewires i's old predecessor, i's new predecessor, and i
    def pointAssign(self, i, val):
        old = self.vals.get(i, 0)
        if old == val:
            return
        if old:
            s = self.chains[old]
            self._setNxt(i, None)  # unlink i first, so its successor is free for its predecessor
            p, nx = s.pred(i), s.succ(i)
            if p is not None:
                self._setNxt(p, self.none if nx is None else nx)
            s.remove(i)
            if not len(s):
                del self.chains[old]
        if val:
            s = self.chains.get(val)
            if s is None:
                s = self.chains[val] = SortedList()
            s.add(i)
            p, nx = s.pred(i), s.succ(i)
            if p is not None:
                self._setNxt(p, i)  # move the predecessor off the successor first, then hand it to i
            self._setNxt(i, self.none if nx is None else nx)
            self.vals[i] = val
        else:
            del self.vals[i]
''' + PY_POINTS + "\n\n" + SL, '''
// Range count distinct with point updates in O(log^2 U), online, over any index range [lo, hi] (huge or negative is
// fine); every position starts at 0. Only nonzero positions are tracked: nxt[i] = the next position with the same
// value (none: NONE = hi + 1), and the distinct nonzero values in [l, r] are #{i in [l, r] : nxt[i] > r}, a 2D count
// on a Fenwick tree (hash maps over offsets) whose node j keeps an order-statistics set (GCC pb_ds) of the nxt values
// < NONE below it, plus a plain count of the NONE ones. 0 is one more distinct value when the range has fewer nonzero
// positions than its length. An assign changes at most 3 nxt values, in an order that never lets two positions share
// an nxt value. T: any type usable as a std::map key (0 must be a value).
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

template <typename T>
struct SparseDistinctBIT {
    using OrderedSet = __gnu_pbds::tree<long long, __gnu_pbds::null_type, less<long long>, __gnu_pbds::rb_tree_tag,
                                        __gnu_pbds::tree_order_statistics_node_update>;
    long long lo, hi, n, none;
    unordered_map<long long, T> vals;          // nonzero values only
    unordered_map<long long, long long> nxt;   // tracked (nonzero) positions only
    unordered_map<long long, long long> last;  // Fenwick tree counting positions with nxt == NONE
    unordered_map<long long, OrderedSet> sets; // Fenwick tree of nxt values < NONE
    map<T, set<long long>> chains;             // nonzero value -> sorted positions

    // O(1) -- all zeros over [lo, hi]
    SparseDistinctBIT(long long lo, long long hi) : lo(lo), hi(hi), n(hi - lo + 1), none(hi + 1) {}

    void lastAdd(long long i, long long d) {
        for (long long j = i - lo + 1; j <= n; j += j & -j) last[j] += d;
    }

    // how many tracked positions p <= x have nxt[p] > r (0 for x < lo)
    long long countPast(long long x, long long r) const {
        long long res = 0;
        for (long long j = x - lo + 1; j > 0; j &= j - 1) {
            auto lt = last.find(j);
            if (lt != last.end()) res += lt->second;
            auto st = sets.find(j);
            if (st != sets.end()) res += (long long)(st->second.size() - st->second.order_of_key(r + 1));
        }
        return res;
    }

    // O(log^2 U) -- nxt[i] = v (LLONG_MIN: i is not tracked, it holds 0)
    void setNxt(long long i, long long v) {
        auto it = nxt.find(i);
        long long old = it == nxt.end() ? LLONG_MIN : it->second;
        if (old == v) return;
        if (old == none) lastAdd(i, -1);
        else if (old != LLONG_MIN)
            for (long long j = i - lo + 1; j <= n; j += j & -j) {
                auto st = sets.find(j);
                st->second.erase(old);
                if (st->second.empty()) sets.erase(st);
            }
        if (v == none) lastAdd(i, 1);
        else if (v != LLONG_MIN)
            for (long long j = i - lo + 1; j <= n; j += j & -j) sets[j].insert(v);
        if (v == LLONG_MIN) nxt.erase(i);
        else nxt[i] = v;
    }

    // O(log^2 U) -- # of distinct values in a[l..r]
    long long countDistinct(long long l, long long r) const {
        if (l > r) return 0;
        long long nonzero = countPast(r, lo - 1) - countPast(l - 1, lo - 1);  // every nxt is > lo - 1
        return countPast(r, r) - countPast(l - 1, r) + (nonzero < r - l + 1);
    }

    // O(log^2 U) -- a[i] = v; rewires i's old predecessor, i's new predecessor, and i
    void pointAssign(long long i, T v) {
        T old = pointGet(i);
        if (old == v) return;
        if (old != T(0)) {
            auto oldIt = chains.find(old);
            set<long long>& from = oldIt->second;
            auto it = from.find(i);
            setNxt(i, LLONG_MIN);  // unlink i first, so its successor is free for its predecessor
            if (it != from.begin()) {
                auto nx = next(it);
                setNxt(*prev(it), nx == from.end() ? none : *nx);
            }
            from.erase(it);
            if (from.empty()) chains.erase(oldIt);
        }
        if (v != T(0)) {
            set<long long>& to = chains[v];
            auto jt = to.insert(i).first;
            auto nx = next(jt);
            if (jt != to.begin()) setNxt(*prev(jt), i);  // move the predecessor off the successor first, then hand it to i
            setNxt(i, nx == to.end() ? none : *nx);
            vals[i] = v;
        } else {
            vals.erase(i);
        }
    }
''' + CPP_POINTS + "};\n")
