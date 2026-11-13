// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/path-distinct-bitset-edge/template.cpp
// @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgePathAllDistinct edgePathAssign edgePathCountDistinct edgeSubtreeAllDistinct edgeSubtreeAssign edgeSubtreeCountDistinct isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: bitset-seg-tree
// @complexities:
//   countAtDepthInSubtree: log(N)
//   depth: 1
//   edgeAdd: log(N)*D/64
//   edgeAssign: log(N)*D/64
//   edgeChmax: log(N)*D/64
//   edgeChmin: log(N)*D/64
//   edgeGet: log(N)
//   edgePathAllDistinct: log^2(N)*D/64
//   edgePathAssign: log^2(N)*D/64
//   edgePathCountDistinct: log^2(N)*D/64
//   edgeSubtreeAllDistinct: log(N)*D/64
//   edgeSubtreeAssign: log(N)*D/64
//   edgeSubtreeCountDistinct: log(N)*D/64
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
//   build: N*D/64
// @memory:
//   layout: none
//   node: bits[2*N*D/64]
//   tags: tag[2*N]
//   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: D = how many distinct values the bitsets have room for (C++: distinctCap), counting every value that ever appeared; a bitset is D / 64 words
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
// distinctCap: how many distinct values can ever appear, the ones here now and every one assigned later (they size the
// bitsets), e.g. Tree<long long> tree(edges, root, 5000). Leave it out when no new value will be assigned.
//
// How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). A segment tree over the positions keeps a bitset per
// node, one bit per distinct weight under it. A path a..b is O(log n) chain pieces, each O(log n) tree nodes: their
// bitsets ORed together have one bit per distinct value on the path. With D distinct values a bitset is D / 64 words,
// so this is for up to a few thousand distinct values (memory is 2 * n * D / 8 bytes). A value gets its bit the first
// time it appears, also later through an assign, and keeps it. An assign over a path or a subtree is kept at the O(log
// n) tree nodes that cover each stretch and handed down only when something below one of them is needed.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    unordered_map<T, int> ids;  // each value's bit, handed out as values first appear
    HotVector<T> values;  // values[b]: the value whose bit is b
    int cap, words;  // how many distinct values the bitsets have room for; how many 64-bit words that is
    // bits: a segment tree over the positions (its leaves n .. 2n - 1), `words` words a node: a bitset with one bit per
    // distinct value under the node; a parent is the OR of its two children
    HotVector<unsigned long long> bits;
    // tag[i]: for a leaf, the bit of its value; for a node above, the bit every value under it was assigned and its
    // children have not been told yet (-1: none)
    HotVector<int> tag;
    HotVector<unsigned long long> acc;  // the bitset a query ORs its nodes into

    // O(n * D / 64) -- builds the layout and the bitset tree; throws invalid_argument when the edges are not one tree
    // on nodes 0..n-1 or 1..n, an edge has no weight, or the values hold more than distinctCap distinct ones
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, int distinctCap = 0) : root(root) {
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
        vector<T> above(hi + 1, T(0));  // above[v]: the weight of the edge above v (the root has none)
        for (const auto& e : edges) {
            int a = (int)e[0], b = (int)e[1];
            above[par[a] == b ? a : b] = (T)e[2];
        }
        for (int i = 1; i < n; i++) ids.emplace(above[order[i]], (int)ids.size());
        cap = distinctCap > 0 ? distinctCap : max(1, (int)ids.size());
        if ((int)ids.size() > cap)
            throw invalid_argument("Tree: the values hold " + to_string(ids.size()) +
                                   " distinct ones, more than distinctCap = " + to_string(cap));
        words = (cap + 63) / 64;
        values.assign(cap, T());
        for (const auto& kept : ids) values[kept.second] = kept.first;
        bits.assign((size_t)2 * n * words, 0), tag.assign(2 * n, -1), acc.assign(words, 0);
        for (int i = 1; i < n; i++) apply(n + i, ids[above[order[i]]]);
        for (int i = n - 1; i > 0; i--) pull(i);
    }

    // seg node i's bitset = the OR of its two children's
    LEETCODE_NO_SANITIZE void pull(int i) {
        unsigned long long *p = &bits[(size_t)i * words], *l = &bits[(size_t)2 * i * words], *r = l + words;
        for (int w = 0; w < words; w++) p[w] = l[w] | r[w];
    }

    // every value under seg node i becomes the one with bit b
    LEETCODE_NO_SANITIZE void apply(int i, int b) {
        unsigned long long* p = &bits[(size_t)i * words];
        for (int w = 0; w < words; w++) p[w] = 0;
        p[b >> 6] = 1ULL << (b & 63);
        tag[i] = b;
    }

    // hands every assign waiting above leaf p down to the two children, top first
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int s = 31 - __builtin_clz(p); s > 0; s--) {
            int i = p >> s, b = tag[i];
            if (b >= 0) {
                apply(2 * i, b), apply(2 * i + 1, b);
                tag[i] = -1;
            }
        }
    }

    // recomputes the seg nodes above leaf p (one with an assign waiting is right as it is)
    LEETCODE_NO_SANITIZE void pullAbove(int p) {
        for (p >>= 1; p > 0; p >>= 1)
            if (tag[p] < 0) pull(p);
    }

    // the bit of value x: a new one the first time x appears (throws length_error once distinctCap values have one)
    int idOf(T x) {
        auto it = ids.find(x);
        if (it != ids.end()) return it->second;
        if ((int)ids.size() >= cap)
            throw length_error("Tree: more than distinctCap = " + to_string(cap) +
                               " distinct values (pass a bigger distinctCap)");
        int b = (int)ids.size();
        ids.emplace(x, b);
        values[b] = x;
        return b;
    }

    // the values at positions l..r all become x (nothing for an empty stretch, l > r)
    void assignRange(int l, int r, T x) {
        if (l > r) return;
        int b = idOf(x);
        l += n, r += n;
        push(l), push(r);
        for (int i = l, j = r + 1; i < j; i >>= 1, j >>= 1) {
            if (i & 1) apply(i++, b);
            if (j & 1) apply(--j, b);
        }
        pullAbove(l), pullAbove(r);
    }

    // the bit of the value at position p: the topmost assign still waiting above its leaf, else the leaf's own
    LEETCODE_NO_SANITIZE int bitAt(int p) const {
        p += n;
        for (int s = 31 - __builtin_clz(p); s > 0; s--)
            if (tag[p >> s] >= 0) return tag[p >> s];
        return tag[p];
    }

    // ORs the bitsets of the values at positions l..r into acc (nothing for an empty stretch, l > r)
    LEETCODE_NO_SANITIZE void orInto(int l, int r) {
        if (l > r) return;
        l += n, r += n;
        push(l), push(r);
        unsigned long long* out = &acc[0];
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) {
                const unsigned long long* p = &bits[(size_t)l++ * words];
                for (int w = 0; w < words; w++) out[w] |= p[w];
            }
            if (r & 1) {
                const unsigned long long* p = &bits[(size_t)--r * words];
                for (int w = 0; w < words; w++) out[w] |= p[w];
            }
        }
    }

    // how many bits acc has set, emptying it for the next query
    LEETCODE_NO_SANITIZE int takeCount() {
        int count = 0;
        for (int w = 0; w < words; w++) count += __builtin_popcountll(acc[w]), acc[w] = 0;
        return count;
    }

    // the path a..b as stretches of positions ls[i]..rs[i], one for each chain piece; returns how many there are
    LEETCODE_NO_SANITIZE int pieces(int a, int b, int* ls, int* rs) const {
        int m = 0;
        while (head[a] != head[b]) {
            if (dep[head[a]] < dep[head[b]]) {
                int t = a;
                a = b, b = t;
            }
            ls[m] = pos[head[a]], rs[m++] = pos[a];
            a = par[head[a]];
        }
        int l = pos[a], r = pos[b];
        if (l > r) {
            int t = l;
            l = r, r = t;
        }
        if (l < r) ls[m] = l + 1, rs[m++] = r;  // (the lca's own position is the edge above it)
        return m;
    }

    // how many distinct edge weights are on the path a..b
    LEETCODE_NO_SANITIZE int pathCount(int a, int b) {
        int ls[64], rs[64], m = pieces(a, b, ls, rs);
        for (int i = 0; i < m; i++) orInto(ls[i], rs[i]);
        return takeCount();
    }

    // the lower end of the edge a - b, the node its weight is kept under (a and b in either order)
    LEETCODE_NO_SANITIZE int edgeAt(const char* name, int a, int b) const {
        if (a < lo || a > hi || b < lo || b > hi) bad(name);
        if (par[a] == b) return a;
        if (par[b] == a) return b;
        throw out_of_range(string(name) + ": needs an edge between a and b");
    }

    // O(log n) -- weight(a - b); a and b are the edge's two ends, in either order
    LEETCODE_NO_SANITIZE T edgeGet(int a, int b) const {
        int p = pos[edgeAt("edgeGet", a, b)];
        return values[bitAt(p)];
    }

    // O(log n * D/64) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    void edgeAssign(int a, int b, T w) {
        int p = pos[edgeAt("edgeAssign", a, b)];
        assignRange(p, p, w);
    }

    // O(log n * D/64) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    void edgeAdd(int a, int b, T w) {
        int p = pos[edgeAt("edgeAdd", a, b)];
        assignRange(p, p, values[bitAt(p)] + w);
    }

    // O(log n * D/64) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    void edgeChmax(int a, int b, T w) {
        int p = pos[edgeAt("edgeChmax", a, b)];
        if (w > values[bitAt(p)]) assignRange(p, p, w);
    }

    // O(log n * D/64) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    void edgeChmin(int a, int b, T w) {
        int p = pos[edgeAt("edgeChmin", a, b)];
        if (w < values[bitAt(p)]) assignRange(p, p, w);
    }

    // O(log^2 n * D/64) -- weight = w for every edge on the path a..b
    void edgePathAssign(int a, int b, T w) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathAssign");
        int ls[64], rs[64], m = pieces(a, b, ls, rs);
        for (int i = 0; i < m; i++) assignRange(ls[i], rs[i], w);
    }

    // O(log^2 n * D/64) -- number of distinct edge weights on the path a..b; 0 when a == b (no edges)
    LEETCODE_NO_SANITIZE int edgePathCountDistinct(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathCountDistinct");
        return pathCount(a, b);
    }

    // O(log^2 n * D/64) -- are all the edge weights on the path a..b distinct?; True when a == b (no edges)
    LEETCODE_NO_SANITIZE bool edgePathAllDistinct(int a, int b) {
        if (a < lo || a > hi || b < lo || b > hi) bad("edgePathAllDistinct");
        return pathCount(a, b) == distOf(a, b);
    }

    // O(log n * D/64) -- weight = w for every edge in node's subtree
    void edgeSubtreeAssign(int node, T w) {
        if (node < lo || node > hi) bad("edgeSubtreeAssign");
        // the edges below node: the positions after its own (none for a leaf: an empty stretch)
        assignRange(pos[node] + 1, pos[node] + sz[node] - 1, w);
    }

    // O(log n * D/64) -- number of distinct edge weights in node's subtree; 0 when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE int edgeSubtreeCountDistinct(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeCountDistinct");
        // the edges below node: the positions after its own (none for a leaf: an empty stretch)
        orInto(pos[node] + 1, pos[node] + sz[node] - 1);
        return takeCount();
    }

    // O(log n * D/64) -- are all the edge weights in node's subtree distinct?; True when node is a leaf (no edges)
    LEETCODE_NO_SANITIZE bool edgeSubtreeAllDistinct(int node) {
        if (node < lo || node > hi) bad("edgeSubtreeAllDistinct");
        // the edges below node: the positions after its own (none for a leaf: an empty stretch)
        orInto(pos[node] + 1, pos[node] + sz[node] - 1);
        int many = takeCount();
        return many == sz[node] - 1;
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
