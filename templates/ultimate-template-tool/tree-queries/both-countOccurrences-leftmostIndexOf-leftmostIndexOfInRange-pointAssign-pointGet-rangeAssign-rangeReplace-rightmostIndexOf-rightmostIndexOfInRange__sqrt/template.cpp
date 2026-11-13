// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeAssign-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange__sqrt/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeAssign-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange__sqrt/fast.cpp
// @operations: countAtDepthInSubtree depth edgeAssign edgeGet edgeNearestAncestorEqX edgePathAssign edgePathCountOccurrences edgePathFirstEqX edgePathLastEqX edgeSubtreeAssign edgeSubtreeCountOccurrences isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAssign nodeGet nodeNearestAncestorEqX nodePathAssign nodePathCountOccurrences nodePathFirstEqX nodePathLastEqX nodeSubtreeAssign nodeSubtreeCountOccurrences parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: sqrt
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   edgeAssign: 1 amortized
//   edgeGet: 1 amortized
//   edgeNearestAncestorEqX: sqrt(N)*log(N)
//   edgePathAssign: sqrt(N)*log(N) amortized
//   edgePathCountOccurrences: sqrt(N)*log(N)
//   edgePathFirstEqX: sqrt(N)*log(N)
//   edgePathLastEqX: sqrt(N)*log(N)
//   edgeSubtreeAssign: sqrt(N) amortized
//   edgeSubtreeCountOccurrences: sqrt(N)
//   isAncestor: 1
//   isOnPath: log(N)
//   kthAncestor: log(N)
//   kthNodeOnPath: log(N)
//   lca: log(N)
//   lcaRootedAt: log(N)
//   median: log(N)
//   nextNodeOnPath: log(N)
//   nodeAssign: 1 amortized
//   nodeGet: 1 amortized
//   nodeNearestAncestorEqX: sqrt(N)*log(N)
//   nodePathAssign: sqrt(N)*log(N) amortized
//   nodePathCountOccurrences: sqrt(N)*log(N)
//   nodePathFirstEqX: sqrt(N)*log(N)
//   nodePathLastEqX: sqrt(N)*log(N)
//   nodeSubtreeAssign: sqrt(N) amortized
//   nodeSubtreeCountOccurrences: sqrt(N)
//   parent: 1
//   parentRootedAt: log(N)
//   pathIntersection: log(N)
//   pathNodes: K+log(N)
//   subtreeSize: 1
//   subtreeSizeRootedAt: log(N)
//   unweightedDist: log(N)
//   unweightedDistBetweenPaths: log(N)
//   unweightedDistToPath: log(N)
//   build: N
// @memory:
//   layout: none
//   node: cls[2*N] par[4*N] val[4*N] cnt[4*N] where[2*N]
//   tags: none
//   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: blocks of about sqrt(N) values; each block's values are classes joined by a union-find (union by size, path halving: O(alpha), counted as O(1)); where maps each value in the block to its class; values are hashed, so any values work
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// Blocks whose values form a union-find of classes (mass change, CF 911G, in O(sqrt N)): the array is cut into blocks
// of about sqrt(N) values. Inside a block equal values form a class, and the classes are joined by a union-find:
// rangeReplace(l, r, x, y) on a whole block renames x's class to y, or joins it into y's, in O(1); rangeAssign joins
// every class. Only the (at most two) partly covered blocks are touched value by value. Any values work (each block
// hashes them). a[i] and a[i] = v are O(1) amortized. All indices 0-based, ranges inclusive [l, r]; searches return
// -1 when nothing qualifies.
// T: any type with a hash (int, long long, char, ...)

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
    // a run of the array: cls[k] is the class of its k-th value. Classes form a union-find
    // (par); a root class holds its value (val) and how many of the block's values are in it (cnt). where: value ->
    // root
    struct Block {
        vector<int> cls, par, cnt;
        vector<T> val;
        unordered_map<T, int, SafeHash> where;

        Block() {}
        explicit Block(const vector<T>& vals) { build(vals); }

        void build(const vector<T>& vals) {  // O(len) -- the classes from scratch
            cls.clear(), par.clear(), cnt.clear(), val.clear(), where.clear();
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
            return val[find(cls[k])];
        }

        vector<T> values() {  // every value, in order
            vector<T> out;
            out.reserve(cls.size());
            for (int c : cls) out.push_back(val[find(c)]);
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

        void assign(int k, const T& v) {
            // O(1) amortized -- the k-th value becomes v (a class of its own if v is new here)
            int c = find(cls[k]);
            if (val[c] == v) return;
            if (!--cnt[c]) where.erase(val[c]);
            auto [it, fresh] = where.try_emplace(v, (int)par.size());
            if (fresh) par.push_back(it->second), val.push_back(v), cnt.push_back(0);
            cnt[it->second]++;
            cls[k] = it->second;
            // (many dead classes: start over, paid for by the assigns)
            if ((int)par.size() > 2 * size() + 8) build(values());
        }
    };

    HotVector<Block> blocks;
    int n = 0, B = 1;

    // O(N) -- arr: the initial array
    explicit SqrtReplace(const vector<T>& arr) { fill(arr); }

    // O(1) -- the length of the array
    LEETCODE_NO_SANITIZE int size() const { return n; }

    // O(N) -- the whole current array
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        for (Block& b : blocks) {
            vector<T> v = b.values();
            out.insert(out.end(), v.begin(), v.end());
        }
        return out;
    }

    // O(1) amortized) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        auto [j, k] = locate(i);
        return blocks[j].get(k);
    }

    // O(1) amortized) -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, const T& v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        auto [j, k] = locate(i);
        blocks[j].assign(k, v);
    }

    // O(sqrt(N)) amortized -- every a[i] == x with l <= i <= r becomes y; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void rangeReplace(int l, int r, const T& x, const T& y) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReplace: needs 0 <= l <= r < size()");
        if (x == y) return;
        span(l, r, [&](Block& b, int lo, int hi, bool whole, int) {
            if (whole) b.replace(x, y);
            else
                for (int k = lo; k <= hi; k++)
                    if (b.get(k) == x) b.assign(k, y);
            return false;
        });
    }

    // O(sqrt(N)) amortized -- a[l..r] = v; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, const T& v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        span(l, r, [&](Block& b, int lo, int hi, bool whole, int) {
            if (whole) b.assignAll(v);
            else
                for (int k = lo; k <= hi; k++) b.assign(k, v);
            return false;
        });
    }

    // O(sqrt(N)) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int countOccurrences(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countOccurrences: needs 0 <= l <= r < size()");
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
    LEETCODE_NO_SANITIZE int leftmostIndexOf(const T& x) { return findIn(0, n - 1, x, true); }

    // O(sqrt(N)) -- the largest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int rightmostIndexOf(const T& x) { return findIn(0, n - 1, x, false); }

    // O(sqrt(N)) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostIndexOfInRange(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        return findIn(l, r, x, true);
    }

    // O(sqrt(N)) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostIndexOfInRange(int l, int r, const T& x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        return findIn(l, r, x, false);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE static int idealB(int m) { return max(1, (int)sqrt((double)m)); }

    LEETCODE_NO_SANITIZE void fill(const vector<T>& vals) {  // blocks of about idealB values holding vals
        n = (int)vals.size(), B = idealB(n);
        blocks.clear();
        for (int s = 0; s < n; s += B) blocks.emplace_back(vector<T>(vals.begin() + s, vals.begin() + min(n, s + B)));
    }

    // (block index, position in it) of a[i]
    LEETCODE_NO_SANITIZE pair<int, int> locate(int i) const { return {i / B, i % B}; }

    // f(block, lo, hi, whole, start) for each block meeting a[l..r] (positions lo..hi of it, whether that is all of
    // it, the index of its first value), until f returns true
    template <class F>
    LEETCODE_NO_SANITIZE void span(int l, int r, F f) {
        for (int j = l / B; j <= r / B; j++) {
            int start = j * B, m = blocks[j].size(), lo = max(l - start, 0), hi = min(r - start, m - 1);
            if (f(blocks[j], lo, hi, lo == 0 && hi == m - 1, start)) return;
        }
    }

    LEETCODE_NO_SANITIZE int findIn(int l, int r, const T& x, bool left) {
        // the first (left) / last i in [l, r] with a[i] == x, or -1
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

// Tree tree(edges, root, vals);
//
// edges: the tree's n - 1 edges with their weights, vector<vector<int>> (vector<vector<long long>> works too). Whether
//        nodes are 0..n-1 or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1,
//        otherwise 1..n; with no edges, from root)
//   {{a, b, w}, ...}     e.g. {{0, 1, 5}, {1, 2, 7}}
// root: the root node (required), e.g. 0 or 1.
// vals: the node values, vector<T> (T = long long, or int; the weights are kept as T too), vals[node] is node's value
//   nodes 0..n-1: size n        e.g. n = 3: {10, 20, 30}         node 0 -> 10
//   nodes 1..n:   size n + 1    e.g. n = 3: {0, 10, 20, 30}      vals[0] is ignored, node 1 -> 10
//
//   Tree<long long> tree({{0, 1, 5}, {1, 2, 7}}, 0, {10, 20, 30});       // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2, 5}, {2, 3, 7}}, 1, {0, 10, 20, 30});    // nodes 1..3, rooted at 1
//
// The node... ops act on the node values and the edge... ops on the edge weights: the two never affect each other. For
// nodes, a path a..b includes both a and b. For edges, a path a..b covers the edges between a and b and a subtree the
// edges below node; an edge is named by its two ends in either order, a search that finds an edge returns its lower end
// (the end farther from the root), and a query with no edges to look at (a path a..a, a leaf's subtree) says what it
// returns. Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree throws
// out_of_range. Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above (SqrtReplace)
// sit over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's weight at its lower
// end's position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n) ranges, one per chain
// it crosses.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    SqrtReplace<T> nodeSeg;  // the node values, in position order
    SqrtReplace<T> edgeSeg;  // each edge's weight, at its lower end's position

    // O(n) -- builds the layout and the two range structures; throws invalid_argument when the edges are not one tree
    // on nodes 0..n-1 or 1..n, an edge has no weight, or vals has the wrong size
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, const vector<T>& vals)
        : nodeSeg(layout(edges, root, vals)), edgeSeg(weights(edges)) {}

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

    // each edge's weight, at its lower end's position (the layout is built by the time this runs)
    template <typename E> vector<T> weights(const vector<vector<E>>& edges) {
        for (const auto& e : edges)
            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");
        // (position 0 is the root's: it holds no edge and is never read)
        vector<T> inOrder(n, edges.empty() ? T(0) : (T)edges[0][2]);
        for (const auto& e : edges) {
            int a = (int)e[0], b = (int)e[1];
            inOrder[par[a] == b ? pos[a] : pos[b]] = (T)e[2];
        }
        return inOrder;
    }

    // O(1) -- val(node)
    LEETCODE_NO_SANITIZE auto nodeGet(int node) {
        if (node < lo || node > hi) bad("nodeGet");
        return nodeSeg.pointGet(pos[node]);
    }

    // O(1) -- val(node) = x
    LEETCODE_NO_SANITIZE void nodeAssign(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeAssign");
        nodeSeg.pointAssign(pos[node], x);
    }

    // O(sqrt(n) * log n) -- val = x for every node on the path a..b
    LEETCODE_NO_SANITIZE void nodePathAssign(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathAssign");
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            nodeSeg.rangeAssign(pos[head[a]], pos[a], x);
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l <= r) nodeSeg.rangeAssign(l, r, x);
        else nodeSeg.rangeAssign(r, l, x);
    }

    // O(sqrt(n) * log n) -- how many node values on the path a..b equal x
    LEETCODE_NO_SANITIZE auto nodePathCountOccurrences(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathCountOccurrences");
        using R = decltype(nodeSeg.countOccurrences(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = nodeSeg.countOccurrences(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        R v = nodeSeg.countOccurrences(l, r, x);
        res += v;
        return res;
    }

    // O(sqrt(n) * log n) -- nearest ancestor of node (node included) with val = x (-1 if none)
    LEETCODE_NO_SANITIZE int nodeNearestAncestorEqX(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeNearestAncestorEqX");
        while (node != -1) {
            int i = nodeSeg.rightmostIndexOfInRange(pos[head[node]], pos[node], x);
            if (i != -1) return order[i];
            node = par[head[node]];
        }
        return -1;
    }

    LEETCODE_NO_SANITIZE int nodeFirstEqX(int a, int b, const T& x) {
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
                int i = nodeSeg.rightmostIndexOfInRange(l, r, x);
                if (i != -1) return order[i];
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] >= pos[b]) {  // the piece holding the lca: b is the top
            int l = pos[b], r = pos[a];
            int i = nodeSeg.rightmostIndexOfInRange(l, r, x);
            if (i != -1) return order[i];
        } else {
            int l = pos[a], r = pos[b];
            int i = nodeSeg.leftmostIndexOfInRange(l, r, x);
            if (i != -1) return order[i];
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
            int i = nodeSeg.leftmostIndexOfInRange(l, r, x);
            if (i != -1) return order[i];
        }
        return -1;
    }

    // O(sqrt(n) * log n) -- first node walking a -> b with val = x (-1 if none)
    LEETCODE_NO_SANITIZE int nodePathFirstEqX(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathFirstEqX");
        return nodeFirstEqX(a, b, x);
    }

    // O(sqrt(n) * log n) -- last node walking a -> b with val = x (-1 if none)
    LEETCODE_NO_SANITIZE int nodePathLastEqX(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLastEqX");
        return nodeFirstEqX(b, a, x);
    }

    // O(sqrt(n)) -- val = x for every node in node's subtree
    LEETCODE_NO_SANITIZE void nodeSubtreeAssign(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeSubtreeAssign");
        int l = pos[node];
        nodeSeg.rangeAssign(l, l + sz[node] - 1, x);
    }

    // O(sqrt(n)) -- how many node values in node's subtree equal x
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountOccurrences(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeSubtreeCountOccurrences");
        int l = pos[node];
        return nodeSeg.countOccurrences(l, l + sz[node] - 1, x);
    }

    // the position that holds the edge a - b: its lower end's (a and b in either order)
    LEETCODE_NO_SANITIZE int edgeAt(const char* name, int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad(name);
        if (par[a] == b) return pos[a];
        if (par[b] == a) return pos[b];
        throw out_of_range(string(name) + ": needs an edge between a and b");
    }

    // O(1) -- weight(a - b); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE auto edgeGet(int a, int b) {
        return edgeSeg.pointGet(edgeAt("edgeGet", a, b));
    }

    // O(1) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeAssign(int a, int b, const T& w) {
        edgeSeg.pointAssign(edgeAt("edgeAssign", a, b), w);
    }

    // O(sqrt(n) * log n) -- weight = w for every edge on the path a..b
    LEETCODE_NO_SANITIZE void edgePathAssign(int a, int b, const T& w) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathAssign");
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            edgeSeg.rangeAssign(pos[head[a]], pos[a], w);
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l < r) edgeSeg.rangeAssign(l + 1, r, w);  // (the lca's own position is the edge above it)
        else if (l > r) edgeSeg.rangeAssign(r + 1, l, w);
    }

    // O(sqrt(n) * log n) -- how many edge weights on the path a..b equal x; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE auto edgePathCountOccurrences(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountOccurrences");
        using R = decltype(edgeSeg.countOccurrences(0, 0, x));
        R res = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            R v = edgeSeg.countOccurrences(pos[head[a]], pos[a], x);
            res += v;
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) {  // (the lca's own position is the edge above it)
            R v = edgeSeg.countOccurrences(l + 1, r, x);
            res += v;
        }
        return res;
    }

    // O(sqrt(n) * log n) -- nearest edge above node (toward the root) with weight = x, as its lower end (-1 if none)
    LEETCODE_NO_SANITIZE int edgeNearestAncestorEqX(int node, const T& x) {
        if (node < lo || node > hi) bad("edgeNearestAncestorEqX");
        while (node != -1) {
            int l = pos[head[node]] ? pos[head[node]] : 1;  // (position 0 is the root's: it holds no edge)
            if (l <= pos[node]) {
                int i = edgeSeg.rightmostIndexOfInRange(l, pos[node], x);
                if (i != -1) return order[i];
            }
            node = par[head[node]];
        }
        return -1;
    }

    LEETCODE_NO_SANITIZE int edgeFirstEqX(int a, int b, const T& x) {
        int downs[64], m = 0;  // the chain pieces on b's side, bottom first (walked last, top first)
        while (head[a] != head[b]) {
            if (dep[head[a]] >= dep[head[b]]) {
                int l = pos[head[a]], r = pos[a];
                int i = edgeSeg.rightmostIndexOfInRange(l, r, x);
                if (i != -1) return order[i];
                a = par[head[a]];
            } else {
                downs[m++] = b;
                b = par[head[b]];
            }
        }
        if (pos[a] > pos[b]) {  // the piece holding the lca (b): its edges sit after the lca's position
            int l = pos[b] + 1, r = pos[a];
            int i = edgeSeg.rightmostIndexOfInRange(l, r, x);
            if (i != -1) return order[i];
        } else if (pos[a] < pos[b]) {
            int l = pos[a] + 1, r = pos[b];
            int i = edgeSeg.leftmostIndexOfInRange(l, r, x);
            if (i != -1) return order[i];
        }
        while (m > 0) {
            int d = downs[--m], l = pos[head[d]], r = pos[d];
            int i = edgeSeg.leftmostIndexOfInRange(l, r, x);
            if (i != -1) return order[i];
        }
        return -1;
    }

    // O(sqrt(n) * log n) -- first edge walking a -> b with weight = x, as its lower end (-1 if none)
    LEETCODE_NO_SANITIZE int edgePathFirstEqX(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathFirstEqX");
        return edgeFirstEqX(a, b, x);
    }

    // O(sqrt(n) * log n) -- last edge walking a -> b with weight = x, as its lower end (-1 if none)
    LEETCODE_NO_SANITIZE int edgePathLastEqX(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLastEqX");
        return edgeFirstEqX(b, a, x);
    }

    // O(sqrt(n)) -- weight = w for every edge in node's subtree
    LEETCODE_NO_SANITIZE void edgeSubtreeAssign(int node, const T& w) {
        if (node < lo || node > hi) bad("edgeSubtreeAssign");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        if (l > r) return;
        edgeSeg.rangeAssign(l, r, w);
    }

    // O(sqrt(n)) -- how many edge weights in node's subtree equal x; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE auto edgeSubtreeCountOccurrences(int node, const T& x) {
        if (node < lo || node > hi) bad("edgeSubtreeCountOccurrences");
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1;  // (l > r for a leaf: no edges below it)
        using R = decltype(edgeSeg.countOccurrences(0, 0, x));
        if (l > r) return R(0);
        return edgeSeg.countOccurrences(l, r, x);
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
