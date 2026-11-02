// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pair-treap-max-hash-xor-and-rev/template.cpp
// @operations: append appendLeft cut getAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeHash rangeHashReversed rangeMax rangeReverse rangeRotateLeft rangeRotateRight rangeTwinSpin rangeXorQuery rangesEqual rightmostGtX rightmostGteX split trisect
// @data-structure-type: pair-treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   cut: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: log(N) expected
//   isPalindrome: log(N) expected
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
//   rangeHash: log(N) expected
//   rangeHashReversed: log(N) expected
//   rangeMax: log(N) expected
//   rangeReverse: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeTwinSpin: log(N) expected
//   rangeXorQuery: log(N) expected
//   rangesEqual: log(N) expected
//   rightmostGtX: log(N) expected
//   rightmostGteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] mx[1*N] fh[1*N] bh[1*N] pw[1*N] xr[1*N] an[1*N]
//   tags: rev[1*N]
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); two treaps per array (even / odd positions); every PairSwapTreap<T> shares one node pool; each lane hashes in base B^2 (pieces move between any of them; nothing to reset)

// Implicit treap pair: an array you can insert into anywhere, swap adjacent pairs in a range (rangeTwinSpin: a[l] <->
// a[l + 1], a[l + 2] <-> a[l + 3], ...), reverse, rotate, cut pieces out of (that is how to erase) and paste them
// back in O(logN) expected each. The values at even positions a[0], a[2], ... are one treap (lane E) and the odd ones
// another (lane O), in one node pool; a range [l, r] is a slice of each, and each node keeps its max, its forward /
// backward hash (and B^size), its xor, its AND over its subtree. All indices 0-based, ranges inclusive [l, r], an
// index always the position in the CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already
// applied to this node, not yet to its children".
// T: int, long long, ...
template <typename T>
struct PairSwapTreap {
    using U64 = unsigned long long;
    // one node pool shared by every PairSwapTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    static inline vector<T> val{T(0)};
    static inline vector<unsigned long long> pri{0};
    static inline vector<int> L{0};
    static inline vector<int> R{0};
    static inline vector<int> sz{0};
    static inline vector<T> mx{T(0)};
    static inline vector<U64> fh{0};
    static inline vector<U64> bh{0};
    static inline vector<U64> pw{1};
    static inline vector<T> xr{T(0)};
    static inline vector<T> an{~T(0)};
    static inline vector<char> rev{0};
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
    // range hashes: mod the prime 2^61 - 1, with a base picked at random each run (so no test can be built against it)
    static constexpr unsigned long long HP = (1ULL << 61) - 1;
    static unsigned long long HB() {
        static unsigned long long b = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
        return b;
    }
    static unsigned long long hmul(unsigned long long a, unsigned long long b) {
        __uint128_t c = (__uint128_t)a * b;
        unsigned long long r = (unsigned long long)(c & HP) + (unsigned long long)(c >> 61);
        r = (r & HP) + (r >> 61);
        return r >= HP ? r - HP : r;
    }
    static unsigned long long hadd(unsigned long long a, unsigned long long b) {
        return a + b >= HP ? a + b - HP : a + b;
    }
    static unsigned long long hraw(T v) {  // v as a residue (what an add changes a hash by, per position)
        long long r = (long long)v % (long long)HP;
        return r < 0 ? (unsigned long long)(r + (long long)HP) : (unsigned long long)r;
    }
    static unsigned long long hval(T v) {  // the hash of value v: v + an offset random per run, so no common value is 0
        static unsigned long long off = 1 + rnd() % (HP - 1);
        return hadd(hraw(v), off);
    }

    static U64 HQ() {  // a lane's base: B^2 (its neighbours in the array are 2 apart)
        static U64 q = hmul(HB(), HB());
        return q;
    }


    // O(1) -- the current length of the array
    int size() const { return sz[rE] + sz[rO]; }

    // O(logN) expected -- append v to the end
    void append(T v) { tie(rE, rO) = pmerge(rE, rO, newNode(v), 0); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[l..r] and return it as a PairSwapTreap of its own (indices from 0)
    PairSwapTreap cut(int l, int r) {
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

    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, newNode(v), 0);
        tie(rE, rO) = pmerge(e, o, ce, co);
    }

    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, build(vector<T>((k + 1) / 2, v)), build(vector<T>(k / 2, v)));
        tie(rE, rO) = pmerge(e, o, ce, co);
    }

    // O(logN) expected -- is a[l..r] a palindrome (its two hashes agree)
    bool isPalindrome(int l, int r) {
        auto [f, b] = hashes(l, r);
        return f == b;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (each lane's walk pruned by the subtree max)
    int leftmostGtX(int l, int r, T x) {
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        int i = laneLeftmostGtX(be, x), j = laneLeftmostGtX(bo, x);
        join(ae, ao, be, bo, ce, co);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return i < 0 ? j : j < 0 ? i : min(i, j);
    }

    // O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1 (each lane's walk pruned by the subtree max)
    int leftmostGteX(int l, int r, T x) {
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        int i = laneLeftmostGteX(be, x), j = laneLeftmostGteX(bo, x);
        join(ae, ao, be, bo, ce, co);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return i < 0 ? j : j < 0 ? i : min(i, j);
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    void merge(PairSwapTreap& other) {
        tie(rE, rO) = pmerge(rE, rO, other.rE, other.rO);
        other.rE = other.rO = 0;
    }

    // O(logN) expected -- insert all of other (any PairSwapTreap, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(int i, PairSwapTreap& other) {
        auto [ae, ao, ce, co] = psplit(rE, rO, i);
        auto [e, o] = pmerge(ae, ao, other.rE, other.rO);
        tie(rE, rO) = pmerge(e, o, ce, co);
        other.rE = other.rO = 0;
    }

    // O(logN) expected -- a[i] += v
    void pointAdd(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        val[t] = val[t] + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = v
    void pointAssign(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        val[t] = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        val[t] = max(val[t], v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        val[t] = min(val[t], v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]
    T pointGet(int i) { return val[locate(i)]; }

    // O(logN) expected -- a[l] & ... & a[r]
    T rangeAndQuery(int l, int r) {
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        T res = an[be] & an[bo];
        join(ae, ao, be, bo, ce, co);
        return res;
    }

    // O(logN) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal
    U64 rangeHash(int l, int r) { return hashes(l, r).first; }

    // O(logN) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    U64 rangeHashReversed(int l, int r) { return hashes(l, r).second; }

    // O(logN) expected -- max of a[l..r]
    T rangeMax(int l, int r) {
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        T res = bo ? max(mx[be], mx[bo]) : mx[be];
        join(ae, ao, be, bo, ce, co);
        return res;
    }

    // O(logN) expected -- reverse a[l..r] in place: each lane reverses, and with an even length they trade places
    void rangeReverse(int l, int r) {
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        applyRev(be), applyRev(bo);
        if ((r - l + 1) % 2 == 0) join(ae, ao, bo, be, ce, co);
        else join(ae, ao, be, bo, ce, co);
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    // it is taken mod the length (negative shifts right)
    void rangeRotateLeft(int l, int r, long long k) {
        int len = r - l + 1;
        k = ((k % len) + len) % len;
        if (!k) return;
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        auto [xe, xo, ye, yo] = psplit(be, bo, (int)k);
        auto [e, o] = pmerge(ye, yo, xe, xo);
        join(ae, ao, e, o, ce, co);
    }

    // O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left)
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(logN) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (odd length: a[r] stays):
    // the pairs' two lanes trade places
    void rangeTwinSpin(int l, int r) {
        int k = (r - l + 1) / 2;
        if (!k) return;
        auto [ae, ao, be, bo, ce, co] = parts(l, l + 2 * k - 1);
        join(ae, ao, bo, be, ce, co);
    }

    // O(logN) expected -- a[l] ^ ... ^ a[r]
    T rangeXorQuery(int l, int r) {
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        T res = xr[be] ^ xr[bo];
        join(ae, ao, be, bo, ce, co);
        return res;
    }

    // O(logN) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    bool rangesEqual(int l1, int r1, int l2, int r2) {
        return r1 - l1 == r2 - l2 && hashes(l1, r1).first == hashes(l2, r2).first;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (each lane's walk pruned by the subtree max)
    int rightmostGtX(int l, int r, T x) {
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        int i = laneRightmostGtX(be, x), j = laneRightmostGtX(bo, x);
        join(ae, ao, be, bo, ce, co);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return max(i, j);
    }

    // O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1 (each lane's walk pruned by the subtree max)
    int rightmostGteX(int l, int r, T x) {
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        int i = laneRightmostGteX(be, x), j = laneRightmostGteX(bo, x);
        join(ae, ao, be, bo, ce, co);
        i = i >= 0 ? l + 2 * i : -1;  // (lane E's k-th value is a[l + 2k], lane O's a[l + 1 + 2k])
        j = j >= 0 ? l + 1 + 2 * j : -1;
        return max(i, j);
    }

    // O(logN) expected -- (a[0..k-1], a[k..]) as two PairSwapTreaps of their own; this one is left empty
    pair<PairSwapTreap, PairSwapTreap> split(int k) {
        PairSwapTreap left = makeEmpty(), right = makeEmpty();
        auto [le, lo, re, ro] = psplit(rE, rO, k);
        left.rE = le, left.rO = lo, right.rE = re, right.rO = ro;
        rE = rO = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PairSwapTreaps of their own; this one is left empty
    tuple<PairSwapTreap, PairSwapTreap, PairSwapTreap> trisect(int l, int r) {
        PairSwapTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        left.rE = ae, left.rO = ao, mid.rE = be, mid.rO = bo, right.rE = ce, right.rO = co;
        rE = rO = 0;
        return {left, mid, right};
    }

    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1);
        mx.push_back(v), fh.push_back(hval(v)), bh.push_back(hval(v)), pw.push_back(HQ()), xr.push_back(v);
        an.push_back(v), rev.push_back(0);
        return (int)val.size() - 1;
    }

    // a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    int build(const vector<T>& vals) {
        vector<int> stk, order, todo;
        for (const T& v : vals) {
            int x = newNode(v), last = 0;
            while (!stk.empty() && pri[stk.back()] < pri[x]) last = stk.back(), stk.pop_back();
            L[x] = last;
            if (!stk.empty()) R[stk.back()] = x;
            stk.push_back(x);
        }
        int rt = stk.empty() ? 0 : stk[0];
        if (rt) todo.push_back(rt);
        while (!todo.empty()) {
            int x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (L[x]) todo.push_back(L[x]);
            if (R[x]) todo.push_back(R[x]);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
        return rt;
    }

    void pull(int x) {  // recompute x from its children
        int l = L[x], r = R[x];
        sz[x] = sz[l] + sz[r] + 1;
        T v = val[x];
        mx[x] = v;
        if (l && mx[l] > mx[x]) mx[x] = mx[l];
        if (r && mx[r] > mx[x]) mx[x] = mx[r];
        U64 B = HQ(), hv = hval(v);
        pw[x] = hmul(hmul(pw[l], B), pw[r]);
        fh[x] = hadd(hmul(hadd(hmul(fh[l], B), hv), pw[r]), fh[r]);
        bh[x] = hadd(hmul(hadd(hmul(bh[r], B), hv), pw[l]), bh[l]);
        xr[x] = xr[l] ^ v ^ xr[r];
        an[x] = an[l] & v & an[r];  // (node 0: the AND of nothing, ~0)
    }

    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        swap(L[x], R[x]), rev[x] ^= 1, swap(fh[x], bh[x]);
    }

    void push(int x) {  // hand x's pending tags to its children
        if (rev[x]) applyRev(L[x]), applyRev(R[x]), rev[x] = 0;
    }

    void split(int t, int k, int& a, int& b) {  // a = first k of t, b = the rest
        if (!t) { a = b = 0; return; }
        push(t);
        if (sz[L[t]] >= k) split(L[t], k, a, L[t]), b = t;
        else split(R[t], k - sz[L[t]] - 1, R[t], b), a = t;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's
        if (!a || !b) return a | b;
        if (pri[a] > pri[b]) {
            push(a);
            R[a] = merge(R[a], b);
            pull(a);
            return a;
        }
        push(b);
        L[b] = merge(a, L[b]);
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
        if ((sz[e1] + sz[o1]) % 2) swap(e2, o2);  // (after an odd length the second's even positions are odd ones)
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
            int ls = sz[L[t]];
            if (k == ls) return t;
            if (path) path->push_back(t);
            if (k < ls) t = L[t];
            else k -= ls + 1, t = R[t];
        }
    }

    vector<T> inorder(int t) {  // the values under t in order, every tag on the way pushed
        vector<T> out;
        vector<int> st;
        while (!st.empty() || t) {
            while (t) push(t), st.push_back(t), t = L[t];
            t = st.back(), st.pop_back();
            out.push_back(val[t]);
            t = R[t];
        }
        return out;
    }

    // (forward, backward) hash of a[l..r]: lane E's slice x holds a[l], a[l + 2], ..., lane O's y the rest; in base B
    // the range reads x0 y0 x1 y1 ..., so forward = H(x) + B H(y) (odd length) or B H(x) + H(y) (even), and backward
    // = Hrev(x) + B Hrev(y)
    pair<U64, U64> hashes(int l, int r) {
        auto [ae, ao, be, bo, ce, co] = parts(l, r);
        U64 B = HB();
        U64 fwd = (r - l) % 2 == 0 ? hadd(fh[be], hmul(B, fh[bo])) : hadd(hmul(B, fh[be]), fh[bo]);
        U64 bwd = hadd(bh[be], hmul(B, bh[bo]));
        join(ae, ao, be, bo, ce, co);
        return {fwd, bwd};
    }

    int laneLeftmostGtX(int t, T x) {  // the first k with lane value k > x under t, or -1
        if (!t || !(mx[t] > x)) return -1;
        int i = 0;
        while (true) {
            push(t);
            if (L[t] && mx[L[t]] > x) t = L[t];
            else if (val[t] > x) return i + sz[L[t]];
            else i += sz[L[t]] + 1, t = R[t];
        }
    }

    int laneLeftmostGteX(int t, T x) {  // the first k with lane value k >= x under t, or -1
        if (!t || !(mx[t] >= x)) return -1;
        int i = 0;
        while (true) {
            push(t);
            if (L[t] && mx[L[t]] >= x) t = L[t];
            else if (val[t] >= x) return i + sz[L[t]];
            else i += sz[L[t]] + 1, t = R[t];
        }
    }

    int laneRightmostGtX(int t, T x) {  // the last k with lane value k > x under t, or -1
        if (!t || !(mx[t] > x)) return -1;
        int i = 0;
        while (true) {
            push(t);
            if (R[t] && mx[R[t]] > x) i += sz[L[t]] + 1, t = R[t];
            else if (val[t] > x) return i + sz[L[t]];
            else t = L[t];
        }
    }

    int laneRightmostGteX(int t, T x) {  // the last k with lane value k >= x under t, or -1
        if (!t || !(mx[t] >= x)) return -1;
        int i = 0;
        while (true) {
            push(t);
            if (R[t] && mx[R[t]] >= x) i += sz[L[t]] + 1, t = R[t];
            else if (val[t] >= x) return i + sz[L[t]];
            else t = L[t];
        }
    }
};

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     PairSwapTreap<int> t({1, 2, 3, 4, 5});
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
