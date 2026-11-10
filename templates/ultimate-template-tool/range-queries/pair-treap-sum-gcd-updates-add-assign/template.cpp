// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pair-treap-sum-gcd-updates-add-assign/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft cut gcdAll getAll insertAt insertCopiesAt merge paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAdd rangeAssign rangeGcd rangeRotateLeft rangeRotateRight rangeSum rangeTwinSpin size split sumAll trisect
// @data-structure-type: pair-treap
// @complexities:
//   append: log(N)*log(U) expected ?
//   appendLeft: log(N)*log(U) expected ?
//   cut: log(N)*log(U) expected ?
//   getAll: N
//   insertAt: log(N)*log(U) expected ?
//   insertCopiesAt: K+log(N)*log(U) expected ?
//   merge: log(N)*log(U) expected ?
//   paste: log(N)*log(U) expected ?
//   pointAdd: log(N)*log(U) expected ?
//   pointAssign: log(N)*log(U) expected ?
//   pointChmax: log(N)*log(U) expected ?
//   pointChmin: log(N)*log(U) expected ?
//   pointGet: log(N) expected
//   rangeAdd: log(N)*log(U) expected ?
//   rangeAssign: log(N)*log(U) expected ?
//   rangeGcd: log(N)*log(U) expected ?
//   rangeRotateLeft: log(N)*log(U) expected ?
//   rangeRotateRight: log(N)*log(U) expected ?
//   rangeSum: log(N)*log(U) expected ?
//   rangeTwinSpin: log(N)*log(U) expected ?
//   split: log(N)*log(U) expected ?
//   trisect: log(N)*log(U) expected ?
//   size: 1
//   pop: log(N)*log(U) expected ?
//   popLeft: log(N)*log(U) expected ?
//   sumAll: 1
//   gcdAll: log(N)*log(U) expected ?
//   build: N*log(U) ?
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] g[1*N] fv[1*N] lv[1*N]
//   tags: asg[1*N] hasAsg[1*N] add[1*N]
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); two treaps per array (even / odd positions); every PairSwapTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

// Implicit treap pair: an array you can insert into anywhere, swap adjacent pairs in a range (rangeTwinSpin: a[l] <->
// a[l + 1], a[l + 2] <-> a[l + 3], ...), rotate, cut pieces out of (that is how to erase) and paste them back in
// O(logN) expected each, with rangeAdd, rangeAssign. The values at even positions a[0], a[2], ... are one treap (lane
// E) and the odd ones another (lane O), in one node pool; a range [l, r] is a slice of each, and each node keeps its
// sum, its gcd over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in the
// CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this node, not yet to
// its children"; a pending assign comes before a pending add.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct PairSwapTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // one node pool shared by every PairSwapTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        S sm = 0;
        T val = T(0);
        T g = T(0);
        T fv = T(0);
        T lv = T(0);
        T asg = T(0);
        T add = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
        char hasAsg = 0;
    };
    static inline vector<Node> nd{Node{}};  // node 0 = the empty tree
    int rE = 0, rO = 0;  // lane E: a[0], a[2], ...; lane O: a[1], a[3], ...

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit PairSwapTreap(const vector<T>& arr = {}) {
        vector<T> ev, od;
        for (size_t i = 0; i < arr.size(); i++) (i % 2 ? od : ev).push_back(arr[i]);
        rE = build(ev), rO = build(od);
    }

    PairSwapTreap makeEmpty() const { return PairSwapTreap(); }  // (a new, empty one)

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(1) -- the current length of the array
    int size() const { return nd[rE].sz + nd[rO].sz; }

    // O(logN * logU) expected -- append v to the end
    void append(T v) { tie(rE, rO) = pmerge(rE, rO, newNode(v), 0); }

    // O(logN * logU) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN * logU) expected -- remove a[l..r] and return it as a PairSwapTreap of its own (indices from 0); needs
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
    vector<T> getAll() {
        vector<T> ev = inorder(rE), od = inorder(rO), out(ev.size() + od.size());
        for (size_t i = 0; i < ev.size(); i++) out[2 * i] = ev[i];
        for (size_t i = 0; i < od.size(); i++) out[2 * i + 1] = od[i];
        return out;
    }

    // O(logN * logU) expected -- insert v so it becomes a[i]; needs 0 <= i <= size(), else throws out_of_range (i =
    // size() appends)
    void insertAt(int i, T v) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, newNode(v), 0);
        tie(rE, rO) = pmerge(e, o, ce, co);
    }

    // O(k + logN * logU) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    // 0 <= i <= size(), else throws out_of_range
    void insertCopiesAt(int i, T v, long long k) {
        if (i < 0 || i > size()) throw out_of_range("insertCopiesAt: needs 0 <= i <= size()");
        if (k <= 0) return;
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, build(vector<T>((k + 1) / 2, v)), build(vector<T>(k / 2, v)));
        tie(rE, rO) = pmerge(e, o, ce, co);
    }

    // O(logN * logU) expected -- append all of other at the end; other is left empty
    void merge(PairSwapTreap& other) {
        tie(rE, rO) = pmerge(rE, rO, other.rE, other.rO);
        other.rE = other.rO = 0;
    }

    // O(logN * logU) expected -- insert all of other (any PairSwapTreap, e.g. a cut piece) so it starts at a[i]
    // (needs 0 <= i <= size(), else throws out_of_range); other is left empty
    void paste(int i, PairSwapTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, other.rE, other.rO);
        tie(rE, rO) = pmerge(e, o, ce, co);
        other.rE = other.rO = 0;
    }

    // O(logN * logU) expected -- a[i] += v; needs 0 <= i < size(), else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAdd: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = nd[t].val + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmax: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = max(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmin: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = min(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return nd[locate(i)].val;
    }

    // O(logN * logU) expected -- a[i] += v for i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeAdd(int l, int r, T v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAdd: needs 0 <= l <= r < size()");
        auto ln = lanes(l, r);
        upd(ln[0][0], ln[0][1], ln[0][2], [&](int x, int off) { applyAdd(x, v); (void)off; },
            [&](T w, int off) { (void)off; return T(w + v); });
        upd(ln[1][0], ln[1][1], ln[1][2], [&](int x, int off) { applyAdd(x, v); (void)off; },
            [&](T w, int off) { (void)off; return T(w + v); });
    }

    // O(logN * logU) expected -- a[i] = v for i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeAssign(int l, int r, T v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        auto ln = lanes(l, r);
        upd(ln[0][0], ln[0][1], ln[0][2], [&](int x, int off) { applyAssign(x, v); (void)off; },
            [&](T w, int off) { (void)off; return v; });
        upd(ln[1][0], ln[1][1], ln[1][2], [&](int x, int off) { applyAssign(x, v); (void)off; },
            [&](T w, int off) { (void)off; return v; });
    }

    // O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeGcd(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeGcd: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        T res = gcd(gcd(nd[be].fv, nd[be].g), nd[bo].g);
        if (bo) res = gcd(res, T(nd[bo].fv - nd[be].fv));
        release(mark);
        return res;
    }

    // O(logN * logU) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it
    // is taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateLeft(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateLeft: needs 0 <= l <= r < size()");
        int len = r - l + 1;
        k = ((k % len) + len) % len;
        if (!k) return;
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        auto [xe, xo, ye, yo] = psplit(be, bo, (int)k);
        auto [e, o] = pmerge(ye, yo, xe, xo);
        join(ae, ao, e, o, ce, co);
    }

    // O(logN * logU) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateRight(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -k);
    }

    // O(logN * logU) expected -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeSum: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        S res = nd[be].sm + nd[bo].sm;
        release(mark);
        return res;
    }

    // O(logN * logU) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (odd length: a[r]
    // stays): the pairs' two lanes trade places; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeTwinSpin(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeTwinSpin: needs 0 <= l <= r < size()");
        int k = (r - l + 1) / 2;
        if (!k) return;
        auto [ae, ao, be, bo, ce, co] = parts(l, l + 2 * k - 1);
        join(ae, ao, bo, be, ce, co);
    }

    // O(logN * logU) expected -- (a[0..k-1], a[k..]) as two PairSwapTreaps of their own; this one is left empty;
    // needs 0 <= k <= size(), else throws out_of_range
    pair<PairSwapTreap, PairSwapTreap> split(int k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        PairSwapTreap left = makeEmpty(), right = makeEmpty();
        auto [le, lo, re, ro] = psplit(rE, rO, k);
        left.rE = le, left.rO = lo, right.rE = re, right.rO = ro;
        rE = rO = 0;
        return {left, right};
    }

    // O(logN * logU) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PairSwapTreaps of their own; this one is
    // left empty; needs 0 <= l <= r < size(), else throws out_of_range
    tuple<PairSwapTreap, PairSwapTreap, PairSwapTreap> trisect(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        PairSwapTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        left.rE = ae, left.rO = ao, mid.rE = be, mid.rO = bo, right.rE = ce, right.rO = co;
        rE = rO = 0;
        return {left, mid, right};
    }

    // O(log(N)*log(U) expected ?) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    T pop() {
        auto n = size();
        if (n < 1) throw out_of_range("pop: needs size() >= 1");
        T v = pointGet(n - 1);
        cut(n - 1, n - 1);
        return v;
    }

    // O(log(N)*log(U) expected ?) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else
    // throws out_of_range
    T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        T v = pointGet(0);
        cut(0, 0);
        return v;
    }

    // O(1) -- sum of the whole array a[0..n-1] (read off the root); needs n >= 1, else throws out_of_range
    auto sumAll() {
        if (size() < 1) throw out_of_range("sumAll: needs n >= 1");
        return nd[rE].sm + nd[rO].sm;
    }

    // O(log(N)*log(U) expected ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else throws
    // out_of_range
    auto gcdAll() {
        if (size() < 1) throw out_of_range("gcdAll: needs n >= 1");
        return rangeGcd(0, size() - 1);
    }

    // ---- internals ----

    int newNode(T v) {
        Node n;
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.g = T(0), n.fv = v, n.lv = v,
        n.asg = T(0), n.hasAsg = 0, n.add = T(0);
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    // a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    int build(const vector<T>& vals) {
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

    void pull(int x) {  // recompute x from its children
        int l = nd[x].L, r = nd[x].R;
        nd[x].sz = nd[l].sz + nd[r].sz + 1;
        T v = nd[x].val;
        nd[x].sm = nd[l].sm + S(v) + nd[r].sm;
        T gg = gcd(nd[l].g, nd[r].g);
        if (l) gg = gcd(gg, T(v - nd[l].lv));
        if (r) gg = gcd(gg, T(nd[r].fv - v));
        nd[x].g = gg;
        nd[x].fv = l ? nd[l].fv : v;
        nd[x].lv = r ? nd[r].lv : v;
    }

    void applyAssign(int x, T v) {  // every value of x's subtree becomes v
        if (!x) return;
        int n = nd[x].sz;
        nd[x].val = v;
        nd[x].sm = S(v) * n;
        nd[x].g = T(0);
        nd[x].fv = nd[x].lv = v;
        nd[x].asg = v, nd[x].hasAsg = 1;
        nd[x].add = T(0);  // (an add pending below the assign is gone)
    }

    void applyAdd(int x, T v) {  // every value of x's subtree gains v
        if (!x) return;
        nd[x].val += v;
        nd[x].sm += S(v) * nd[x].sz;
        nd[x].fv += v, nd[x].lv += v;
        nd[x].add += v;
    }

    void push(int x) {  // hand x's pending tags to its children
        if (nd[x].hasAsg) applyAssign(nd[x].L, nd[x].asg), applyAssign(nd[x].R, nd[x].asg), nd[x].hasAsg = 0;
        if (nd[x].add != T(0)) applyAdd(nd[x].L, nd[x].add), applyAdd(nd[x].R, nd[x].add), nd[x].add = T(0);
    }

    void split(int t, int k, int& a, int& b) {  // a = first k of t, b = the rest
        if (!t) { a = b = 0; return; }
        push(t);
        if (nd[nd[t].L].sz >= k) split(nd[t].L, k, a, nd[t].L), b = t;
        else split(nd[t].R, k - nd[nd[t].L].sz - 1, nd[t].R, b), a = t;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's
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

    array<int, 4> psplit(int e, int o, int k) {  // lanes of (the first k values, the rest)
        int e1, e2, o1, o2;
        split(e, (k + 1) / 2, e1, e2);
        split(o, k / 2, o1, o2);
        if (k % 2) return {e1, o1, o2, e2};  // (an odd k: the rest starts on an odd position)
        return {e1, o1, e2, o2};
    }

    pair<int, int> pmerge(int e1, int o1, int e2, int o2) {  // lanes of (the first array, then the second)
        if ((nd[e1].sz + nd[o1].sz) % 2) swap(e2, o2);  // (after an odd length: its even positions are odd ones)
        return {merge(e1, e2), merge(o1, o2)};
    }

    array<int, 6> parts(int l, int r) {  // lanes of a[..l-1], a[l..r], a[r+1..]
        auto [ae, ao, xe, xo] = psplit(rE, rO, l);
        auto [be, bo, ce, co] = psplit(xe, xo, r - l + 1);
        return {ae, ao, be, bo, ce, co};
    }

    void join(int ae, int ao, int be, int bo, int ce, int co) {
        auto [e, o] = pmerge(ae, ao, be, bo);
        tie(rE, rO) = pmerge(e, o, ce, co);
    }

    int locate(int i, vector<int>* path = nullptr) {  // the node holding a[i], every tag on the way pushed
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

    vector<T> inorder(int t) {  // the values under t in order, every tag on the way pushed
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

    // ---- queries, searches and range updates walk the pieces of [l, r] instead of cutting it out ----



    // a node over a[l..r] of t's subtree: t itself if that is all of it, else temporaries made only where two parts
    // meet (pending tags on the way pushed down)
    int rq(int t, int l, int r) {
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

    int clone(int x) {  // a temporary copy of node x (sharing its children), dropped by release
        Node n;
        n.val = nd[x].val, n.pri = nd[x].pri, n.L = nd[x].L, n.R = nd[x].R, n.sz = nd[x].sz, n.sm = nd[x].sm,
        n.g = nd[x].g, n.fv = nd[x].fv, n.lv = nd[x].lv, n.asg = nd[x].asg, n.hasAsg = nd[x].hasAsg, n.add = nd[x].add;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    void release(size_t mark) {  // drop every node made after mark (temporaries: no tree points to them)
        nd.resize(mark);
        nd.resize(mark);
        nd.resize(mark);
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
    void upd(int t, int l, int r, const F& f, const H& h) {
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
    array<array<int, 3>, 2> lanes(int l, int r) {
        int roots[2] = {rE, rO};
        array<int, 3> e = {roots[l % 2], l / 2, (r - (r - l) % 2) / 2};
        array<int, 3> o = l < r ? array<int,
            3>{roots[(l + 1) % 2], (l + 1) / 2, (r - (r - l - 1) % 2) / 2} : array<int, 3>{0, 0, -1};
        return {e, o};
    }

    // temporary nodes over the two lane slices of a[l..r]; mark = the pool size release() goes back to
    pair<int, int> laneNodes(int l, int r, size_t& mark) {
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
