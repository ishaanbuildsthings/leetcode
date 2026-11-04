// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pair-treap-sum-max-gcd-rev-find/template.cpp
// @operations: append appendLeft cut find getAll insertAt insertCopiesAt leftmostGtX leftmostGteX merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd rangeMax rangeReverse rangeRotateLeft rangeRotateRight rangeSum rangeTwinSpin rightmostGtX rightmostGteX size split trisect
// @data-structure-type: pair-treap
// @complexities:
//   append: log(N)*log(U) expected ?
//   appendLeft: log(N)*log(U) expected ?
//   cut: log(N)*log(U) expected ?
//   find: log(N)*log(U) expected ?
//   getAll: N
//   insertAt: log(N)*log(U) expected ?
//   insertCopiesAt: log(N)*log(U) expected ?
//   leftmostGtX: log(N)*log(U) expected ?
//   leftmostGteX: log(N)*log(U) expected ?
//   merge: log(N)*log(U) expected ?
//   paste: log(N)*log(U) expected ?
//   pointAdd: log(N)*log(U) expected ?
//   pointAssign: log(N)*log(U) expected ?
//   pointChmax: log(N)*log(U) expected ?
//   pointChmin: log(N)*log(U) expected ?
//   pointGet: log(N) expected
//   rangeGcd: log(N)*log(U) expected ?
//   rangeMax: log(N)*log(U) expected ?
//   rangeReverse: log(N)*log(U) expected ?
//   rangeRotateLeft: log(N)*log(U) expected ?
//   rangeRotateRight: log(N)*log(U) expected ?
//   rangeSum: log(N)*log(U) expected ?
//   rangeTwinSpin: log(N)*log(U) expected ?
//   rightmostGtX: log(N)*log(U) expected ?
//   rightmostGteX: log(N)*log(U) expected ?
//   split: log(N)*log(U) expected ?
//   trisect: log(N)*log(U) expected ?
//   size: 1
//   build: N*log(U) ?
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mx[1*N] g[1*N] par[1*N]
//   tags: rev[1*N]
//   other: where[1*N]
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); two treaps per array (even / odd positions); every PairSwapTreap<T> shares one node pool (pieces move between any of them; nothing to reset); find: a parent per node and a map value -> node

// Implicit treap pair: an array you can insert into anywhere, swap adjacent pairs in a range (rangeTwinSpin: a[l] <->
// a[l + 1], a[l + 2] <-> a[l + 3], ...), reverse, rotate, cut pieces out of (that is how to erase) and paste them
// back in O(logN) expected each, and find any value's index (values distinct). The values at even positions a[0],
// a[2], ... are one treap (lane E) and the odd ones another (lane O), in one node pool; a range [l, r] is a slice of
// each, and each node keeps its sum, its max, its gcd over its subtree. All indices 0-based, ranges inclusive [l, r],
// an index always the position in the CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean
// "already applied to this node, not yet to its children".
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct PairSwapTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct SafeHash {  // splitmix64 with a seed random per run (the default hash of an integer is easy to attack)
        size_t operator()(const T& x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    // one node pool shared by every PairSwapTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        S sm = 0;
        T val = T(0);
        T mx = T(0);
        T g = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
        int par = 0;
        char rev = 0;
    };
    static inline vector<Node> nd{Node{}};  // node 0 = the empty tree
    static inline unordered_map<T, int, SafeHash> where;
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

    // O(logN * logU) expected -- the index of x, or -1 if x isn't in this treap (values distinct across all treaps)
    int find(T x) {
        auto it = where.find(x);
        if (it == where.end() || nd[it->second].val != x) return -1;
        int t = it->second;
        vector<int> path{t};
        while (true) {  // up to the root (a parent counts only while it still has the node as a child)
            int c = path.back(), p = nd[c].par;
            if (!p || (nd[p].L != c && nd[p].R != c)) break;
            path.push_back(p);
        }
        int top = path.back();
        if (top != rE && top != rO) return -1;  // (erased, or in another treap)
        for (int k = (int)path.size() - 1; k >= 0; k--) push(path[k]);  // (pending reverses above it, top-down)
        int i = nd[nd[t].L].sz;
        for (size_t k = 1; k < path.size(); k++)
            if (nd[path[k]].R == path[k - 1]) i += nd[nd[path[k]].L].sz + 1;
        return 2 * i + (top == rO);  // (lane index i: a[2i] in lane E, a[2i + 1] in lane O)
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

    // O(logN * logU) expected -- the first i in [l, r] with a[i] > x, or -1 (each lane's walk pruned by the subtree
    // max); needs 0 <= l <= r < size(), else throws out_of_range
    int leftmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGtX: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        int i = laneLeftmostGtX(be, x), j = laneLeftmostGtX(bo, x);
        release(mark);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return i < 0 ? j : j < 0 ? i : min(i, j);
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] >= x, or -1 (each lane's walk pruned by the subtree
    // max); needs 0 <= l <= r < size(), else throws out_of_range
    int leftmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGteX: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        int i = laneLeftmostGteX(be, x), j = laneLeftmostGteX(bo, x);
        release(mark);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return i < 0 ? j : j < 0 ? i : min(i, j);
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
        T old = nd[t].val;
        nd[t].val = nd[t].val + v;
        rekey(t, old);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        T old = nd[t].val;
        nd[t].val = v;
        rekey(t, old);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmax: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        T old = nd[t].val;
        nd[t].val = max(nd[t].val, v);
        rekey(t, old);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmin: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        T old = nd[t].val;
        nd[t].val = min(nd[t].val, v);
        rekey(t, old);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return nd[locate(i)].val;
    }

    // O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeGcd(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeGcd: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        T res = gcd(nd[be].g, nd[bo].g);
        release(mark);
        return res;
    }

    // O(logN * logU) expected -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMax: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        T res = bo ? max(nd[be].mx, nd[bo].mx) : nd[be].mx;
        release(mark);
        return res;
    }

    // O(logN * logU) expected -- reverse a[l..r] in place: each lane reverses, and with an even length they trade
    // places; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeReverse(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReverse: needs 0 <= l <= r < size()");
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        applyRev(be), applyRev(bo);
        if ((r - l + 1) % 2 == 0) join(ae, ao, bo, be, ce, co);
        else join(ae, ao, be, bo, ce, co);
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

    // O(logN * logU) expected -- the last i in [l, r] with a[i] > x, or -1 (each lane's walk pruned by the subtree
    // max); needs 0 <= l <= r < size(), else throws out_of_range
    int rightmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGtX: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        int i = laneRightmostGtX(be, x), j = laneRightmostGtX(bo, x);
        release(mark);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return max(i, j);
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] >= x, or -1 (each lane's walk pruned by the subtree
    // max); needs 0 <= l <= r < size(), else throws out_of_range
    int rightmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGteX: needs 0 <= l <= r < size()");
        size_t mark;
        auto [be, bo] = laneNodes(l, r, mark);
        int i = laneRightmostGteX(be, x), j = laneRightmostGteX(bo, x);
        release(mark);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return max(i, j);
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

    // ---- internals ----

    int newNode(T v) {
        Node n;
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.mx = v, n.g = v < T(0) ? T(-v) : v,
        n.rev = 0, n.par = 0;
        nd.push_back(n);
        where[v] = (int)nd.size() - 1;
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
        nd[l].par = nd[r].par = x;
        T v = nd[x].val;
        nd[x].sm = nd[l].sm + S(v) + nd[r].sm;
        nd[x].mx = v;
        if (l && nd[l].mx > nd[x].mx) nd[x].mx = nd[l].mx;
        if (r && nd[r].mx > nd[x].mx) nd[x].mx = nd[r].mx;
        nd[x].g = gcd(gcd(nd[l].g, v), nd[r].g);
    }

    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        swap(nd[x].L, nd[x].R), nd[x].rev ^= 1;
    }

    void push(int x) {  // hand x's pending tags to its children
        if (nd[x].rev) applyRev(nd[x].L), applyRev(nd[x].R), nd[x].rev = 0;
    }

    void rekey(int t, T old) {  // t's value changed from old: the map follows (find needs distinct values)
        auto it = where.find(old);
        if (it != where.end() && it->second == t) where.erase(it);
        where[nd[t].val] = t;
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

    int laneLeftmostGtX(int t, T x) {  // the first k with lane value k > x under t, or -1
        if (!t || !(nd[t].mx > x)) return -1;
        int i = 0;
        while (true) {
            push(t);
            if (nd[t].L && nd[nd[t].L].mx > x) t = nd[t].L;
            else if (nd[t].val > x) return i + nd[nd[t].L].sz;
            else i += nd[nd[t].L].sz + 1, t = nd[t].R;
        }
    }

    int laneLeftmostGteX(int t, T x) {  // the first k with lane value k >= x under t, or -1
        if (!t || !(nd[t].mx >= x)) return -1;
        int i = 0;
        while (true) {
            push(t);
            if (nd[t].L && nd[nd[t].L].mx >= x) t = nd[t].L;
            else if (nd[t].val >= x) return i + nd[nd[t].L].sz;
            else i += nd[nd[t].L].sz + 1, t = nd[t].R;
        }
    }

    int laneRightmostGtX(int t, T x) {  // the last k with lane value k > x under t, or -1
        if (!t || !(nd[t].mx > x)) return -1;
        int i = 0;
        while (true) {
            push(t);
            if (nd[t].R && nd[nd[t].R].mx > x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
            else if (nd[t].val > x) return i + nd[nd[t].L].sz;
            else t = nd[t].L;
        }
    }

    int laneRightmostGteX(int t, T x) {  // the last k with lane value k >= x under t, or -1
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
        int pa = nd[a].par, pb = nd[b].par;  // (a temporary's pull must not move its children's parents)
        pull(y);
        nd[a].par = pa, nd[b].par = pb;
        return y;
    }

    int clone(int x) {  // a temporary copy of node x (sharing its children), dropped by release
        Node n;
        n.val = nd[x].val, n.pri = nd[x].pri, n.L = nd[x].L, n.R = nd[x].R, n.sz = nd[x].sz, n.sm = nd[x].sm,
        n.mx = nd[x].mx, n.g = nd[x].g, n.par = nd[x].par, n.rev = nd[x].rev;
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
