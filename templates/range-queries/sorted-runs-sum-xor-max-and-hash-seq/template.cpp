// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sorted-runs-sum-xor-max-and-hash-seq/template.cpp
// @operations: append appendLeft cut getAll insertAt insertCopiesAt isPalindrome merge moveRange paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeAssign rangeHash rangeHashReversed rangeMax rangeReverse rangeRotateLeft rangeRotateRight rangeSortAsc rangeSortDesc rangeSum rangeXorQuery rangesEqual split trisect
// @data-structure-type: sorted-runs
// @complexities:
//   append: log(N)+log(U) amortized
//   appendLeft: log(N)+log(U) amortized
//   cut: log(N)+log(U) amortized
//   getAll: N*log(U)
//   insertAt: log(N)+log(U) amortized
//   insertCopiesAt: log(N)+log(U) amortized
//   isPalindrome: log(N)+log(U) amortized
//   merge: log(N)+log(U) amortized
//   moveRange: log(N)+log(U) amortized
//   paste: log(N)+log(U) amortized
//   pointAdd: log(N)+log(U) amortized
//   pointAssign: log(N)+log(U) amortized
//   pointChmax: log(N)+log(U) amortized
//   pointChmin: log(N)+log(U) amortized
//   pointGet: log(N)+log(U) expected
//   rangeAndQuery: log(N)+log(U) amortized
//   rangeAssign: log(N)+log(U) amortized
//   rangeHash: log(N)+log(U) amortized
//   rangeHashReversed: log(N)+log(U) amortized
//   rangeMax: log(N)+log(U) amortized
//   rangeReverse: log(N)+log(U) amortized
//   rangeRotateLeft: log(N)+log(U) amortized
//   rangeRotateRight: log(N)+log(U) amortized
//   rangeSortAsc: log(N)+log(U) amortized
//   rangeSortDesc: log(N)+log(U) amortized
//   rangeSum: log(N)+log(U) amortized
//   rangeXorQuery: log(N)+log(U) amortized
//   rangesEqual: log(N)+log(U) amortized
//   split: log(N)+log(U) amortized
//   trisect: log(N)+log(U) amortized
//   build: N*log(U)
// @memory:
//   layout: none
//   node: Lc[1*N*log(U)] Rc[1*N*log(U)] cnt[1*N*log(U)] sm[1*N*log(U)] xr[1*N*log(U)] av[1*N*log(U)] fh[1*N*log(U)] bh[1*N*log(U)]
//   tags: none
//   other: TL[1*N] TR[1*N] TP[1*N] TV[1*N] TN[1*N] TD[1*N] TS[1*N] TF[1*N] Ssm[1*N] Sxr[1*N] Omx[1*N] Smx[1*N] Sav[1*N] Sfh[1*N] Sbh[1*N] pw[1*N] gs[1*N]
//   note: value nodes: N log U to start, plus O(log U) per cut (merges free nodes, which are reused); the runs are the nodes of an implicit treap (expected depth log N); U = valHi - valLo + 1

// An array whose ranges you can sort in place (ascending or descending), amortized O(log N + log U) a sort, with point
// reads / writes, rangeAssign, range sums, range xors, range maxes, range ands, range hashes both ways (isPalindrome,
// rangesEqual), insert / erase / reverse / rotate / move anywhere and the whole array. It is kept as a sequence of
// sorted runs: each run is a dynamic value seg tree over [valLo, valHi] (copies per node) and an up / down flag, and
// the runs, in order, are the nodes of an implicit treap (random priorities, expected depth log N), each also keeping
// its subtree's length and sum / xor / max / and / hashes; a reverse flips the order of the runs and each run's up /
// down flag. Sorting [l, r] cuts the runs at l and r + 1 and merges every run inside into one; a[i] is the k-th value
// of the run holding it; a query cuts at l and r + 1 too, then reads whole runs. Merges cost about as many nodes as
// they free and every run is merged away at most once, hence the amortized bounds (the treap's are expected as well).
// Indices 0-based, ranges inclusive, every index is a position in the current array. Hashes are polynomial, mod the
// prime 2^61 - 1, with a base and a value offset random per run: hash(x1..xk) = x1 B^(k-1) + ... + xk; a value tree
// keeps the hash of its values in sorted order both ways.
// T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct SortedRunsSumXorMaxAndHashSeq {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Pool {  // the node arrays (node 0 = the empty tree), shared with every piece cut from this one
        long long vlo, vhi;
        vector<int> Lc{0}, Rc{0}, freeList;  // value node 0 = the empty tree; nodes freed by merges are reused first
        vector<long long> cnt{0};
        vector<S> sm{S(0)};
        vector<T> xr{T(0)};
        vector<T> av{T(~T(0))};  // node 0 holds every bit (AND's identity)
        vector<unsigned long long> fh{0}, bh{0}, pw{1}, gs{0};  // hashes both ways; B^k; 1 + B + ... + B^(k-1)
        // treap of runs (node 0 = empty): children TL / TR, priority TP, value tree TV, length TN, descending TD,
        // subtree length TS, pending reverse TF, subtree sum / xor / max / and / hashes (O: the run's own min / max)
        vector<int> TL{0}, TR{0}, TV{0}, TN{0}, TS{0}, tfree;
        vector<unsigned long long> TP{0};
        vector<char> TD{0}, TF{0};
        vector<S> Ssm{S(0)};
        vector<T> Sxr{T(0)};
        vector<T> Omx{numeric_limits<T>::lowest()};
        vector<T> Smx{numeric_limits<T>::lowest()};
        vector<T> Sav{T(~T(0))};
        vector<unsigned long long> Sfh{0};
        vector<unsigned long long> Sbh{0};
    };
    shared_ptr<Pool> pool;  // (freed with the last object using it)
    long long& vlo;
    long long& vhi;
    vector<int>& Lc;
    vector<int>& Rc;
    vector<int>& freeList;
    vector<long long>& cnt;
    vector<S>& sm;
    vector<T>& xr;
    vector<T>& av;
    vector<unsigned long long>& fh;
    vector<unsigned long long>& bh;
    vector<unsigned long long>& pw;
    vector<unsigned long long>& gs;
    vector<int>& TL;
    vector<int>& TR;
    vector<int>& TV;
    vector<int>& TN;
    vector<int>& TS;
    vector<int>& tfree;
    vector<unsigned long long>& TP;
    vector<char>& TD;
    vector<char>& TF;
    vector<S>& Ssm;
    vector<T>& Sxr;
    vector<T>& Omx;
    vector<T>& Smx;
    vector<T>& Sav;
    vector<unsigned long long>& Sfh;
    vector<unsigned long long>& Sbh;
    int n = 0, rt = 0;
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
    static unsigned long long hadd(unsigned long long a, unsigned long long b) { return a + b >= HP ? a + b - HP : a + b; }
    static unsigned long long hraw(T v) {  // v as a residue (what an add changes a hash by, per position)
        long long r = (long long)v % (long long)HP;
        return r < 0 ? (unsigned long long)(r + (long long)HP) : (unsigned long long)r;
    }
    static unsigned long long hval(T v) {  // the hash of value v: v + an offset random per run, so no common value is 0
        static unsigned long long off = 1 + rnd() % (HP - 1);
        return hadd(hraw(v), off);
    }


    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N log U) -- arr: the initial array (may be empty); every value a[i] ever holds must lie in [valLo, valHi]
    // (U = valHi - valLo + 1). No reset between test cases: the nodes are freed with the last object using them
    SortedRunsSumXorMaxAndHashSeq(const vector<T>& arr, long long valLo, long long valHi)
        : SortedRunsSumXorMaxAndHashSeq(make_shared<Pool>()) {
        vlo = valLo, vhi = valHi;
        buildFrom(arr);
    }

    // O(N log U) -- an array over arr that shares other's nodes (and value range), so pieces can move between the two
    // (pieces cut from it share them already)
    SortedRunsSumXorMaxAndHashSeq(const vector<T>& arr, const SortedRunsSumXorMaxAndHashSeq& other)
        : SortedRunsSumXorMaxAndHashSeq(other.pool) {
        buildFrom(arr);
    }

    // an empty one on pool p
    explicit SortedRunsSumXorMaxAndHashSeq(shared_ptr<Pool> p)
        : pool(p), vlo(p->vlo), vhi(p->vhi), Lc(p->Lc), Rc(p->Rc), freeList(p->freeList), cnt(p->cnt), sm(p->sm),
          xr(p->xr), av(p->av), fh(p->fh), bh(p->bh), pw(p->pw), gs(p->gs), TL(p->TL), TR(p->TR), TV(p->TV),
          TN(p->TN), TS(p->TS), tfree(p->tfree), TP(p->TP), TD(p->TD), TF(p->TF), Ssm(p->Ssm), Sxr(p->Sxr),
          Omx(p->Omx), Smx(p->Smx), Sav(p->Sav), Sfh(p->Sfh), Sbh(p->Sbh) {}

    void buildFrom(const vector<T>& arr) {
        n = (int)arr.size();
        grow(n);
        vector<int> st;  // O(N) build: the treap's right spine
        for (const T& v : arr) {
            int x = run(leaf(v), 1, false), last = 0;
            while (!st.empty() && TP[st.back()] < TP[x]) last = st.back(), st.pop_back(), tpull(last);
            TL[x] = last;
            if (!st.empty()) TR[st.back()] = x;
            st.push_back(x);
        }
        for (int i = (int)st.size() - 1; i >= 0; i--) tpull(st[i]);
        rt = st.empty() ? 0 : st[0];
    }

    // O(1) -- the current length
    int size() const { return n; }

    // O(log N + log U) expected -- a[i]
    T pointGet(int i) {
        for (int x = rt;;) {
            push(x);
            int ls = TS[TL[x]];
            if (i < ls) x = TL[x];
            else if (i < ls + TN[x]) {
                int k = i - ls;
                return kth(TV[x], TD[x] ? TN[x] - k : k + 1);
            } else i -= ls + TN[x], x = TR[x];
        }
    }

    // O(log N + log U) amortized -- a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // O(log N + log U) amortized -- a[i] += v
    void pointAdd(int i, T v) { pointAssign(i, pointGet(i) + v); }

    // O(log N + log U) amortized -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(log N + log U) amortized -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // O(log N + log U) amortized -- sort a[l..r] ascending
    void rangeSortAsc(int l, int r) { sortRange(l, r, false); }

    // O(log N + log U) amortized -- sort a[l..r] descending
    void rangeSortDesc(int l, int r) { sortRange(l, r, true); }

    // O(log N + log U) amortized -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {
        auto [A, B, C] = extract(l, r);
        drop(B);
        join(A, run(leaf(v, r - l + 1), r - l + 1, false), C);
    }

    // O(log N + log U) amortized -- reverse a[l..r]
    void rangeReverse(int l, int r) {
        auto [A, B, C] = extract(l, r);
        rev(B);
        join(A, B, C);
    }

    // O(log N + log U) amortized -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) { insertCopiesAt(i, v, 1); }

    // O(log N + log U) amortized -- insert k copies of v starting at index i (0 <= i <= size(); k <= 0 does nothing)
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        n += (int)k;
        grow(n);
        auto [A, C] = tsplit(rt, i);
        rt = tmerge(tmerge(A, run(leaf(v, k), (int)k, false)), C);
    }

    // O(log N + log U) amortized -- append v
    void append(T v) { insertCopiesAt(n, v, 1); }

    // O(log N + log U) amortized -- insert v at the front (it becomes a[0])
    void appendLeft(T v) { insertCopiesAt(0, v, 1); }

    // O(log N + log U) amortized -- remove a[l..r] and return it as one of its own (indices from 0; drop it to erase)
    SortedRunsSumXorMaxAndHashSeq cut(int l, int r) {
        auto [A, B, C] = extract(l, r);
        rt = tmerge(A, C), n -= r - l + 1;
        SortedRunsSumXorMaxAndHashSeq piece(pool);
        piece.rt = B, piece.n = r - l + 1;
        return piece;
    }

    // O(log N + log U) amortized -- insert other at a[i] (0 <= i <= size()), leaving it empty; it must share
    // this one's nodes (a piece cut from it, or built with SortedRunsSumXorMaxAndHashSeq(arr, this one))
    void paste(int i, SortedRunsSumXorMaxAndHashSeq& other) {
        n += other.n;
        grow(n);  // (before the merge reads the powers)
        auto [A, C] = tsplit(rt, i);
        rt = tmerge(tmerge(A, other.rt), C), other.rt = other.n = 0;
    }

    // O(log N + log U) amortized -- append all of other at the end, leaving it empty (it must share this one's nodes)
    void merge(SortedRunsSumXorMaxAndHashSeq& other) { paste(n, other); }

    // O(log N + log U) amortized -- (a[0..k-1], a[k..]) as two of their own; this one is left empty
    pair<SortedRunsSumXorMaxAndHashSeq, SortedRunsSumXorMaxAndHashSeq> split(int k) {
        SortedRunsSumXorMaxAndHashSeq left(pool), right(pool);
        tie(left.rt, right.rt) = tsplit(rt, k);
        left.n = k, right.n = n - k, rt = n = 0;
        return {left, right};
    }

    // O(log N + log U) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three of their own; this one is left empty
    tuple<SortedRunsSumXorMaxAndHashSeq, SortedRunsSumXorMaxAndHashSeq, SortedRunsSumXorMaxAndHashSeq> trisect(int l, int r) {
        SortedRunsSumXorMaxAndHashSeq left(pool), mid(pool), right(pool);
        tie(left.rt, mid.rt, right.rt) = extract(l, r);
        left.n = l, mid.n = r - l + 1, right.n = n - r - 1, rt = n = 0;
        return {left, mid, right};
    }

    // O(log N + log U) amortized -- rotate a[l..r] left by k (a[l + k] comes first; any k, negative = right)
    void rangeRotateLeft(int l, int r, long long k) {
        long long m = r - l + 1;
        k = ((k % m) + m) % m;
        if (!k) return;
        auto [A, B, C] = extract(l, r);
        auto [X, Y] = tsplit(B, (int)k);
        join(A, tmerge(Y, X), C);
    }

    // O(log N + log U) amortized -- rotate a[l..r] right by k (any k, negative = left)
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(log N + log U) amortized -- cut a[l..r] out and paste it so it starts at index i of what is left
    // (0 <= i <= size() - (r - l + 1))
    void moveRange(int l, int r, int i) {
        auto [A, B, C] = extract(l, r);
        auto [X, Y] = tsplit(tmerge(A, C), i);
        rt = tmerge(tmerge(X, B), Y);
    }

    // O(log N + log U) amortized -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        auto [A, B, C] = extract(l, r);
        S res = Ssm[B];
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- a[l] ^ ... ^ a[r]
    T rangeXorQuery(int l, int r) {
        auto [A, B, C] = extract(l, r);
        T res = Sxr[B];
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- max of a[l..r]
    T rangeMax(int l, int r) {
        auto [A, B, C] = extract(l, r);
        T res = Smx[B];
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- a[l] & ... & a[r]
    T rangeAndQuery(int l, int r) {
        auto [A, B, C] = extract(l, r);
        T res = Sav[B];
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- is a[l..r] a palindrome?
    bool isPalindrome(int l, int r) {
        auto [A, B, C] = extract(l, r);
        bool res = Sfh[B] == Sbh[B];
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- hash of a[l..r] read left to right (a[l] B^(len-1) + ... + a[r], mod 2^61 - 1; B random per run): equal ranges hash equal
    unsigned long long rangeHash(int l, int r) {
        auto [A, B, C] = extract(l, r);
        unsigned long long res = Sfh[B];
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    unsigned long long rangeHashReversed(int l, int r) {
        auto [A, B, C] = extract(l, r);
        unsigned long long res = Sbh[B];
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- a[l1..r1] == a[l2..r2]? (equal lengths and equal hashes)
    bool rangesEqual(int l1, int r1, int l2, int r2) { return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2); }

    // O(N log U) -- the whole current array
    vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        vector<int> st;
        for (int x = rt; !st.empty() || x;) {
            for (; x; x = TL[x]) push(x), st.push_back(x);
            x = st.back();
            st.pop_back();
            values(TV[x], TD[x], out);
            x = TR[x];
        }
        return out;
    }

    // ---- internals: the treap of runs ----

    // a new run node: value tree t, length ln, descending?
    int run(int t, int ln, bool d) {
        int x;
        if (!tfree.empty()) x = tfree.back(), tfree.pop_back(), TL[x] = TR[x] = 0, TF[x] = 0;
        else {
            x = (int)TS.size();
            TL.push_back(0), TR.push_back(0), TV.push_back(0), TN.push_back(0), TS.push_back(0), TP.push_back(0);
            TD.push_back(0), TF.push_back(0), Ssm.push_back(S(0)), Sxr.push_back(T(0)), Omx.push_back(numeric_limits<T>::lowest()), Smx.push_back(numeric_limits<T>::lowest()), Sav.push_back(T(~T(0))), Sfh.push_back(0), Sbh.push_back(0);
        }
        TP[x] = rnd(), TV[x] = t, TN[x] = ln, TD[x] = d;
        Omx[x] = kth(t, cnt[t]);
        tpull(x);
        return x;
    }

    void tpull(int x) {
        int L = TL[x], R = TR[x], t = TV[x];
        TS[x] = TS[L] + TN[x] + TS[R];
        Ssm[x] = Ssm[L] + sm[t] + Ssm[R];
        Sxr[x] = Sxr[L] ^ xr[t] ^ Sxr[R];
        Smx[x] = max(Omx[x], max(Smx[L], Smx[R]));
        Sav[x] = Sav[L] & av[t] & Sav[R];
        unsigned long long f = TD[x] ? bh[t] : fh[t], b = TD[x] ? fh[t] : bh[t];  // the run, read left to right / right to left
        Sfh[x] = hadd(hmul(hadd(hmul(Sfh[L], pw[TN[x]]), f), pw[TS[R]]), Sfh[R]);
        Sbh[x] = hadd(hmul(hadd(hmul(Sbh[R], pw[TN[x]]), b), pw[TS[L]]), Sbh[L]);
    }

    void rev(int x) {  // reverse x's subtree: swap its children (and below, lazily), flip its run
        if (x) swap(TL[x], TR[x]), TD[x] ^= 1, swap(Sfh[x], Sbh[x]), TF[x] ^= 1;
    }

    void push(int x) {
        if (TF[x]) rev(TL[x]), rev(TR[x]), TF[x] = 0;
    }

    // (the first k elements, the rest), cutting the run that straddles k
    pair<int, int> tsplit(int x, int k) {
        if (!x || k <= 0) return {0, x};
        if (k >= TS[x]) return {x, 0};
        push(x);
        int ls = TS[TL[x]];
        if (k <= ls) {
            auto [a, b] = tsplit(TL[x], k);
            TL[x] = b;
            tpull(x);
            return {a, x};
        }
        if (k >= ls + TN[x]) {
            auto [a, b] = tsplit(TR[x], k - ls - TN[x]);
            TR[x] = a;
            tpull(x);
            return {x, b};
        }
        k -= ls;  // cut this run: x keeps its first k elements, a new node the rest
        int t = TV[x], ln = TN[x], a, b;
        if (TD[x]) split(t, ln - k, vlo, vhi, b, a);  // the first k are the k largest
        else split(t, k, vlo, vhi, a, b);
        TV[x] = a, TN[x] = k;
        Omx[x] = kth(a, cnt[a]);
        int u = run(b, ln - k, TD[x]), R = TR[x];
        TR[x] = 0;
        tpull(x);
        return {x, tmerge(u, R)};
    }

    int tmerge(int a, int b) {
        if (!a || !b) return a ? a : b;
        if (TP[a] > TP[b]) {
            push(a);
            int r = tmerge(TR[a], b);
            TR[a] = r;
            tpull(a);
            return a;
        }
        push(b);
        int l = tmerge(a, TL[b]);
        TL[b] = l;
        tpull(b);
        return b;
    }

    // (before l, a[l..r], after r) as three treaps
    tuple<int, int, int> extract(int l, int r) {
        auto [A, B] = tsplit(rt, l);
        auto [B2, C] = tsplit(B, r - l + 1);
        return {A, B2, C};
    }

    void join(int A, int B, int C) { rt = tmerge(tmerge(A, B), C); }

    vector<int> nodes(int x) const {  // every run node of x's treap
        vector<int> out, st;
        if (x) st.push_back(x);
        while (!st.empty()) {
            int y = st.back();
            st.pop_back();
            out.push_back(y);
            if (TL[y]) st.push_back(TL[y]);
            if (TR[y]) st.push_back(TR[y]);
        }
        return out;
    }

    void drop(int x) {  // free every run of x (value trees and treap nodes)
        for (int y : nodes(x)) freeTree(TV[y]), tfree.push_back(y);
    }

    // a[l..r] becomes one sorted run: every run inside merges into one
    void sortRange(int l, int r, bool d) {
        auto [A, B, C] = extract(l, r);
        int t = 0;
        for (int y : nodes(B)) t = merge(t, TV[y], vlo, vhi), tfree.push_back(y);
        join(A, run(t, r - l + 1, d), C);
    }

    // ---- internals: value trees (node 0 = the empty tree) ----

    int node() {
        if (!freeList.empty()) {
            int t = freeList.back();
            freeList.pop_back();
            Lc[t] = Rc[t] = 0, cnt[t] = 0;
            return t;
        }
        Lc.push_back(0), Rc.push_back(0), cnt.push_back(0), sm.push_back(S(0)), xr.push_back(T(0)), av.push_back(T(~T(0))), fh.push_back(0), bh.push_back(0);
        return (int)cnt.size() - 1;
    }

    void freeTree(int t) {  // hand every node of t back
        vector<int> st;
        if (t) st.push_back(t);
        while (!st.empty()) {
            int u = st.back();
            st.pop_back();
            freeList.push_back(u);
            if (Lc[u]) st.push_back(Lc[u]);
            if (Rc[u]) st.push_back(Rc[u]);
        }
    }

    // node x holds c copies of v (a leaf, or a node with one value under it)
    void setLeaf(int x, long long v, long long c) {
        cnt[x] = c;
        sm[x] = S(c) * S(v);
        xr[x] = (c & 1) ? T(v) : T(0);
        av[x] = T(v);
        fh[x] = bh[x] = hmul(hval(T(v)), gs[c]);
    }

    void pull(int x) {
        int l = Lc[x], r = Rc[x];
        cnt[x] = cnt[l] + cnt[r];
        sm[x] = sm[l] + sm[r];
        xr[x] = xr[l] ^ xr[r];
        av[x] = av[l] & av[r];
        fh[x] = hadd(hmul(fh[l], pw[cnt[r]]), fh[r]);
        bh[x] = hadd(hmul(bh[r], pw[cnt[l]]), bh[l]);
    }

    // hash tables up to length m
    void grow(long long m) {
        while ((long long)pw.size() <= m) gs.push_back(hadd(gs.back(), pw.back())), pw.push_back(hmul(pw.back(), HB()));
    }

    // a tree holding c copies of v: one node per level
    int leaf(T v, long long c = 1) {
        int top_ = node(), t = top_;
        long long nl = vlo, nh = vhi;
        while (true) {
            setLeaf(t, (long long)v, c);
            if (nl == nh) return top_;
            long long mid = nl + (nh - nl) / 2;
            int u = node();
            if ((long long)v <= mid) Lc[t] = u, nh = mid;
            else Rc[t] = u, nl = mid + 1;
            t = u;
        }
    }

    // a = the k smallest of t, b = the rest (0 <= k <= cnt[t]); t keeps the first part, new nodes (one path) the second
    void split(int t, long long k, long long nl, long long nh, int& a, int& b) {
        if (k <= 0) { a = 0, b = t; return; }
        if (k >= cnt[t]) { a = t, b = 0; return; }
        int nb = node();
        if (nl == nh) {  // one value: split its copies
            setLeaf(nb, nl, cnt[t] - k), setLeaf(t, nl, k);
            a = t, b = nb;
            return;
        }
        long long mid = nl + (nh - nl) / 2, cl = cnt[Lc[t]];
        int x, y;
        if (k <= cl) {
            split(Lc[t], k, nl, mid, x, y);
            Lc[t] = x, Lc[nb] = y, Rc[nb] = Rc[t], Rc[t] = 0;
        } else {
            split(Rc[t], k - cl, mid + 1, nh, x, y);
            Rc[t] = x, Rc[nb] = y;
        }
        pull(t), pull(nb);
        a = t, b = nb;
    }

    // the union of a and b, overlaid node by node (b's nodes where both have one are freed)
    int merge(int a, int b, long long nl, long long nh) {
        if (!a || !b) return a ? a : b;
        if (nl == nh) {
            setLeaf(a, nl, cnt[a] + cnt[b]);
        } else {
            long long mid = nl + (nh - nl) / 2;
            int x = merge(Lc[a], Lc[b], nl, mid);
            Lc[a] = x;
            int y = merge(Rc[a], Rc[b], mid + 1, nh);
            Rc[a] = y;
            pull(a);
        }
        freeList.push_back(b);
        return a;
    }

    // the k-th smallest value of t, 1 <= k <= cnt[t]
    T kth(int t, long long k) const {
        long long nl = vlo, nh = vhi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, cl = cnt[Lc[t]];
            if (k <= cl) t = Lc[t], nh = mid;
            else k -= cl, t = Rc[t], nl = mid + 1;
        }
        return T(nl);
    }

    // append t's values, ascending (or descending), to out
    void values(int t, bool d, vector<T>& out) const {
        size_t from = out.size();
        vector<tuple<int, long long, long long>> st{{t, vlo, vhi}};
        while (!st.empty()) {  // in-order, pushed right first
            auto [u, nl, nh] = st.back();
            st.pop_back();
            if (!cnt[u]) continue;
            if (nl == nh) {
                out.insert(out.end(), cnt[u], T(nl));
                continue;
            }
            long long mid = nl + (nh - nl) / 2;
            st.push_back({Rc[u], mid + 1, nh}), st.push_back({Lc[u], nl, mid});
        }
        if (d) reverse(out.begin() + from, out.end());
    }
};
