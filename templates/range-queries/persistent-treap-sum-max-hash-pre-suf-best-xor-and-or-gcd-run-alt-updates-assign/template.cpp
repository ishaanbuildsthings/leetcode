// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-treap-sum-max-hash-pre-suf-best-xor-and-or-gcd-run-alt-updates-assign/template.cpp
// @operations: append appendLeft copy cut getAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX leftmostPrefixSumGtX leftmostPrefixSumGteX longestEqualRun maxAltSubseqSum maxPrefixSum maxSubarraySum maxSuffixSum merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeAssign rangeGcd rangeHash rangeHashReversed rangeMax rangeOrQuery rangeRotateLeft rangeRotateRight rangeSum rangeXorQuery rangesEqual rightmostGtX rightmostGteX rightmostSuffixSumGtX rightmostSuffixSumGteX split trisect
// @data-structure-type: persistent-treap
// @complexities:
//   append: log(N)*log(U) expected ?
//   appendLeft: log(N)*log(U) expected ?
//   copy: log(N)*log(U) expected ?
//   cut: log(N)*log(U) expected ?
//   getAll: N
//   insertAt: log(N)*log(U) expected ?
//   insertCopiesAt: log(N)*log(U) expected ?
//   isPalindrome: log(N)*log(U) expected ?
//   leftmostGtX: log(N)*log(U) expected ?
//   leftmostGteX: log(N)*log(U) expected ?
//   leftmostPrefixSumGtX: log(N)*log(U) expected ?
//   leftmostPrefixSumGteX: log(N)*log(U) expected ?
//   longestEqualRun: log(N)*log(U) expected ?
//   maxAltSubseqSum: log(N)*log(U) expected ?
//   maxPrefixSum: log(N)*log(U) expected ?
//   maxSubarraySum: log(N)*log(U) expected ?
//   maxSuffixSum: log(N)*log(U) expected ?
//   merge: log(N)*log(U) expected ?
//   paste: log(N)*log(U) expected ?
//   pointAdd: log(N)*log(U) expected ?
//   pointAssign: log(N)*log(U) expected ?
//   pointChmax: log(N)*log(U) expected ?
//   pointChmin: log(N)*log(U) expected ?
//   pointGet: log(N) expected
//   rangeAndQuery: log(N)*log(U) expected ?
//   rangeAssign: log(N)*log(U) expected ?
//   rangeGcd: log(N)*log(U) expected ?
//   rangeHash: log(N)*log(U) expected ?
//   rangeHashReversed: log(N)*log(U) expected ?
//   rangeMax: log(N)*log(U) expected ?
//   rangeOrQuery: log(N)*log(U) expected ?
//   rangeRotateLeft: log(N)*log(U) expected ?
//   rangeRotateRight: log(N)*log(U) expected ?
//   rangeSum: log(N)*log(U) expected ?
//   rangeXorQuery: log(N)*log(U) expected ?
//   rangesEqual: log(N)*log(U) expected ?
//   rightmostGtX: log(N)*log(U) expected ?
//   rightmostGteX: log(N)*log(U) expected ?
//   rightmostSuffixSumGtX: log(N)*log(U) expected ?
//   rightmostSuffixSumGteX: log(N)*log(U) expected ?
//   split: log(N)*log(U) expected ?
//   trisect: log(N)*log(U) expected ?
//   build: N*log(U) ?
// @memory:
//   layout: none
//   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] sm[1*N*log(N)] mx[1*N*log(N)] fh[1*N*log(N)] bh[1*N*log(N)] pw[1*N*log(N)] gs[1*N*log(N)] pre[1*N*log(N)] suf[1*N*log(N)] best[1*N*log(N)] xr[1*N*log(N)] an[1*N*log(N)] orr[1*N*log(N)] g[1*N*log(N)] fv[1*N*log(N)] lv[1*N*log(N)] pr[1*N*log(N)] sr[1*N*log(N)] br[1*N*log(N)] a00[1*N*log(N)] a01[1*N*log(N)] a10[1*N*log(N)] a11[1*N*log(N)]
//   tags: asg[1*N*log(N)] hasAsg[1*N*log(N)]
//   other: none
//   note: nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and copies share every node they don't change; log(N) is of the length, which can be huge (long long)

// Persistent implicit treap with composable aggregates: an array you can insert into anywhere, rotate, cut pieces out
// of (that is how to erase), paste them back and copy (copy(l, r): a[l..r] as a treap of its own in O(logN) however
// long, since the copy shares the same nodes; this one is unchanged), with rangeAssign; each node keeps its sum, its
// max, its forward / backward hash (and B^size), its best prefix sum, its best suffix sum, its best subarray sum, its
// xor, its AND, its OR, its gcd, its first / last value and the equal runs at its ends and inside, its best
// alternating (+ - + ...) subsequence sum for each start / end sign over its subtree. No node changes once another
// tree can see it: an op copies the nodes on its paths, so a copy and its original never affect each other. Lengths
// and indices are long long. All indices 0-based, ranges inclusive [l, r], an index always the position in the
// CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this node, not yet to
// its children".
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct PersistentTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    // one node pool shared by every PersistentTreap<T>: cut / paste move nodes between them, so a piece from one can
    // go into any other (node 0 = the empty tree). Nodes are never freed (memory = O(log N) per op, over the whole
    // run), so there is nothing to reset between test cases
    static inline vector<T> val{T(0)};
    static inline vector<int> L{0};
    static inline vector<int> R{0};
    static inline vector<long long> sz{0};
    static inline vector<S> sm{0};
    static inline vector<T> mx{T(0)};
    static inline vector<U64> fh{0};
    static inline vector<U64> bh{0};
    static inline vector<U64> pw{1};
    static inline vector<U64> gs{0};
    static inline vector<S> pre{0};
    static inline vector<S> suf{0};
    static inline vector<S> best{0};
    static inline vector<T> xr{T(0)};
    static inline vector<T> an{~T(0)};
    static inline vector<T> orr{T(0)};
    static inline vector<T> g{T(0)};
    static inline vector<T> fv{T(0)};
    static inline vector<T> lv{T(0)};
    static inline vector<long long> pr{0};
    static inline vector<long long> sr{0};
    static inline vector<long long> br{0};
    static inline vector<S> a00{0};
    static inline vector<S> a01{0};
    static inline vector<S> a10{0};
    static inline vector<S> a11{0};
    static inline vector<T> asg{T(0)};
    static inline vector<char> hasAsg{0};
    int root = 0;

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit PersistentTreap(const vector<T>& arr = {}) { root = build(arr); }

    PersistentTreap makeEmpty() const { return PersistentTreap(); }  // (a new, empty one)

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


    // O(1) -- the current length of the array
    long long size() const { return sz[root]; }

    // O(logN * logU) expected -- append v to the end
    void append(T v) { root = merge(root, newNode(v)); }

    // O(logN * logU) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(1) -- the whole array as a PersistentTreap of its own; this one is unchanged (they share nodes)
    PersistentTreap copy() const { return *this; }

    // O(logN * logU) expected -- a[l..r] as a PersistentTreap of its own; this one is unchanged. The copy shares this one's
    // nodes, so it costs O(logN) however long it is
    PersistentTreap copy(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        PersistentTreap piece = makeEmpty();
        piece.root = b;
        return piece;
    }

    // O(logN * logU) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
    PersistentTreap cut(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        root = merge(a, c);
        PersistentTreap piece = makeEmpty();
        piece.root = b;
        return piece;
    }

    // O(N) -- the whole current array, every pending tag applied on the way
    vector<T> getAll() {
        vector<T> out;
        out.reserve(size());
        vector<int> st;
        int t = root;
        while (!st.empty() || t) {
            while (t) push(t), st.push_back(t), t = L[t];
            t = st.back(), st.pop_back();
            out.push_back(val[t]);
            t = R[t];
        }
        return out;
    }

    // O(logN * logU) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(long long i, T v) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN * logU) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(long long i, T v, long long k) {
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN * logU) expected -- is a[l..r] a palindrome (its two hashes agree)
    bool isPalindrome(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        bool res = fh[b] == bh[b];
        return res;
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] > x, or -1 (pruned by the subtree max)
    long long leftmostGtX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && mx[t] > x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (L[t] && mx[L[t]] > x) t = L[t];
                else if (val[t] > x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
            }
        }
        return res;
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max)
    long long leftmostGteX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && mx[t] >= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (L[t] && mx[L[t]] >= x) t = L[t];
                else if (val[t] >= x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
            }
        }
        return res;
    }

    // O(logN * logU) expected -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (pruned by best prefix sums)
    long long leftmostPrefixSumGtX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        S acc = 0;
        if (t && pre[t] > S(x)) {
            while (true) {
                push(t);
                int lt = L[t];
                if (lt && acc + pre[lt] > S(x)) { t = lt; continue; }
                acc += sm[lt];
                if (acc + S(val[t]) > S(x)) { res = l + i + sz[lt]; break; }
                acc += S(val[t]), i += sz[lt] + 1, t = R[t];
            }
        }
        return res;
    }

    // O(logN * logU) expected -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (pruned by best prefix sums)
    long long leftmostPrefixSumGteX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        S acc = 0;
        if (t && pre[t] >= S(x)) {
            while (true) {
                push(t);
                int lt = L[t];
                if (lt && acc + pre[lt] >= S(x)) { t = lt; continue; }
                acc += sm[lt];
                if (acc + S(val[t]) >= S(x)) { res = l + i + sz[lt]; break; }
                acc += S(val[t]), i += sz[lt] + 1, t = R[t];
            }
        }
        return res;
    }

    // O(logN * logU) expected -- the longest run of equal adjacent values in a[l..r]
    long long longestEqualRun(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        int res = br[b];
        return res;
    }

    // O(logN * logU) expected -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]
    S maxAltSubseqSum(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = max(a00[b], a01[b]);
        return res;
    }

    // O(logN * logU) expected -- max of a[l] + ... + a[i] over i in [l, r]
    S maxPrefixSum(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = pre[b];
        return res;
    }

    // O(logN * logU) expected -- max sum of a non-empty contiguous subarray of a[l..r]
    S maxSubarraySum(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = best[b];
        return res;
    }

    // O(logN * logU) expected -- max of a[i] + ... + a[r] over i in [l, r]
    S maxSuffixSum(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = suf[b];
        return res;
    }

    // O(logN * logU) expected -- append all of other at the end; other is left empty
    void merge(PersistentTreap& other) { root = merge(root, other.root), other.root = 0; }
    void merge(PersistentTreap&& other) { merge(other); }  // (a temporary: merge(t.copy()))

    // O(logN * logU) expected -- insert all of other (any PersistentTreap, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(long long i, PersistentTreap& other) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }
    void paste(long long i, PersistentTreap&& other) { paste(i, other); }  // (a temporary: paste(i, t.copy(l, r)))

    // O(logN * logU) expected -- a[i] += v
    void pointAdd(long long i, T v) {
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        val[b] = T(val[b] + v);
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN * logU) expected -- a[i] = v
    void pointAssign(long long i, T v) {
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        val[b] = v;
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN * logU) expected -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) {
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        val[b] = max(val[b], v);
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN * logU) expected -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) {
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        val[b] = min(val[b], v);
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i]
    T pointGet(long long i) { return val[locate(i)]; }

    // O(logN * logU) expected -- a[l] & ... & a[r]
    T rangeAndQuery(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = an[b];
        return res;
    }

    // O(logN * logU) expected -- a[i] = v for i in [l, r]
    void rangeAssign(long long l, long long r, T v) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyAssign(b, v);
        root = merge(merge(a, b), c);
    }

    // O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|
    T rangeGcd(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = g[b];
        return res;
    }

    // O(logN * logU) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal
    U64 rangeHash(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        U64 res = fh[b];
        return res;
    }

    // O(logN * logU) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    U64 rangeHashReversed(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        U64 res = bh[b];
        return res;
    }

    // O(logN * logU) expected -- max of a[l..r]
    T rangeMax(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = mx[b];
        return res;
    }

    // O(logN * logU) expected -- a[l] | ... | a[r]
    T rangeOrQuery(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = orr[b];
        return res;
    }

    // O(logN * logU) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    // it is taken mod the length (negative shifts right)
    void rangeRotateLeft(long long l, long long r, long long k) {
        int a, b, c;
        long long len = r - l + 1;
        cut(l, r, a, b, c);
        k = ((k % len) + len) % len;
        if (k) {
            int b1, b2;
            split(b, k, b1, b2);
            b = merge(b2, b1);
        }
        root = merge(merge(a, b), c);
    }

    // O(logN * logU) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left)
    void rangeRotateRight(long long l, long long r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(logN * logU) expected -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = sm[b];
        return res;
    }

    // O(logN * logU) expected -- a[l] ^ ... ^ a[r]
    T rangeXorQuery(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = xr[b];
        return res;
    }

    // O(logN * logU) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    bool rangesEqual(long long l1, long long r1, long long l2, long long r2) {
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] > x, or -1 (pruned by the subtree max)
    long long rightmostGtX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && mx[t] > x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (R[t] && mx[R[t]] > x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] > x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
            }
        }
        return res;
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max)
    long long rightmostGteX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && mx[t] >= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (R[t] && mx[R[t]] >= x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] >= x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
            }
        }
        return res;
    }

    // O(logN * logU) expected -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (pruned by best suffix sums)
    long long rightmostSuffixSumGtX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        S acc = 0;
        if (t && suf[t] > S(x)) {
            while (true) {
                push(t);
                int rt = R[t];
                if (rt && acc + suf[rt] > S(x)) { i += sz[L[t]] + 1, t = rt; continue; }
                acc += sm[rt];
                if (acc + S(val[t]) > S(x)) { res = l + i + sz[L[t]]; break; }
                acc += S(val[t]), t = L[t];
            }
        }
        return res;
    }

    // O(logN * logU) expected -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (pruned by best suffix sums)
    long long rightmostSuffixSumGteX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        S acc = 0;
        if (t && suf[t] >= S(x)) {
            while (true) {
                push(t);
                int rt = R[t];
                if (rt && acc + suf[rt] >= S(x)) { i += sz[L[t]] + 1, t = rt; continue; }
                acc += sm[rt];
                if (acc + S(val[t]) >= S(x)) { res = l + i + sz[L[t]]; break; }
                acc += S(val[t]), t = L[t];
            }
        }
        return res;
    }

    // O(logN * logU) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    pair<PersistentTreap, PersistentTreap> split(long long k) {
        PersistentTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN * logU) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    tuple<PersistentTreap, PersistentTreap, PersistentTreap> trisect(long long l, long long r) {
        PersistentTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cut(l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), L.push_back(0), R.push_back(0), sz.push_back(1);
        sm.push_back(S(v)), mx.push_back(v), fh.push_back(hval(v)), bh.push_back(hval(v)), pw.push_back(HB());
        gs.push_back(1), pre.push_back(S(v)), suf.push_back(S(v)), best.push_back(S(v)), xr.push_back(v);
        an.push_back(v), orr.push_back(v), g.push_back(v < T(0) ? T(-v) : v), fv.push_back(v), lv.push_back(v);
        pr.push_back(1), sr.push_back(1), br.push_back(1), a00.push_back(S(v)), a01.push_back(NEG);
        a10.push_back(NEG), a11.push_back(-S(v)), asg.push_back(T(0)), hasAsg.push_back(0);
        return (int)val.size() - 1;
    }

    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
    }

    int build(const vector<T>& vals) { return build(vals, 0, (int)vals.size()); }

    int build(const vector<T>& vals, int lo, int hi) {  // a balanced tree of new nodes holding vals[lo, hi), O(len)
        if (lo >= hi) return 0;
        int mid = (lo + hi) / 2, x = newNode(vals[mid]);
        int l = build(vals, lo, mid), r = build(vals, mid + 1, hi);
        L[x] = l, R[x] = r;
        pull(x);
        return x;
    }

    int clone(int x) {  // a new copy of node x (sharing its children)
        val.push_back(val[x]);
        L.push_back(L[x]);
        R.push_back(R[x]);
        sz.push_back(sz[x]);
        sm.push_back(sm[x]);
        mx.push_back(mx[x]);
        fh.push_back(fh[x]);
        bh.push_back(bh[x]);
        pw.push_back(pw[x]);
        gs.push_back(gs[x]);
        pre.push_back(pre[x]);
        suf.push_back(suf[x]);
        best.push_back(best[x]);
        xr.push_back(xr[x]);
        an.push_back(an[x]);
        orr.push_back(orr[x]);
        g.push_back(g[x]);
        fv.push_back(fv[x]);
        lv.push_back(lv[x]);
        pr.push_back(pr[x]);
        sr.push_back(sr[x]);
        br.push_back(br[x]);
        a00.push_back(a00[x]);
        a01.push_back(a01[x]);
        a10.push_back(a10[x]);
        a11.push_back(a11[x]);
        asg.push_back(asg[x]);
        hasAsg.push_back(hasAsg[x]);
        return (int)val.size() - 1;
    }

    void pull(int x) {  // recompute x from its children
        int l = L[x], r = R[x];
        sz[x] = sz[l] + sz[r] + 1;
        T v = val[x];
        S s = S(v), p = S(v), q = S(v), b = S(v);  // the node alone, then with its left / right parts
        if (l) {
            S ls = sm[l], lp = pre[l], lq = suf[l], lb = best[l];
            S ns = ls + s, np = max(lp, ls + p), nq = max(q, s + lq), nb = max({lb, b, lq + p});
            s = ns, p = np, q = nq, b = nb;
        }
        if (r) {
            S rs = sm[r], rp = pre[r], rq = suf[r], rb = best[r];
            S ns = s + rs, np = max(p, s + rp), nq = max(rq, rs + q), nb = max({b, rb, q + rp});
            s = ns, p = np, q = nq, b = nb;
        }
        sm[x] = s, pre[x] = p, suf[x] = q, best[x] = b;
        mx[x] = v;
        if (l && mx[l] > mx[x]) mx[x] = mx[l];
        if (r && mx[r] > mx[x]) mx[x] = mx[r];
        U64 B = HB(), hv = hval(v);
        pw[x] = hmul(hmul(pw[l], B), pw[r]);
        gs[x] = hadd(hmul(hadd(hmul(gs[l], B), 1), pw[r]), gs[r]);
        fh[x] = hadd(hmul(hadd(hmul(fh[l], B), hv), pw[r]), fh[r]);
        bh[x] = hadd(hmul(hadd(hmul(bh[r], B), hv), pw[l]), bh[l]);
        xr[x] = xr[l] ^ v ^ xr[r];
        an[x] = an[l] & v & an[r];  // (node 0: the AND of nothing, ~0)
        orr[x] = orr[l] | v | orr[r];
        g[x] = gcd(gcd(g[l], v), g[r]);
        long long rp = 1, rq = 1, bb = 1;
        if (l) {
            bool j = lv[l] == v;
            rp = pr[l] + (j && pr[l] == sz[l]);
            rq = j ? sr[l] + 1 : 1;
            bb = max(br[l], rq);
        }
        if (r) {
            bool j = v == fv[r];
            bb = max({bb, br[r], j ? rq + pr[r] : 0});
            if (j && rp == sz[l] + 1) rp += pr[r];
            rq = j && sr[r] == sz[r] ? sr[r] + rq : sr[r];
        }
        pr[x] = rp, sr[x] = rq, br[x] = bb;
        fv[x] = l ? fv[l] : v;
        lv[x] = r ? lv[r] : v;
        array<S, 4> c{S(v), NEG, NEG, -S(v)};
        if (l) c = altJoin({a00[l], a01[l], a10[l], a11[l]}, c);
        if (r) c = altJoin(c, {a00[r], a01[r], a10[r], a11[r]});
        a00[x] = c[0], a01[x] = c[1], a10[x] = c[2], a11[x] = c[3];
    }

    void applyAssign(int x, T v) {  // every value of x's subtree becomes v
        if (!x) return;
        long long n = sz[x];
        val[x] = v;
        sm[x] = S(v) * n;
        mx[x] = v;
        an[x] = v;
        orr[x] = v;
        fh[x] = bh[x] = hmul(hval(v), gs[x]);
        pre[x] = suf[x] = best[x] = v > T(0) ? S(v) * n : S(v);
        xr[x] = n & 1 ? v : T(0);
        g[x] = v < T(0) ? T(-v) : v;
        fv[x] = lv[x] = v;
        pr[x] = sr[x] = br[x] = n;
        a00[x] = S(v), a11[x] = -S(v), a01[x] = a10[x] = n > 1 ? S(0) : NEG;
        asg[x] = v, hasAsg[x] = 1;
    }

    void push(int x) {  // hand x's pending tags to its children
        if (!(hasAsg[x])) return;
        if (L[x]) L[x] = clone(L[x]);  // (the children get tags: fresh copies of them, since other trees may share them)
        if (R[x]) R[x] = clone(R[x]);
        if (hasAsg[x]) applyAssign(L[x], asg[x]), applyAssign(R[x], asg[x]), hasAsg[x] = 0;
    }

    void split(int t, long long k, int& a, int& b) {  // a = first k of t, b = the rest, as new nodes (t's are left as they were)
        if (!t) { a = b = 0; return; }
        t = clone(t);
        push(t);
        int x, y;  // (not straight into L[t] / R[t]: the clones below may move those arrays)
        if (sz[L[t]] >= k) split(L[t], k, x, y), L[t] = y, a = x, b = t;
        else split(R[t], k - sz[L[t]] - 1, x, y), R[t] = x, a = t, b = y;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's, as new nodes; the root is a with probability |a| / (|a| + |b|)
        if (!a || !b) return a | b;
        if (rnd() % (unsigned long long)(sz[a] + sz[b]) < (unsigned long long)sz[a]) {
            a = clone(a);
            push(a);
            R[a] = merge(R[a], b);
            pull(a);
            return a;
        }
        b = clone(b);
        push(b);
        L[b] = merge(a, L[b]);
        pull(b);
        return b;
    }

    void cut(long long l, long long r, int& a, int& b, int& c) {  // a[0..l-1], a[l..r], a[r+1..]
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    int locate(long long i) {  // the node holding a[i], every tag on the way pushed (harmless in place: see the top)
        int t = root;
        while (true) {
            push(t);
            long long ls = sz[L[t]];
            if (i == ls) return t;
            if (i < ls) t = L[t];
            else i -= ls + 1, t = R[t];
        }
    }
};

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     PersistentTreap<int> t({1, 2, 3, 4, 5});
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
