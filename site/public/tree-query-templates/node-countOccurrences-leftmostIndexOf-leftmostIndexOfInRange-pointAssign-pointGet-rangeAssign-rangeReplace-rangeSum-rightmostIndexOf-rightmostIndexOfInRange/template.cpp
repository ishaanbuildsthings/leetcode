// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/node-countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeAssign-rangeReplace-rangeSum-rightmostIndexOf-rightmostIndexOfInRange/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeAssign-rangeReplace-rangeSum-rightmostIndexOf-rightmostIndexOfInRange/fast.cpp
// @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAssign nodeGet nodeNearestAncestorEqX nodePathAssign nodePathCountOccurrences nodePathFirstEqX nodePathLastEqX nodePathSum nodeSubtreeAssign nodeSubtreeCountOccurrences nodeSubtreeSum parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: lazy-seg-tree
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   isAncestor: 1
//   isOnPath: log(N)
//   kthAncestor: log(N)
//   kthNodeOnPath: log(N)
//   lca: log(N)
//   lcaRootedAt: log(N)
//   median: log(N)
//   nextNodeOnPath: log(N)
//   nodeAssign: U*log(N)
//   nodeGet: log(N)
//   nodeNearestAncestorEqX: U*log^2(N)
//   nodePathAssign: U*log^2(N)
//   nodePathCountOccurrences: U*log^2(N)
//   nodePathFirstEqX: U*log^2(N)
//   nodePathLastEqX: U*log^2(N)
//   nodePathSum: U*log^2(N)
//   nodeSubtreeAssign: U*log(N)
//   nodeSubtreeCountOccurrences: U*log(N)
//   nodeSubtreeSum: U*log(N)
//   parent: 1
//   parentRootedAt: log(N)
//   pathIntersection: log(N)
//   pathNodes: K+log(N)
//   subtreeSize: 1
//   subtreeSizeRootedAt: log(N)
//   unweightedDist: log(N)
//   unweightedDistBetweenPaths: log(N)
//   unweightedDistToPath: log(N)
//   build: N*U
// @memory:
//   layout: pow2-iterative
//   node: t[4*N] cnt[2*N*U] sm[4*N]
//   tags: mp[2*N*U]
//   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: U = valHi - valLo + 1 (every value ever in the array is in [valLo, valHi]); each tag is a whole map old value -> new value, so a push costs O(U); a map is kept only while pending (handed down, its memory is reused), so mp is far below 2*N*U in practice
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// Lazy seg tree whose tag is a value map (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r]
// into y, and rangeAssign(l, r, v) sets a[l..r] = v, in O(U log N), U = valHi - valLo + 1: good when the values are
// few (911G: 1..100). A pending tag is a map old value -> new value for the whole segment, so any mix of changes
// composes into one map. Each node also keeps how many times each value appears below it and its sum, for
// countOccurrences / where x first / last appears / rangeSum. All indices 0-based, ranges inclusive [l, r]; searches
// return -1 when nothing qualifies.
// T: int, long long, char, ...: the values; valLo / valHi bound every value the array will ever hold

#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct ValueMapSeg {
    using S = long long;  // sums
    // leaves t[cap + i] hold a[i] - valLo (-1: padding past n); node k's pending map for its children is
    // rows[row[k] * U ..] (row[k] = -1: none). A map row exists only while pending: pushed down, it is reused
    // cnt[k * U + v]: how many leaves below internal node k hold v (its own map already applied)
    int n, cap, lg, U;
    T valLo;
    HotVector<int> t, row, rows, freeRows, gbuf, tmp;
    HotVector<int> cnt;
    HotVector<S> sm;

    // O(N*U) -- arr: the initial array; every value it will ever hold must be in [valLo, valHi]
    ValueMapSeg(const vector<T>& arr, T valLo, T valHi) : n((int)arr.size()), cap(1), lg(0),
        U(int(valHi - valLo) + 1), valLo(valLo) {
        while (cap < n) cap <<= 1, lg++;
        t.assign(2 * cap, -1), row.assign(cap, -1), tmp.assign(U, 0);
        cnt.assign((size_t)cap * U, 0);
        sm.assign(2 * cap, 0);
        for (int i = 0; i < n; i++) {
            t[cap + i] = off(arr[i]);
            sm[cap + i] = S(arr[i]);
        }
        for (int k = cap - 1; k >= 1; k--) pull(k);
    }

    // O(1) -- the length of the array
    LEETCODE_NO_SANITIZE int size() const { return n; }

    // O(logN) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        int k = cap + i, v = t[k];
        for (k >>= 1; k; k >>= 1)  // (a map higher up is newer: apply them bottom-up)
            if (row[k] >= 0) v = rows[(size_t)row[k] * U + v];
        return T(v + valLo);
    }

    // O(U*logN) -- a[i] = v; needs valLo <= v <= valHi; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, const T& v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        int o = off(v), k = cap + i;
        for (int h = lg; h >= 1; h--) push(k >> h);
        t[k] = o;
        sm[k] = S(v);
        for (k >>= 1; k; k >>= 1) pull(k);
    }

    // O(U*logN) -- every a[i] == x with l <= i <= r becomes y; needs valLo <= y <= valHi; needs 0 <= l <= r < size(),
    // else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeReplace(int l, int r, const T& x, const T& y) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReplace: needs 0 <= l <= r < size()");
        int b = off(y);
        long long a = (long long)x - (long long)valLo;
        if (a < 0 || a >= U || a == b) return;
        update(l, r, [&](int k) { applyRep(k, (int)a, b); });
    }

    // O(U*logN) -- a[l..r] = v; needs valLo <= v <= valHi; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, const T& v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        vector<int> g(U, off(v));
        update(l, r, [&](int k) { applyMap(k, g.data()); });
    }

    // O(N log N) -- the whole current array
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = pointGet(i);
        return out;
    }

    // O(U*logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countOccurrences(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countOccurrences: needs 0 <= l <= r < size()");
        long long a = (long long)x - (long long)valLo;
        if (a < 0 || a >= U) return 0;
        int res = 0;
        cover(l, r, [&](int k) { res += countOf(k, (int)a); });
        return res;
    }

    // O(U*logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int leftmostIndexOf(const T& x) { return find(x, 0, n - 1, true); }

    // O(U*logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int rightmostIndexOf(const T& x) { return find(x, 0, n - 1, false); }

    // O(U*logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostIndexOfInRange(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        return find(x, l, r, true);
    }

    // O(U*logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostIndexOfInRange(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        return find(x, l, r, false);
    }

    // O(U*logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeSum: needs 0 <= l <= r < size()");
        S res = 0;
        cover(l, r, [&](int k) { res += sm[k]; });
        return res;
    }

    // O(U*log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (size() < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, size() - 1);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE int off(const T& v) const {  // v's index into a map
        long long o = (long long)v - (long long)valLo;
        if (o < 0 || o >= U) throw invalid_argument("value outside [valLo, valHi]");
        return (int)o;
    }

    LEETCODE_NO_SANITIZE void applyMap(int k, const int* g) {
        // node k's segment goes through map g (newer than anything below k)
        if (k >= cap) {
            if (t[k] >= 0) {
                t[k] = g[t[k]];
                sm[k] = S(t[k] + valLo);
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
        int* c = &cnt[(size_t)k * U];
        fill(tmp.begin(), tmp.end(), 0);
        for (int v = 0; v < U; v++) if (c[v]) tmp[g[v]] += c[v];
        copy(tmp.begin(), tmp.end(), c);
        sm[k] = 0;
        for (int v = 0; v < U; v++) if (c[v]) sm[k] += S(c[v]) * S(v + valLo);
    }

    LEETCODE_NO_SANITIZE void applyRep(int k, int a, int b) {  // every a in node k's segment becomes b
        if (k >= cap) {
            if (t[k] == a) {
                t[k] = b;
                sm[k] = S(b + valLo);
            }
            return;
        }
        if (row[k] < 0) {
            row[k] = newRow();
            iota(&rows[(size_t)row[k] * U], &rows[(size_t)row[k] * U] + U, 0);
        }
        int* m = &rows[(size_t)row[k] * U];
        for (int v = 0; v < U; v++) if (m[v] == a) m[v] = b;
        int* c = &cnt[(size_t)k * U];
        sm[k] += S(b - a) * S(c[a]);
        c[b] += c[a], c[a] = 0;
    }

    LEETCODE_NO_SANITIZE void push(int k) {  // hand node k's pending map to its children (its row is free again)
        if (row[k] < 0) return;
        gbuf.assign(rows.begin() + (size_t)row[k] * U, rows.begin() + (size_t)(row[k] + 1) * U);
        freeRows.push_back(row[k]), row[k] = -1;
        applyMap(2 * k, gbuf.data()), applyMap(2 * k + 1, gbuf.data());
    }

    LEETCODE_NO_SANITIZE int newRow() {  // a map row (a freed one if there is one)
        if (!freeRows.empty()) {
            int r = freeRows.back();
            freeRows.pop_back();
            return r;
        }
        rows.resize(rows.size() + U);
        return int(rows.size() / U) - 1;
    }

    LEETCODE_NO_SANITIZE void pull(int k) {  // recompute internal node k from its children (k has no pending map)
        int* c = &cnt[(size_t)k * U];
        if (2 * k >= cap) {
            fill(c, c + U, 0);
            for (int j = 2 * k; j <= 2 * k + 1; j++) if (t[j] >= 0) c[t[j]]++;
        } else {
            const int* p = &cnt[(size_t)(2 * k) * U];
            const int* q = &cnt[(size_t)(2 * k + 1) * U];
            for (int v = 0; v < U; v++) c[v] = p[v] + q[v];
        }
        sm[k] = sm[2 * k] + sm[2 * k + 1];
    }

    LEETCODE_NO_SANITIZE void pushAbove(int l, int r) {
        // push every map above the leaves l..r - 1 (offset by cap) down to them
        for (int h = lg; h >= 1; h--) {
            if (((l >> h) << h) != l) push(l >> h);
            if (((r >> h) << h) != r) push((r - 1) >> h);
        }
    }

    template <class F>
    LEETCODE_NO_SANITIZE void update(int l, int r, F apply) {
        l += cap, r += cap + 1;
        pushAbove(l, r);
        for (int a = l, b = r; a < b; a >>= 1, b >>= 1) {
            if (a & 1) apply(a++);
            if (b & 1) apply(--b);
        }
        for (int h = 1; h <= lg; h++) {
            if (((l >> h) << h) != l) pull(l >> h);
            if (((r >> h) << h) != r) pull((r - 1) >> h);
        }
    }

    template <class F>
    LEETCODE_NO_SANITIZE void cover(int l, int r, F visit) {
        // visit the nodes that exactly cover a[l..r], every map above them pushed
        l += cap, r += cap + 1;
        pushAbove(l, r);
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) visit(l++);
            if (r & 1) visit(--r);
        }
    }

    LEETCODE_NO_SANITIZE int countOf(int k, int a) const { return k >= cap ? int(t[k] == a) : cnt[(size_t)k * U + a]; }

    LEETCODE_NO_SANITIZE int find(const T& x, int l, int r, bool left) {
        // the first (left) / last i in [l, r] with a[i] == x, or -1
        long long a = (long long)x - (long long)valLo;
        return a < 0 || a >= U ? -1 : walk(1, 0, cap - 1, l, r, (int)a, left);
    }

    LEETCODE_NO_SANITIZE int walk(int k, int nl, int nr, int l, int r, int a, bool left) {
        if (r < nl || nr < l || !countOf(k, a)) return -1;
        if (k >= cap) return nl;
        push(k);
        int m = (nl + nr) >> 1;
        int res = left ? walk(2 * k, nl, m, l, r, a, left) : walk(2 * k + 1, m + 1, nr, l, r, a, left);
        if (res != -1) return res;
        return left ? walk(2 * k + 1, m + 1, nr, l, r, a, left) : walk(2 * k, nl, m, l, r, a, left);
    }
};

// Tree tree(edges, root, vals, valLo, valHi);
//
// edges: the tree's n - 1 edges, vector<vector<int>> (vector<vector<long long>> works too). Whether nodes are 0..n-1
//        or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with
//        no edges, from root)
//   {{a, b}, ...}        e.g. {{0, 1}, {1, 2}}
//   {{a, b, w}, ...}     also accepted: the weights are ignored here
// root: the root node (required), e.g. 0 or 1.
// vals: the node values, vector<T> (T = long long, or int), vals[node] is node's value
//   nodes 0..n-1: size n        e.g. n = 3: {10, 20, 30}         node 0 -> 10
//   nodes 1..n:   size n + 1    e.g. n = 3: {0, 10, 20, 30}      vals[0] is ignored, node 1 -> 10
// valLo: every value ever held is >= valLo (any integer, negative is fine).
// valHi: every value ever held is <= valHi.
//
//   Tree<long long> tree({{0, 1}, {1, 2}}, 0, {10, 20, 30}, valLo, valHi);       // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2}, {2, 3}}, 1, {0, 10, 20, 30}, valLo, valHi);    // nodes 1..3, rooted at 1
//
// Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree throws
// out_of_range. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). The values sit in the range structure above
// (ValueMapSeg) in position order: a subtree is one range of it, and a path a..b is O(log n) ranges, one per chain it
// crosses.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    ValueMapSeg<T> seg;  // the values, in position order

    // O(n * U) -- builds the layout and the range structure; throws invalid_argument when the edges are not one tree on
    // nodes 0..n-1 or 1..n, or vals has the wrong size
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, const vector<T>& vals,
                                    T valLo, T valHi)
        : seg(layout(edges, root, vals), valLo, valHi) {}

    // lays the tree out (fills the arrays above) and returns the values in position order
    template <typename E> vector<T> layout(const vector<vector<E>>& edges, int root, const vector<T>& vals) {
        this->root = root;
        n = (int)edges.size() + 1;
        long long least = root;
        if (!edges.empty()) {
            least = LLONG_MAX;
            for (const auto& e : edges) {
                if (e.size() != 2 && e.size() != 3)
                    throw invalid_argument("Tree: every edge needs 2 or 3 numbers, {a, b} or {a, b, w}");
                least = min({least, (long long)e[0], (long long)e[1]});
            }
        }
        if (least != 0 && least != 1)
            throw invalid_argument("Tree: nodes must be labeled 0..n-1 or 1..n, but the smallest label is " +
                                   to_string(least));
        lo = (int)least, hi = lo + n - 1;
        string nodes = to_string(lo) + ".." + to_string(hi);
        if (root < lo || root > hi)
            throw invalid_argument("Tree: root must be one of the nodes " + nodes + ", got " + to_string(root));
        int size = hi + 1;

        // the neighbors of v are adj[start[v] .. start[v + 1])
        vector<int> start(size + 1, 0), adj(2 * (n - 1));
        for (const auto& e : edges) {
            if ((long long)e[0] > hi || (long long)e[1] > hi)
                throw invalid_argument("Tree: " + to_string(n - 1) + " edges means the nodes are " + nodes +
                                       ", got the edge (" + to_string(e[0]) + ", " + to_string(e[1]) + ")");
            start[e[0] + 1]++, start[e[1] + 1]++;
        }
        for (int v = 0; v < size; v++) start[v + 1] += start[v];
        vector<int> at(start.begin(), start.end() - 1);
        for (const auto& e : edges) {
            int a = (int)e[0], b = (int)e[1];
            adj[at[a]++] = b, adj[at[b]++] = a;
        }

        // parents and depths, top down (par is -2 until a node is reached)
        par.assign(size, -2), dep.assign(size, 0);
        vector<int> bfs(n);
        int reached = 0;
        par[root] = -1, bfs[reached++] = root;
        for (int i = 0; i < reached; i++) {
            int v = bfs[i];
            for (int k = start[v]; k < start[v + 1]; k++) {
                int u = adj[k];
                if (par[u] == -2) par[u] = v, dep[u] = dep[v] + 1, bfs[reached++] = u;
            }
        }
        if (reached != n)
            throw invalid_argument("Tree: the edges do not form one tree (some node cannot be reached from root)");

        // subtree sizes bottom up, then each node's heavy child (the one with the biggest subtree)
        sz.assign(size, 1);
        for (int i = n - 1; i > 0; i--) sz[par[bfs[i]]] += sz[bfs[i]];
        vector<int> heavy(size, -1);
        for (int i = 1; i < n; i++) {
            int v = bfs[i], p = par[v];
            if (heavy[p] == -1 || sz[v] > sz[heavy[p]]) heavy[p] = v;
        }

        // positions: a preorder that always steps into the heavy child first, so a heavy chain is one stretch
        head.assign(size, 0), pos.assign(size, 0), order.assign(n, 0);
        vector<int> todo = {root};
        todo.reserve(n);
        head[root] = root;
        int t = 0;
        while (!todo.empty()) {
            int v = todo.back();
            todo.pop_back();
            pos[v] = t, order[t++] = v;
            int h = heavy[v], p = par[v];
            for (int k = start[v]; k < start[v + 1]; k++) {
                int u = adj[k];
                if (u != p && u != h) head[u] = u, todo.push_back(u);
            }
            if (h != -1) head[h] = head[v], todo.push_back(h);  // pushed last, so it is popped next
        }

        int maxDep = dep[bfs[n - 1]];
        depthStart.assign(maxDep + 2, 0), depthPos.assign(n, 0);
        for (int i = 0; i < n; i++) depthStart[dep[bfs[i]] + 1]++;
        for (int d = 0; d <= maxDep; d++) depthStart[d + 1] += depthStart[d];
        vector<int> slot(depthStart.begin(), depthStart.end() - 1);
        for (int i = 0; i < n; i++) depthPos[slot[dep[order[i]]]++] = i;
        if ((int)vals.size() != hi + 1)
            throw invalid_argument("Tree: vals[node] is node's value, so nodes " + nodes + " need vals.size() = " +
                                   to_string(hi + 1) + ", got " + to_string(vals.size()));
        vector<T> inOrder(n);
        for (int i = 0; i < n; i++) inOrder[i] = vals[order[i]];
        return inOrder;
    }

    // O(log n) -- val(node)
    LEETCODE_NO_SANITIZE auto nodeGet(int node) {
        if (node < lo || node > hi) bad("nodeGet");
        return seg.pointGet(pos[node]);
    }

    // O(U * log n) -- val(node) = x
    LEETCODE_NO_SANITIZE void nodeAssign(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeAssign");
        seg.pointAssign(pos[node], x);
    }

    // O(U * log^2 n) -- val = x for every node on the path a..b
    LEETCODE_NO_SANITIZE void nodePathAssign(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathAssign");
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            seg.rangeAssign(pos[head[a]], pos[a], x);
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l <= r) seg.rangeAssign(l, r, x);
        else seg.rangeAssign(r, l, x);
    }

    // O(U * log^2 n) -- sum of the node values on the path a..b
    LEETCODE_NO_SANITIZE auto nodePathSum(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathSum");
        using R = decltype(seg.rangeSum(0, 0));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.rangeSum(pos[head[a]], pos[a]);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.rangeSum(l, r);
        res += v;
        return res;
    }

    // O(U * log^2 n) -- how many node values on the path a..b equal x
    LEETCODE_NO_SANITIZE auto nodePathCountOccurrences(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountOccurrences");
        using R = decltype(seg.countOccurrences(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = seg.countOccurrences(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = seg.countOccurrences(l, r, x);
        res += v;
        return res;
    }

    // O(U * log^2 n) -- nearest ancestor of node (node included) with val = x (-1 if none)
    LEETCODE_NO_SANITIZE int nodeNearestAncestorEqX(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeNearestAncestorEqX");
        while (node != -1) {
            int i = seg.rightmostIndexOfInRange(pos[head[node]], pos[node], x);
            if (i != -1) return order[i];
            node = par[head[node]];
        }
        return -1;
    }

    LEETCODE_NO_SANITIZE int firstEqX(int a, int b, const T& x) {
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
                int i = seg.rightmostIndexOfInRange(l, r, x);
                if (i != -1) return order[i];
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] >= pos[b]) {  // the piece holding the lca: b is the top
            int l = pos[b], r = pos[a];
            int i = seg.rightmostIndexOfInRange(l, r, x);
            if (i != -1) return order[i];
        } else {
            int l = pos[a], r = pos[b];
            int i = seg.leftmostIndexOfInRange(l, r, x);
            if (i != -1) return order[i];
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
            int i = seg.leftmostIndexOfInRange(l, r, x);
            if (i != -1) return order[i];
        }
        return -1;
    }

    // O(U * log^2 n) -- first node walking a -> b with val = x (-1 if none)
    LEETCODE_NO_SANITIZE int nodePathFirstEqX(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathFirstEqX");
        return firstEqX(a, b, x);
    }

    // O(U * log^2 n) -- last node walking a -> b with val = x (-1 if none)
    LEETCODE_NO_SANITIZE int nodePathLastEqX(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLastEqX");
        return firstEqX(b, a, x);
    }

    // O(U * log n) -- val = x for every node in node's subtree
    LEETCODE_NO_SANITIZE void nodeSubtreeAssign(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeSubtreeAssign");
        int l = pos[node];
        seg.rangeAssign(l, l + sz[node] - 1, x);
    }

    // O(U * log n) -- sum of the node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeSum(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeSum");
        int l = pos[node];
        return seg.rangeSum(l, l + sz[node] - 1);
    }

    // O(U * log n) -- how many node values in node's subtree equal x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountOccurrences(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountOccurrences");
        int l = pos[node];
        return seg.countOccurrences(l, l + sz[node] - 1, x);
    }

    [[noreturn]] void bad(const char* name) const {
        throw out_of_range(string(name) + ": needs " + to_string(lo) + " <= node <= " + to_string(hi));
    }

    LEETCODE_NO_SANITIZE int lcaOf(int a, int b) const {
        while (head[a] != head[b]) {
            if (dep[head[a]] > dep[head[b]]) a = par[head[a]];
            else b = par[head[b]];
        }
        return dep[a] < dep[b] ? a : b;
    }

    // the node k steps above node (k <= its depth): a whole chain at a time
    LEETCODE_NO_SANITIZE int kthOf(int node, int k) const {
        while (true) {
            int h = head[node], d = pos[node] - pos[h];
            if (k <= d) return order[pos[node] - k];
            k -= d + 1;
            node = par[h];
        }
    }

    LEETCODE_NO_SANITIZE int distOf(int a, int b) const { return dep[a] + dep[b] - 2 * dep[lcaOf(a, b)]; }

    // of the three pairwise lcas two are equal and the third, the deeper one, is the median
    LEETCODE_NO_SANITIZE int medianOf(int a, int b, int c) const {
        int x = lcaOf(a, b), y = lcaOf(a, c), z = lcaOf(b, c);
        if (dep[y] > dep[x]) x = y;
        return dep[z] > dep[x] ? z : x;
    }

    LEETCODE_NO_SANITIZE bool above(int a, int b) const { return pos[a] <= pos[b] && pos[b] < pos[a] + sz[a]; }

    LEETCODE_NO_SANITIZE bool onPath(int a, int b, int node) const {
        return above(lcaOf(a, b), node) && (above(node, a) || above(node, b));
    }

    // the neighbor of a on the way to b (a != b): the child holding b when b is below a, else a's parent
    LEETCODE_NO_SANITIZE int nextOf(int a, int b) const {
        return above(a, b) ? kthOf(b, dep[b] - dep[a] - 1) : par[a];
    }

    LEETCODE_NO_SANITIZE int lowerPos(int s, int e, int x) const {  // first index in [s, e) with depthPos >= x
        while (s < e) {
            int m = (s + e) >> 1;
            if (depthPos[m] < x) s = m + 1;
            else e = m;
        }
        return s;
    }

    // O(log n) -- lowest common ancestor of a and b
    LEETCODE_NO_SANITIZE int lca(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("lca");
        return lcaOf(a, b);
    }

    // O(log n) -- number of edges on the path a..b
    LEETCODE_NO_SANITIZE int unweightedDist(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("unweightedDist");
        return distOf(a, b);
    }

    // O(1) -- edges from the root to node (the root is depth 0)
    LEETCODE_NO_SANITIZE int depth(int node) const {
        if (node < lo || node > hi) bad("depth");
        return dep[node];
    }

    // O(1) -- node's parent (-1 for the root)
    LEETCODE_NO_SANITIZE int parent(int node) const {
        if (node < lo || node > hi) bad("parent");
        return par[node];
    }

    // O(log n) -- the node k steps above node (k = 0 is node itself; -1 if that is past the root); needs k >= 0
    LEETCODE_NO_SANITIZE int kthAncestor(int node, int k) const {
        if (node < lo || node > hi) bad("kthAncestor");
        if (k < 0) throw out_of_range("kthAncestor: needs k >= 0");
        return k <= dep[node] ? kthOf(node, k) : -1;
    }

    // O(1) -- is a an ancestor of b? (true when a == b)
    LEETCODE_NO_SANITIZE bool isAncestor(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("isAncestor");
        return above(a, b);
    }

    // O(1) -- number of nodes in node's subtree (node included)
    LEETCODE_NO_SANITIZE int subtreeSize(int node) const {
        if (node < lo || node > hi) bad("subtreeSize");
        return sz[node];
    }

    // O(log n) -- number of nodes in node's subtree at depth d (the root is depth 0); 0 when there are none
    LEETCODE_NO_SANITIZE int countAtDepthInSubtree(int node, int d) const {
        if (node < lo || node > hi) bad("countAtDepthInSubtree");
        if (d < 0 || d + 1 >= (int)depthStart.size()) return 0;
        int s = depthStart[d], e = depthStart[d + 1], l = pos[node];
        return lowerPos(s, e, l + sz[node]) - lowerPos(s, e, l);
    }

    // O(log n) -- lca of a and b if the tree were rooted at r instead
    LEETCODE_NO_SANITIZE int lcaRootedAt(int r, int a, int b) const {
        if (r < lo || r > hi || a < lo || a > hi || b < lo || b > hi) bad("lcaRootedAt");
        return medianOf(a, b, r);
    }

    // O(log n) -- node's parent if the tree were rooted at r (-1 when node == r)
    LEETCODE_NO_SANITIZE int parentRootedAt(int r, int node) const {
        if (r < lo || r > hi || node < lo || node > hi) bad("parentRootedAt");
        return node == r ? -1 : nextOf(node, r);
    }

    // O(log n) -- size of node's subtree if the tree were rooted at r
    LEETCODE_NO_SANITIZE int subtreeSizeRootedAt(int r, int node) const {
        if (r < lo || r > hi || node < lo || node > hi) bad("subtreeSizeRootedAt");
        if (node == r) return n;
        // r hangs below node: everything but the child holding r
        if (above(node, r)) return n - sz[kthOf(r, dep[r] - dep[node] - 1)];
        return sz[node];
    }

    // O(log n) -- the kth node walking a -> b (k = 0 is a, k = unweightedDist(a, b) is b; -1 if k is past b); needs
    // k >= 0
    LEETCODE_NO_SANITIZE int kthNodeOnPath(int a, int b, int k) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("kthNodeOnPath");
        if (k < 0) throw out_of_range("kthNodeOnPath: needs k >= 0");
        int c = lcaOf(a, b), up = dep[a] - dep[c], total = up + dep[b] - dep[c];
        if (k > total) return -1;
        return k <= up ? kthOf(a, k) : kthOf(b, total - k);
    }

    // O(log n) -- the neighbor of a one step toward b (-1 if a == b)
    LEETCODE_NO_SANITIZE int nextNodeOnPath(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("nextNodeOnPath");
        return a == b ? -1 : nextOf(a, b);
    }

    // O(log n) -- does the path a..b pass through node? (a and b count)
    LEETCODE_NO_SANITIZE bool isOnPath(int a, int b, int node) const {
        if (a < lo || a > hi || b < lo || b > hi || node < lo || node > hi) bad("isOnPath");
        return onPath(a, b, node);
    }

    // O(log n) -- fewest edges from node to any node on the path a..b (0 if node is on it)
    LEETCODE_NO_SANITIZE int unweightedDistToPath(int a, int b, int node) const {
        if (a < lo || a > hi || b < lo || b > hi || node < lo || node > hi) bad("unweightedDistToPath");
        return distOf(node, medianOf(a, b, node));
    }

    // O(log n) -- fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)
    LEETCODE_NO_SANITIZE int unweightedDistBetweenPaths(int a, int b, int c, int d) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi || d < lo || d > hi)
            bad("unweightedDistBetweenPaths");
        int p = medianOf(a, b, c);  // where c's side meets the path a..b
        if (p != medianOf(a, b, d)) return 0;  // c and d meet it at different nodes, so c..d runs along it
        return distOf(p, medianOf(c, d, p));
    }

    // O(log n) -- the one node that lies on all three paths between a, b and c
    LEETCODE_NO_SANITIZE int median(int a, int b, int c) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi) bad("median");
        return medianOf(a, b, c);
    }

    // O(log n) -- the shared part of paths a..b and c..d as its two end nodes {p, q}, p first walking a -> b; p == q
    // if they share one node; {-1, -1} if they share none
    LEETCODE_NO_SANITIZE pair<int, int> pathIntersection(int a, int b, int c, int d) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi || d < lo || d > hi) bad("pathIntersection");
        int p = medianOf(a, b, c), q = medianOf(a, b, d);  // where c's side and d's side meet the path a..b
        if (p == q) return onPath(c, d, p) ? pair<int, int>{p, p} : pair<int, int>{-1, -1};
        return distOf(a, p) < distOf(a, q) ? pair<int, int>{p, q} : pair<int, int>{q, p};
    }

    // O(K + log n) -- every node on the path a..b, in order from a (K = how many)
    LEETCODE_NO_SANITIZE vector<int> pathNodes(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("pathNodes");
        int c = lcaOf(a, b), up = dep[a] - dep[c], len = up + dep[b] - dep[c] + 1;
        vector<int> out(len);
        int* p = out.data();
        for (int i = 0; a != c; a = par[a]) p[i++] = a;
        p[up] = c;
        for (int i = len - 1; b != c; b = par[b]) p[i--] = b;
        return out;
    }
};
