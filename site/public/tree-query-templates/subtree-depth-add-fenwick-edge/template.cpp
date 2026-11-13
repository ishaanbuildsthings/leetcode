// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/subtree-depth-add-fenwick-edge/template.cpp
// @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgePathSum edgeSubtreeAdd edgeSubtreeAddByDepth edgeSubtreeSum isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: euler-fenwick
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   edgeAdd: log(N)
//   edgeAssign: log(N)
//   edgeChmax: log(N)
//   edgeChmin: log(N)
//   edgeGet: log(N)
//   edgePathSum: log(N)
//   edgeSubtreeAdd: log(N)
//   edgeSubtreeAddByDepth: log(N)
//   edgeSubtreeSum: log(N)
//   isAncestor: 1
//   isOnPath: log(N)
//   kthAncestor: log(N)
//   kthNodeOnPath: log(N)
//   lca: log(N)
//   lcaRootedAt: log(N)
//   median: log(N)
//   nextNodeOnPath: log(N)
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
//   node: ca[1*N] cb[1*N] sa[1*N] sb[1*N] up[1*N]
//   tags: none
//   other: base[1*N] first[1*N] depSum[1*N] rootSum[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.
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
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

// Tree<long long> tree(edges, root);
//
// edges: the tree's n - 1 edges with their weights, vector<vector<int>> (vector<vector<long long>> works too). Whether
//        nodes are 0..n-1 or 1..n is detected automatically from the edge list (smallest label is 0 -> 0..n-1,
//        otherwise 1..n; with no edges, from root)
//   {{a, b, w}, ...}     e.g. {{0, 1, 5}, {1, 2, 7}}
// root: the root node (required), e.g. 0 or 1.
//
//   Tree<long long> tree({{0, 1, 5}, {1, 2, 7}}, 0);    // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2, 5}, {2, 3, 7}}, 1);    // nodes 1..3, rooted at 1
//
// T is the type the weights are kept in (long long, or int).
// An edge is named by its two ends in either order: (a, b) and (b, a) are the same edge. A path a..b covers the edges
// between a and b, and a subtree covers the edges below node. A search that finds an edge returns its lower end (the
// end farther from the root). A query with no edges to look at (a path a..a, a leaf's subtree) says what it returns.
// Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree throws out_of_range.
// Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: one heavy-light pass gives every node a position, so that each subtree is one stretch of positions
// (pos[node] .. pos[node] + sz[node] - 1). Adding by depth gives the edge at depth d the amount A + B * d, with the
// same A and B for the whole subtree (B = step, and A = start minus step times the depth where the subtree starts). So
// every update is "add A + B * depth over a stretch of positions", and five Fenwick trees over the positions keep them.
// ca and cb are difference trees: a prefix sum is the A (the B) that applies at a position, which gives one value. sa
// and sb are their partners for a sum over a stretch (sb weighs each B by the depths it covers), which gives a
// subtree's sum. up keeps what the updates added to the path from the root down to a node, apart from the part that
// follows from that node's own depth d: A * d + B * (0 + 1 + ... + d). With it the sum on root..v is one read, and a
// path a..b is root..a plus root..b minus what lies above their lca.
//
// The arithmetic is done mod 2^64 (unsigned), because a product on the way can pass 64 bits though the answer fits: the
// answers are exact whenever they fit the value type.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    // every number is kept mod 2^64: a product on the way can pass 64 bits though the answer fits, and unsigned
    // arithmetic wraps without harm, so an answer is exact whenever it fits the value type
    using C = unsigned long long;
    using W = unsigned long long;
    // base[v]: the weight of the edge above v (the root has none) at the start, plus what was added to it alone.
    // first[i]: the starting values at positions below i, summed. depSum[i]: the depths at positions below i, summed.
    // rootSum[v]: the starting values on the path root..v, summed.
    HotVector<C> base, first, depSum, rootSum;
    // Five Fenwick trees over the positions (1-based), filled by the updates, each "add A + B * depth over a stretch":
    // ca, cb (a prefix sum is the A, the B that applies at a position), sa, sb (with them, the sum over a stretch) and
    // up (what the updates gave the path from the root, apart from its depth terms).
    HotVector<C> ca, cb, sa, sb, up;

    // O(n) -- builds the layout and the sums of the starting values; throws invalid_argument when the edges are not one
    // tree on nodes 0..n-1 or 1..n, or an edge has no weight
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root) : root(root) {
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
        for (const auto& e : edges)
            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");
        base.assign(hi + 1, 0);
        for (const auto& e : edges) {
            int a = (int)e[0], b = (int)e[1];
            base[par[a] == b ? a : b] = fit(wide((T)e[2]));
        }
        first.assign(n + 1, 0), depSum.assign(n + 1, 0), rootSum.assign(hi + 1, 0);
        for (int i = 0; i < n; i++) {
            int v = order[i];
            first[i + 1] = fit((W)first[i] + (W)base[v]);
            depSum[i + 1] = fit((W)depSum[i] + (W)dep[v]);
            rootSum[v] = fit((W)base[v] + (v == root ? W(0) : (W)rootSum[par[v]]));
        }
        ca.assign(n + 1, 0), cb = sa = sb = up = ca;
    }

    // (the MOD version of this template reduces here; this one keeps every number as it is, mod 2^64)
    LEETCODE_NO_SANITIZE static C fit(W x) { return x; }
    LEETCODE_NO_SANITIZE static W wide(T x) { return (W)(long long)x; }

    // 0 + 1 + ... + d
    LEETCODE_NO_SANITIZE static W tri(W d) { return d * (d + 1) / 2; }

    // one Fenwick step in all five trees: from position p on, ca += a, cb += b, sa += c, sb += d, up += e (nothing when
    // p is past the last position)
    LEETCODE_NO_SANITIZE void mark(int p, W a, W b, W c, W d, W e) {
        C fa = fit(a), fb = fit(b), fc = fit(c), fd = fit(d), fe = fit(e);
        for (p++; p <= n; p += p & -p) ca[p] += fa, cb[p] += fb, sa[p] += fc, sb[p] += fd, up[p] += fe;
    }

    // the five trees' prefix sums through one position
    struct Read {
        W a, b, sumA, sumB, up;
    };
    LEETCODE_NO_SANITIZE Read read(int p) const {
        W a = 0, b = 0, c = 0, d = 0, e = 0;
        for (p++; p > 0; p -= p & -p) a += ca[p], b += cb[p], c += sa[p], d += sb[p], e += up[p];
        return Read{a, b, c, d, e};
    }

    // every value at positions l..r gets A + B * (its depth) added; top: the depth of the shallowest of them (nothing
    // for an empty stretch, l > r)
    LEETCODE_NO_SANITIZE void spread(int l, int r, int top, W A, W B) {
        if (l > r) return;
        // what a path from the root gains, apart from its depth terms
        W gain = A * (W)(long long)(1 - top) - B * tri(top - 1);
        mark(l, A, B, A * (W)l, B * (W)depSum[l], gain);
        mark(r + 1, 0 - A, 0 - B, 0 - A * (W)(r + 1), 0 - B * (W)depSum[r + 1], 0 - gain);
    }

    // the value kept at node v grows by x (it alone)
    LEETCODE_NO_SANITIZE void bump(int v, W x) {
        base[v] = fit((W)base[v] + x);
        mark(pos[v], 0, 0, 0 - x, 0, x);
        mark(pos[v] + sz[v], 0, 0, 0, 0, 0 - x);
    }

    // the value kept at node v
    LEETCODE_NO_SANITIZE C valueOf(int v) const {
        Read s = read(pos[v]);
        return fit((W)base[v] + s.a + s.b * (W)dep[v]);
    }

    // the sum of the values at positions 0..k (0 when k is -1)
    LEETCODE_NO_SANITIZE C upTo(int k) const {
        Read s = read(k);
        return fit((W)first[k + 1] + (W)(k + 1) * s.a - s.sumA + (W)depSum[k + 1] * s.b - s.sumB);
    }

    // the sum of the values kept on the path root..v
    LEETCODE_NO_SANITIZE C fromRoot(int v) const {
        Read s = read(pos[v]);
        return fit((W)rootSum[v] + s.up + s.a * (W)dep[v] + s.b * tri(dep[v]));
    }

    // the lower end of the edge a - b, the node its weight is kept under (a and b in either order)
    LEETCODE_NO_SANITIZE int edgeAt(const char* name, int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad(name);
        if (par[a] == b) return a;
        if (par[b] == a) return b;
        throw out_of_range(string(name) + ": needs an edge between a and b");
    }

    // O(log n) -- weight(a - b); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE T edgeGet(int a, int b) {
        int v = edgeAt("edgeGet", a, b);
        return (T)(long long)valueOf(v);
    }

    // O(log n) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeAssign(int a, int b, T w) {
        int v = edgeAt("edgeAssign", a, b);
        bump(v, wide(w) - (W)valueOf(v));
    }

    // O(log n) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeAdd(int a, int b, T w) {
        int v = edgeAt("edgeAdd", a, b);
        bump(v, wide(w));
    }

    // O(log n) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeChmax(int a, int b, T w) {
        int v = edgeAt("edgeChmax", a, b);
        T now = (T)(long long)valueOf(v);
        if (w > now) bump(v, wide(w) - wide(now));
    }

    // O(log n) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE void edgeChmin(int a, int b, T w) {
        int v = edgeAt("edgeChmin", a, b);
        T now = (T)(long long)valueOf(v);
        if (w < now) bump(v, wide(w) - wide(now));
    }

    // O(log n) -- weight += w for every edge in node's subtree
    LEETCODE_NO_SANITIZE void edgeSubtreeAdd(int node, T w) {
        if (node < lo || node > hi) bad("edgeSubtreeAdd");
        // the edges below node: the positions after its own, the shallowest one level below node
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1, top = dep[node] + 1;
        spread(l, r, top, (W)fit(wide(w)), 0);
    }

    // O(log n) -- every edge in node's subtree gets start + step * k added, k = how many edges lie between node and the
    // edge's upper end (0 for the edges just below node)
    LEETCODE_NO_SANITIZE void edgeSubtreeAddByDepth(int node, T start, T step) {
        if (node < lo || node > hi) bad("edgeSubtreeAddByDepth");
        // the edges below node: the positions after its own, the shallowest one level below node
        int l = pos[node] + 1, r = pos[node] + sz[node] - 1, top = dep[node] + 1;
        spread(l, r, top, (W)fit(wide(start) - wide(step) * (W)top), (W)fit(wide(step)));
    }

    // O(log n) -- sum of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE T edgeSubtreeSum(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeSum");
        return (T)(long long)fit((W)upTo(pos[node] + sz[node] - 1) - (W)upTo(pos[node]));
    }

    // O(log n) -- sum of the edge weights on the path a..b; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE T edgePathSum(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSum");
        return (T)(long long)fit((W)fromRoot(a) + (W)fromRoot(b) - (W)2 * (W)fromRoot(lcaOf(a, b)));
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
