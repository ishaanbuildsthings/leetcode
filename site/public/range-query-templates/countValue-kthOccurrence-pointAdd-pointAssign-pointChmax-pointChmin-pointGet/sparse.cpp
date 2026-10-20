// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countValue-kthOccurrence-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/sparse.cpp
// @operations: countValue kthOccurrence pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: BIT
// @complexities:
//   countValue: log(U)
//   kthOccurrence: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: cnt[1*log(U)]
//   tags: none
//   other: children[2*log(U)] vals[1]
//   note: per point write, the O(logU) entries above it; position i stores [a[i] == number] - [0 == number], so the untouched store nothing; kthOccurrence descends / binary-lifts. A dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases

// Count / find the k-th occurrence of one value (fixed at build time) in a range, with point updates, over any index
// range [lo, hi] (huge or negative is fine); every position starts at 0. An index counts if a[i] == number; untouched
// positions count iff number == 0 (z below), so position i stores [a[i] == number] - z in a dynamic prefix-sum tree
// and a count over k positions is z * k plus the stored sum. kthOccurrence descends the tree. Nodes live in one pool
// shared by every SparseCountValueBIT<T>. T: any type with ==.
template <typename T>
struct SparseCountValueBIT {
    struct Node { long long f; T v; int l, r; };  // f: total of the stored changes under the node; v: a leaf's value
    static inline vector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root = 0;

    // O(1) -- forget every node of every SparseCountValueBIT<T>; call between test cases, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{});
        return (int)pool.size() - 1;
    }

    // O(logU) -- the change v at position i, added into every node on its root path
    void add(long long i, long long v) {
        if (!root) root = make();
        int y = root;
        long long a = lo, b = hi;
        while (true) {
            pool[y].f += v;
            if (a == b) return;
            long long m = a + (b - a) / 2;
            bool right = i > m;
            int c = right ? pool[y].r : pool[y].l;
            if (!c) {
                c = make();
                (right ? pool[y].r : pool[y].l) = c;
            }
            y = c;
            if (right) a = m + 1;
            else b = m;
        }
    }

    // O(logU) -- the leaf of position i, created with its root path if missing
    int leafOf(long long i) {
        if (!root) root = make();
        int y = root;
        long long a = lo, b = hi;
        while (a < b) {
            long long m = a + (b - a) / 2;
            bool right = i > m;
            int c = right ? pool[y].r : pool[y].l;
            if (!c) {
                c = make();
                (right ? pool[y].r : pool[y].l) = c;
            }
            y = c;
            if (right) a = m + 1;
            else b = m;
        }
        return y;
    }

    // O(logU) -- a[i]: its leaf's value (0 if never written)
    T valueAt(long long i) const {
        int y = root;
        long long a = lo, b = hi;
        while (y && a < b) {
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else y = pool[y].r, a = m + 1;
        }
        return pool[y].v;
    }

    // O(logU) -- total of the changes at positions lo..i (0 for i < lo)
    long long prefix(long long i) const {
        long long s = 0;
        int y = i < lo ? 0 : root;
        long long a = lo, b = hi;
        while (y) {
            if (b <= i) { s += pool[y].f; break; }
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else s += pool[pool[y].l].f, y = pool[y].r, a = m + 1;
        }
        return s;
    }

    T number;
    long long z;

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
        long long diff = (long long)(v == number) - (long long)(valueAt(i) == number);
        if (diff) add(i, diff);
        pool[leafOf(i)].v = v;
    }

    // a[i]
    T pointGet(long long i) const { return valueAt(i); }

    // a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
