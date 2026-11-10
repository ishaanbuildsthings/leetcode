// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/treap-sum-hash-npre-nsuf-nbest-rev-find/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft cut find getAll hashAll hashAllReversed insertAt insertCopiesAt isPalindrome leftmostPrefixSumLtX leftmostPrefixSumLteX longestPalCenteredAtI longestPalCenteredAtIPlusOne merge minPrefixSum minSubarraySum minSuffixSum paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeHash rangeHashReversed rangeReverse rangeRotateLeft rangeRotateRight rangeSum rangesEqual rightmostSuffixSumLtX rightmostSuffixSumLteX size split sumAll trisect
// @data-structure-type: treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   cut: log(N) expected
//   find: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: K+log(N) expected
//   isPalindrome: log(N) expected
//   leftmostPrefixSumLtX: log(N) expected
//   leftmostPrefixSumLteX: log(N) expected
//   merge: log(N) expected
//   minPrefixSum: log(N) expected
//   minSubarraySum: log(N) expected
//   minSuffixSum: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeHash: log(N) expected
//   rangeHashReversed: log(N) expected
//   rangeReverse: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeSum: log(N) expected
//   rangesEqual: log(N) expected
//   rightmostSuffixSumLtX: log(N) expected
//   rightmostSuffixSumLteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   size: 1
//   pop: log(N) expected
//   popLeft: log(N) expected
//   longestPalCenteredAtI: log^2(N) expected
//   longestPalCenteredAtIPlusOne: log^2(N) expected
//   hashAll: 1
//   sumAll: 1
//   hashAllReversed: 1
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] fh[1*N] bh[1*N] pw[1*N] npre[1*N] nsuf[1*N] nbest[1*N] par[1*N]
//   tags: rev[1*N]
//   other: where[1*N]
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset); find: a parent per node and a map value -> node

// Implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, move, cut pieces
// out of (that is how to erase) and paste them back in O(logN) expected each, and find any value's index (values
// distinct); each node keeps its sum, its forward / backward hash (and B^size), its min prefix sum, its min suffix
// sum, its min subarray sum over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the
// position in the CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this
// node, not yet to its children".
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    struct SafeHash {  // splitmix64 with a seed random per run (the default hash of an integer is easy to attack)
        size_t operator()(const T& x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        U64 fh = 0;
        U64 bh = 0;
        U64 pw = 1;
        S sm = 0;
        S npre = 0;
        S nsuf = 0;
        S nbest = 0;
        T val = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
        int par = 0;
        char rev = 0;
    };
    static inline vector<Node> nd{Node{}};  // node 0 = the empty tree
    static inline unordered_map<T, int, SafeHash> where;
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

    // O(logN) expected -- the index of x, or -1 if x isn't in this treap (values distinct across all treaps)
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
        if (path.back() != root) return -1;  // (erased, or in another treap)
        for (int k = (int)path.size() - 1; k >= 0; k--) push(path[k]);  // (pending reverses above it, top-down)
        int i = nd[nd[t].L].sz;
        for (size_t k = 1; k < path.size(); k++)
            if (nd[path[k]].R == path[k - 1]) i += nd[nd[path[k]].L].sz + 1;
        return i;
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
        size_t mark;
        int b = rangeNode(l, r, mark);
        bool res = nd[b].fh == nd[b].bh;
        release(mark);
        return res;
    }

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] < x, or -1 (a walk pruned by min prefix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int leftmostPrefixSumLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumLtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int pos = l;  // (the index of the current piece's first value; acc: the sum before it)
        S acc = 0;
        for (auto [t, whole] : ps) {
            if (!whole) {
                acc += S(nd[t].val);
                if (acc < S(x)) return pos;
                pos++;
                continue;
            }
            if (acc + nd[t].npre < S(x)) {
                int i = 0;
                while (true) {
                    push(t);
                    int lt = nd[t].L;
                    if (lt && acc + nd[lt].npre < S(x)) {
                        t = lt;
                        continue;
                    }
                    acc += nd[lt].sm;
                    if (acc + S(nd[t].val) < S(x)) return pos + i + nd[lt].sz;
                    acc += S(nd[t].val), i += nd[lt].sz + 1, t = nd[t].R;
                }
            }
            acc += nd[t].sm, pos += nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] <= x, or -1 (a walk pruned by min prefix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int leftmostPrefixSumLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumLteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int pos = l;  // (the index of the current piece's first value; acc: the sum before it)
        S acc = 0;
        for (auto [t, whole] : ps) {
            if (!whole) {
                acc += S(nd[t].val);
                if (acc <= S(x)) return pos;
                pos++;
                continue;
            }
            if (acc + nd[t].npre <= S(x)) {
                int i = 0;
                while (true) {
                    push(t);
                    int lt = nd[t].L;
                    if (lt && acc + nd[lt].npre <= S(x)) {
                        t = lt;
                        continue;
                    }
                    acc += nd[lt].sm;
                    if (acc + S(nd[t].val) <= S(x)) return pos + i + nd[lt].sz;
                    acc += S(nd[t].val), i += nd[lt].sz + 1, t = nd[t].R;
                }
            }
            acc += nd[t].sm, pos += nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    void merge(ImplicitTreap& other) { root = merge(root, other.root), other.root = 0; }

    // O(logN) expected -- min of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S minPrefixSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("minPrefixSum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].npre;
        release(mark);
        return res;
    }

    // O(logN) expected -- min sum of a non-empty contiguous subarray of a[l..r]; needs 0 <= l <= r < size(), else
    // throws out_of_range
    S minSubarraySum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("minSubarraySum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].nbest;
        release(mark);
        return res;
    }

    // O(logN) expected -- min of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S minSuffixSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("minSuffixSum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].nsuf;
        release(mark);
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
        T old = nd[t].val;
        nd[t].val = nd[t].val + v;
        rekey(t, old);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
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

    // O(logN) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else throws out_of_range
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

    // O(logN) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else throws out_of_range
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

    // O(logN) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    // 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHash(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHash: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        U64 res = nd[b].fh;
        release(mark);
        return res;
    }

    // O(logN) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs
    // 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHashReversed(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHashReversed: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        U64 res = nd[b].bh;
        release(mark);
        return res;
    }

    // O(logN) expected -- reverse a[l..r] in place; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeReverse(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReverse: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
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
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].sm;
        release(mark);
        return res;
    }

    // O(logN) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    // 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), else throws out_of_range
    bool rangesEqual(int l1, int r1, int l2, int r2) {
        if (l1 < 0 || l1 > r1 || r1 >= size() || l2 < 0 || l2 > r2 || r2 >= size())
            throw out_of_range("rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size()");
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] < x, or -1 (a walk pruned by min suffix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int rightmostSuffixSumLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostSuffixSumLtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int end = r;  // (the index of the current piece's last value; acc: the sum after it)
        S acc = 0;
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                acc += S(nd[t].val);
                if (acc < S(x)) return end;
                end--;
                continue;
            }
            if (acc + nd[t].nsuf < S(x)) {
                int start = end - nd[t].sz + 1, i = 0;
                while (true) {
                    push(t);
                    int rt = nd[t].R;
                    if (rt && acc + nd[rt].nsuf < S(x)) {
                        i += nd[nd[t].L].sz + 1, t = rt;
                        continue;
                    }
                    acc += nd[rt].sm;
                    if (acc + S(nd[t].val) < S(x)) return start + i + nd[nd[t].L].sz;
                    acc += S(nd[t].val), t = nd[t].L;
                }
            }
            acc += nd[t].sm, end -= nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] <= x, or -1 (a walk pruned by min suffix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    int rightmostSuffixSumLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostSuffixSumLteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int end = r;  // (the index of the current piece's last value; acc: the sum after it)
        S acc = 0;
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                acc += S(nd[t].val);
                if (acc <= S(x)) return end;
                end--;
                continue;
            }
            if (acc + nd[t].nsuf <= S(x)) {
                int start = end - nd[t].sz + 1, i = 0;
                while (true) {
                    push(t);
                    int rt = nd[t].R;
                    if (rt && acc + nd[rt].nsuf <= S(x)) {
                        i += nd[nd[t].L].sz + 1, t = rt;
                        continue;
                    }
                    acc += nd[rt].sm;
                    if (acc + S(nd[t].val) <= S(x)) return start + i + nd[nd[t].L].sz;
                    acc += S(nd[t].val), t = nd[t].L;
                }
            }
            acc += nd[t].sm, end -= nd[t].sz;
        }
        return -1;
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

    // O(log(N) expected) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    T pop() {
        auto n = size();
        if (n < 1) throw out_of_range("pop: needs size() >= 1");
        T v = pointGet(n - 1);
        cut(n - 1, n - 1);
        return v;
    }

    // O(log(N) expected) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws
    // out_of_range
    T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        T v = pointGet(0);
        cut(0, 0);
        return v;
    }

    // O(log^2(N) expected) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)): a binary
    // search on
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

    // O(log^2(N) expected) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1,
    // i), the empty
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

    // O(1) -- hash of the whole array a[0..n-1], read off the root: the same base and mod as rangeHash (shared by every
    // structure this run, so it compares with another one's hashes); needs n >= 1, else throws out_of_range
    auto hashAll() {
        if (size() < 1) throw out_of_range("hashAll: needs n >= 1");
        return nd[root].fh;
    }

    // O(1) -- sum of the whole array a[0..n-1] (read off the root); needs n >= 1, else throws out_of_range
    auto sumAll() {
        if (size() < 1) throw out_of_range("sumAll: needs n >= 1");
        return nd[root].sm;
    }

    // O(1) -- hash of the whole array reversed, a[n-1], ..., a[0] (read off the root); it uses the same base and mod as
    // rangeHash, so it equals rangeHash of any range holding those values in that order (and any structure's hashes
    // this run); needs n >= 1, else throws out_of_range
    auto hashAllReversed() {
        if (size() < 1) throw out_of_range("hashAllReversed: needs n >= 1");
        return nd[root].bh;
    }

    // ---- internals ----

    int newNode(T v) {
        Node n;
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.fh = hval(v), n.bh = hval(v), n.pw = HB(),
        n.npre = S(v), n.nsuf = S(v), n.nbest = S(v), n.rev = 0, n.par = 0;
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
        S s = S(v), u = S(v), w = S(v), z = S(v);  // the node alone, then with its left / right parts
        if (l) {
            S ls = nd[l].sm, lu = nd[l].npre, lw = nd[l].nsuf, lz = nd[l].nbest;
            S ns = ls + s, nu = min(lu, ls + u), nw = min(w, s + lw), nz = min({lz, z, lw + u});
            s = ns, u = nu, w = nw, z = nz;
        }
        if (r) {
            S rs = nd[r].sm, ru = nd[r].npre, rw = nd[r].nsuf, rz = nd[r].nbest;
            S ns = s + rs, nu = min(u, s + ru), nw = min(rw, rs + w), nz = min({z, rz, w + ru});
            s = ns, u = nu, w = nw, z = nz;
        }
        nd[x].sm = s, nd[x].npre = u, nd[x].nsuf = w, nd[x].nbest = z;
        U64 B = HB(), hv = hval(v);
        nd[x].pw = hmul(hmul(nd[l].pw, B), nd[r].pw);
        nd[x].fh = hadd(hmul(hadd(hmul(nd[l].fh, B), hv), nd[r].pw), nd[r].fh);
        nd[x].bh = hadd(hmul(hadd(hmul(nd[r].bh, B), hv), nd[l].pw), nd[l].bh);
    }

    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        swap(nd[x].L, nd[x].R), nd[x].rev ^= 1, swap(nd[x].fh, nd[x].bh), swap(nd[x].npre, nd[x].nsuf);
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

    // ---- queries, searches and range updates walk the pieces of [l, r] instead of cutting it out ----

    // a[l..r] of t's subtree as (node, whole subtree?) in order; pending tags on the way pushed down
    void pieces(int t, int l, int r, vector<pair<int, bool>>& out) {
        if (!t || r < 0 || l >= nd[t].sz) return;
        if (l <= 0 && nd[t].sz - 1 <= r) {
            out.push_back({t, true});
            return;
        }
        push(t);
        int ls = nd[nd[t].L].sz;
        pieces(nd[t].L, l, r, out);
        if (l <= ls && ls <= r) out.push_back({t, false});
        pieces(nd[t].R, l - ls - 1, r - ls - 1, out);
    }

    // a temporary node holding a[l..r]'s aggregates; mark = the pool size release() goes back to
    int rangeNode(int l, int r, size_t& mark) {
        mark = nd.size();
        return rq(root, l, r);
    }

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
        n.fh = nd[x].fh, n.bh = nd[x].bh, n.pw = nd[x].pw, n.npre = nd[x].npre, n.nsuf = nd[x].nsuf,
        n.nbest = nd[x].nbest, n.par = nd[x].par, n.rev = nd[x].rev;
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
};

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     ImplicitTreap<int> t({1, 2, 3, 4, 5});
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
