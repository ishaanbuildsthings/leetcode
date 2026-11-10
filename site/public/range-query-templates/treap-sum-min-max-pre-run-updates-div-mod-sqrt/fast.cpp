// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/treap-sum-min-max-pre-run-updates-div-mod-sqrt/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft cut getAll insertAt insertCopiesAt leftmostGtX leftmostGteX leftmostLtX leftmostLteX leftmostPrefixSumGtX leftmostPrefixSumGteX longestEqualRun maxAll maxPrefixSum merge minAll paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeFloorDiv rangeFloorSqrt rangeMax rangeMin rangeMod rangeRotateLeft rangeRotateRight rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX size split sumAll trisect
// @data-structure-type: treap
// @letters: same
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   cut: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: K+log(N) expected
//   leftmostGtX: log(N) expected
//   leftmostGteX: log(N) expected
//   leftmostLtX: log(N) expected
//   leftmostLteX: log(N) expected
//   leftmostPrefixSumGtX: log(N) expected
//   leftmostPrefixSumGteX: log(N) expected
//   longestEqualRun: log(N) expected
//   maxPrefixSum: log(N) expected
//   merge: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeFloorDiv: log(N)*log(U) amortized
//   rangeFloorSqrt: log(N)*log(log(U)) amortized
//   rangeMax: log(N) expected
//   rangeMin: log(N) expected
//   rangeMod: log(N)*log(U) amortized
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeSum: log(N) expected
//   rightmostGtX: log(N) expected
//   rightmostGteX: log(N) expected
//   rightmostLtX: log(N) expected
//   rightmostLteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   size: 1
//   pop: log(N) expected
//   popLeft: log(N) expected
//   sumAll: 1
//   minAll: 1
//   maxAll: 1
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mn[1*N] mx[1*N] pre[1*N] fv[1*N] lv[1*N] pr[1*N] sr[1*N] br[1*N]
//   tags: none
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

// Implicit treap with composable aggregates: an array you can insert into anywhere, rotate, move, cut pieces out of
// (that is how to erase) and paste them back in O(logN) expected each, with rangeFloorDiv, rangeMod, rangeFloorSqrt;
// each node keeps its sum, its min, its max, its best prefix sum, its first / last value and the equal runs at its
// ends and inside over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in the
// CURRENT array; searches return -1 when nothing qualifies.
// T: int, long long, ...; sums are kept in S (long long for small T).
// FAST MODE drawbacks compared with template.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        S sm = 0;
        S pre = 0;
        T val = T(0);
        T mn = T(0);
        T mx = T(0);
        T fv = T(0);
        T lv = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
        int pr = 0;
        int sr = 0;
        int br = 0;
    };
    static inline HotVector<Node> nd{Node{}};  // node 0 = the empty tree
    int root = 0;

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit ImplicitTreap(const vector<T>& arr = {}) { root = build(arr); }

    ImplicitTreap makeEmpty() const { return ImplicitTreap(); }  // (a new, empty one)

    LEETCODE_NO_SANITIZE static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(1) -- the current length of the array
    LEETCODE_NO_SANITIZE int size() const { return nd[root].sz; }

    // O(logN) expected -- append v to the end
    LEETCODE_NO_SANITIZE void append(T v) { root = merge(root, newNode(v)); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    LEETCODE_NO_SANITIZE void appendLeft(T v) { insertAt(0, v); }

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
    LEETCODE_NO_SANITIZE vector<T> getAll() {
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
    LEETCODE_NO_SANITIZE void insertAt(int i, T v) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    // 0 <= i <= size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void insertCopiesAt(int i, T v, long long k) {
        if (i < 0 || i > size()) throw out_of_range("insertCopiesAt: needs 0 <= i <= size()");
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int pos = l;  // (the index of the current piece's first value)
        for (auto [t, whole] : ps) {
            if (!whole) {
                if (nd[t].val > x) return pos;
                pos++;
                continue;
            }
            if (nd[t].mx > x) {
                int i = 0;
                while (true) {
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
    LEETCODE_NO_SANITIZE int leftmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostGteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int pos = l;  // (the index of the current piece's first value)
        for (auto [t, whole] : ps) {
            if (!whole) {
                if (nd[t].val >= x) return pos;
                pos++;
                continue;
            }
            if (nd[t].mx >= x) {
                int i = 0;
                while (true) {
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
    LEETCODE_NO_SANITIZE int leftmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostLtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int pos = l;  // (the index of the current piece's first value)
        for (auto [t, whole] : ps) {
            if (!whole) {
                if (nd[t].val < x) return pos;
                pos++;
                continue;
            }
            if (nd[t].mn < x) {
                int i = 0;
                while (true) {
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
    LEETCODE_NO_SANITIZE int leftmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostLteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int pos = l;  // (the index of the current piece's first value)
        for (auto [t, whole] : ps) {
            if (!whole) {
                if (nd[t].val <= x) return pos;
                pos++;
                continue;
            }
            if (nd[t].mn <= x) {
                int i = 0;
                while (true) {
                    if (nd[t].L && nd[nd[t].L].mn <= x) t = nd[t].L;
                    else if (nd[t].val <= x) return pos + i + nd[nd[t].L].sz;
                    else i += nd[nd[t].L].sz + 1, t = nd[t].R;
                }
            }
            pos += nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostPrefixSumGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumGtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int pos = l;  // (the index of the current piece's first value; acc: the sum before it)
        S acc = 0;
        for (auto [t, whole] : ps) {
            if (!whole) {
                acc += S(nd[t].val);
                if (acc > S(x)) return pos;
                pos++;
                continue;
            }
            if (acc + nd[t].pre > S(x)) {
                int i = 0;
                while (true) {
                    int lt = nd[t].L;
                    if (lt && acc + nd[lt].pre > S(x)) {
                        t = lt;
                        continue;
                    }
                    acc += nd[lt].sm;
                    if (acc + S(nd[t].val) > S(x)) return pos + i + nd[lt].sz;
                    acc += S(nd[t].val), i += nd[lt].sz + 1, t = nd[t].R;
                }
            }
            acc += nd[t].sm, pos += nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (a walk pruned by best prefix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostPrefixSumGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumGteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int pos = l;  // (the index of the current piece's first value; acc: the sum before it)
        S acc = 0;
        for (auto [t, whole] : ps) {
            if (!whole) {
                acc += S(nd[t].val);
                if (acc >= S(x)) return pos;
                pos++;
                continue;
            }
            if (acc + nd[t].pre >= S(x)) {
                int i = 0;
                while (true) {
                    int lt = nd[t].L;
                    if (lt && acc + nd[lt].pre >= S(x)) {
                        t = lt;
                        continue;
                    }
                    acc += nd[lt].sm;
                    if (acc + S(nd[t].val) >= S(x)) return pos + i + nd[lt].sz;
                    acc += S(nd[t].val), i += nd[lt].sz + 1, t = nd[t].R;
                }
            }
            acc += nd[t].sm, pos += nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- the longest run of equal adjacent values in a[l..r]; needs 0 <= l <= r < size(), else
    // throws out_of_range
    LEETCODE_NO_SANITIZE int longestEqualRun(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("longestEqualRun: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        int res = nd[b].br;
        release(mark);
        return res;
    }

    // O(logN) expected -- max of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S maxPrefixSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("maxPrefixSum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].pre;
        release(mark);
        return res;
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    LEETCODE_NO_SANITIZE void merge(ImplicitTreap& other) { root = merge(root, other.root), other.root = 0; }

    // O(logN) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i] (needs
    // 0 <= i <= size(), else throws out_of_range); other is left empty
    LEETCODE_NO_SANITIZE void paste(int i, ImplicitTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }

    // O(logN) expected -- a[i] += v; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAdd: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = nd[t].val + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmax: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = max(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmin: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = min(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return nd[locate(i)].val;
    }

    // amortized O(logN * logU) expected -- a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing);
    // needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeFloorDiv(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeFloorDiv: needs 0 <= l <= r < size()");
        if (x >= 2) upd(root, l, r, [&](int y, int off) { (void)off; shrink(y, T(1), [x](T v) { return T(v / x); }); },
            [&](T w, int off) { (void)off; return w >= 1 ? T(w / x) : w; });
    }

    // amortized O(logN * loglogU) expected -- a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0); needs
    // 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeFloorSqrt(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeFloorSqrt: needs 0 <= l <= r < size()");
        upd(root, l, r, [&](int y, int off) { (void)off; shrink(y, T(2), isqrtT); },
            [&](T w, int off) { (void)off; return w >= 2 ? isqrtT(w) : w; });
    }

    // O(logN) expected -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMax: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        T res = nd[b].mx;
        release(mark);
        return res;
    }

    // O(logN) expected -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMin: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        T res = nd[b].mn;
        release(mark);
        return res;
    }

    // amortized O(logN * logU) expected -- a[i] %= x for i in [l, r] (values >= 0, x >= 1); needs
    // 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeMod(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMod: needs 0 <= l <= r < size()");
        if (x >= 1) upd(root, l, r, [&](int y, int off) { (void)off; shrink(y, x, [x](T v) { return T(v % x); }); },
            [&](T w, int off) { (void)off; return w >= x ? T(w % x) : w; });
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
    // taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateLeft(int l, int r, long long k) {
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
    LEETCODE_NO_SANITIZE void rangeRotateRight(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -k);
    }

    // O(logN) expected -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeSum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].sm;
        release(mark);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int end = r;  // (the index of the current piece's last value)
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                if (nd[t].val > x) return end;
                end--;
                continue;
            }
            if (nd[t].mx > x) {
                int start = end - nd[t].sz + 1, i = 0;
                while (true) {
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
    LEETCODE_NO_SANITIZE int rightmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostGteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int end = r;  // (the index of the current piece's last value)
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                if (nd[t].val >= x) return end;
                end--;
                continue;
            }
            if (nd[t].mx >= x) {
                int start = end - nd[t].sz + 1, i = 0;
                while (true) {
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
    LEETCODE_NO_SANITIZE int rightmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostLtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int end = r;  // (the index of the current piece's last value)
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                if (nd[t].val < x) return end;
                end--;
                continue;
            }
            if (nd[t].mn < x) {
                int start = end - nd[t].sz + 1, i = 0;
                while (true) {
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
    LEETCODE_NO_SANITIZE int rightmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostLteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        int end = r;  // (the index of the current piece's last value)
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                if (nd[t].val <= x) return end;
                end--;
                continue;
            }
            if (nd[t].mn <= x) {
                int start = end - nd[t].sz + 1, i = 0;
                while (true) {
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
    LEETCODE_NO_SANITIZE pair<ImplicitTreap, ImplicitTreap> split(int k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        ImplicitTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty; needs
    // 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE tuple<ImplicitTreap, ImplicitTreap, ImplicitTreap> trisect(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        ImplicitTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cut(l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // O(log(N) expected) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T pop() {
        auto n = size();
        if (n < 1) throw out_of_range("pop: needs size() >= 1");
        T v = pointGet(n - 1);
        cut(n - 1, n - 1);
        return v;
    }

    // O(log(N) expected) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        T v = pointGet(0);
        cut(0, 0);
        return v;
    }

    // O(1) -- sum of the whole array a[0..n-1] (read off the root); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (size() < 1) throw out_of_range("sumAll: needs n >= 1");
        return nd[root].sm;
    }

    // O(1) -- min of the whole array a[0..n-1] (read off the root); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto minAll() {
        if (size() < 1) throw out_of_range("minAll: needs n >= 1");
        return nd[root].mn;
    }

    // O(1) -- max of the whole array a[0..n-1] (read off the root); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto maxAll() {
        if (size() < 1) throw out_of_range("maxAll: needs n >= 1");
        return nd[root].mx;
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE int newNode(T v) {
        Node n;
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.mn = v, n.mx = v, n.pre = S(v), n.fv = v,
        n.lv = v, n.pr = 1, n.sr = 1, n.br = 1;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    // a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    LEETCODE_NO_SANITIZE int build(const vector<T>& vals) {
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

    LEETCODE_NO_SANITIZE void pull(int x) {  // recompute x from its children
        int l = nd[x].L, r = nd[x].R;
        nd[x].sz = nd[l].sz + nd[r].sz + 1;
        T v = nd[x].val;
        S s = S(v), p = S(v);  // the node alone, then with its left / right parts
        if (l) {
            S ls = nd[l].sm, lp = nd[l].pre;
            S ns = ls + s, np = max(lp, ls + p);
            s = ns, p = np;
        }
        if (r) {
            S rs = nd[r].sm, rp = nd[r].pre;
            S ns = s + rs, np = max(p, s + rp);
            s = ns, p = np;
        }
        nd[x].sm = s, nd[x].pre = p;
        nd[x].mn = v;
        if (l && nd[l].mn < nd[x].mn) nd[x].mn = nd[l].mn;
        if (r && nd[r].mn < nd[x].mn) nd[x].mn = nd[r].mn;
        nd[x].mx = v;
        if (l && nd[l].mx > nd[x].mx) nd[x].mx = nd[l].mx;
        if (r && nd[r].mx > nd[x].mx) nd[x].mx = nd[r].mx;
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
    }

    // floor(sqrt(v)) for v >= 0, exact for every 64-bit value
    LEETCODE_NO_SANITIZE static T isqrtT(T v) {
        T r = (T)sqrtl((long double)v);
        while (r > 0 && (__int128)r * r > v) r--;
        while ((__int128)(r + 1) * (r + 1) <= v) r++;
        return r;
    }

    template <class F>
    LEETCODE_NO_SANITIZE void shrink(int t, T lim, const F& f) {
        // every value v >= lim under t becomes f(v) (the rest are fixed)
        if (!t || nd[t].mx < lim) return;
        if (nd[t].val >= lim) nd[t].val = f(nd[t].val);
        shrink(nd[t].L, lim, f), shrink(nd[t].R, lim, f);
        pull(t);
    }

    LEETCODE_NO_SANITIZE void split(int t, int k, int& a, int& b) {  // a = first k of t, b = the rest
        if (!t) { a = b = 0; return; }
        if (nd[nd[t].L].sz >= k) split(nd[t].L, k, a, nd[t].L), b = t;
        else split(nd[t].R, k - nd[nd[t].L].sz - 1, nd[t].R, b), a = t;
        pull(t);
    }

    LEETCODE_NO_SANITIZE int merge(int a, int b) {  // a's elements, then b's
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

    LEETCODE_NO_SANITIZE void cut(int l, int r, int& a, int& b, int& c) {  // a[0..l-1], a[l..r], a[r+1..]
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    LEETCODE_NO_SANITIZE int locate(int i, vector<int>* path = nullptr) {
        // the node holding a[i], every tag on the way pushed
        int t = root;
        while (true) {
            int ls = nd[nd[t].L].sz;
            if (i == ls) return t;
            if (path) path->push_back(t);
            if (i < ls) t = nd[t].L;
            else i -= ls + 1, t = nd[t].R;
        }
    }

    // ---- queries, searches and range updates walk the pieces of [l, r] instead of cutting it out ----

    // a[l..r] of t's subtree as (node, whole subtree?) in order; pending tags on the way pushed down
    LEETCODE_NO_SANITIZE void pieces(int t, int l, int r, vector<pair<int, bool>>& out) {
        if (!t || r < 0 || l >= nd[t].sz) return;
        if (l <= 0 && nd[t].sz - 1 <= r) {
            out.push_back({t, true});
            return;
        }
        int ls = nd[nd[t].L].sz;
        pieces(nd[t].L, l, r, out);
        if (l <= ls && ls <= r) out.push_back({t, false});
        pieces(nd[t].R, l - ls - 1, r - ls - 1, out);
    }

    // a temporary node holding a[l..r]'s aggregates; mark = the pool size release() goes back to
    LEETCODE_NO_SANITIZE int rangeNode(int l, int r, size_t& mark) {
        mark = nd.size();
        return rq(root, l, r);
    }

    // a node over a[l..r] of t's subtree: t itself if that is all of it, else temporaries made only where two parts
    // meet (pending tags on the way pushed down)
    LEETCODE_NO_SANITIZE int rq(int t, int l, int r) {
        if (!t || r < 0 || l >= nd[t].sz) return 0;
        if (l <= 0 && nd[t].sz - 1 <= r) return t;
        int ls = nd[nd[t].L].sz;
        if (r < ls) return rq(nd[t].L, l, r);
        if (l > ls) return rq(nd[t].R, l - ls - 1, r - ls - 1);
        int a = rq(nd[t].L, l, r), b = rq(nd[t].R, l - ls - 1, r - ls - 1);
        int y = clone(t);
        nd[y].L = a, nd[y].R = b;
        pull(y);
        return y;
    }

    LEETCODE_NO_SANITIZE int clone(int x) {  // a temporary copy of node x (sharing its children), dropped by release
        Node n;
        n.val = nd[x].val, n.pri = nd[x].pri, n.L = nd[x].L, n.R = nd[x].R, n.sz = nd[x].sz, n.sm = nd[x].sm,
        n.mn = nd[x].mn, n.mx = nd[x].mx, n.pre = nd[x].pre, n.fv = nd[x].fv, n.lv = nd[x].lv, n.pr = nd[x].pr,
        n.sr = nd[x].sr, n.br = nd[x].br;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    LEETCODE_NO_SANITIZE void release(size_t mark) {
        // drop every node made after mark (temporaries: no tree points to them)
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
    LEETCODE_NO_SANITIZE void upd(int t, int l, int r, const F& f, const H& h) {
        if (!t || r < 0 || l >= nd[t].sz) return;
        if (l <= 0 && nd[t].sz - 1 <= r) {
            f(t, -l);
            return;
        }
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
