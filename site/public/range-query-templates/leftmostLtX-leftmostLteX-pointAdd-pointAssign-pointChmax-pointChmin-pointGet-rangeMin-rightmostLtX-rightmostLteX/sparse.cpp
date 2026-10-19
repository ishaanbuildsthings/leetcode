// @operations: leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeMin rightmostLtX rightmostLteX
// @data-structure-type: seg-tree
// @complexities:
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeMin: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mn[1*log(U)]
//   tags: none
//   other: links[2*log(U)]
//   note: per update, one node per level of the touched path;  C++: one shared node pool (node 0 = all zeros), call resetPool() between test cases; Python: a dict keyed by heap index, a missing key is a block of zeros

// Range min and leftmost / rightmost index with a[i] <= / < x, with point updates, over
// any index range [lo, hi] (huge or negative is fine); every position starts at 0. Searches return lo - 1 when nothing
// qualifies (-1 when lo = 0). Sparse: only the nodes on updated paths exist, in one pool shared by every SparseMinSearchTree; node 0 is the
// shared all-zeros block. A search prunes any node whose min can't pass, so it visits O(log U) nodes.
// T: int, long long, ...
template <typename T>
struct SparseMinSearchTree {
    struct Agg { T mn; };
    struct Node { Agg v; int l, r; };
    static inline vector<Node> pool{Node{Agg{}, 0, 0}};  // node 0: the shared all-zeros block
    long long lo, hi;
    int root = 0;

    // O(1) -- an all-zero array over [lo, hi]; any long long range works
    SparseMinSearchTree(long long lo, long long hi) : lo(lo), hi(hi) {}

    // O(1) -- forget every node of every SparseMinSearchTree; call once per test case, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional: reserve room for this many nodes up front (about log U per update)
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{Agg{}, 0, 0});
        return (int)pool.size() - 1;
    }

    // walk from the root to leaf i, creating missing nodes; fills path[] with the nodes above the leaf and
    // returns the leaf. len[] / starts[] (when given) receive each path node's range.
    int descend(long long i, int* path, int& depth, long long* starts = nullptr, long long* ends = nullptr) {
        if (!root) root = make();
        int x = root;
        long long a = lo, b = hi;
        depth = 0;
        while (a < b) {
            if (starts) starts[depth] = a, ends[depth] = b;
            path[depth++] = x;
            long long m = a + (b - a) / 2;
            if (i <= m) {
                if (!pool[x].l) { int y = make(); pool[x].l = y; }
                x = pool[x].l, b = m;
            } else {
                if (!pool[x].r) { int y = make(); pool[x].r = y; }
                x = pool[x].r, a = m + 1;
            }
        }
        return x;
    }

    // O(logU) -- the leaf for i, or 0 if no update has touched it
    int find(long long i) const {
        int x = root;
        long long a = lo, b = hi;
        while (x && a < b) {
            long long m = a + (b - a) / 2;
            if (i <= m) x = pool[x].l, b = m;
            else x = pool[x].r, a = m + 1;
        }
        return x;
    }

    static Agg merge(const Agg& a, const Agg& b) { return Agg{min(a.mn, b.mn)}; }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int path[130], depth;
        int x = descend(i, path, depth);
        pool[x].v = Agg{v};
        while (depth) {
            int y = path[--depth];
            pool[y].v = merge(pool[pool[y].l].v, pool[pool[y].r].v);
        }
    }

    T foldmn(int x, long long a, long long b, long long l, long long r) const {
        if (r < a || b < l) return numeric_limits<T>::max();
        if (!x || (l <= a && b <= r)) return pool[x].v.mn;  // node 0 holds 0, the value of a block of zeros
        long long m = a + (b - a) / 2;
        return min(foldmn(pool[x].l, a, m, l, r), foldmn(pool[x].r, m + 1, b, l, r));
    }

    // O(logU) -- min of a[l..r]
    T rangeMin(long long l, long long r) const { return foldmn(root, lo, hi, l, r); }

    long long leftLte(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mn <= v)) return lo - 1;
        if (!x) return max(a, l);  // a block of zeros, and 0 passes
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = leftLte(pool[x].l, a, m, l, r, v);
        return res != lo - 1 ? res : leftLte(pool[x].r, m + 1, b, l, r, v);
    }

    long long rightLte(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mn <= v)) return lo - 1;
        if (!x) return min(b, r);
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = rightLte(pool[x].r, m + 1, b, l, r, v);
        return res != lo - 1 ? res : rightLte(pool[x].l, a, m, l, r, v);
    }

    // O(logU) -- first i in [l, r] with a[i] <= x, or lo - 1
    long long leftmostLteX(long long l, long long r, T x) const { return leftLte(root, lo, hi, l, r, x); }

    // O(logU) -- last i in [l, r] with a[i] <= x, or lo - 1
    long long rightmostLteX(long long l, long long r, T x) const { return rightLte(root, lo, hi, l, r, x); }

    long long leftLt(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mn < v)) return lo - 1;
        if (!x) return max(a, l);  // a block of zeros, and 0 passes
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = leftLt(pool[x].l, a, m, l, r, v);
        return res != lo - 1 ? res : leftLt(pool[x].r, m + 1, b, l, r, v);
    }

    long long rightLt(int x, long long a, long long b, long long l, long long r, T v) const {
        if (r < a || b < l || !(pool[x].v.mn < v)) return lo - 1;
        if (!x) return min(b, r);
        if (a == b) return a;
        long long m = a + (b - a) / 2, res = rightLt(pool[x].r, m + 1, b, l, r, v);
        return res != lo - 1 ? res : rightLt(pool[x].l, a, m, l, r, v);
    }

    // O(logU) -- first i in [l, r] with a[i] < x, or lo - 1
    long long leftmostLtX(long long l, long long r, T x) const { return leftLt(root, lo, hi, l, r, x); }

    // O(logU) -- last i in [l, r] with a[i] < x, or lo - 1
    long long rightmostLtX(long long l, long long r, T x) const { return rightLt(root, lo, hi, l, r, x); }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return pool[find(i)].v.mn; }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
