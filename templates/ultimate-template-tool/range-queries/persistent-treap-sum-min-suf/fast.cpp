// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/persistent-treap-sum-min-suf/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft copy cut getAll insertAt insertCopiesAt leftmostLtX leftmostLteX maxSuffixSum merge minAll paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeMin rangeRotateLeft rangeRotateRight rangeSum rightmostLtX rightmostLteX rightmostSuffixSumGtX rightmostSuffixSumGteX size split sumAll trisect
// @data-structure-type: persistent-treap
// @letters: same
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   copy: log(N) expected
//   cut: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: K+log(N) expected
//   leftmostLtX: log(N) expected
//   leftmostLteX: log(N) expected
//   maxSuffixSum: log(N) expected
//   merge: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeMin: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeSum: log(N) expected
//   rightmostLtX: log(N) expected
//   rightmostLteX: log(N) expected
//   rightmostSuffixSumGtX: log(N) expected
//   rightmostSuffixSumGteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   size: 1
//   pop: log(N) expected
//   popLeft: log(N) expected
//   sumAll: 1
//   minAll: 1
//   build: N
// @memory:
//   layout: none
//   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] sm[1*N*log(N)] mn[1*N*log(N)] suf[1*N*log(N)]
//   tags: none
//   other: none
//   note: nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and copies share every node they don't change; log(N) is of the length, which can be huge (long long)

// Persistent implicit treap with composable aggregates: an array you can insert into anywhere, rotate, cut pieces out
// of (that is how to erase), paste them back and copy (copy(l, r): a[l..r] as a treap of its own in O(logN) however
// long, since the copy shares the same nodes; this one is unchanged); each node keeps its sum, its min, its best
// suffix sum over its subtree. No node changes once another tree can see it: an op copies the nodes on its paths, so
// a copy and its original never affect each other. Lengths and indices are long long. All indices 0-based, ranges
// inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when nothing qualifies.
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
struct PersistentTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // one node pool shared by every PersistentTreap<T>: cut / paste move nodes between them, so a piece from one can
    // go into any other (node 0 = the empty tree). Nodes are never freed (memory = O(log N) per op, over the whole
    // run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        S sm = 0;
        S suf = 0;
        long long sz = 0;
        T val = T(0);
        T mn = T(0);
        int L = 0;
        int R = 0;
    };
    static inline HotVector<Node> nd{Node{}};  // node 0 = the empty tree
    int root = 0;

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit PersistentTreap(const vector<T>& arr = {}) { root = build(arr); }

    PersistentTreap makeEmpty() const { return PersistentTreap(); }  // (a new, empty one)

    LEETCODE_NO_SANITIZE static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(1) -- the current length of the array
    LEETCODE_NO_SANITIZE long long size() const { return nd[root].sz; }

    // O(logN) expected -- append v to the end
    LEETCODE_NO_SANITIZE void append(T v) { root = merge(root, newNode(v)); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    LEETCODE_NO_SANITIZE void appendLeft(T v) { insertAt(0, v); }

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
    LEETCODE_NO_SANITIZE void insertAt(long long i, T v) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    // 0 <= i <= size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void insertCopiesAt(long long i, T v, long long k) {
        if (i < 0 || i > size()) throw out_of_range("insertCopiesAt: needs 0 <= i <= size()");
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN) expected -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min); needs
    // 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostLtX(long long l, long long r, T x) {
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
    LEETCODE_NO_SANITIZE long long leftmostLteX(long long l, long long r, T x) {
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
                    if (nd[t].L && nd[nd[t].L].mn <= x) t = nd[t].L;
                    else if (nd[t].val <= x) return pos + i + nd[nd[t].L].sz;
                    else i += nd[nd[t].L].sz + 1, t = nd[t].R;
                }
            }
            pos += nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- max of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE S maxSuffixSum(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("maxSuffixSum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].suf;
        release(mark);
        return res;
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    LEETCODE_NO_SANITIZE void merge(PersistentTreap& other) { root = merge(root, other.root), other.root = 0; }
    LEETCODE_NO_SANITIZE void merge(PersistentTreap&& other) { merge(other); }  // (a temporary: merge(t.copy()))

    // O(logN) expected -- insert all of other (any PersistentTreap, e.g. a cut piece) so it starts at a[i] (needs
    // 0 <= i <= size(), else throws out_of_range); other is left empty
    LEETCODE_NO_SANITIZE void paste(long long i, PersistentTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }
    // (a temporary: paste(i, t.copy(l, r)))
    LEETCODE_NO_SANITIZE void paste(long long i, PersistentTreap&& other) { paste(i, other); }

    // O(logN) expected -- a[i] += v (copies the one path down to a[i]); needs 0 <= i < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAdd: needs 0 <= i < size()");
        root = setAt(root, i, [&](T w) { return T(w + v); });
    }

    // O(logN) expected -- a[i] = v (copies the one path down to a[i]); needs 0 <= i < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        root = setAt(root, i, [&](T w) { return v; });
    }

    // O(logN) expected -- a[i] = max(a[i], v) (copies the one path down to a[i]); needs 0 <= i < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(long long i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmax: needs 0 <= i < size()");
        root = setAt(root, i, [&](T w) { return max(w, v); });
    }

    // O(logN) expected -- a[i] = min(a[i], v) (copies the one path down to a[i]); needs 0 <= i < size(), else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(long long i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmin: needs 0 <= i < size()");
        root = setAt(root, i, [&](T w) { return min(w, v); });
    }

    // O(logN) expected -- a[i]; needs 0 <= i < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return nd[locate(i)].val;
    }

    // O(logN) expected -- min of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMin: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        T res = nd[b].mn;
        release(mark);
        return res;
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
    // taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeRotateLeft(long long l, long long r, long long k) {
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
    LEETCODE_NO_SANITIZE void rangeRotateRight(long long l, long long r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -k);
    }

    // O(logN) expected -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeSum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].sm;
        release(mark);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min); needs
    // 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostLtX(long long l, long long r, T x) {
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
    LEETCODE_NO_SANITIZE long long rightmostLteX(long long l, long long r, T x) {
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
                    if (nd[t].R && nd[nd[t].R].mn <= x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                    else if (nd[t].val <= x) return start + i + nd[nd[t].L].sz;
                    else t = nd[t].L;
                }
            }
            end -= nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostSuffixSumGtX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostSuffixSumGtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long end = r;  // (the index of the current piece's last value; acc: the sum after it)
        S acc = 0;
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                acc += S(nd[t].val);
                if (acc > S(x)) return end;
                end--;
                continue;
            }
            if (acc + nd[t].suf > S(x)) {
                long long start = end - nd[t].sz + 1, i = 0;
                while (true) {
                    int rt = nd[t].R;
                    if (rt && acc + nd[rt].suf > S(x)) {
                        i += nd[nd[t].L].sz + 1, t = rt;
                        continue;
                    }
                    acc += nd[rt].sm;
                    if (acc + S(nd[t].val) > S(x)) return start + i + nd[nd[t].L].sz;
                    acc += S(nd[t].val), t = nd[t].L;
                }
            }
            acc += nd[t].sm, end -= nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (a walk pruned by best suffix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostSuffixSumGteX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostSuffixSumGteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long end = r;  // (the index of the current piece's last value; acc: the sum after it)
        S acc = 0;
        for (int k = (int)ps.size() - 1; k >= 0; k--) {
            auto [t, whole] = ps[k];
            if (!whole) {
                acc += S(nd[t].val);
                if (acc >= S(x)) return end;
                end--;
                continue;
            }
            if (acc + nd[t].suf >= S(x)) {
                long long start = end - nd[t].sz + 1, i = 0;
                while (true) {
                    int rt = nd[t].R;
                    if (rt && acc + nd[rt].suf >= S(x)) {
                        i += nd[nd[t].L].sz + 1, t = rt;
                        continue;
                    }
                    acc += nd[rt].sm;
                    if (acc + S(nd[t].val) >= S(x)) return start + i + nd[nd[t].L].sz;
                    acc += S(nd[t].val), t = nd[t].L;
                }
            }
            acc += nd[t].sm, end -= nd[t].sz;
        }
        return -1;
    }

    // O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty; needs
    // 0 <= k <= size(), else throws out_of_range
    LEETCODE_NO_SANITIZE pair<PersistentTreap, PersistentTreap> split(long long k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        PersistentTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty; needs
    // 0 <= l <= r < size(), else throws out_of_range
    LEETCODE_NO_SANITIZE tuple<PersistentTreap, PersistentTreap, PersistentTreap> trisect(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        PersistentTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
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

    // ---- internals ----

    LEETCODE_NO_SANITIZE int newNode(T v) {
        Node n;
        n.val = v, n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.mn = v, n.suf = S(v);
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    LEETCODE_NO_SANITIZE int build(const vector<T>& vals) { return build(vals, 0, (int)vals.size()); }

    LEETCODE_NO_SANITIZE int build(const vector<T>& vals, int lo, int hi) {
        // a balanced tree of new nodes holding vals[lo, hi), O(len)
        if (lo >= hi) return 0;
        int mid = (lo + hi) / 2, x = newNode(vals[mid]);
        int l = build(vals, lo, mid), r = build(vals, mid + 1, hi);
        nd[x].L = l, nd[x].R = r;
        pull(x);
        return x;
    }

    LEETCODE_NO_SANITIZE int clone(int x) {  // a new copy of node x (sharing its children)
        Node n;
        n.val = nd[x].val, n.L = nd[x].L, n.R = nd[x].R, n.sz = nd[x].sz, n.sm = nd[x].sm, n.mn = nd[x].mn,
        n.suf = nd[x].suf;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    LEETCODE_NO_SANITIZE void pull(int x) {  // recompute x from its children
        int l = nd[x].L, r = nd[x].R;
        nd[x].sz = nd[l].sz + nd[r].sz + 1;
        T v = nd[x].val;
        S s = S(v), q = S(v);  // the node alone, then with its left / right parts
        if (l) {
            S ls = nd[l].sm, lq = nd[l].suf;
            S ns = ls + s, nq = max(q, s + lq);
            s = ns, q = nq;
        }
        if (r) {
            S rs = nd[r].sm, rq = nd[r].suf;
            S ns = s + rs, nq = max(rq, rs + q);
            s = ns, q = nq;
        }
        nd[x].sm = s, nd[x].suf = q;
        nd[x].mn = v;
        if (l && nd[l].mn < nd[x].mn) nd[x].mn = nd[l].mn;
        if (r && nd[r].mn < nd[x].mn) nd[x].mn = nd[r].mn;
    }

    LEETCODE_NO_SANITIZE void split(int t, long long k, int& a, int& b) {
        // a = first k of t, b = the rest (as new nodes)
        if (!t) { a = b = 0; return; }
        t = clone(t);
        int x, y;  // (not straight into L[t] / R[t]: the clones below may move those arrays)
        if (nd[nd[t].L].sz >= k) split(nd[t].L, k, x, y), nd[t].L = y, a = x, b = t;
        else split(nd[t].R, k - nd[nd[t].L].sz - 1, x, y), nd[t].R = x, a = t, b = y;
        pull(t);
    }

    LEETCODE_NO_SANITIZE int merge(int a, int b) {
        // a's elements, then b's, as new nodes; the root is a with probability |a| / (|a| + |b|)
        if (!a || !b) return a | b;
        if (rnd() % (unsigned long long)(nd[a].sz + nd[b].sz) < (unsigned long long)nd[a].sz) {
            a = clone(a);
            nd[a].R = merge(nd[a].R, b);
            pull(a);
            return a;
        }
        b = clone(b);
        nd[b].L = merge(a, nd[b].L);
        pull(b);
        return b;
    }

    LEETCODE_NO_SANITIZE void cut(long long l, long long r, int& a, int& b, int& c) {  // a[0..l-1], a[l..r], a[r+1..]
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    LEETCODE_NO_SANITIZE int locate(long long i) {
        // the node holding a[i], every tag on the way pushed (harmless in place: see the top)
        int t = root;
        while (true) {
            long long ls = nd[nd[t].L].sz;
            if (i == ls) return t;
            if (i < ls) t = nd[t].L;
            else i -= ls + 1, t = nd[t].R;
        }
    }

    // ---- read-only range queries keep no copies; updates copy only the nodes they reach ----

    // a[l..r] of t's subtree as (node, whole subtree?) in order; a pending tag on the way is pushed down in place
    // (harmless: see the top), which copies only the children it hands the tag to, once
    LEETCODE_NO_SANITIZE void pieces(int t, long long l, long long r, vector<pair<int, bool>>& out) {
        if (!t || r < 0 || l >= nd[t].sz) return;
        if (l <= 0 && nd[t].sz - 1 <= r) {
            out.push_back({t, true});
            return;
        }
        long long ls = nd[nd[t].L].sz;
        pieces(nd[t].L, l, r, out);
        if (l <= ls && ls <= r) out.push_back({t, false});
        pieces(nd[t].R, l - ls - 1, r - ls - 1, out);
    }

    // a temporary node holding a[l..r]'s aggregates; mark = the pool size release() goes back to
    LEETCODE_NO_SANITIZE int rangeNode(long long l, long long r, size_t& mark) {
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);  // (every pending tag on the two boundary paths pushed down first)
        mark = nd.size();
        return rq(root, l, r);
    }

    LEETCODE_NO_SANITIZE int rq(int t, long long l, long long r) {
        // a node over a[l..r] of t's subtree: t itself if that is all of it
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

    LEETCODE_NO_SANITIZE void release(size_t mark) {
        // drop every node made after mark (temporaries: no tree points to them)
        nd.resize(mark);
    }

    template <class F>
    LEETCODE_NO_SANITIZE int setAt(int t, long long i, const F& f) {
        // t with a[i] = f(a[i]): new copies of the nodes on the path to it
        t = clone(t);
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
    LEETCODE_NO_SANITIZE int upd(int t, long long l, long long r, const F& f) {
        if (!t || r < 0 || l >= nd[t].sz) return t;
        t = clone(t);
        if (l <= 0 && nd[t].sz - 1 <= r) {
            f(t, -l);
            return t;
        }
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
