// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-min-max-hash-pre-suf-best-npre-nsuf-xor-and-or-gcd-run-alt-updates-assign-rev/template.cpp
// @operations: append appendLeft cut getAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX leftmostLtX leftmostLteX leftmostPrefixSumGtX leftmostPrefixSumGteX longestEqualRun maxAltSubseqSum maxPrefixSum maxSubarraySum maxSuffixSum merge minPrefixSum minSuffixSum paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeAssign rangeGcd rangeHash rangeHashReversed rangeMax rangeMin rangeOrQuery rangeReverse rangeRotateLeft rangeRotateRight rangeSum rangeXorQuery rangesEqual rightmostGtX rightmostGteX rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX split trisect
// @data-structure-type: treap
// @complexities:
//   append: log(N)*log(U) expected ?
//   appendLeft: log(N)*log(U) expected ?
//   cut: log(N)*log(U) expected ?
//   getAll: N
//   insertAt: log(N)*log(U) expected ?
//   insertCopiesAt: log(N)*log(U) expected ?
//   isPalindrome: log(N)*log(U) expected ?
//   leftmostGtX: log(N)*log(U) expected ?
//   leftmostGteX: log(N)*log(U) expected ?
//   leftmostLtX: log(N)*log(U) expected ?
//   leftmostLteX: log(N)*log(U) expected ?
//   leftmostPrefixSumGtX: log(N)*log(U) expected ?
//   leftmostPrefixSumGteX: log(N)*log(U) expected ?
//   longestEqualRun: log(N)*log(U) expected ?
//   maxAltSubseqSum: log(N)*log(U) expected ?
//   maxPrefixSum: log(N)*log(U) expected ?
//   maxSubarraySum: log(N)*log(U) expected ?
//   maxSuffixSum: log(N)*log(U) expected ?
//   merge: log(N)*log(U) expected ?
//   minPrefixSum: log(N)*log(U) expected ?
//   minSuffixSum: log(N)*log(U) expected ?
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
//   rangeMin: log(N)*log(U) expected ?
//   rangeOrQuery: log(N)*log(U) expected ?
//   rangeReverse: log(N)*log(U) expected ?
//   rangeRotateLeft: log(N)*log(U) expected ?
//   rangeRotateRight: log(N)*log(U) expected ?
//   rangeSum: log(N)*log(U) expected ?
//   rangeXorQuery: log(N)*log(U) expected ?
//   rangesEqual: log(N)*log(U) expected ?
//   rightmostGtX: log(N)*log(U) expected ?
//   rightmostGteX: log(N)*log(U) expected ?
//   rightmostLtX: log(N)*log(U) expected ?
//   rightmostLteX: log(N)*log(U) expected ?
//   rightmostSuffixSumGtX: log(N)*log(U) expected ?
//   rightmostSuffixSumGteX: log(N)*log(U) expected ?
//   split: log(N)*log(U) expected ?
//   trisect: log(N)*log(U) expected ?
//   build: N*log(U) ?
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mn[1*N] mx[1*N] fh[1*N] bh[1*N] pw[1*N] gs[1*N] pre[1*N] suf[1*N] best[1*N] npre[1*N] nsuf[1*N] xr[1*N] an[1*N] orr[1*N] g[1*N] fv[1*N] lv[1*N] pr[1*N] sr[1*N] br[1*N] a00[1*N] a01[1*N] a10[1*N] a11[1*N]
//   tags: rev[1*N] asg[1*N] hasAsg[1*N]
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

// Implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, move, cut pieces
// out of (that is how to erase) and paste them back in O(logN) expected each, with rangeAssign; each node keeps its
// sum, its min, its max, its forward / backward hash (and B^size), its best prefix sum, its best suffix sum, its best
// subarray sum, its min prefix sum, its min suffix sum, its xor, its AND, its OR, its gcd, its first / last value and
// the equal runs at its ends and inside, its best alternating (+ - + ...) subsequence sum for each start / end sign
// over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array;
// searches return -1 when nothing qualifies. Lazy tags mean "already applied to this node, not yet to its children".
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        U64 fh = 0;
        U64 bh = 0;
        U64 pw = 1;
        U64 gs = 0;
        S sm = 0;
        S pre = 0;
        S suf = 0;
        S best = 0;
        S npre = 0;
        S nsuf = 0;
        S a00 = 0;
        S a01 = 0;
        S a10 = 0;
        S a11 = 0;
        T val = T(0);
        T mn = T(0);
        T mx = T(0);
        T xr = T(0);
        T an = ~T(0);
        T orr = T(0);
        T g = T(0);
        T fv = T(0);
        T lv = T(0);
        T asg = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
        int pr = 0;
        int sr = 0;
        int br = 0;
        char rev = 0;
        char hasAsg = 0;
    };
    static inline vector<Node> nd{Node{}};  // node 0 = the empty tree
    int root = 0;

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit ImplicitTreap(const vector<T>& arr = {}) { root = build(arr); }

    ImplicitTreap makeEmpty() const { return ImplicitTreap(); }  // (a new, empty one)

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
    int size() const { return nd[root].sz; }

    // O(logN * logU) expected -- append v to the end
    void append(T v) { root = merge(root, newNode(v)); }

    // O(logN * logU) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN * logU) expected -- remove a[l..r] and return it as a treap of its own (indices from 0); needs
    // 0 <= l <= r < size(), else throws out_of_range
    ImplicitTreap cut(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("cut: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        root = merge(a, c);
        ImplicitTreap piece = makeEmpty();
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
            while (t) push(t), st.push_back(t), t = nd[t].L;
            t = st.back(), st.pop_back();
            out.push_back(nd[t].val);
            t = nd[t].R;
        }
        return out;
    }

    // O(logN * logU) expected -- insert v so it becomes a[i]; needs 0 <= i <= size(), else throws out_of_range (i =
    // size() appends)
    void insertAt(int i, T v) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN * logU) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    // 0 <= i <= size(), else throws out_of_range
    void insertCopiesAt(int i, T v, long long k) {
        if (i < 0 || i > size()) throw out_of_range("insertCopiesAt: needs 0 <= i <= size()");
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN * logU) expected -- is a[l..r] a palindrome (its two hashes agree); needs 0 <= l <= r < size(), else
    // throws out_of_range
    bool isPalindrome(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("isPalindrome: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        bool res = nd[b].fh == nd[b].bh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] > x, or -1 (pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int leftmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx > x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].L && nd[nd[t].L].mx > x) t = nd[t].L;
                else if (nd[t].val > x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int leftmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx >= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].L && nd[nd[t].L].mx >= x) t = nd[t].L;
                else if (nd[t].val >= x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] < x, or -1 (pruned by the subtree min); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int leftmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostLtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mn < x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].L && nd[nd[t].L].mn < x) t = nd[t].L;
                else if (nd[t].val < x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] <= x, or -1 (pruned by the subtree min); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int leftmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostLteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mn <= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].L && nd[nd[t].L].mn <= x) t = nd[t].L;
                else if (nd[t].val <= x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (pruned by best prefix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int leftmostPrefixSumGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumGtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].pre > S(x)) {
            while (true) {
                push(t);
                int lt = nd[t].L;
                if (lt && acc + nd[lt].pre > S(x)) { t = lt; continue; }
                acc += nd[lt].sm;
                if (acc + S(nd[t].val) > S(x)) { res = l + i + nd[lt].sz; break; }
                acc += S(nd[t].val), i += nd[lt].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (pruned by best prefix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int leftmostPrefixSumGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumGteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].pre >= S(x)) {
            while (true) {
                push(t);
                int lt = nd[t].L;
                if (lt && acc + nd[lt].pre >= S(x)) { t = lt; continue; }
                acc += nd[lt].sm;
                if (acc + S(nd[t].val) >= S(x)) { res = l + i + nd[lt].sz; break; }
                acc += S(nd[t].val), i += nd[lt].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the longest run of equal adjacent values in a[l..r]; needs 0 <= l <= r < size(),
    // else throws out_of_range
    int longestEqualRun(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("longestEqualRun: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int res = nd[b].br;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]; needs
    // 0 <= l <= r < size(), else throws out_of_range
    S maxAltSubseqSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("maxAltSubseqSum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = max(nd[b].a00, nd[b].a01);
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- max of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S maxPrefixSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("maxPrefixSum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].pre;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- max sum of a non-empty contiguous subarray of a[l..r]; needs 0 <= l <= r < size(),
    // else throws out_of_range
    S maxSubarraySum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("maxSubarraySum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].best;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- max of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S maxSuffixSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("maxSuffixSum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].suf;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- append all of other at the end; other is left empty
    void merge(ImplicitTreap& other) { root = merge(root, other.root), other.root = 0; }

    // O(logN * logU) expected -- min of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S minPrefixSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("minPrefixSum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].npre;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- min of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S minSuffixSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("minSuffixSum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].nsuf;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i]
    // (needs 0 <= i <= size(), else throws out_of_range); other is left empty
    void paste(int i, ImplicitTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
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

    // O(logN * logU) expected -- a[l] & ... & a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeAndQuery(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].an;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- a[i] = v for i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeAssign(int l, int r, T v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        applyAssign(b, v);
        root = merge(merge(a, b), c);
    }

    // O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeGcd(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeGcd: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].g;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal;
    // needs 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHash(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHash: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        U64 res = nd[b].fh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs
    // 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHashReversed(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHashReversed: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        U64 res = nd[b].bh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMax: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].mx;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMin(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMin: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].mn;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- a[l] | ... | a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeOrQuery(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeOrQuery: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].orr;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- reverse a[l..r] in place; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeReverse(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReverse: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }

    // O(logN * logU) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it
    // is taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateLeft(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateLeft: needs 0 <= l <= r < size()");
        int a, b, c, len = r - l + 1;
        cut(l, r, a, b, c);
        k = ((k % len) + len) % len;
        if (k) {
            int b1, b2;
            split(b, (int)k, b1, b2);
            b = merge(b2, b1);
        }
        root = merge(merge(a, b), c);
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
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].sm;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeXorQuery(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeXorQuery: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].xr;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    // 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), else throws out_of_range
    bool rangesEqual(int l1, int r1, int l2, int r2) {
        if (l1 < 0 || l1 > r1 || r1 >= size() || l2 < 0 || l2 > r2 || r2 >= size())
            throw out_of_range("rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size()");
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] > x, or -1 (pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int rightmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx > x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].R && nd[nd[t].R].mx > x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val > x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int rightmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx >= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].R && nd[nd[t].R].mx >= x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val >= x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] < x, or -1 (pruned by the subtree min); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int rightmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostLtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mn < x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].R && nd[nd[t].R].mn < x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val < x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] <= x, or -1 (pruned by the subtree min); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int rightmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostLteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mn <= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].R && nd[nd[t].R].mn <= x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val <= x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (pruned by best suffix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int rightmostSuffixSumGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostSuffixSumGtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].suf > S(x)) {
            while (true) {
                push(t);
                int rt = nd[t].R;
                if (rt && acc + nd[rt].suf > S(x)) { i += nd[nd[t].L].sz + 1, t = rt; continue; }
                acc += nd[rt].sm;
                if (acc + S(nd[t].val) > S(x)) { res = l + i + nd[nd[t].L].sz; break; }
                acc += S(nd[t].val), t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (pruned by best suffix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int rightmostSuffixSumGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostSuffixSumGteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].suf >= S(x)) {
            while (true) {
                push(t);
                int rt = nd[t].R;
                if (rt && acc + nd[rt].suf >= S(x)) { i += nd[nd[t].L].sz + 1, t = rt; continue; }
                acc += nd[rt].sm;
                if (acc + S(nd[t].val) >= S(x)) { res = l + i + nd[nd[t].L].sz; break; }
                acc += S(nd[t].val), t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty; needs
    // 0 <= k <= size(), else throws out_of_range
    pair<ImplicitTreap, ImplicitTreap> split(int k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        ImplicitTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN * logU) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty;
    // needs 0 <= l <= r < size(), else throws out_of_range
    tuple<ImplicitTreap, ImplicitTreap, ImplicitTreap> trisect(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        ImplicitTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cut(l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // ---- internals ----

    int newNode(T v) {
        Node n;
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.mn = v, n.mx = v, n.fh = hval(v),
        n.bh = hval(v), n.pw = HB(), n.gs = 1, n.pre = S(v), n.suf = S(v), n.best = S(v), n.npre = S(v), n.nsuf = S(v),
        n.xr = v, n.an = v, n.orr = v, n.g = v < T(0) ? T(-v) : v, n.fv = v, n.lv = v, n.pr = 1, n.sr = 1, n.br = 1,
        n.a00 = S(v), n.a01 = NEG, n.a10 = NEG, n.a11 = -S(v), n.rev = 0, n.asg = T(0), n.hasAsg = 0;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
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
        // the node alone, then with its left / right parts
        S s = S(v), p = S(v), q = S(v), b = S(v), u = S(v), w = S(v);
        if (l) {
            S ls = nd[l].sm, lp = nd[l].pre, lq = nd[l].suf, lb = nd[l].best, lu = nd[l].npre, lw = nd[l].nsuf;
            S ns = ls + s, np = max(lp, ls + p), nq = max(q, s + lq), nb = max({lb, b, lq + p}), nu = min(lu, ls + u),
                nw = min(w, s + lw);
            s = ns, p = np, q = nq, b = nb, u = nu, w = nw;
        }
        if (r) {
            S rs = nd[r].sm, rp = nd[r].pre, rq = nd[r].suf, rb = nd[r].best, ru = nd[r].npre, rw = nd[r].nsuf;
            S ns = s + rs, np = max(p, s + rp), nq = max(rq, rs + q), nb = max({b, rb, q + rp}), nu = min(u, s + ru),
                nw = min(rw, rs + w);
            s = ns, p = np, q = nq, b = nb, u = nu, w = nw;
        }
        nd[x].sm = s, nd[x].pre = p, nd[x].suf = q, nd[x].best = b, nd[x].npre = u, nd[x].nsuf = w;
        nd[x].mn = v;
        if (l && nd[l].mn < nd[x].mn) nd[x].mn = nd[l].mn;
        if (r && nd[r].mn < nd[x].mn) nd[x].mn = nd[r].mn;
        nd[x].mx = v;
        if (l && nd[l].mx > nd[x].mx) nd[x].mx = nd[l].mx;
        if (r && nd[r].mx > nd[x].mx) nd[x].mx = nd[r].mx;
        U64 B = HB(), hv = hval(v);
        nd[x].pw = hmul(hmul(nd[l].pw, B), nd[r].pw);
        nd[x].gs = hadd(hmul(hadd(hmul(nd[l].gs, B), 1), nd[r].pw), nd[r].gs);
        nd[x].fh = hadd(hmul(hadd(hmul(nd[l].fh, B), hv), nd[r].pw), nd[r].fh);
        nd[x].bh = hadd(hmul(hadd(hmul(nd[r].bh, B), hv), nd[l].pw), nd[l].bh);
        nd[x].xr = nd[l].xr ^ v ^ nd[r].xr;
        nd[x].an = nd[l].an & v & nd[r].an;  // (node 0: the AND of nothing, ~0)
        nd[x].orr = nd[l].orr | v | nd[r].orr;
        nd[x].g = gcd(gcd(nd[l].g, v), nd[r].g);
        int rp = 1, rq = 1, bb = 1;
        if (l) {
            bool j = nd[l].lv == v;
            rp = nd[l].pr + (j && nd[l].pr == nd[l].sz);
            rq = j ? nd[l].sr + 1 : 1;
            bb = max(nd[l].br, rq);
        }
        if (r) {
            bool j = v == nd[r].fv;
            bb = max({bb, nd[r].br, j ? rq + nd[r].pr : 0});
            if (j && rp == nd[l].sz + 1) rp += nd[r].pr;
            rq = j && nd[r].sr == nd[r].sz ? nd[r].sr + rq : nd[r].sr;
        }
        nd[x].pr = rp, nd[x].sr = rq, nd[x].br = bb;
        nd[x].fv = l ? nd[l].fv : v;
        nd[x].lv = r ? nd[r].lv : v;
        array<S, 4> c{S(v), NEG, NEG, -S(v)};
        if (l) c = altJoin({nd[l].a00, nd[l].a01, nd[l].a10, nd[l].a11}, c);
        if (r) c = altJoin(c, {nd[r].a00, nd[r].a01, nd[r].a10, nd[r].a11});
        nd[x].a00 = c[0], nd[x].a01 = c[1], nd[x].a10 = c[2], nd[x].a11 = c[3];
    }

    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        swap(nd[x].L, nd[x].R), nd[x].rev ^= 1, swap(nd[x].fh, nd[x].bh), swap(nd[x].pre, nd[x].suf),
            swap(nd[x].npre, nd[x].nsuf),
        swap(nd[x].fv, nd[x].lv), swap(nd[x].pr, nd[x].sr), swap(nd[x].a01, nd[x].a10);
    }

    void applyAssign(int x, T v) {  // every value of x's subtree becomes v
        if (!x) return;
        int n = nd[x].sz;
        nd[x].val = v;
        nd[x].sm = S(v) * n;
        nd[x].mn = v;
        nd[x].mx = v;
        nd[x].an = v;
        nd[x].orr = v;
        nd[x].fh = nd[x].bh = hmul(hval(v), nd[x].gs);
        nd[x].pre = nd[x].suf = nd[x].best = v > T(0) ? S(v) * n : S(v);
        nd[x].npre = nd[x].nsuf = v < T(0) ? S(v) * n : S(v);
        nd[x].xr = n & 1 ? v : T(0);
        nd[x].g = v < T(0) ? T(-v) : v;
        nd[x].fv = nd[x].lv = v;
        nd[x].pr = nd[x].sr = nd[x].br = n;
        nd[x].a00 = S(v), nd[x].a11 = -S(v), nd[x].a01 = nd[x].a10 = n > 1 ? S(0) : NEG;
        nd[x].asg = v, nd[x].hasAsg = 1;
    }

    void push(int x) {  // hand x's pending tags to its children
        if (nd[x].rev) applyRev(nd[x].L), applyRev(nd[x].R), nd[x].rev = 0;
        if (nd[x].hasAsg) applyAssign(nd[x].L, nd[x].asg), applyAssign(nd[x].R, nd[x].asg), nd[x].hasAsg = 0;
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

    void cut(int l, int r, int& a, int& b, int& c) {  // a[0..l-1], a[l..r], a[r+1..]
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    int locate(int i, vector<int>* path = nullptr) {  // the node holding a[i], every tag on the way pushed
        int t = root;
        while (true) {
            push(t);
            int ls = nd[nd[t].L].sz;
            if (i == ls) return t;
            if (path) path->push_back(t);
            if (i < ls) t = nd[t].L;
            else i -= ls + 1, t = nd[t].R;
        }
    }
};

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     ImplicitTreap<int> t({1, 2, 3, 4, 5});
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
