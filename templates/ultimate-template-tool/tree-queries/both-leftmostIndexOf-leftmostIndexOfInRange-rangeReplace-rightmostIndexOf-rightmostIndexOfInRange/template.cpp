// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-leftmostIndexOf-leftmostIndexOfInRange-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostIndexOf-leftmostIndexOfInRange-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange/fast.cpp
// @operations: countAtDepthInSubtree depth edgeNearestAncestorEqX edgePathFirstEqX edgePathLastEqX isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeNearestAncestorEqX nodePathFirstEqX nodePathLastEqX parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: position-trees
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   edgeNearestAncestorEqX: log^2(N)
//   edgePathFirstEqX: log^2(N)
//   edgePathLastEqX: log^2(N)
//   isAncestor: 1
//   isOnPath: log(N)
//   kthAncestor: log(N)
//   kthNodeOnPath: log(N)
//   lca: log(N)
//   lcaRootedAt: log(N)
//   median: log(N)
//   nextNodeOnPath: log(N)
//   nodeNearestAncestorEqX: log^2(N)
//   nodePathFirstEqX: log^2(N)
//   nodePathLastEqX: log^2(N)
//   parent: 1
//   parentRootedAt: log(N)
//   pathIntersection: log(N)
//   pathNodes: K+log(N)
//   subtreeSize: 1
//   subtreeSizeRootedAt: log(N)
//   unweightedDist: log(N)
//   unweightedDistBetweenPaths: log(N)
//   unweightedDistToPath: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: L[2*N*log(N)] R[2*N*log(N)]
//   tags: none
//   other: roots[2*N] vals[2*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: one dynamic seg tree over the positions per distinct value; at most about N log N nodes live at once (freed nodes are reused); values are hashed, so any values work
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// One seg tree over the positions per value (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r]
// into y in O(log N) amortized, for any values. Each distinct value keeps a seg tree over 0..n-1 holding the positions
// where it is; a change splits x's tree at [l, r] (O(log N) new nodes) and merges the cut part into y's
// tree (each step of a merge frees a node, so merges cost O(log N) amortized over the whole run). Also: where x first
// / last appears (in a range). All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies.
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
    // node 0 = the empty tree; L / R: children
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int L = 0, R = 0;
    };
    int n;
    HotVector<Node> nd;
    HotVector<int> roots, freeList;
    HotVector<T> vals;
    unordered_map<T, int, SafeHash> ids;

    // O(N log N) -- arr: the initial array
    PositionTrees(const vector<T>& arr) : n((int)arr.size()), nd(1) {
        nd.reserve(2 * n + 2);
        for (int i = 0; i < n; i++) {
            int k = id(arr[i]);
            roots[k] = insert(roots[k], i);
        }
    }

    // O(1) -- the length of the array
    LEETCODE_NO_SANITIZE int size() const { return n; }

    // O(logN) amortized -- every a[i] == x with l <= i <= r becomes y; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void rangeReplace(int l, int r, const T& x, const T& y) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReplace: needs 0 <= l <= r < size()");
        auto it = ids.find(x);
        if (it != ids.end() && x != y) moveTo(it->second, l, r, y);
    }

    // O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int leftmostIndexOf(const T& x) const { return edgeOf(x, true); }

    // O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    LEETCODE_NO_SANITIZE int rightmostIndexOf(const T& x) const { return edgeOf(x, false); }

    // O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = ids.find(x);
        return it == ids.end() ? -1 : firstIn(roots[it->second], 0, n - 1, l, r, true);
    }

    // O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = ids.find(x);
        return it == ids.end() ? -1 : firstIn(roots[it->second], 0, n - 1, l, r, false);
    }

    // O(N log N) -- the whole current array
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
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

    LEETCODE_NO_SANITIZE int id(const T& v) {
        // v's index into vals / roots (a new one, with an empty tree, the first time v is seen)
        auto [it, fresh] = ids.try_emplace(v, (int)vals.size());
        if (fresh) vals.push_back(v), roots.push_back(0);
        return it->second;
    }

    LEETCODE_NO_SANITIZE int newNode() {  // an empty node (a freed one if there is one)
        if (!freeList.empty()) {
            int x = freeList.back();
            freeList.pop_back();
            nd[x] = Node();
            return x;
        }
        nd.emplace_back();
        return (int)nd.size() - 1;
    }

    LEETCODE_NO_SANITIZE int pull(int x) {  // recompute x from its children
        return x;
    }

    LEETCODE_NO_SANITIZE int insert(int t, int i) {  // t's tree with position i (not in it) added; returns the root
        if (!t) t = newNode();
        int root = t, lo = 0, hi = n - 1;
        while (true) {
            if (lo == hi) {
                return root;
            }
            int mid = (lo + hi) >> 1;
            bool left = i <= mid;
            if (!(left ? nd[t].L : nd[t].R)) {
                int c = newNode();
                (left ? nd[t].L : nd[t].R) = c;
            }
            t = left ? nd[t].L : nd[t].R;
            (left ? hi : lo) = left ? mid : mid + 1;
        }
    }

    // (t without the positions in [l, r], a tree of just those); no empty nodes are left behind
    LEETCODE_NO_SANITIZE pair<int, int> split(int t, int lo, int hi, int l, int r) {
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

    LEETCODE_NO_SANITIZE int merge(int a, int b) {
        // the union of two trees over disjoint positions; b's nodes that overlap a's are freed
        if (!a || !b) return a ? a : b;
        int l = merge(nd[a].L, nd[b].L);
        int r = merge(nd[a].R, nd[b].R);
        nd[a].L = l, nd[a].R = r;
        freeList.push_back(b);
        return pull(a);
    }

    LEETCODE_NO_SANITIZE void moveTo(int k, int l, int r, const T& y) {
        // the positions in [l, r] of vals[k]'s tree go to y's
        auto [keep, cut] = split(roots[k], 0, n - 1, l, r);
        roots[k] = keep;
        if (!cut) return;
        int ky = id(y);
        int t = roots[ky] = merge(roots[ky], cut);
        (void)t;
    }

    LEETCODE_NO_SANITIZE int edgeOf(const T& x, bool left) const {  // the first (left) / last position of x, or -1
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

    LEETCODE_NO_SANITIZE int firstIn(int t, int lo, int hi, int l, int r, bool left) const {
        // the first (left) / last position in [l, r], or -1
        if (!t || r < lo || hi < l) return -1;
        if (lo == hi) return lo;
        int mid = (lo + hi) >> 1;
        int res = left ? firstIn(nd[t].L, lo, mid, l, r, left) : firstIn(nd[t].R, mid + 1, hi, l, r, left);
        if (res != -1) return res;
        return left ? firstIn(nd[t].R, mid + 1, hi, l, r, left) : firstIn(nd[t].L, lo, mid, l, r, left);
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
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above (PositionTrees)
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
    PositionTrees<T> nodeSeg;  // the node values, in position order
    PositionTrees<T> edgeSeg;  // each edge's weight, at its lower end's position

    // O(n * log n) -- builds the layout and the two range structures; throws invalid_argument when the edges are not
    // one tree on nodes 0..n-1 or 1..n, an edge has no weight, or vals has the wrong size
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

    // O(log^2 n) -- nearest ancestor of node (node included) with val = x (-1 if none)
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

    // O(log^2 n) -- first node walking a -> b with val = x (-1 if none)
    LEETCODE_NO_SANITIZE int nodePathFirstEqX(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathFirstEqX");
        return nodeFirstEqX(a, b, x);
    }

    // O(log^2 n) -- last node walking a -> b with val = x (-1 if none)
    LEETCODE_NO_SANITIZE int nodePathLastEqX(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("nodePathLastEqX");
        return nodeFirstEqX(b, a, x);
    }

    // O(log^2 n) -- nearest edge above node (toward the root) with weight = x, as its lower end (-1 if none)
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

    // O(log^2 n) -- first edge walking a -> b with weight = x, as its lower end (-1 if none)
    LEETCODE_NO_SANITIZE int edgePathFirstEqX(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathFirstEqX");
        return edgeFirstEqX(a, b, x);
    }

    // O(log^2 n) -- last edge walking a -> b with weight = x, as its lower end (-1 if none)
    LEETCODE_NO_SANITIZE int edgePathLastEqX(int a, int b, const T& x) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathLastEqX");
        return edgeFirstEqX(b, a, x);
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
