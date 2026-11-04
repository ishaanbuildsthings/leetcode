// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-max-hash-pre-suf-npre-nsuf-nbest/letters.cpp
// @operations: append appendLeft cut getAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX merge paste pointAssign pointChmax pointChmin pointGet rangeHash rangeHashReversed rangeMax rangeRotateLeft rangeRotateRight rangesEqual rightmostGtX rightmostGteX size split trisect
// @data-structure-type: treap
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
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeHash: log(N) expected
//   rangeHashReversed: log(N) expected
//   rangeMax: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangesEqual: log(N) expected
//   rightmostGtX: log(N) expected
//   rightmostGteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   size: 1
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mx[1*N] fh[1*N] bh[1*N] pw[1*N] pre[1*N] suf[1*N] npre[1*N] nsuf[1*N] nbest[1*N]
//   tags: none
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

// Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
// operations that make sense on characters are listed.
// Implicit treap with composable aggregates: an array you can insert into anywhere, rotate, move, cut pieces out of
// (that is how to erase) and paste them back in O(logN) expected each; each node keeps its sum, its max, its forward
// / backward hash (and B^size), its best prefix sum, its best suffix sum, its min prefix sum, its min suffix sum, its
// min subarray sum over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in
// the CURRENT array; searches return -1 when nothing qualifies.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        U64 fh = 0;
        U64 bh = 0;
        U64 pw = 1;
        S sm = 0;
        S pre = 0;
        S suf = 0;
        S npre = 0;
        S nsuf = 0;
        S nbest = 0;
        T val = T(0);
        T mx = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
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

    // O(logN) expected -- append v to the end
    void append(T v) { root = merge(root, newNode(v)); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0); needs
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
            while (t) st.push_back(t), t = nd[t].L;
            t = st.back(), st.pop_back();
            out.push_back(nd[t].val);
            t = nd[t].R;
        }
        return out;
    }

    // O(logN) expected -- insert v so it becomes a[i]; needs 0 <= i <= size(), else throws out_of_range (i = size()
    // appends)
    void insertAt(int i, T v) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    // 0 <= i <= size(), else throws out_of_range
    void insertCopiesAt(int i, T v, long long k) {
        if (i < 0 || i > size()) throw out_of_range("insertCopiesAt: needs 0 <= i <= size()");
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN) expected -- is a[l..r] a palindrome (its two hashes agree); needs 0 <= l <= r < size(), else throws
    // out_of_range
    bool isPalindrome(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("isPalindrome: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        bool res = nd[b].fh == nd[b].bh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int leftmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx > x) {  // some value in a[l..r] passes
            while (true) {
                if (nd[t].L && nd[nd[t].L].mx > x) t = nd[t].L;
                else if (nd[t].val > x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int leftmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx >= x) {  // some value in a[l..r] passes
            while (true) {
                if (nd[t].L && nd[nd[t].L].mx >= x) t = nd[t].L;
                else if (nd[t].val >= x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int leftmostPrefixSumGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumGtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].pre > S(x)) {
            while (true) {
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

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (a walk pruned by best prefix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int leftmostPrefixSumGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumGteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].pre >= S(x)) {
            while (true) {
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

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] < x, or -1 (a walk pruned by min prefix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int leftmostPrefixSumLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumLtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].npre < S(x)) {
            while (true) {
                int lt = nd[t].L;
                if (lt && acc + nd[lt].npre < S(x)) { t = lt; continue; }
                acc += nd[lt].sm;
                if (acc + S(nd[t].val) < S(x)) { res = l + i + nd[lt].sz; break; }
                acc += S(nd[t].val), i += nd[lt].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] <= x, or -1 (a walk pruned by min prefix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int leftmostPrefixSumLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumLteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].npre <= S(x)) {
            while (true) {
                int lt = nd[t].L;
                if (lt && acc + nd[lt].npre <= S(x)) { t = lt; continue; }
                acc += nd[lt].sm;
                if (acc + S(nd[t].val) <= S(x)) { res = l + i + nd[lt].sz; break; }
                acc += S(nd[t].val), i += nd[lt].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- max of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S maxPrefixSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("maxPrefixSum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].pre;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- max of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S maxSuffixSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("maxSuffixSum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].suf;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    void merge(ImplicitTreap& other) { root = merge(root, other.root), other.root = 0; }

    // O(logN) expected -- min of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S minPrefixSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("minPrefixSum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].npre;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- min sum of a non-empty contiguous subarray of a[l..r]; needs 0 <= l <= r < size(), else
    // throws out_of_range
    S minSubarraySum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("minSubarraySum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].nbest;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- min of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S minSuffixSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("minSuffixSum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].nsuf;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i] (needs
    // 0 <= i <= size(), else throws out_of_range); other is left empty
    void paste(int i, ImplicitTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }

    // O(logN) expected -- a[i] += v; needs 0 <= i < size(), else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAdd: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = nd[t].val + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmax: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = max(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else throws out_of_range
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

    // O(logN) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    // 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHash(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHash: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        U64 res = nd[b].fh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs
    // 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHashReversed(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHashReversed: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        U64 res = nd[b].bh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMax: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].mx;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
    // taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
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

    // O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    // (negative shifts left); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateRight(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -k);
    }

    // O(logN) expected -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeSum: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].sm;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    // 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), else throws out_of_range
    bool rangesEqual(int l1, int r1, int l2, int r2) {
        if (l1 < 0 || l1 > r1 || r1 >= size() || l2 < 0 || l2 > r2 || r2 >= size())
            throw out_of_range("rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size()");
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int rightmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx > x) {  // some value in a[l..r] passes
            while (true) {
                if (nd[t].R && nd[nd[t].R].mx > x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val > x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int rightmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx >= x) {  // some value in a[l..r] passes
            while (true) {
                if (nd[t].R && nd[nd[t].R].mx >= x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val >= x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int rightmostSuffixSumGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostSuffixSumGtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].suf > S(x)) {
            while (true) {
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

    // O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (a walk pruned by best suffix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int rightmostSuffixSumGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostSuffixSumGteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].suf >= S(x)) {
            while (true) {
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

    // O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] < x, or -1 (a walk pruned by min suffix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int rightmostSuffixSumLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostSuffixSumLtX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].nsuf < S(x)) {
            while (true) {
                int rt = nd[t].R;
                if (rt && acc + nd[rt].nsuf < S(x)) { i += nd[nd[t].L].sz + 1, t = rt; continue; }
                acc += nd[rt].sm;
                if (acc + S(nd[t].val) < S(x)) { res = l + i + nd[nd[t].L].sz; break; }
                acc += S(nd[t].val), t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] <= x, or -1 (a walk pruned by min suffix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int rightmostSuffixSumLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostSuffixSumLteX: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        S acc = 0;
        if (t && nd[t].nsuf <= S(x)) {
            while (true) {
                int rt = nd[t].R;
                if (rt && acc + nd[rt].nsuf <= S(x)) { i += nd[nd[t].L].sz + 1, t = rt; continue; }
                acc += nd[rt].sm;
                if (acc + S(nd[t].val) <= S(x)) { res = l + i + nd[nd[t].L].sz; break; }
                acc += S(nd[t].val), t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty; needs
    // 0 <= k <= size(), else throws out_of_range
    pair<ImplicitTreap, ImplicitTreap> split(int k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        ImplicitTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty; needs
    // 0 <= l <= r < size(), else throws out_of_range
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
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.mx = v, n.fh = hval(v), n.bh = hval(v),
        n.pw = HB(), n.pre = S(v), n.suf = S(v), n.npre = S(v), n.nsuf = S(v), n.nbest = S(v);
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
        // the node alone, then with its left / right parts
        S s = S(v), p = S(v), q = S(v), u = S(v), w = S(v), z = S(v);
        if (l) {
            S ls = nd[l].sm, lp = nd[l].pre, lq = nd[l].suf, lu = nd[l].npre, lw = nd[l].nsuf, lz = nd[l].nbest;
            S ns = ls + s, np = max(lp, ls + p), nq = max(q, s + lq), nu = min(lu, ls + u), nw = min(w, s + lw),
                nz = min({lz, z, lw + u});
            s = ns, p = np, q = nq, u = nu, w = nw, z = nz;
        }
        if (r) {
            S rs = nd[r].sm, rp = nd[r].pre, rq = nd[r].suf, ru = nd[r].npre, rw = nd[r].nsuf, rz = nd[r].nbest;
            S ns = s + rs, np = max(p, s + rp), nq = max(rq, rs + q), nu = min(u, s + ru), nw = min(rw, rs + w),
                nz = min({z, rz, w + ru});
            s = ns, p = np, q = nq, u = nu, w = nw, z = nz;
        }
        nd[x].sm = s, nd[x].pre = p, nd[x].suf = q, nd[x].npre = u, nd[x].nsuf = w, nd[x].nbest = z;
        nd[x].mx = v;
        if (l && nd[l].mx > nd[x].mx) nd[x].mx = nd[l].mx;
        if (r && nd[r].mx > nd[x].mx) nd[x].mx = nd[r].mx;
        U64 B = HB(), hv = hval(v);
        nd[x].pw = hmul(hmul(nd[l].pw, B), nd[r].pw);
        nd[x].fh = hadd(hmul(hadd(hmul(nd[l].fh, B), hv), nd[r].pw), nd[r].fh);
        nd[x].bh = hadd(hmul(hadd(hmul(nd[r].bh, B), hv), nd[l].pw), nd[l].bh);
    }

    void split(int t, int k, int& a, int& b) {  // a = first k of t, b = the rest
        if (!t) { a = b = 0; return; }
        if (nd[nd[t].L].sz >= k) split(nd[t].L, k, a, nd[t].L), b = t;
        else split(nd[t].R, k - nd[nd[t].L].sz - 1, nd[t].R, b), a = t;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's
        if (!a || !b) return a | b;
        if (nd[a].pri > nd[b].pri) {
            nd[a].R = merge(nd[a].R, b);
            pull(a);
            return a;
        }
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
