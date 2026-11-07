// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-treap-sum-min-max-hash-run-alt-updates-assign/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft copy cut getAll hashAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX leftmostLtX leftmostLteX longestEqualRun longestPalCenteredAtI longestPalCenteredAtIPlusOne maxAll maxAltSubseqSum merge minAll paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAssign rangeHash rangeHashReversed rangeMax rangeMin rangeRotateLeft rangeRotateRight rangeSum rangesEqual rightmostGtX rightmostGteX rightmostLtX rightmostLteX size split sumAll trisect
// @data-structure-type: persistent-treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   copy: log(N) expected
//   cut: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: log(N) expected
//   isPalindrome: log(N) expected
//   leftmostGtX: log(N) expected
//   leftmostGteX: log(N) expected
//   leftmostLtX: log(N) expected
//   leftmostLteX: log(N) expected
//   longestEqualRun: log(N) expected
//   maxAltSubseqSum: log(N) expected
//   merge: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeAssign: log(N) expected
//   rangeHash: log(N) expected
//   rangeHashReversed: log(N) expected
//   rangeMax: log(N) expected
//   rangeMin: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeSum: log(N) expected
//   rangesEqual: log(N) expected
//   rightmostGtX: log(N) expected
//   rightmostGteX: log(N) expected
//   rightmostLtX: log(N) expected
//   rightmostLteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   size: 1
//   pop: log(N) expected
//   popLeft: log(N) expected
//   longestPalCenteredAtI: log^2(N) expected
//   longestPalCenteredAtIPlusOne: log^2(N) expected
//   hashAll: 1
//   sumAll: 1
//   minAll: 1
//   maxAll: 1
//   build: N
// @memory:
//   layout: none
//   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] sm[1*N*log(N)] mn[1*N*log(N)] mx[1*N*log(N)] fh[1*N*log(N)] bh[1*N*log(N)] pw[1*N*log(N)] gs[1*N*log(N)] fv[1*N*log(N)] lv[1*N*log(N)] pr[1*N*log(N)] sr[1*N*log(N)] br[1*N*log(N)] a00[1*N*log(N)] a01[1*N*log(N)] a10[1*N*log(N)] a11[1*N*log(N)]
//   tags: asg[1*N*log(N)] hasAsg[1*N*log(N)]
//   other: none
//   note: nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and copies share every node they don't change; log(N) is of the length, which can be huge (long long)

// Persistent implicit treap with composable aggregates: an array you can insert into anywhere, rotate, cut pieces out
// of (that is how to erase), paste them back and copy (copy(l, r): a[l..r] as a treap of its own in O(logN) however
// long, since the copy shares the same nodes; this one is unchanged), with rangeAssign; each node keeps its sum, its
// min, its max, its forward / backward hash (and B^size), its first / last value and the equal runs at its ends and
// inside, its best alternating (+ - + ...) subsequence sum for each start / end sign over its subtree. No node
// changes once another tree can see it: an op copies the nodes on its paths, so a copy and its original never affect
// each other. Lengths and indices are long long. All indices 0-based, ranges inclusive [l, r], an index always the
// position in the CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this
// node, not yet to its children".
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct PersistentTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    // one node pool shared by every PersistentTreap<T>: cut / paste move nodes between them, so a piece from one can
    // go into any other (node 0 = the empty tree). Nodes are never freed (memory = O(log N) per op, over the whole
    // run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        U64 fh = 0;
        U64 bh = 0;
        U64 pw = 1;
        U64 gs = 0;
        S sm = 0;
        S a00 = 0;
        S a01 = 0;
        S a10 = 0;
        S a11 = 0;
        long long sz = 0;
        long long pr = 0;
        long long sr = 0;
        long long br = 0;
        T val = T(0);
        T mn = T(0);
        T mx = T(0);
        T fv = T(0);
        T lv = T(0);
        T asg = T(0);
        int L = 0;
        int R = 0;
        char hasAsg = 0;
    };
    static inline vector<Node> nd{Node{}};  // node 0 = the empty tree
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
    long long size() const { return nd[root].sz; }

    // O(logN) expected -- append v to the end
    void append(T v) { root = merge(root, newNode(v)); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(1) -- the whole array as a PersistentTreap of its own; this one is unchanged (they share nodes)
    PersistentTreap copy() const { return *this; }

    // O(logN) expected -- a[l..r] as a PersistentTreap of its own; this one is unchanged. The copy shares this one's
    // nodes, so it costs O(logN) however long it is; needs 0 <= l <= r < size(), else throws out_of_range
    PersistentTreap copy(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("copy: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        PersistentTreap piece = makeEmpty();
        piece.root = b;
        return piece;
    }

    // O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0); needs
    // 0 <= l <= r < size(), else throws out_of_range
    PersistentTreap cut(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("cut: needs 0 <= l <= r < size()");
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
            while (t) push(t), st.push_back(t), t = nd[t].L;
            t = st.back(), st.pop_back();
            out.push_back(nd[t].val);
            t = nd[t].R;
        }
        return out;
    }

    // O(logN) expected -- insert v so it becomes a[i]; needs 0 <= i <= size(), else throws out_of_range (i = size()
    // appends)
    void insertAt(long long i, T v) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    // 0 <= i <= size(), else throws out_of_range
    void insertCopiesAt(long long i, T v, long long k) {
        if (i < 0 || i > size()) throw out_of_range("insertCopiesAt: needs 0 <= i <= size()");
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN) expected -- is a[l..r] a palindrome (its two hashes agree); needs 0 <= l <= r < size(), else throws
    // out_of_range
    bool isPalindrome(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("isPalindrome: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        bool res = nd[b].fh == nd[b].bh;
        release(mark);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    long long leftmostGtX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long pos = l;  // (the index of the current piece's first value)
        for (auto [t, whole] : ps) {
            if (!whole) {
                if (nd[t].val > x) return pos;
                pos++;
                continue;
            }
            if (nd[t].mx > x) {
                long long i = 0;
                while (true) {
                    push(t);
                    if (nd[t].L && nd[nd[t].L].mx > x) t = nd[t].L;
                    else if (nd[t].val > x) return pos + i + nd[nd[t].L].sz;
                    else i += nd[nd[t].L].sz + 1, t = nd[t].R;
                }
            }
            pos += nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    long long leftmostGteX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long pos = l;  // (the index of the current piece's first value)
        for (auto [t, whole] : ps) {
            if (!whole) {
                if (nd[t].val >= x) return pos;
                pos++;
                continue;
            }
            if (nd[t].mx >= x) {
                long long i = 0;
                while (true) {
                    push(t);
                    if (nd[t].L && nd[nd[t].L].mx >= x) t = nd[t].L;
                    else if (nd[t].val >= x) return pos + i + nd[nd[t].L].sz;
                    else i += nd[nd[t].L].sz + 1, t = nd[t].R;
                }
            }
            pos += nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min); needs
    // 0 <= l <= r < size(), else throws out_of_range
    long long leftmostLtX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostLtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long pos = l;  // (the index of the current piece's first value)
        for (auto [t, whole] : ps) {
            if (!whole) {
                if (nd[t].val < x) return pos;
                pos++;
                continue;
            }
            if (nd[t].mn < x) {
                long long i = 0;
                while (true) {
                    push(t);
                    if (nd[t].L && nd[nd[t].L].mn < x) t = nd[t].L;
                    else if (nd[t].val < x) return pos + i + nd[nd[t].L].sz;
                    else i += nd[nd[t].L].sz + 1, t = nd[t].R;
                }
            }
            pos += nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the subtree min); needs
    // 0 <= l <= r < size(), else throws out_of_range
    long long leftmostLteX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostLteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long pos = l;  // (the index of the current piece's first value)
        for (auto [t, whole] : ps) {
            if (!whole) {
                if (nd[t].val <= x) return pos;
                pos++;
                continue;
            }
            if (nd[t].mn <= x) {
                long long i = 0;
                while (true) {
                    push(t);
                    if (nd[t].L && nd[nd[t].L].mn <= x) t = nd[t].L;
                    else if (nd[t].val <= x) return pos + i + nd[nd[t].L].sz;
                    else i += nd[nd[t].L].sz + 1, t = nd[t].R;
                }
            }
            pos += nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- the longest run of equal adjacent values in a[l..r]; needs 0 <= l <= r < size(), else
    // throws out_of_range
    long long longestEqualRun(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("longestEqualRun: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        int res = nd[b].br;
        release(mark);
        return res;
    }

    // O(logN) expected -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]; needs
    // 0 <= l <= r < size(), else throws out_of_range
    S maxAltSubseqSum(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("maxAltSubseqSum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = max(nd[b].a00, nd[b].a01);
        release(mark);
        return res;
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    void merge(PersistentTreap& other) { root = merge(root, other.root), other.root = 0; }
    void merge(PersistentTreap&& other) { merge(other); }  // (a temporary: merge(t.copy()))

    // O(logN) expected -- insert all of other (any PersistentTreap, e.g. a cut piece) so it starts at a[i] (needs
    // 0 <= i <= size(), else throws out_of_range); other is left empty
    void paste(long long i, PersistentTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }
    void paste(long long i, PersistentTreap&& other) { paste(i, other); }  // (a temporary: paste(i, t.copy(l, r)))

    // O(logN) expected -- a[i] += v (copies the one path down to a[i]); needs 0 <= i < size(), else throws
    // out_of_range
    void pointAdd(long long i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAdd: needs 0 <= i < size()");
        root = setAt(root, i, [&](T w) { return T(w + v); });
    }

    // O(logN) expected -- a[i] = v (copies the one path down to a[i]); needs 0 <= i < size(), else throws
    // out_of_range
    void pointAssign(long long i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        root = setAt(root, i, [&](T w) { return v; });
    }

    // O(logN) expected -- a[i] = max(a[i], v) (copies the one path down to a[i]); needs 0 <= i < size(), else throws
    // out_of_range
    void pointChmax(long long i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmax: needs 0 <= i < size()");
        root = setAt(root, i, [&](T w) { return max(w, v); });
    }

    // O(logN) expected -- a[i] = min(a[i], v) (copies the one path down to a[i]); needs 0 <= i < size(), else throws
    // out_of_range
    void pointChmin(long long i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmin: needs 0 <= i < size()");
        root = setAt(root, i, [&](T w) { return min(w, v); });
    }

    // O(logN) expected -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(long long i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return nd[locate(i)].val;
    }

    // O(logN) expected -- a[i] = v for i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeAssign(long long l, long long r, T v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        root = upd(root, l, r, [&](int x, long long off) { applyAssign(x, v); (void)off; });
    }

    // O(logN) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    // 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHash(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHash: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        U64 res = nd[b].fh;
        release(mark);
        return res;
    }

    // O(logN) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs
    // 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHashReversed(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHashReversed: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        U64 res = nd[b].bh;
        release(mark);
        return res;
    }

    // O(logN) expected -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMax(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMax: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        T res = nd[b].mx;
        release(mark);
        return res;
    }

    // O(logN) expected -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMin(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMin: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        T res = nd[b].mn;
        release(mark);
        return res;
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
    // taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateLeft(long long l, long long r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateLeft: needs 0 <= l <= r < size()");
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

    // O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    // (negative shifts left); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateRight(long long l, long long r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -k);
    }

    // O(logN) expected -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    S rangeSum(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeSum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].sm;
        release(mark);
        return res;
    }

    // O(logN) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    // 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), else throws out_of_range
    bool rangesEqual(long long l1, long long r1, long long l2, long long r2) {
        if (l1 < 0 || l1 > r1 || r1 >= size() || l2 < 0 || l2 > r2 || r2 >= size())
            throw out_of_range("rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size()");
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    long long rightmostGtX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long end = r;  // (the index of the current piece's last value)
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                if (nd[t].val > x) return end;
                end--;
                continue;
            }
            if (nd[t].mx > x) {
                long long start = end - nd[t].sz + 1, i = 0;
                while (true) {
                    push(t);
                    if (nd[t].R && nd[nd[t].R].mx > x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                    else if (nd[t].val > x) return start + i + nd[nd[t].L].sz;
                    else t = nd[t].L;
                }
            }
            end -= nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    long long rightmostGteX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long end = r;  // (the index of the current piece's last value)
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                if (nd[t].val >= x) return end;
                end--;
                continue;
            }
            if (nd[t].mx >= x) {
                long long start = end - nd[t].sz + 1, i = 0;
                while (true) {
                    push(t);
                    if (nd[t].R && nd[nd[t].R].mx >= x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                    else if (nd[t].val >= x) return start + i + nd[nd[t].L].sz;
                    else t = nd[t].L;
                }
            }
            end -= nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min); needs
    // 0 <= l <= r < size(), else throws out_of_range
    long long rightmostLtX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostLtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long end = r;  // (the index of the current piece's last value)
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                if (nd[t].val < x) return end;
                end--;
                continue;
            }
            if (nd[t].mn < x) {
                long long start = end - nd[t].sz + 1, i = 0;
                while (true) {
                    push(t);
                    if (nd[t].R && nd[nd[t].R].mn < x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                    else if (nd[t].val < x) return start + i + nd[nd[t].L].sz;
                    else t = nd[t].L;
                }
            }
            end -= nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the subtree min); needs
    // 0 <= l <= r < size(), else throws out_of_range
    long long rightmostLteX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostLteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long end = r;  // (the index of the current piece's last value)
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                if (nd[t].val <= x) return end;
                end--;
                continue;
            }
            if (nd[t].mn <= x) {
                long long start = end - nd[t].sz + 1, i = 0;
                while (true) {
                    push(t);
                    if (nd[t].R && nd[nd[t].R].mn <= x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                    else if (nd[t].val <= x) return start + i + nd[nd[t].L].sz;
                    else t = nd[t].L;
                }
            }
            end -= nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty; needs
    // 0 <= k <= size(), else throws out_of_range
    pair<PersistentTreap, PersistentTreap> split(long long k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        PersistentTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty; needs
    // 0 <= l <= r < size(), else throws out_of_range
    tuple<PersistentTreap, PersistentTreap, PersistentTreap> trisect(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        PersistentTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
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

    // O(log(N) expected) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws out_of_range
    T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        T v = pointGet(0);
        cut(0, 0);
        return v;
    }

    // O(log^2(N) expected) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)): a binary search on
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

    // O(log^2(N) expected) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the empty
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

    // O(1) -- min of the whole array a[0..n-1] (read off the root); needs n >= 1, else throws out_of_range
    auto minAll() {
        if (size() < 1) throw out_of_range("minAll: needs n >= 1");
        return nd[root].mn;
    }

    // O(1) -- max of the whole array a[0..n-1] (read off the root); needs n >= 1, else throws out_of_range
    auto maxAll() {
        if (size() < 1) throw out_of_range("maxAll: needs n >= 1");
        return nd[root].mx;
    }

    // ---- internals ----

    int newNode(T v) {
        Node n;
        n.val = v, n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.mn = v, n.mx = v, n.fh = hval(v), n.bh = hval(v),
        n.pw = HB(), n.gs = 1, n.fv = v, n.lv = v, n.pr = 1, n.sr = 1, n.br = 1, n.a00 = S(v), n.a01 = NEG,
        n.a10 = NEG, n.a11 = -S(v), n.asg = T(0), n.hasAsg = 0;
        nd.push_back(n);
        return (int)nd.size() - 1;
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
        nd[x].L = l, nd[x].R = r;
        pull(x);
        return x;
    }

    int clone(int x) {  // a new copy of node x (sharing its children)
        Node n;
        n.val = nd[x].val, n.L = nd[x].L, n.R = nd[x].R, n.sz = nd[x].sz, n.sm = nd[x].sm, n.mn = nd[x].mn,
        n.mx = nd[x].mx, n.fh = nd[x].fh, n.bh = nd[x].bh, n.pw = nd[x].pw, n.gs = nd[x].gs, n.fv = nd[x].fv,
        n.lv = nd[x].lv, n.pr = nd[x].pr, n.sr = nd[x].sr, n.br = nd[x].br, n.a00 = nd[x].a00, n.a01 = nd[x].a01,
        n.a10 = nd[x].a10, n.a11 = nd[x].a11, n.asg = nd[x].asg, n.hasAsg = nd[x].hasAsg;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    void pull(int x) {  // recompute x from its children
        int l = nd[x].L, r = nd[x].R;
        nd[x].sz = nd[l].sz + nd[r].sz + 1;
        T v = nd[x].val;
        nd[x].sm = nd[l].sm + S(v) + nd[r].sm;
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
        long long rp = 1, rq = 1, bb = 1;
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

    void applyAssign(int x, T v) {  // every value of x's subtree becomes v
        if (!x) return;
        long long n = nd[x].sz;
        nd[x].val = v;
        nd[x].sm = S(v) * n;
        nd[x].mn = v;
        nd[x].mx = v;
        nd[x].fh = nd[x].bh = hmul(hval(v), nd[x].gs);
        nd[x].fv = nd[x].lv = v;
        nd[x].pr = nd[x].sr = nd[x].br = n;
        nd[x].a00 = S(v), nd[x].a11 = -S(v), nd[x].a01 = nd[x].a10 = n > 1 ? S(0) : NEG;
        nd[x].asg = v, nd[x].hasAsg = 1;
    }

    void push(int x) {  // hand x's pending tags to its children
        if (!(nd[x].hasAsg)) return;
        // (the children get tags: fresh copies of them, since other trees may share them)
        if (nd[x].L) nd[x].L = clone(nd[x].L);
        if (nd[x].R) nd[x].R = clone(nd[x].R);
        if (nd[x].hasAsg) applyAssign(nd[x].L, nd[x].asg), applyAssign(nd[x].R, nd[x].asg), nd[x].hasAsg = 0;
    }

    void split(int t, long long k, int& a, int& b) {  // a = first k of t, b = the rest (as new nodes)
        if (!t) { a = b = 0; return; }
        t = clone(t);
        push(t);
        int x, y;  // (not straight into L[t] / R[t]: the clones below may move those arrays)
        if (nd[nd[t].L].sz >= k) split(nd[t].L, k, x, y), nd[t].L = y, a = x, b = t;
        else split(nd[t].R, k - nd[nd[t].L].sz - 1, x, y), nd[t].R = x, a = t, b = y;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's, as new nodes; the root is a with probability |a| / (|a| + |b|)
        if (!a || !b) return a | b;
        if (rnd() % (unsigned long long)(nd[a].sz + nd[b].sz) < (unsigned long long)nd[a].sz) {
            a = clone(a);
            push(a);
            nd[a].R = merge(nd[a].R, b);
            pull(a);
            return a;
        }
        b = clone(b);
        push(b);
        nd[b].L = merge(a, nd[b].L);
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
            long long ls = nd[nd[t].L].sz;
            if (i == ls) return t;
            if (i < ls) t = nd[t].L;
            else i -= ls + 1, t = nd[t].R;
        }
    }

    // ---- read-only range queries keep no copies; updates copy only the nodes they reach ----

    // a[l..r] of t's subtree as (node, whole subtree?) in order; a pending tag on the way is pushed down in place
    // (harmless: see the top), which copies only the children it hands the tag to, once
    void pieces(int t, long long l, long long r, vector<pair<int, bool>>& out) {
        if (!t || r < 0 || l >= nd[t].sz) return;
        if (l <= 0 && nd[t].sz - 1 <= r) {
            out.push_back({t, true});
            return;
        }
        push(t);
        long long ls = nd[nd[t].L].sz;
        pieces(nd[t].L, l, r, out);
        if (l <= ls && ls <= r) out.push_back({t, false});
        pieces(nd[t].R, l - ls - 1, r - ls - 1, out);
    }

    // a temporary node holding a[l..r]'s aggregates; mark = the pool size release() goes back to
    int rangeNode(long long l, long long r, size_t& mark) {
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);  // (every pending tag on the two boundary paths pushed down first)
        mark = nd.size();
        return rq(root, l, r);
    }

    int rq(int t, long long l, long long r) {  // a node over a[l..r] of t's subtree: t itself if that is all of it
        if (!t || r < 0 || l >= nd[t].sz) return 0;
        if (l <= 0 && nd[t].sz - 1 <= r) return t;
        long long ls = nd[nd[t].L].sz;
        if (r < ls) return rq(nd[t].L, l, r);
        if (l > ls) return rq(nd[t].R, l - ls - 1, r - ls - 1);
        int a = rq(nd[t].L, l, r), b = rq(nd[t].R, l - ls - 1, r - ls - 1);
        int y = clone(t);
        nd[y].L = a, nd[y].R = b;
        pull(y);
        return y;
    }

    void release(size_t mark) {  // drop every node made after mark (temporaries: no tree points to them)
        nd.resize(mark);
    }

    template <class F>
    int setAt(int t, long long i, const F& f) {  // t with a[i] = f(a[i]): new copies of the nodes on the path to it
        t = clone(t);
        push(t);
        long long ls = nd[nd[t].L].sz;
        if (i < ls) {
            int c = setAt(nd[t].L, i, f);
            nd[t].L = c;
        } else if (i > ls) {
            int c = setAt(nd[t].R, i - ls - 1, f);
            nd[t].R = c;
        } else {
            nd[t].val = f(nd[t].val);
        }
        pull(t);
        return t;
    }

    // t with the update f(x, off) on a[l..r] of its subtree (x: a node covered whole, off: its first value's distance
    // from l), copying only the nodes on the range's two boundary paths
    template <class F>
    int upd(int t, long long l, long long r, const F& f) {
        if (!t || r < 0 || l >= nd[t].sz) return t;
        t = clone(t);
        if (l <= 0 && nd[t].sz - 1 <= r) {
            f(t, -l);
            return t;
        }
        push(t);
        long long ls = nd[nd[t].L].sz;
        int a = upd(nd[t].L, l, r, f), b = upd(nd[t].R, l - ls - 1, r - ls - 1, f);
        nd[t].L = a, nd[t].R = b;
        if (l <= ls && ls <= r) {  // (t's own value: the update on a lone temporary copy of it)
            int y = clone(t);
            nd[y].L = nd[y].R = 0;
            pull(y);
            f(y, ls - l);
            nd[t].val = nd[y].val;
            release(y);
        }
        pull(t);
        return t;
    }
};

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     PersistentTreap<int> t({1, 2, 3, 4, 5});
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
