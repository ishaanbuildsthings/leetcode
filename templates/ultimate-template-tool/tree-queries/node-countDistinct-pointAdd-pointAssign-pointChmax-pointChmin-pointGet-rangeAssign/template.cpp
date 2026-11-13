// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/node-countDistinct-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/template.cpp
// The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countDistinct-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/fast.cpp
// @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathAssign nodeSubtreeAssign nodeSubtreeCountDistinct parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
// @data-structure-type: BIT
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
//   nodeAdd: log^2(N) amortized
//   nodeAssign: log^2(N) amortized
//   nodeChmax: log^2(N) amortized
//   nodeChmin: log^2(N) amortized
//   nodeGet: log(N)
//   nodePathAssign: log^3(N) amortized
//   nodeSubtreeAssign: log^2(N) amortized
//   nodeSubtreeCountDistinct: log^2(N)
//   parent: 1
//   parentRootedAt: log(N)
//   pathIntersection: log(N)
//   pathNodes: K+log(N)
//   subtreeSize: 1
//   subtreeSizeRootedAt: log(N)
//   unweightedDist: log(N)
//   unweightedDistBetweenPaths: log(N)
//   unweightedDistToPath: log(N)
//   build: N*log^2(N)
// @memory:
//   layout: none
//   node: sets[1*N*log(N)] last[1*N]
//   tags: none
//   other: nxt[1*N] end[1*N] val[1*N] starts[1*N] chains[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
//   note: the array is kept as runs of equal values; Fenwick node j keeps an ordered set of the nxt values in its lowbit(j) positions, at most N*log(N)/2 keys in all (fewer once assigns merge runs); those are balanced-tree / bucket entries, several times heavier than a plain int
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// FAST MODE (this is the only C++ version): sanitizers are skipped inside this template, so a bad access in it goes
// unreported. To turn that off (say, when debugging with sanitizers), put this line above the template:
//   #define LEETCODE_NO_SANITIZE
// Without sanitizers (Codeforces, a plain -O2 build) it changes nothing. It needs GCC or Clang.

// Range count distinct with range assign, online. All indices 0-based, ranges inclusive [l, r].
// The array is kept as runs: run s covers s..end[s], all holding val[s] (at first every element is its own run; an
// assign makes l..r one run). starts holds every run start, chains[v] the starts of the runs holding v.
// Only a run's last position e has a point: nxt[e] = the start of the next run holding the same value, else n (every
// other position has nxt = -1: its next equal value is right after it). A value is counted once in a[l..r] at its last
// occurrence there, so countDistinct(l, r) = [the run holding r continues past r] + #{run ends e in [l, r] : nxt[e] >
// r}.
// Points with nxt == n always count, so a plain Fenwick tree tracks them; every other nxt is a distinct run start < n,
// kept in a Fenwick tree of order-statistics sets (GCC pb_ds): node j holds the nxt values of the lowbit(j) positions
// it covers, so a prefix count of "nxt > r" visits log N nodes with one order_of_key each.
// An assign removes the runs it covers (each one was made by an earlier op, so that is O(1) amortized of them) and
// changes O(1) points per run added or removed. No two positions may share an nxt value < n at any moment (the C++
// version keeps them in sets, not multisets), so a point is always cleared before its value is handed on.
// T: any type usable as a std::map key.
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

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
struct DynamicDistinctAssign {
    using OrderedSet = __gnu_pbds::tree<int, __gnu_pbds::null_type, less<int>, __gnu_pbds::rb_tree_tag,
        __gnu_pbds::tree_order_statistics_node_update>;
    int n;
    // nxt[e] at run ends, -1 elsewhere; last: Fenwick tree counting positions with nxt == n
    HotVector<int> nxt, last;
    HotVector<OrderedSet> sets;  // 1-indexed Fenwick tree of nxt values in [0, n)
    HotVector<int> end;          // end[s] = last index of the run starting at s
    HotVector<T> val;            // val[s] = the value of the run starting at s
    set<int> starts;          // every run start
    map<T, set<int>> chains;  // value -> starts of the runs holding it

    // O(N log^2 N)
    explicit DynamicDistinctAssign(const vector<T>& arr)
        : n((int)arr.size()), nxt(n, n), last(n + 1), sets(n + 1), end(n), val(arr) {
        map<T, int> prev;
        for (int i = 0; i < n; i++) {
            auto it = prev.find(arr[i]);
            if (it != prev.end()) nxt[it->second] = i;
            prev[arr[i]] = i;
            set<int>& c = chains[arr[i]];
            c.emplace_hint(c.end(), i);
            starts.emplace_hint(starts.end(), i);
            end[i] = i;
        }
        for (int i = 1; i <= n; i++) {
            last[i] += nxt[i - 1] == n;
            int j = i + (i & -i);
            if (j <= n) last[j] += last[i];
            for (int k = i - (i & -i); k < i; k++)
                if (nxt[k] < n) sets[i].insert(nxt[k]);
        }
    }

    LEETCODE_NO_SANITIZE void lastAdd(int i, int d) {
        for (i++; i <= n; i += i & -i) last[i] += d;
    }

    // how many i in [0, x] have nxt[i] > r (x = -1 gives 0)
    LEETCODE_NO_SANITIZE int countPast(int x, int r) const {
        int res = 0;
        for (int j = x + 1; j > 0; j &= j - 1) res += last[j] + int(sets[j].size() - sets[j].order_of_key(r + 1));
        return res;
    }

    // O(log^2 N) -- nxt[i] = v (-1: no point)
    LEETCODE_NO_SANITIZE void setNxt(int i, int v) {
        int old = nxt[i];
        if (old == v) return;
        if (old == n) lastAdd(i, -1);
        else if (old >= 0) for (int j = i + 1; j <= n; j += j & -j) sets[j].erase(old);
        if (v == n) lastAdd(i, 1);
        else if (v >= 0) for (int j = i + 1; j <= n; j += j & -j) sets[j].insert(v);
        nxt[i] = v;
    }

    // O(logN) -- the start of the run holding i
    LEETCODE_NO_SANITIZE int runOf(int i) const { return *prev(starts.upper_bound(i)); }

    // O(log^2 N) -- make a run start at x (0 < x < n): the left part's new last position x - 1 points at x
    LEETCODE_NO_SANITIZE void split(int x) {
        int p = runOf(x);
        if (p == x) return;
        end[x] = end[p], val[x] = val[p], end[p] = x - 1;
        starts.insert(x);
        chains.find(val[x])->second.insert(x);
        setNxt(x - 1, x);
    }

    // O(log^2 N) -- # of distinct values in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int countDistinct(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countDistinct: needs 0 <= l <= r < n");
        int tail = end[runOf(r)] > r;  // a[r]'s run goes on past r: count it here
        return tail + countPast(r, r) - countPast(l - 1, r);
    }

    // O(log^2 N) amortized -- a[i] = v for every i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, const T& v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        split(l);
        if (r + 1 < n) split(r + 1);
        for (auto it = starts.lower_bound(l); it != starts.end() && *it <= r;) {  // drop every run inside l..r
            int s = *it;
            auto cit = chains.find(val[s]);
            set<int>& c = cit->second;
            auto jt = c.find(s);
            int q = jt == c.begin() ? -1 : *prev(jt);
            auto nx = next(jt);
            int after = nx == c.end() ? n : *nx;
            setNxt(end[s], -1);  // clear s's point first, so the value it held is free for q
            c.erase(jt);
            if (c.empty()) chains.erase(cit);
            if (q != -1) setNxt(end[q], after);
            if (s != l) it = starts.erase(it);
            else ++it;
        }
        end[l] = r, val[l] = v;
        set<int>& c = chains[v];
        auto jt = c.insert(l).first;
        auto nx = next(jt);
        if (jt != c.begin()) setNxt(end[*prev(jt)], l);  // move q off `after` first, then hand `after` to the new run
        setNxt(r, nx == c.end() ? n : *nx);
    }

    // O(log^2 N) amortized -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        rangeAssign(i, i, v);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return val[runOf(i)];
    }

    // O(N) -- the whole array (a copy)
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out;
        out.reserve(n);
        for (int s : starts) out.insert(out.end(), end[s] - s + 1, val[s]);
        return out;
    }

    // O(log^2 N) amortized -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, const T& delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAssign(i, i, pointGet(i) + delta);
    }

    // O(log^2 N) amortized -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) rangeAssign(i, i, v);
    }

    // O(log^2 N) amortized -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, const T& v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) rangeAssign(i, i, v);
    }
};

// Tree tree(edges, root, vals);
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
//
//   Tree<long long> tree({{0, 1}, {1, 2}}, 0, {10, 20, 30});       // nodes 0..2, rooted at 0
//   Tree<long long> tree({{1, 2}, {2, 3}}, 1, {0, 10, 20, 30});    // nodes 1..3, rooted at 1
//
// Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree throws
// out_of_range. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
//
// How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
// stretch of positions (pos[node] .. pos[node] + sz[node] - 1). The values sit in the range structure above
// (DynamicDistinctAssign) in position order: a subtree is one range of it, and a path a..b is O(log n) ranges, one per
// chain it crosses.
template <typename T>
struct Tree {
    int n, lo, hi, root;  // nodes are lo..hi
    // by node label: parent (-1 for the root), depth, subtree size, top of its chain, position
    HotVector<int> par, dep, sz, head, pos;
    HotVector<int> order;  // order[pos[v]] = v
    // depthPos[depthStart[d] .. depthStart[d + 1]) = the positions of the nodes at depth d, increasing
    HotVector<int> depthStart, depthPos;
    DynamicDistinctAssign<T> seg;  // the values, in position order

    // O(n * log^2 n) -- builds the layout and the range structure; throws invalid_argument when the edges are not one
    // tree on nodes 0..n-1 or 1..n, or vals has the wrong size
    template <typename E = int> Tree(const vector<vector<E>>& edges, int root, const vector<T>& vals)
        : seg(layout(edges, root, vals)) {}

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

    // O(log^2 n) -- val(node) = x
    LEETCODE_NO_SANITIZE void nodeAssign(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeAssign");
        seg.pointAssign(pos[node], x);
    }

    // O(log^2 n) -- val(node) += x
    LEETCODE_NO_SANITIZE void nodeAdd(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeAdd");
        seg.pointAdd(pos[node], x);
    }

    // O(log^2 n) -- val(node) = max(val, x)
    LEETCODE_NO_SANITIZE void nodeChmax(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeChmax");
        seg.pointChmax(pos[node], x);
    }

    // O(log^2 n) -- val(node) = min(val, x)
    LEETCODE_NO_SANITIZE void nodeChmin(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeChmin");
        seg.pointChmin(pos[node], x);
    }

    // O(log^3 n) -- val = x for every node on the path a..b
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

    // O(log^2 n) -- val = x for every node in node's subtree
    LEETCODE_NO_SANITIZE void nodeSubtreeAssign(int node, const T& x) {
        if (node < lo || node > hi) bad("nodeSubtreeAssign");
        int l = pos[node];
        seg.rangeAssign(l, l + sz[node] - 1, x);
    }

    // O(log^2 n) -- number of distinct node values in node's subtree
    LEETCODE_NO_SANITIZE auto nodeSubtreeCountDistinct(int node) {
        if (node < lo || node > hi) bad("nodeSubtreeCountDistinct");
        int l = pos[node];
        return seg.countDistinct(l, l + sz[node] - 1);
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
