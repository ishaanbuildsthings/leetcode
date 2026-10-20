// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeMax/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeMax
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeMax: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: v[1*log(U)]
//   tags: none
//   other: children[2*log(U)]
//   note: per update, one node per level of the touched path;  one shared node pool (node 0 = all zeros), call resetPool() between test cases

// Point updates + range max, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
// Sparse: only the nodes on updated paths exist, in one pool shared by every SparseMaxTree; node 0 is the shared
// all-zeros block, so a missing child needs no special case. Point updates walk down, then recompute the path.
// T: int, long long, ....
template <typename T>
struct SparseMaxTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { T v; int l, r; };
    static inline vector<Node> pool{Node{0, 0, 0}};  // node 0: the shared all-zeros block
    long long lo, hi;
    int root = 0;

    // O(1) -- an all-zero array over [lo, hi]; any long long range works
    SparseMaxTree(long long lo, long long hi) : lo(lo), hi(hi) {}

    // O(1) -- forget every node of every SparseMaxTree; call once per test case, then build new trees
    static void resetPool() { pool.resize(1); }

    // optional: reserve room for this many nodes up front (about log U per update)
    static void reservePool(size_t nodes) { pool.reserve(nodes); }

    static int make() {
        pool.push_back(Node{0, 0, 0});
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

    static T merge(T a, T b) { return max(a, b); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int path[130], depth;
        int x = descend(i, path, depth);
        pool[x].v = v;
        while (depth) {
            int y = path[--depth];
            pool[y].v = merge(pool[pool[y].l].v, pool[pool[y].r].v);
        }
    }

    T query(int x, long long a, long long b, long long l, long long r) const {
        if (r < a || b < l) return numeric_limits<T>::lowest();
        if (!x || (l <= a && b <= r)) return pool[x].v;  // node 0 holds 0, the value of a block of zeros
        long long m = a + (b - a) / 2;
        return merge(query(pool[x].l, a, m, l, r), query(pool[x].r, m + 1, b, l, r));
    }

    // O(logU) -- max of a[l..r]
    T rangeMax(long long l, long long r) const { return query(root, lo, hi, l, r); }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(pool[find(i)].v); }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
