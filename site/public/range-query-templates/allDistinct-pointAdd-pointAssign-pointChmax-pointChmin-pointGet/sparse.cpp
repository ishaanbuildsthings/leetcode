// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/allDistinct-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/sparse.cpp
// @operations: allDistinct pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: seg-tree
// @complexities:
//   allDistinct: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mn[3*log(U)] cnt[3*log(U)]
//   tags: none
//   other: children[6*log(U)] chains[1] vals[1]
//   note: per point write, at most 3 root paths (i, its old and new predecessor); each node keeps the min nxt and the number of nonzero positions below it; chains maps each nonzero value to its sorted positions (std::set). A node pool per tree (node 0 = untouched)

// "Are all values in a[l..r] distinct?" with point updates, over any index range [lo, hi] (huge or negative is fine);
// every position starts at 0. Two zeros repeat, so a range with >= 2 positions holding 0 is not distinct. Among the
// nonzero positions, nxt[i] = the next position with the same value (none: INF), and they are distinct iff
// min(nxt[l..r]) > r. Sparse: a dynamic tree keeps, per node, the min nxt and the number of nonzero positions (and a
// leaf keeps its position's value); nodes live in a pool the tree owns, node 0 is the untouched block. T: a std::map
// key type.
template <typename T>
struct SparseDistinctTree {
    static constexpr long long INF = numeric_limits<long long>::max();
    struct Node { long long mn, cnt; T v; int l, r; };  // v: a leaf's value
    vector<Node> pool{Node{INF, 0, T(0), 0, 0}};  // node 0: untouched (no nxt, no nonzero, 0), children itself
    long long lo, hi;
    int root = 0;
    map<T, set<long long>> chains;  // nonzero value -> sorted positions

    // O(1) -- all zeros over [lo, hi]
    SparseDistinctTree(long long lo, long long hi) : lo(lo), hi(hi) {}


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { pool.reserve(nodes); }

    int make() {
        pool.push_back(Node{INF, 0, T(0), 0, 0});
        return (int)pool.size() - 1;
    }

    // O(logU) -- position i now has nxt[i] = v and is nonzero (c = 1) or zero (c = 0, v = INF); returns its leaf
    int setLeaf(long long i, long long v, long long c) {
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
        int leaf = y;
        while (d--) {
            Node& p = pool[path[d]];
            p.mn = min(pool[p.l].mn, pool[p.r].mn);
            p.cnt = pool[p.l].cnt + pool[p.r].cnt;
        }
        return leaf;
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
            int leaf = setLeaf(i, nx == to.end() ? INF : *nx, 1);
            pool[leaf].v = v;
            if (jt != to.begin()) setLeaf(*prev(jt), i, 1);
        } else {
            int leaf = setLeaf(i, INF, 0);
            pool[leaf].v = T(0);
        }
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
