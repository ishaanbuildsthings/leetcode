// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeXorApply-rangeXorQuery/sparse.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeXorApply rangeXorQuery
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAssign: log(U)
//   rangeXorApply: log(U)
//   rangeXorQuery: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: xr[4*log(U)]
//   tags: asg[4*log(U)] hasAsg[4*log(U)] tx[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Lazy segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; range updates (rangeAssign, rangeXorApply) and range queries in O(logU), U = hi - lo + 1;
// each node keeps its xor over its range. Ranges inclusive [l, r]; searches return lo - 1 when nothing qualifies. The
// root covers 2^D >= U positions from lo (the ones past hi are zeros nobody reads), so a node of level s covers 2^s
// positions; children are created on demand as blocks of zeros, right before anything descends past a node, and a
// node's pending tags ("applied here, not yet to my children") go down as it is passed.
// T: int, long long, ...
template <typename T>
struct SparseLazySegTree {
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        T xr = T(0);
        T asg = T(0);
        T tx = T(0);
        int L = 0;
        int R = 0;
        char hasAsg = 0;
    };
    vector<Node> nd{Node{}};  // node 0: none; node 1 is the root

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseLazySegTree(long long lo, long long hi) : first(lo), last(hi),
        D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        newZero(D);
    }

    // O(logU) -- a[i] += v; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAdd: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, T(leaf(x) + v)), up(path);
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, v), up(path);
    }

    // O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmax(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmax: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, max(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmin(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmin: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, min(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    T pointGet(long long i) {
        if (i < first || i > last) throw out_of_range("pointGet: needs lo <= i <= hi");
        int path[64];
        return leaf(leafOf(i, path));
    }

    // O(logU) -- a[i] = v for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeAssign(long long l, long long r, T v) {
        if (l < first || l > r || r > last) throw out_of_range("rangeAssign: needs lo <= l <= r <= hi");
        update(1, D, first, l, r, [&](int t, int s, long long) { applyAssign(t, s, v); });
    }

    // O(logU) -- a[i] ^= v for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeXorApply(long long l, long long r, T v) {
        if (l < first || l > r || r > last) throw out_of_range("rangeXorApply: needs lo <= l <= r <= hi");
        update(1, D, first, l, r, [&](int t, int s, long long) { applyXor(t, s, v); });
    }

    // O(logU) -- a[l] ^ ... ^ a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeXorQuery(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeXorQuery: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res ^= nd[ns[i]].xr;
        return res;
    }

    // ---- internals ----

    int newZero(int s) {  // a new node: a block of 2^s zeros
        Node n;
        n.L = 0, n.R = 0, n.xr = T(0), n.asg = T(0), n.hasAsg = 0, n.tx = T(0);
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    void kids(int x, int s) {  // create node x's children (blocks of zeros) if it has none yet
        if (nd[x].L) return;
        int a = newZero(s - 1), b = newZero(s - 1);
        nd[x].L = a, nd[x].R = b;
    }

    // the nodes covering a[l..r] left to right: ns, their levels ls, their first indices ts
    int cover(long long l, long long r, int* ns, int* ls, long long* ts) {
        int c = 0;
        collect(1, D, first, l, r, ns, ls, ts, c);
        return c;
    }

    int cover(long long l, long long r, int* ns, int* ls) {
        long long ts[128];
        return cover(l, r, ns, ls, ts);
    }

    void collect(int x, int s, long long tl, long long l, long long r, int* ns, int* ls, long long* ts, int& c) {
        if (l <= tl && tl + (1LL << s) - 1 <= r) {
            ns[c] = x, ls[c] = s, ts[c++] = tl;
            return;
        }
        kids(x, s);
        push(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) collect(nd[x].L, s - 1, tl, l, r, ns, ls, ts, c);
        if (r >= m) collect(nd[x].R, s - 1, m, l, r, ns, ls, ts, c);
    }

    template <class F>  // f(node, level, first index) on every node covering a[l..r], then pull up
    void update(int x, int s, long long tl, long long l, long long r, const F& f) {
        if (l <= tl && tl + (1LL << s) - 1 <= r) {
            f(x, s, tl);
            return;
        }
        kids(x, s);
        push(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) update(nd[x].L, s - 1, tl, l, r, f);
        if (r >= m) update(nd[x].R, s - 1, m, l, r, f);
        pull(x, s);
    }

    int leafOf(long long i, int* path) {  // the leaf holding a[i]; path: the nodes above it top-down, every tag pushed
        int x = 1;
        long long tl = first;
        for (int s = D; s > 0; s--) {
            kids(x, s);
            push(x, s);
            path[D - s] = x;
            if (i >= tl + (1LL << (s - 1))) tl += 1LL << (s - 1), x = nd[x].R;
            else x = nd[x].L;
        }
        return x;
    }

    void up(const int* path) {  // recompute the nodes of path, deepest first (path[k] has level D - k)
        for (int k = D - 1; k >= 0; k--) pull(path[k], D - k);
    }

    void setLeaf(int p, T v) {  // leaf p holds v alone
        nd[p].xr = v;
    }

    T leaf(int p) const { return T(nd[p].xr); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = nd[x].L, b = nd[x].R;
        nd[x].xr = nd[a].xr ^ nd[b].xr;
    }

    void setAssign(int x, int s, T v) {  // every value under node x becomes v
        long long k = 1LL << s;
        nd[x].xr = k & 1 ? v : T(0);
    }

    void applyAssign(int x, int s, T v) {
        setAssign(x, s, v);
        nd[x].asg = v, nd[x].hasAsg = 1, nd[x].tx = T(0);
    }

    void setXor(int x, int s, T v) {  // every value under node x is xored with v (an even count leaves the xor alone)
        if (s == 0) nd[x].xr ^= v;
    }

    void applyXor(int x, int s, T v) {
        setXor(x, s, v);
        if (nd[x].hasAsg) nd[x].asg ^= v;
        else nd[x].tx ^= v;
    }

    void push(int x, int s) {  // hand node x's pending tags to its children
        int a = nd[x].L, b = nd[x].R, c = s - 1;  // (their level)
        if (nd[x].hasAsg) applyAssign(a, c, nd[x].asg), applyAssign(b, c, nd[x].asg), nd[x].hasAsg = 0;
        if (nd[x].tx != T(0)) applyXor(a, c, nd[x].tx), applyXor(b, c, nd[x].tx), nd[x].tx = T(0);
    }
};
