// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sorted-runs-min-or-hash-seq/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft cut getAll hashAll hashAllReversed insertAt insertCopiesAt isPalindrome longestPalCenteredAtI longestPalCenteredAtIPlusOne merge minAll orAll paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAssign rangeHash rangeHashReversed rangeMin rangeOrQuery rangeReverse rangeRotateLeft rangeRotateRight rangeSortAsc rangeSortDesc rangesEqual size split trisect
// @data-structure-type: sorted-runs
// @complexities:
//   append: log(N)+log(U) amortized
//   appendLeft: log(N)+log(U) amortized
//   cut: log(N)+log(U) amortized
//   getAll: N*log(U)
//   insertAt: log(N)+log(U) amortized
//   insertCopiesAt: K+log(N)+log(U) amortized
//   isPalindrome: log(N)+log(U) amortized
//   merge: log(N)+log(U) amortized
//   paste: log(N)+log(U) amortized
//   pointAdd: log(N)+log(U) amortized
//   pointAssign: log(N)+log(U) amortized
//   pointChmax: log(N)+log(U) amortized
//   pointChmin: log(N)+log(U) amortized
//   pointGet: log(N)+log(U) expected
//   rangeAssign: log(N)+log(U) amortized
//   rangeHash: log(N)+log(U) amortized
//   rangeHashReversed: log(N)+log(U) amortized
//   rangeMin: log(N)+log(U) amortized
//   rangeOrQuery: log(N)+log(U) amortized
//   rangeReverse: log(N)+log(U) amortized
//   rangeRotateLeft: log(N)+log(U) amortized
//   rangeRotateRight: log(N)+log(U) amortized
//   rangeSortAsc: log(N)+log(U) amortized
//   rangeSortDesc: log(N)+log(U) amortized
//   rangesEqual: log(N)+log(U) amortized
//   split: log(N)+log(U) amortized
//   trisect: log(N)+log(U) amortized
//   size: 1
//   pop: log(N)+log(U) amortized
//   popLeft: log(N)+log(U) amortized
//   longestPalCenteredAtI: log^2(N)+log(N)*log(U) amortized
//   longestPalCenteredAtIPlusOne: log^2(N)+log(N)*log(U) amortized
//   hashAll: log(N)+log(U) amortized
//   minAll: log(N)+log(U) amortized
//   orAll: log(N)+log(U) amortized
//   hashAllReversed: log(N)+log(U) amortized
//   build: N*log(U)
// @memory:
//   layout: none
//   node: Lc[1*N*log(U)] Rc[1*N*log(U)] cnt[1*N*log(U)] ov[1*N*log(U)] fh[1*N*log(U)] bh[1*N*log(U)]
//   tags: none
//   other: TL[1*N] TR[1*N] TP[1*N] TV[1*N] TN[1*N] TD[1*N] TS[1*N] TF[1*N] Omn[1*N] Smn[1*N] Sov[1*N] Sfh[1*N] Sbh[1*N] pw[1*N] gs[1*N]
//   note: value nodes: N log U to start, plus O(log U) per cut (merges free nodes, which are reused); the runs are the nodes of an implicit treap (expected depth log N); U = valHi - valLo + 1

// An array whose ranges you can sort in place (ascending or descending), amortized O(log N + log U) a sort, with point
// reads / writes, rangeAssign, range mins, range ors, range hashes both ways (isPalindrome, rangesEqual), insert /
// erase / reverse / rotate / move anywhere and the whole array. It is kept as a sequence of sorted runs: each run is a
// dynamic value seg tree over [valLo, valHi] (copies per node) and an up / down flag, and the runs, in order, are the
// nodes of an implicit treap (random priorities, expected depth log N), each also keeping its subtree's length and min
// / or / hashes; a reverse flips the order of the runs and each run's up / down flag. Sorting [l, r] cuts the runs at
// l and r + 1 and merges every run inside into one; a[i] is the k-th value of the run holding it; a query cuts at l
// and r + 1 too, then reads whole runs. Merges cost about as many nodes as they free and every run is merged away at
// most once, hence the amortized bounds (the treap's are expected as well). Indices 0-based, ranges inclusive, every
// index is a position in the current array. Hashes are polynomial, mod the prime 2^61 - 1, with a base and a value
// offset random per run: hash(x1..xk) = x1 B^(k-1) + ... + xk; a value tree keeps the hash of its values in sorted
// order both ways.
// T: int, long long, ...; sums in S (long long for small T).
template <typename T>
struct SortedRunsMinOrHashSeq {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // one node pool shared by every SortedRunsMinOrHashSeq<T>: cut / paste move nodes between them, so a piece from
    // one can go into any other (node 0 = the empty tree). Nodes freed by merges are reused, and there is nothing to
    // reset between test cases
    struct VNode {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long fh = 0;
        unsigned long long bh = 0;
        long long cnt = 0;
        T ov = T(0);
        int Lc = 0;
        int Rc = 0;
    };
    static inline vector<VNode> vn{VNode{}};  // node 0 = the empty tree
    struct Run {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long TP = 0;
        unsigned long long Sfh = 0;
        unsigned long long Sbh = 0;
        T Omn = numeric_limits<T>::max();
        T Smn = numeric_limits<T>::max();
        T Sov = T(0);
        int TL = 0;
        int TR = 0;
        int TV = 0;
        int TN = 0;
        int TS = 0;
        char TD = 0;
        char TF = 0;
    };
    static inline vector<Run> rn{Run{}};  // node 0 = the empty tree
    static inline vector<int> freeList;  // value nodes freed by merges, reused first
    static inline vector<unsigned long long> pw{1}, gs{0};  // B^k; 1 + B + ... + B^(k-1)
    // treap of runs (node 0 = empty): children TL / TR, priority TP, value tree TV, length TN, descending TD,
    // subtree length TS, pending reverse TF, subtree min / or / hashes (O: the run's own min / max)
    static inline vector<int> tfree;
    long long vlo, vhi;  // (each one's value range)
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


    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N log U) -- arr: the initial array; every value a[i] ever holds must lie in [valLo, valHi]
    // (U = valHi - valLo + 1)
    SortedRunsMinOrHashSeq(const vector<T>& arr, long long valLo, long long valHi) : vlo(valLo),
        vhi(valHi) { buildFrom(arr); }

    // (a new, empty one: same pool, same value range)
    SortedRunsMinOrHashSeq makeEmpty() const { return SortedRunsMinOrHashSeq({}, vlo, vhi); }

    void buildFrom(const vector<T>& arr) {
        n = (int)arr.size();
        grow(n);
        vector<int> st;  // O(N) build: the treap's right spine
        for (const T& v : arr) {
            int x = run(leaf(v), 1, false), last = 0;
            while (!st.empty() && rn[st.back()].TP < rn[x].TP) last = st.back(), st.pop_back(), tpull(last);
            rn[x].TL = last;
            if (!st.empty()) rn[st.back()].TR = x;
            st.push_back(x);
        }
        for (int i = (int)st.size() - 1; i >= 0; i--) tpull(st[i]);
        rt = st.empty() ? 0 : st[0];
    }

    // O(1) -- the current length
    int size() const { return n; }

    // O(log N + log U) expected -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        for (int x = rt;;) {
            push(x);
            int ls = rn[rn[x].TL].TS;
            if (i < ls) x = rn[x].TL;
            else if (i < ls + rn[x].TN) {
                int k = i - ls;
                return kth(rn[x].TV, rn[x].TD ? rn[x].TN - k : k + 1);
            } else i -= ls + rn[x].TN, x = rn[x].TR;
        }
    }

    // O(log N + log U) amortized -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        rangeAssign(i, i, v);
    }

    // O(log N + log U) amortized -- a[i] += v; needs 0 <= i < size(), else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAdd: needs 0 <= i < size()");
        pointAssign(i, pointGet(i) + v);
    }

    // O(log N + log U) amortized -- a[i] = max(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmax: needs 0 <= i < size()");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(log N + log U) amortized -- a[i] = min(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmin: needs 0 <= i < size()");
        if (v < pointGet(i)) pointAssign(i, v);
    }

    // O(log N + log U) amortized -- sort a[l..r] ascending; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeSortAsc(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeSortAsc: needs 0 <= l <= r < size()");
        sortRange(l, r, false);
    }

    // O(log N + log U) amortized -- sort a[l..r] descending; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeSortDesc(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeSortDesc: needs 0 <= l <= r < size()");
        sortRange(l, r, true);
    }

    // O(log N + log U) amortized -- a[i] = v for i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeAssign(int l, int r, T v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        auto [A, B, C] = extract(l, r);
        drop(B);
        join(A, run(leaf(v, r - l + 1), r - l + 1, false), C);
    }

    // O(log N + log U) amortized -- reverse a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeReverse(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReverse: needs 0 <= l <= r < size()");
        auto [A, B, C] = extract(l, r);
        rev(B);
        join(A, B, C);
    }

    // O(log N + log U) amortized -- insert v so it becomes a[i]; needs 0 <= i <= size(), else throws out_of_range (i
    // = size() appends)
    void insertAt(int i, T v) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        insertCopiesAt(i, v, 1);
    }

    // O(log N + log U) amortized -- insert k copies of v starting at index i (needs 0 <= i <= size(), else throws
    // out_of_range; k <= 0 does nothing)
    void insertCopiesAt(int i, T v, long long k) {
        if (i < 0 || i > size()) throw out_of_range("insertCopiesAt: needs 0 <= i <= size()");
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

    // O(log N + log U) amortized -- remove a[l..r] and return it as one of its own (indices from 0); needs
    // 0 <= l <= r < size(), else throws out_of_range
    SortedRunsMinOrHashSeq cut(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("cut: needs 0 <= l <= r < size()");
        auto [A, B, C] = extract(l, r);
        rt = tmerge(A, C), n -= r - l + 1;
        SortedRunsMinOrHashSeq piece = makeEmpty();
        piece.rt = B, piece.n = r - l + 1;
        return piece;
    }

    // O(log N + log U) amortized -- insert all of other (one with the same valLo / valHi, e.g. a cut piece) so it
    // starts at a[i] (needs 0 <= i <= size(), else throws out_of_range); other is left empty
    void paste(int i, SortedRunsMinOrHashSeq& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        n += other.n;
        grow(n);  // (before the merge reads the powers)
        auto [A, C] = tsplit(rt, i);
        rt = tmerge(tmerge(A, other.rt), C), other.rt = other.n = 0;
    }

    // O(log N + log U) amortized -- append all of other at the end, leaving it empty (it must share this one's nodes)
    void merge(SortedRunsMinOrHashSeq& other) { paste(n, other); }

    // O(log N + log U) amortized -- (a[0..k-1], a[k..]) as two of their own; this one is left empty; needs
    // 0 <= k <= size(), else throws out_of_range
    pair<SortedRunsMinOrHashSeq, SortedRunsMinOrHashSeq> split(int k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        SortedRunsMinOrHashSeq left = makeEmpty(), right = makeEmpty();
        tie(left.rt, right.rt) = tsplit(rt, k);
        left.n = k, right.n = n - k, rt = n = 0;
        return {left, right};
    }

    // O(log N + log U) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three of their own; this one is left empty;
    // needs 0 <= l <= r < size(), else throws out_of_range
    tuple<SortedRunsMinOrHashSeq, SortedRunsMinOrHashSeq, SortedRunsMinOrHashSeq> trisect(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        SortedRunsMinOrHashSeq left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        tie(left.rt, mid.rt, right.rt) = extract(l, r);
        left.n = l, mid.n = r - l + 1, right.n = n - r - 1, rt = n = 0;
        return {left, mid, right};
    }

    // O(log N + log U) amortized -- rotate a[l..r] left by k (a[l + k] comes first); k can be huge or negative: it is
    // taken mod the length (negative = right); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateLeft(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateLeft: needs 0 <= l <= r < size()");
        long long m = r - l + 1;
        k = ((k % m) + m) % m;
        if (!k) return;
        auto [A, B, C] = extract(l, r);
        auto [X, Y] = tsplit(B, (int)k);
        join(A, tmerge(Y, X), C);
    }

    // O(log N + log U) amortized -- rotate a[l..r] right by k; k can be huge or negative: it is taken mod the length
    // (negative = left); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateRight(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -k);
    }

    // O(log N + log U) amortized -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMin(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMin: needs 0 <= l <= r < size()");
        auto [A, B, C] = extract(l, r);
        T res = rn[B].Smn;
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- a[l] | ... | a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeOrQuery(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeOrQuery: needs 0 <= l <= r < size()");
        auto [A, B, C] = extract(l, r);
        T res = rn[B].Sov;
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- is a[l..r] a palindrome?; needs 0 <= l <= r < size(), else throws out_of_range
    bool isPalindrome(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("isPalindrome: needs 0 <= l <= r < size()");
        auto [A, B, C] = extract(l, r);
        bool res = rn[B].Sfh == rn[B].Sbh;
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- hash of a[l..r] read left to right (a[l] B^(len-1) + ... + a[r], mod 2^61 - 1; B
    // random per run): equal ranges hash equal; needs 0 <= l <= r < size(), else throws out_of_range
    unsigned long long rangeHash(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHash: needs 0 <= l <= r < size()");
        auto [A, B, C] = extract(l, r);
        unsigned long long res = rn[B].Sfh;
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs
    // 0 <= l <= r < size(), else throws out_of_range
    unsigned long long rangeHashReversed(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHashReversed: needs 0 <= l <= r < size()");
        auto [A, B, C] = extract(l, r);
        unsigned long long res = rn[B].Sbh;
        join(A, B, C);
        return res;
    }

    // O(log N + log U) amortized -- a[l1..r1] == a[l2..r2]? (equal lengths and equal hashes); needs
    // 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), else throws out_of_range
    bool rangesEqual(int l1, int r1, int l2, int r2) {
        if (l1 < 0 || l1 > r1 || r1 >= size() || l2 < 0 || l2 > r2 || r2 >= size())
            throw out_of_range("rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size()");
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(N log U) -- the whole current array
    vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        vector<int> st;
        for (int x = rt; !st.empty() || x;) {
            for (; x; x = rn[x].TL) push(x), st.push_back(x);
            x = st.back();
            st.pop_back();
            values(rn[x].TV, rn[x].TD, out);
            x = rn[x].TR;
        }
        return out;
    }

    // O(log(N)+log(U) amortized) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    T pop() {
        auto n = size();
        if (n < 1) throw out_of_range("pop: needs size() >= 1");
        T v = pointGet(n - 1);
        cut(n - 1, n - 1);
        return v;
    }

    // O(log(N)+log(U) amortized) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else
    // throws out_of_range
    T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        T v = pointGet(0);
        cut(0, 0);
        return v;
    }

    // O(log^2(N)+log(N)*log(U) amortized) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i,
    // i)): a binary search on
    // its radius, log N calls of isPalindrome; needs 0 <= i < n, else throws out_of_range
    pair<long long, long long> longestPalCenteredAtI(long long i) {
        long long len = size();
        if (i < 0 || i >= len) throw out_of_range("longestPalCenteredAtI: needs 0 <= i < n");
        long long lo = 0, hi = min(i, len - 1 - i);
        while (lo < hi) {
            long long mid = (lo + hi + 1) / 2;
            if (isPalindrome(i - mid, i + mid)) lo = mid;
            else hi = mid - 1;
        }
        return {i - lo, i + lo};
    }

    // O(log^2(N)+log(N)*log(U) amortized) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and
    // a[i+1]; (i + 1, i), the empty
    // range, when there is none (so also for i = n - 1): a binary search on its radius, log N calls of isPalindrome;
    // needs 0 <= i < n, else throws out_of_range
    pair<long long, long long> longestPalCenteredAtIPlusOne(long long i) {
        long long len = size();
        if (i < 0 || i >= len) throw out_of_range("longestPalCenteredAtIPlusOne: needs 0 <= i < n");
        long long lo = 0, hi = min(i + 1, len - 1 - i);
        while (lo < hi) {
            long long mid = (lo + hi + 1) / 2;
            if (isPalindrome(i - mid + 1, i + mid)) lo = mid;
            else hi = mid - 1;
        }
        return {i - lo + 1, i + lo};
    }

    // O(log(N)+log(U) amortized) -- hash of the whole array a[0..n-1]: the same base and mod as rangeHash (shared by
    // every structure
    // this run, so it compares with another one's hashes); needs n >= 1, else throws out_of_range
    auto hashAll() {
        if (size() < 1) throw out_of_range("hashAll: needs n >= 1");
        return rangeHash(0, size() - 1);
    }

    // O(log(N)+log(U) amortized) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws
    // out_of_range
    auto minAll() {
        if (size() < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, size() - 1);
    }

    // O(log(N)+log(U) amortized) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else throws
    // out_of_range
    auto orAll() {
        if (size() < 1) throw out_of_range("orAll: needs n >= 1");
        return rangeOrQuery(0, size() - 1);
    }

    // O(log(N)+log(U) amortized) -- hash of the whole array reversed, a[n-1], ..., a[0] (rangeHashReversed(0, n - 1));
    // it uses the same base and mod as rangeHash, so it equals rangeHash of any range holding those values in that
    // order (and any structure's hashes this run); needs n >= 1, else throws out_of_range
    auto hashAllReversed() {
        if (size() < 1) throw out_of_range("hashAllReversed: needs n >= 1");
        return rangeHashReversed(0, size() - 1);
    }

    // ---- internals: the treap of runs ----

    // a new run node: value tree t, length ln, descending?
    int run(int t, int ln, bool d) {
        int x;
        if (!tfree.empty()) x = tfree.back(), tfree.pop_back(), rn[x].TL = rn[x].TR = 0, rn[x].TF = 0;
        else {
            x = (int)rn.size();
            Run n;
            n.TL = 0, n.TR = 0, n.TV = 0, n.TN = 0, n.TS = 0, n.TP = 0, n.TD = 0, n.TF = 0,
            n.Omn = numeric_limits<T>::max(), n.Smn = numeric_limits<T>::max(), n.Sov = T(0), n.Sfh = 0, n.Sbh = 0;
            rn.push_back(n);
        }
        rn[x].TP = rnd(), rn[x].TV = t, rn[x].TN = ln, rn[x].TD = d;
        rn[x].Omn = kth(t, 1);
        tpull(x);
        return x;
    }

    void tpull(int x) {
        int L = rn[x].TL, R = rn[x].TR, t = rn[x].TV;
        rn[x].TS = rn[L].TS + rn[x].TN + rn[R].TS;
        rn[x].Smn = min(rn[x].Omn, min(rn[L].Smn, rn[R].Smn));
        rn[x].Sov = rn[L].Sov | vn[t].ov | rn[R].Sov;
        // the run, read left to right / right to left
        unsigned long long f = rn[x].TD ? vn[t].bh : vn[t].fh, b = rn[x].TD ? vn[t].fh : vn[t].bh;
        rn[x].Sfh = hadd(hmul(hadd(hmul(rn[L].Sfh, pw[rn[x].TN]), f), pw[rn[R].TS]), rn[R].Sfh);
        rn[x].Sbh = hadd(hmul(hadd(hmul(rn[R].Sbh, pw[rn[x].TN]), b), pw[rn[L].TS]), rn[L].Sbh);
    }

    void rev(int x) {  // reverse x's subtree: swap its children (and below, lazily), flip its run
        if (x) swap(rn[x].TL, rn[x].TR), rn[x].TD ^= 1, swap(rn[x].Sfh, rn[x].Sbh), rn[x].TF ^= 1;
    }

    void push(int x) {
        if (rn[x].TF) rev(rn[x].TL), rev(rn[x].TR), rn[x].TF = 0;
    }

    // (the first k elements, the rest), cutting the run that straddles k
    pair<int, int> tsplit(int x, int k) {
        if (!x || k <= 0) return {0, x};
        if (k >= rn[x].TS) return {x, 0};
        push(x);
        int ls = rn[rn[x].TL].TS;
        if (k <= ls) {
            auto [a, b] = tsplit(rn[x].TL, k);
            rn[x].TL = b;
            tpull(x);
            return {a, x};
        }
        if (k >= ls + rn[x].TN) {
            auto [a, b] = tsplit(rn[x].TR, k - ls - rn[x].TN);
            rn[x].TR = a;
            tpull(x);
            return {x, b};
        }
        k -= ls;  // cut this run: x keeps its first k elements, a new node the rest
        int t = rn[x].TV, ln = rn[x].TN, a, b;
        if (rn[x].TD) split(t, ln - k, vlo, vhi, b, a);  // the first k are the k largest
        else split(t, k, vlo, vhi, a, b);
        rn[x].TV = a, rn[x].TN = k;
        rn[x].Omn = kth(a, 1);
        int u = run(b, ln - k, rn[x].TD), R = rn[x].TR;
        rn[x].TR = 0;
        tpull(x);
        return {x, tmerge(u, R)};
    }

    int tmerge(int a, int b) {
        if (!a || !b) return a ? a : b;
        if (rn[a].TP > rn[b].TP) {
            push(a);
            int r = tmerge(rn[a].TR, b);
            rn[a].TR = r;
            tpull(a);
            return a;
        }
        push(b);
        int l = tmerge(a, rn[b].TL);
        rn[b].TL = l;
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
            if (rn[y].TL) st.push_back(rn[y].TL);
            if (rn[y].TR) st.push_back(rn[y].TR);
        }
        return out;
    }

    void drop(int x) {  // free every run of x (value trees and treap nodes)
        for (int y : nodes(x)) freeTree(rn[y].TV), tfree.push_back(y);
    }

    // a[l..r] becomes one sorted run: every run inside merges into one
    void sortRange(int l, int r, bool d) {
        auto [A, B, C] = extract(l, r);
        int t = 0;
        for (int y : nodes(B)) t = merge(t, rn[y].TV, vlo, vhi), tfree.push_back(y);
        join(A, run(t, r - l + 1, d), C);
    }

    // ---- internals: value trees (node 0 = the empty tree) ----

    int node() {
        if (!freeList.empty()) {
            int t = freeList.back();
            freeList.pop_back();
            vn[t].Lc = vn[t].Rc = 0, vn[t].cnt = 0;
            return t;
        }
        VNode n;
        n.Lc = 0, n.Rc = 0, n.cnt = 0, n.ov = T(0), n.fh = 0, n.bh = 0;
        vn.push_back(n);
        return (int)vn.size() - 1;
    }

    void freeTree(int t) {  // hand every node of t back
        vector<int> st;
        if (t) st.push_back(t);
        while (!st.empty()) {
            int u = st.back();
            st.pop_back();
            freeList.push_back(u);
            if (vn[u].Lc) st.push_back(vn[u].Lc);
            if (vn[u].Rc) st.push_back(vn[u].Rc);
        }
    }

    // node x holds c copies of v (a leaf, or a node with one value under it)
    void setLeaf(int x, long long v, long long c) {
        vn[x].cnt = c;
        vn[x].ov = T(v);
        vn[x].fh = vn[x].bh = hmul(hval(T(v)), gs[c]);
    }

    void pull(int x) {
        int l = vn[x].Lc, r = vn[x].Rc;
        vn[x].cnt = vn[l].cnt + vn[r].cnt;
        vn[x].ov = vn[l].ov | vn[r].ov;
        vn[x].fh = hadd(hmul(vn[l].fh, pw[vn[r].cnt]), vn[r].fh);
        vn[x].bh = hadd(hmul(vn[r].bh, pw[vn[l].cnt]), vn[l].bh);
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
            if ((long long)v <= mid) vn[t].Lc = u, nh = mid;
            else vn[t].Rc = u, nl = mid + 1;
            t = u;
        }
    }

    // O(logN + logU) amortized -- a = the k smallest of t, b = the rest (0 <= k <= cnt[t]); t keeps the first part, new
    // nodes (one path) the second
    void split(int t, long long k, long long nl, long long nh, int& a, int& b) {
        if (k <= 0) { a = 0, b = t; return; }
        if (k >= vn[t].cnt) { a = t, b = 0; return; }
        int nb = node();
        if (nl == nh) {  // one value: split its copies
            setLeaf(nb, nl, vn[t].cnt - k), setLeaf(t, nl, k);
            a = t, b = nb;
            return;
        }
        long long mid = nl + (nh - nl) / 2, cl = vn[vn[t].Lc].cnt;
        int x, y;
        if (k <= cl) {
            split(vn[t].Lc, k, nl, mid, x, y);
            vn[t].Lc = x, vn[nb].Lc = y, vn[nb].Rc = vn[t].Rc, vn[t].Rc = 0;
        } else {
            split(vn[t].Rc, k - cl, mid + 1, nh, x, y);
            vn[t].Rc = x, vn[nb].Rc = y;
        }
        pull(t), pull(nb);
        a = t, b = nb;
    }

    // O(logN + logU) amortized -- the union of a and b, overlaid node by node (b's nodes where both have one are freed)
    int merge(int a, int b, long long nl, long long nh) {
        if (!a || !b) return a ? a : b;
        if (nl == nh) {
            setLeaf(a, nl, vn[a].cnt + vn[b].cnt);
        } else {
            long long mid = nl + (nh - nl) / 2;
            int x = merge(vn[a].Lc, vn[b].Lc, nl, mid);
            vn[a].Lc = x;
            int y = merge(vn[a].Rc, vn[b].Rc, mid + 1, nh);
            vn[a].Rc = y;
            pull(a);
        }
        freeList.push_back(b);
        return a;
    }

    // the k-th smallest value of t, 1 <= k <= cnt[t]
    T kth(int t, long long k) const {
        long long nl = vlo, nh = vhi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, cl = vn[vn[t].Lc].cnt;
            if (k <= cl) t = vn[t].Lc, nh = mid;
            else k -= cl, t = vn[t].Rc, nl = mid + 1;
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
            if (!vn[u].cnt) continue;
            if (nl == nh) {
                out.insert(out.end(), vn[u].cnt, T(nl));
                continue;
            }
            long long mid = nl + (nh - nl) / 2;
            st.push_back({vn[u].Rc, mid + 1, nh}), st.push_back({vn[u].Lc, nl, mid});
        }
        if (d) reverse(out.begin() + from, out.end());
    }
};

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     SortedRunsMinOrHashSeq<int> t({1, 2, 3, 4, 5}, 1, 5);
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
