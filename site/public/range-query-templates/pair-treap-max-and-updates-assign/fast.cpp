// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pair-treap-max-and-updates-assign/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andAll append appendLeft cut getAll insertAt insertCopiesAt leftmostGtX leftmostGteX maxAll merge paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAndQuery rangeAssign rangeMax rangeRotateLeft rangeRotateRight rangeTwinSpin rightmostGtX rightmostGteX size split trisect
// @data-structure-type: pair-treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   cut: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: K+log(N) expected
//   leftmostGtX: log(N) expected
//   leftmostGteX: log(N) expected
//   merge: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeAndQuery: log(N) expected
//   rangeAssign: log(N) expected
//   rangeMax: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeTwinSpin: log(N) expected
//   rightmostGtX: log(N) expected
//   rightmostGteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   size: 1
//   pop: log(N) expected
//   popLeft: log(N) expected
//   maxAll: log(N) expected
//   andAll: 1
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] mx[1*N] an[1*N]
//   tags: asg[1*N] hasAsg[1*N]
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); two treaps per array (even / odd positions); every PairSwapTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

// Implicit treap pair: an array you can insert into anywhere, swap adjacent pairs in a range (rangeTwinSpin: a[l] <->
// a[l + 1], a[l + 2] <-> a[l + 3], ...), rotate, cut pieces out of (that is how to erase) and paste them back in
// O(logN) expected each, with rangeAssign. The values at even positions a[0], a[2], ... are one treap (lane E) and
// the odd ones another (lane O), in one node pool; a range [l, r] is a slice of each, and each node keeps its max,
// its AND over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT
// array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this node, not yet to its
// children".
// T: int, long long, ...
// FAST MODE drawbacks compared with template.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
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
struct PairSwapTreap {
    // one node pool shared by every PairSwapTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        T val = T(0);
        T mx = T(0);
        T an = ~T(0);
        T asg = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
        char hasAsg = 0;
    };
    static inline HotVector<Node> nd{Node{}};  // node 0 = the empty tree
    int rE = 0, rO = 0;  // lane E: a[0], a[2], ...; lane O: a[1], a[3], ...

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit PairSwapTreap(const vector<T>& arr = {}) {
        vector<T> ev, od;
        for (size_t i = 0; i < arr.size(); i++) (i % 2 ? od : ev).push_back(arr[i]);
        rE = build(ev), rO = build(od);
    }

    PairSwapTreap makeEmpty() const { return PairSwapTreap(); }  // (a new, empty one)

    LEETCODE_NO_SANITIZE static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(1) -- the current length of the array
    LEETCODE_NO_SANITIZE int size() const { return nd[rE].sz + nd[rO].sz; }

    // O(logN) expected -- append v to the end
    LEETCODE_NO_SANITIZE void append(T v) { tie(rE, rO) = pmerge(rE, rO, newNode(v), 0); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    LEETCODE_NO_SANITIZE void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[l..r] and return it as a PairSwapTreap of its own (indices from 0); needs
    // 0 <= l <= r < size(), else throws out_of_range
    PairSwapTreap cut(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("cut: needs 0 <= l <= r < size()");
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        tie(rE, rO) = pmerge(ae, ao, ce, co);
        PairSwapTreap piece = makeEmpty();
        piece.rE = be, piece.rO = bo;
        return piece;
    }

    // O(N) -- the whole current array, every pending tag applied on the way
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        vector<T> ev = inorder(rE), od = inorder(rO), out(ev.size() + od.size());
        for (size_t i = 0; i < ev.size(); i++) out[2 * i] = ev[i];
        for (size_t i = 0; i < od.size(); i++) out[2 * i + 1] = od[i];
        return out;
    }

    // O(logN) expected -- insert v so it becomes a[i]; needs 0 <= i <= size(), else throws out_of_range (i = size()
    // appends)
    LEETCODE_NO_SANITIZE void insertAt(int i, T v) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, newNode(v), 0);
        tie(rE, rO) = pmerge(e, o, ce, co);
    }

    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    // 0 <= i <= size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void insertCopiesAt(int i, T v, long long k) {
        if (i < 0 || i > size()) throw out_of_range("insertCopiesAt: needs 0 <= i <= size()");
        if (k <= 0) return;
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, build(vector<T>((k + 1) / 2, v)), build(vector<T>(k / 2, v)));
        tie(rE, rO) = pmerge(e, o, ce, co);
    }

    // O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (each lane's walk pruned by the subtree max);
    // needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGtX: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        int i = laneLeftmostGtX(be, x), j = laneLeftmostGtX(bo, x);
        release(mark);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return i < 0 ? j : j < 0 ? i : min(i, j);
    }

    // O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1 (each lane's walk pruned by the subtree max);
    // needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGteX: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        int i = laneLeftmostGteX(be, x), j = laneLeftmostGteX(bo, x);
        release(mark);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return i < 0 ? j : j < 0 ? i : min(i, j);
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    LEETCODE_NO_SANITIZE void merge(PairSwapTreap& other) {
        tie(rE, rO) = pmerge(rE, rO, other.rE, other.rO);
        other.rE = other.rO = 0;
    }

    // O(logN) expected -- insert all of other (any PairSwapTreap, e.g. a cut piece) so it starts at a[i] (needs
    // 0 <= i <= size(), else throws out_of_range); other is left empty
    LEETCODE_NO_SANITIZE void paste(int i, PairSwapTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, other.rE, other.rO);
        tie(rE, rO) = pmerge(e, o, ce, co);
        other.rE = other.rO = 0;
    }

    // O(logN) expected -- a[i] += v; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAdd: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = nd[t].val + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmax: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = max(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmin: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = min(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return nd[locate(i)].val;
    }

    // O(logN) expected -- a[l] & ... & a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeAndQuery(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        T res = nd[be].an & nd[bo].an;
        release(mark);
        return res;
    }

    // O(logN) expected -- a[i] = v for i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, T v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        auto ln = lanes(l, r);
        upd(ln[0][0], ln[0][1], ln[0][2], [&](int x, int off) { applyAssign(x, v); (void)off; },
            [&](T w, int off) { (void)off; return v; });
        upd(ln[1][0], ln[1][1], ln[1][2], [&](int x, int off) { applyAssign(x, v); (void)off; },
            [&](T w, int off) { (void)off; return v; });
    }

    // O(logN) expected -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMax: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        T res = bo ? max(nd[be].mx, nd[bo].mx) : nd[be].mx;
        release(mark);
        return res;
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
    // taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateLeft(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateLeft: needs 0 <= l <= r < size()");
        int len = r - l + 1;
        k = ((k % len) + len) % len;
        if (!k) return;
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        auto [xe, xo, ye, yo] = psplit(be, bo, (int)k);
        auto [e, o] = pmerge(ye, yo, xe, xo);
        join(ae, ao, e, o, ce, co);
    }

    // O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    // (negative shifts left); needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateRight(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -k);
    }

    // O(logN) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (odd length: a[r] stays):
    // the pairs' two lanes trade places; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeTwinSpin(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeTwinSpin: needs 0 <= l <= r < size()");
        int k = (r - l + 1) / 2;
        if (!k) return;
        auto [ae, ao, be, bo, ce, co] = parts(l, l + 2 * k - 1);
        join(ae, ao, bo, be, ce, co);
    }

    // O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (each lane's walk pruned by the subtree max);
    // needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGtX: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        int i = laneRightmostGtX(be, x), j = laneRightmostGtX(bo, x);
        release(mark);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return max(i, j);
    }

    // O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1 (each lane's walk pruned by the subtree max);
    // needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGteX: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        int i = laneRightmostGteX(be, x), j = laneRightmostGteX(bo, x);
        release(mark);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return max(i, j);
    }

    // O(logN) expected -- (a[0..k-1], a[k..]) as two PairSwapTreaps of their own; this one is left empty; needs
    // 0 <= k <= size(), else throws out_of_range
    LEETCODE_NO_SANITIZE pair<PairSwapTreap, PairSwapTreap> split(int k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        PairSwapTreap left = makeEmpty(), right = makeEmpty();
        auto [le, lo, re, ro] = psplit(rE, rO, k);
        left.rE = le, left.rO = lo, right.rE = re, right.rO = ro;
        rE = rO = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PairSwapTreaps of their own; this one is left
    // empty; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE tuple<PairSwapTreap, PairSwapTreap, PairSwapTreap> trisect(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        PairSwapTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        left.rE = ae, left.rO = ao, mid.rE = be, mid.rO = bo, right.rE = ce, right.rO = co;
        rE = rO = 0;
        return {left, mid, right};
    }

    // O(log(N) expected) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T pop() {
        auto n = size();
        if (n < 1) throw out_of_range("pop: needs size() >= 1");
        T v = pointGet(n - 1);
        cut(n - 1, n - 1);
        return v;
    }

    // O(log(N) expected) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        T v = pointGet(0);
        cut(0, 0);
        return v;
    }

    // O(log(N) expected) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE auto maxAll() {
        if (size() < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, size() - 1);
    }

    // O(1) -- AND of the whole array a[0..n-1] (read off the root); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto andAll() {
        if (size() < 1) throw out_of_range("andAll: needs n >= 1");
        return nd[rE].an & nd[rO].an;
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE int newNode(T v) {
        Node n;
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.mx = v, n.an = v, n.asg = T(0), n.hasAsg = 0;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    // a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    LEETCODE_NO_SANITIZE int build(const vector<T>& vals) {
        vector<int> stk, order, todo;
        for (const T& v : vals) {
            int x = newNode(v), last = 0;
            while (!stk.empty() && nd[stk.back()].pri < nd[x].pri) last = stk.back(), stk.pop_back();
            nd[x].L = last;
            if (!stk.empty()) nd[stk.back()].R = x;
            stk.push_back(x);
        }
        int rt = stk.empty() ? 0 : stk[0];
        if (rt) todo.push_back(rt);
        while (!todo.empty()) {
            int x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (nd[x].L) todo.push_back(nd[x].L);
            if (nd[x].R) todo.push_back(nd[x].R);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
        return rt;
    }

    LEETCODE_NO_SANITIZE void pull(int x) {  // recompute x from its children
        int l = nd[x].L, r = nd[x].R;
        nd[x].sz = nd[l].sz + nd[r].sz + 1;
        T v = nd[x].val;
        nd[x].mx = v;
        if (l && nd[l].mx > nd[x].mx) nd[x].mx = nd[l].mx;
        if (r && nd[r].mx > nd[x].mx) nd[x].mx = nd[r].mx;
        nd[x].an = nd[l].an & v & nd[r].an;  // (node 0: the AND of nothing, ~0)
    }

    LEETCODE_NO_SANITIZE void applyAssign(int x, T v) {  // every value of x's subtree becomes v
        if (!x) return;
        nd[x].val = v;
        nd[x].mx = v;
        nd[x].an = v;
        nd[x].asg = v, nd[x].hasAsg = 1;
    }

    LEETCODE_NO_SANITIZE void push(int x) {  // hand x's pending tags to its children
        if (nd[x].hasAsg) applyAssign(nd[x].L, nd[x].asg), applyAssign(nd[x].R, nd[x].asg), nd[x].hasAsg = 0;
    }

    LEETCODE_NO_SANITIZE void split(int t, int k, int& a, int& b) {  // a = first k of t, b = the rest
        if (!t) { a = b = 0; return; }
        push(t);
        if (nd[nd[t].L].sz >= k) split(nd[t].L, k, a, nd[t].L), b = t;
        else split(nd[t].R, k - nd[nd[t].L].sz - 1, nd[t].R, b), a = t;
        pull(t);
    }

    LEETCODE_NO_SANITIZE int merge(int a, int b) {  // a's elements, then b's
        if (!a || !b) return a | b;
        if (nd[a].pri > nd[b].pri) {
            push(a);
            nd[a].R = merge(nd[a].R, b);
            pull(a);
            return a;
        }
        push(b);
        nd[b].L = merge(a, nd[b].L);
        pull(b);
        return b;
    }

    // ---- the lanes: an array is a pair (E, O) of treaps, E holding its values at even positions, O the odd ones ----

    LEETCODE_NO_SANITIZE array<int, 4> psplit(int e, int o, int k) {  // lanes of (the first k values, the rest)
        int e1, e2, o1, o2;
        split(e, (k + 1) / 2, e1, e2);
        split(o, k / 2, o1, o2);
        if (k % 2) return {e1, o1, o2, e2};  // (an odd k: the rest starts on an odd position)
        return {e1, o1, e2, o2};
    }

    LEETCODE_NO_SANITIZE pair<int, int> pmerge(int e1, int o1, int e2, int o2) {
        // lanes of (the first array, then the second)
        if ((nd[e1].sz + nd[o1].sz) % 2) swap(e2, o2);  // (after an odd length: its even positions are odd ones)
        return {merge(e1, e2), merge(o1, o2)};
    }

    LEETCODE_NO_SANITIZE array<int, 6> parts(int l, int r) {  // lanes of a[..l-1], a[l..r], a[r+1..]
        auto [ae, ao, xe, xo] = psplit(rE, rO, l);
        auto [be, bo, ce, co] = psplit(xe, xo, r - l + 1);
        return {ae, ao, be, bo, ce, co};
    }

    LEETCODE_NO_SANITIZE void join(int ae, int ao, int be, int bo, int ce, int co) {
        auto [e, o] = pmerge(ae, ao, be, bo);
        tie(rE, rO) = pmerge(e, o, ce, co);
    }

    LEETCODE_NO_SANITIZE int locate(int i, vector<int>* path = nullptr) {
        // the node holding a[i], every tag on the way pushed
        int t = i % 2 ? rO : rE, k = i / 2;
        while (true) {
            push(t);
            int ls = nd[nd[t].L].sz;
            if (k == ls) return t;
            if (path) path->push_back(t);
            if (k < ls) t = nd[t].L;
            else k -= ls + 1, t = nd[t].R;
        }
    }

    LEETCODE_NO_SANITIZE vector<T> inorder(int t) {  // the values under t in order, every tag on the way pushed
        vector<T> out;
        vector<int> st;
        while (!st.empty() || t) {
            while (t) push(t), st.push_back(t), t = nd[t].L;
            t = st.back(), st.pop_back();
            out.push_back(nd[t].val);
            t = nd[t].R;
        }
        return out;
    }

    LEETCODE_NO_SANITIZE int laneLeftmostGtX(int t, T x) {  // the first k with lane value k > x under t, or -1
        if (!t || !(nd[t].mx > x)) return -1;
        int i = 0;
        while (true) {
            push(t);
            if (nd[t].L && nd[nd[t].L].mx > x) t = nd[t].L;
            else if (nd[t].val > x) return i + nd[nd[t].L].sz;
            else i += nd[nd[t].L].sz + 1, t = nd[t].R;
        }
    }

    LEETCODE_NO_SANITIZE int laneLeftmostGteX(int t, T x) {  // the first k with lane value k >= x under t, or -1
        if (!t || !(nd[t].mx >= x)) return -1;
        int i = 0;
        while (true) {
            push(t);
            if (nd[t].L && nd[nd[t].L].mx >= x) t = nd[t].L;
            else if (nd[t].val >= x) return i + nd[nd[t].L].sz;
            else i += nd[nd[t].L].sz + 1, t = nd[t].R;
        }
    }

    LEETCODE_NO_SANITIZE int laneRightmostGtX(int t, T x) {  // the last k with lane value k > x under t, or -1
        if (!t || !(nd[t].mx > x)) return -1;
        int i = 0;
        while (true) {
            push(t);
            if (nd[t].R && nd[nd[t].R].mx > x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
            else if (nd[t].val > x) return i + nd[nd[t].L].sz;
            else t = nd[t].L;
        }
    }

    LEETCODE_NO_SANITIZE int laneRightmostGteX(int t, T x) {  // the last k with lane value k >= x under t, or -1
        if (!t || !(nd[t].mx >= x)) return -1;
        int i = 0;
        while (true) {
            push(t);
            if (nd[t].R && nd[nd[t].R].mx >= x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
            else if (nd[t].val >= x) return i + nd[nd[t].L].sz;
            else t = nd[t].L;
        }
    }

    // ---- queries, searches and range updates walk the pieces of [l, r] instead of cutting it out ----



    // a node over a[l..r] of t's subtree: t itself if that is all of it, else temporaries made only where two parts
    // meet (pending tags on the way pushed down)
    LEETCODE_NO_SANITIZE int rq(int t, int l, int r) {
        if (!t || r < 0 || l >= nd[t].sz) return 0;
        if (l <= 0 && nd[t].sz - 1 <= r) return t;
        push(t);
        int ls = nd[nd[t].L].sz;
        if (r < ls) return rq(nd[t].L, l, r);
        if (l > ls) return rq(nd[t].R, l - ls - 1, r - ls - 1);
        int a = rq(nd[t].L, l, r), b = rq(nd[t].R, l - ls - 1, r - ls - 1);
        int y = clone(t);
        nd[y].L = a, nd[y].R = b;
        pull(y);
        return y;
    }

    LEETCODE_NO_SANITIZE int clone(int x) {  // a temporary copy of node x (sharing its children), dropped by release
        Node n;
        n.val = nd[x].val, n.pri = nd[x].pri, n.L = nd[x].L, n.R = nd[x].R, n.sz = nd[x].sz, n.mx = nd[x].mx,
        n.an = nd[x].an, n.asg = nd[x].asg, n.hasAsg = nd[x].hasAsg;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    LEETCODE_NO_SANITIZE void release(size_t mark) {
        // drop every node made after mark (temporaries: no tree points to them)
        nd.resize(mark);
        nd.resize(mark);
        nd.resize(mark);
        nd.resize(mark);
        nd.resize(mark);
        nd.resize(mark);
        nd.resize(mark);
        nd.resize(mark);
        nd.resize(mark);
    }

    // the update on a[l..r] of t's subtree, in place: f(x, off) on a node x covered whole, h(w, off) the new value of a
    // lone value w (off: the distance from l). Only the nodes on the range's two boundary paths are recomputed, nothing
    // is cut out
    template <class F, class H>
    LEETCODE_NO_SANITIZE void upd(int t, int l, int r, const F& f, const H& h) {
        if (!t || r < 0 || l >= nd[t].sz) return;
        if (l <= 0 && nd[t].sz - 1 <= r) {
            f(t, -l);
            return;
        }
        push(t);
        int ls = nd[nd[t].L].sz;
        upd(nd[t].L, l, r, f, h);
        upd(nd[t].R, l - ls - 1, r - ls - 1, f, h);
        if (l <= ls && ls <= r) nd[t].val = h(nd[t].val, ls - l);
        pull(t);
    }

    // {lane, first k, last k} holding a[l], a[l + 2], ..., then the one holding a[l + 1], a[l + 3], ...
    LEETCODE_NO_SANITIZE array<array<int, 3>, 2> lanes(int l, int r) {
        int roots[2] = {rE, rO};
        array<int, 3> e = {roots[l % 2], l / 2, (r - (r - l) % 2) / 2};
        array<int, 3> o = l < r ? array<int,
            3>{roots[(l + 1) % 2], (l + 1) / 2, (r - (r - l - 1) % 2) / 2} : array<int, 3>{0, 0, -1};
        return {e, o};
    }

    // temporary nodes over the two lane slices of a[l..r]; mark = the pool size release() goes back to
    LEETCODE_NO_SANITIZE pair<int, int> laneNodes(int l, int r, size_t& mark) {
        auto ln = lanes(l, r);
        mark = nd.size();
        int be = rq(ln[0][0], ln[0][1], ln[0][2]);
        int bo = rq(ln[1][0], ln[1][1], ln[1][2]);
        return {be, bo};
    }
};

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     PairSwapTreap<int> t({1, 2, 3, 4, 5});
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
