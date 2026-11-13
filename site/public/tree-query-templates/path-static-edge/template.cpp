// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/path-static-edge/template.cpp
// @operations: countAtDepthInSubtree depth edgeGet edgePathHash edgePathHashReversed edgePathIsPalindrome edgePathSum edgePathXOR edgePathsEqual edgeSubtreeSum edgeSubtreeXOR isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: root-prefix
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   edgeGet: 1
//   edgePathHash: 1
//   edgePathHashReversed: 1
//   edgePathIsPalindrome: 1
//   edgePathSum: 1
//   edgePathXOR: 1
//   edgePathsEqual: 1
//   edgeSubtreeSum: 1
//   edgeSubtreeXOR: 1
//   isAncestor: 1
//   isOnPath: 1
//   kthAncestor: log(N)
//   kthNodeOnPath: log(N)
//   lca: 1
//   lcaRootedAt: 1
//   median: 1
//   nextNodeOnPath: log(N)
//   parent: 1
//   parentRootedAt: log(N)
//   pathIntersection: 1
//   pathNodes: K
//   subtreeSize: 1
//   subtreeSizeRootedAt: log(N)
//   unweightedDist: 1
//   unweightedDistBetweenPaths: 1
//   unweightedDistToPath: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: sumTo[1*N] xorTo[1*N] sumAt[1*N] xorAt[1*N] down[1*N] up[1*N]
//   tags: none
//   other: val[1*N] pw[1*N] ipw[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N] table[1*N*log(N)]
//   note: the n log n part is the lca table (what makes every query O(1)); pw / ipw are as long as the tree is deep
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
// How it works: the values never change, so a sum, a xor and a hash along the path from the root to a node are kept for
// every node, and a path a..b is two or three reads of them around the lca of a and b. The lca is O(1): one heavy-light
// pass gives every node a position, and a sparse table over the positions finds it (between two nodes' positions, the
// parent that sits earliest is their lca). A subtree is one stretch of positions (pos[node] .. pos[node] + sz[node] -
// 1), so prefix arrays over the positions give its sum and xor. For the hash, up[v] is the sum of hash(edge) *
// base^depth along root..v: the difference of two of them is the hash of the stretch between, read upwards, times
// base^(the depth of its top), which an inverse power of the base takes off. down[v] is the hash of root..v read
// downwards. The way up to the lca and the way down from it are then joined like any two hashes.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    // table[j * n + i] = the earliest parent position among the nodes at positions i .. i + 2^j - 1
    HotVector<int> table;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;  // what sums are kept in
    using U64 = unsigned long long;
    // val[v]: the weight of the edge above v (the root has none). Along the path root..v: sumTo[v] and xorTo[v] (the
    // sum and the xor of its edge weights), down[v] (their hash read downwards) and up[v] (the sum of hash(value) *
    // base^depth). Over the positions: sumAt[i] and xorAt[i], the sum and the xor of the values at positions below i.
    // pw[d] = base^d and ipw[d] = 1 / base^d.
    HotVector<T> val, xorTo, xorAt;
    HotVector<S> sumTo, sumAt;
    HotVector<U64> down, up, pw, ipw;

    // hashes are mod the prime 2^61 - 1, with a base picked at random each run (so no test can be built against it)
    static U64 rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
    static constexpr U64 HP = (1ULL << 61) - 1;
    static U64 HB() {
        static U64 b = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
        return b;
    }
    LEETCODE_NO_SANITIZE static U64 hmul(U64 a, U64 b) {
        unsigned __int128 c = (unsigned __int128)a * b;
        U64 r = (U64)(c & HP) + (U64)(c >> 61);
        r = (r & HP) + (r >> 61);
        return r >= HP ? r - HP : r;
    }
    LEETCODE_NO_SANITIZE static U64 hadd(U64 a, U64 b) { return a + b >= HP ? a + b - HP : a + b; }
    LEETCODE_NO_SANITIZE static U64 hsub(U64 a, U64 b) { return a >= b ? a - b : a + HP - b; }
    // the hash of one value: v + an offset random per run, so no common value is 0 (a 0 in front would vanish)
    static U64 hval(T v) {
        static U64 off = 1 + rnd() % (HP - 1);
        long long r = (long long)v % (long long)HP;
        return hadd(r < 0 ? (U64)(r + (long long)HP) : (U64)r, off);
    }

    // O(n log n) -- builds the layout, the lca table and the sums from the root; throws invalid_argument when the edges
    // are not one tree on nodes 0..n-1 or 1..n, or an edge has no weight
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

        int levels = 1;
        while ((2 << (levels - 1)) < n) levels++;
        table.assign((size_t)levels * n, 0);
        for (int i = 1; i < n; i++) table[i] = pos[par[order[i]]];
        for (int j = 1; j < levels; j++) {
            int half = 1 << (j - 1);
            const int* below = &table[(size_t)(j - 1) * n];
            int* row = &table[(size_t)j * n];
            for (int i = 0; i + 2 * half <= n; i++) row[i] = below[i] < below[i + half] ? below[i] : below[i + half];
        }
        for (const auto& e : edges)
            if (e.size() != 3) throw invalid_argument("Tree: every edge needs its weight here, {a, b, w}");
        val.assign(hi + 1, T(0));
        for (const auto& e : edges) {
            int a = (int)e[0], b = (int)e[1];
            val[par[a] == b ? a : b] = (T)e[2];
        }
        int deepest = 0;
        for (int i = 0; i < n; i++) deepest = max(deepest, dep[order[i]]);
        U64 inverse = 1, base = HB();
        for (U64 e = HP - 2, b = base; e > 0; e >>= 1, b = hmul(b, b))  // base^(HP - 2) is 1 / base
            if (e & 1) inverse = hmul(inverse, b);
        pw.assign(deepest + 2, 1), ipw.assign(deepest + 2, 1);
        for (int d = 1; d < deepest + 2; d++) pw[d] = hmul(pw[d - 1], base), ipw[d] = hmul(ipw[d - 1], inverse);
        sumTo.assign(hi + 1, 0), xorTo.assign(hi + 1, 0), down.assign(hi + 1, 0), up.assign(hi + 1, 0);
        sumAt.assign(n + 1, 0), xorAt.assign(n + 1, 0);
        for (int i = 0; i < n; i++) {
            int v = order[i], p = par[v];
            T x = val[v];
            sumAt[i + 1] = sumAt[i] + x, xorAt[i + 1] = xorAt[i] ^ x;
            if (v == root) {
                continue;  // (no edge above the root: its sums stay 0)
            }
            U64 h = hval(x);
            sumTo[v] = sumTo[p] + x, xorTo[v] = xorTo[p] ^ x;
            down[v] = hadd(hmul(down[p], base), h), up[v] = hadd(up[p], hmul(h, pw[dep[v]]));
        }
    }

    // the hash of the edge weights read walking a -> b
    LEETCODE_NO_SANITIZE U64 hashOf(int a, int b) const {
        int c = lcaOf(a, b), d = dep[c];
        // the way up: the edges below the lca, the shallowest one level under it
        U64 head = hmul(hsub(up[a], up[c]), ipw[d + 1]);
        int m = dep[b] - d;  // how many values the way down from the lca holds
        return hadd(hmul(hsub(head, down[c]), pw[m]), down[b]);
    }

    // O(1) -- weight(a - b); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE T edgeGet(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgeGet");
        if (par[a] == b) return val[a];
        if (par[b] == a) return val[b];
        throw out_of_range("edgeGet: needs an edge between a and b");
    }

    // O(1) -- sum of the edge weights on the path a..b; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE S edgePathSum(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathSum");
        return sumTo[a] + sumTo[b] - 2 * sumTo[lcaOf(a, b)];
    }

    // O(1) -- xor of the edge weights on the path a..b; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE T edgePathXOR(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathXOR");
        return xorTo[a] ^ xorTo[b];
    }

    // O(1) -- hash of the edge weights read a -> b (mod 2^61 - 1, random base): equal sequences hash equal; 0 when a ==
    // b (no edges)
    LEETCODE_NO_SANITIZE unsigned long long edgePathHash(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathHash");
        return hashOf(a, b);
    }

    // O(1) -- hash of the edge weights read b -> a (equal to edgePathHash(b, a)); 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE unsigned long long edgePathHashReversed(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathHashReversed");
        return hashOf(b, a);
    }

    // O(1) -- do the edge weights read the same a -> b and b -> a? (True when a == b: no edges)
    LEETCODE_NO_SANITIZE bool edgePathIsPalindrome(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathIsPalindrome");
        return hashOf(a, b) == hashOf(b, a);
    }

    // O(1) -- do the edge weights read a -> b equal those read c -> d? (two paths with no edges are equal)
    LEETCODE_NO_SANITIZE bool edgePathsEqual(int a, int b, int c, int d) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi || d < lo || d > hi) bad("edgePathsEqual");
        return distOf(a, b) == distOf(c, d) && hashOf(a, b) == hashOf(c, d);
    }

    // O(1) -- sum of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE S edgeSubtreeSum(int node) const {
        if (node < lo || node > hi) bad("edgeSubtreeSum");
        return sumAt[pos[node] + sz[node]] - sumAt[pos[node] + 1];
    }

    // O(1) -- xor of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE T edgeSubtreeXOR(int node) const {
        if (node < lo || node > hi) bad("edgeSubtreeXOR");
        return xorAt[pos[node] + sz[node]] ^ xorAt[pos[node] + 1];
    }

    [[noreturn]] void bad(const char* name) const {
        throw out_of_range(string(name) + ": needs " + to_string(lo) + " <= node <= " + to_string(hi));
    }

    LEETCODE_NO_SANITIZE int lcaOf(int a, int b) const {
        if (a == b) return a;
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        int j = 31 - __builtin_clz(r - l);
        const int* row = &table[(size_t)j * n];
        int x = row[l + 1], y = row[r - (1 << j) + 1];
        return order[x < y ? x : y];
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

    // O(1) -- lowest common ancestor of a and b
    LEETCODE_NO_SANITIZE int lca(int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad("lca");
        return lcaOf(a, b);
    }

    // O(1) -- number of edges on the path a..b
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

    // O(1) -- lca of a and b if the tree were rooted at r instead
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

    // O(1) -- does the path a..b pass through node? (a and b count)
    LEETCODE_NO_SANITIZE bool isOnPath(int a, int b, int node) const {
        if (a < lo || a > hi || b < lo || b > hi || node < lo || node > hi) bad("isOnPath");
        return onPath(a, b, node);
    }

    // O(1) -- fewest edges from node to any node on the path a..b (0 if node is on it)
    LEETCODE_NO_SANITIZE int unweightedDistToPath(int a, int b, int node) const {
        if (a < lo || a > hi || b < lo || b > hi || node < lo || node > hi) bad("unweightedDistToPath");
        return distOf(node, medianOf(a, b, node));
    }

    // O(1) -- fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)
    LEETCODE_NO_SANITIZE int unweightedDistBetweenPaths(int a, int b, int c, int d) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi || d < lo || d > hi)
            bad("unweightedDistBetweenPaths");
        int p = medianOf(a, b, c);  // where c's side meets the path a..b
        if (p != medianOf(a, b, d)) return 0;  // c and d meet it at different nodes, so c..d runs along it
        return distOf(p, medianOf(c, d, p));
    }

    // O(1) -- the one node that lies on all three paths between a, b and c
    LEETCODE_NO_SANITIZE int median(int a, int b, int c) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi) bad("median");
        return medianOf(a, b, c);
    }

    // O(1) -- the shared part of paths a..b and c..d as its two end nodes {p, q}, p first walking a -> b; p == q
    // if they share one node; {-1, -1} if they share none
    LEETCODE_NO_SANITIZE pair<int, int> pathIntersection(int a, int b, int c, int d) const {
        if (a < lo || a > hi || b < lo || b > hi || c < lo || c > hi || d < lo || d > hi) bad("pathIntersection");
        int p = medianOf(a, b, c), q = medianOf(a, b, d);  // where c's side and d's side meet the path a..b
        if (p == q) return onPath(c, d, p) ? pair<int, int>{p, p} : pair<int, int>{-1, -1};
        return distOf(a, p) < distOf(a, q) ? pair<int, int>{p, q} : pair<int, int>{q, p};
    }

    // O(K) -- every node on the path a..b, in order from a (K = how many)
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
