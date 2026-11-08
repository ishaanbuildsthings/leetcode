// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/persistent-treap-sum-suf-npre/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft copy cut getAll insertAt insertCopiesAt leftmostPrefixSumLtX leftmostPrefixSumLteX maxSuffixSum merge minPrefixSum paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeRotateLeft rangeRotateRight rangeSum rightmostSuffixSumGtX rightmostSuffixSumGteX size split sumAll trisect
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
//   leftmostPrefixSumLtX: log(N) expected
//   leftmostPrefixSumLteX: log(N) expected
//   maxSuffixSum: log(N) expected
//   merge: log(N) expected
//   minPrefixSum: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeSum: log(N) expected
//   rightmostSuffixSumGtX: log(N) expected
//   rightmostSuffixSumGteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   size: 1
//   pop: log(N) expected
//   popLeft: log(N) expected
//   sumAll: 1
//   build: N
// @memory:
//   layout: none
//   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] sm[1*N*log(N)] suf[1*N*log(N)] npre[1*N*log(N)]
//   tags: none
//   other: none
//   note: nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and copies share every node they don't change; log(N) is of the length, which can be huge (long long)

// Persistent implicit treap with composable aggregates: an array you can insert into anywhere, rotate, cut pieces out
// of (that is how to erase), paste them back and copy (copy(l, r): a[l..r] as a treap of its own in O(logN) however
// long, since the copy shares the same nodes; this one is unchanged); each node keeps its sum, its best suffix sum,
// its min prefix sum over its subtree. No node changes once another tree can see it: an op copies the nodes on its
// paths, so a copy and its original never affect each other. Lengths and indices are long long. All indices 0-based,
// ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when nothing
// qualifies.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct PersistentTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // one node pool shared by every PersistentTreap<T>: cut / paste move nodes between them, so a piece from one can
    // go into any other (node 0 = the empty tree). Nodes are never freed (memory = O(log N) per op, over the whole
    // run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        S sm = 0;
        S suf = 0;
        S npre = 0;
        long long sz = 0;
        T val = T(0);
        int L = 0;
        int R = 0;
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
            while (t) st.push_back(t), t = nd[t].L;
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

    // O(logN) expected -- first i in [l, r] with a[l] + ... + a[i] < x, or -1 (a walk pruned by min prefix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    long long leftmostPrefixSumLtX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumLtX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long pos = l;  // (the index of the current piece's first value; acc: the sum before it)
        S acc = 0;
        for (auto [t, whole] : ps) {
            if (!whole) {
                acc += S(nd[t].val);
                if (acc < S(x)) return pos;
                pos++;
                continue;
            }
            if (acc + nd[t].npre < S(x)) {
                long long i = 0;
                while (true) {
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
    long long leftmostPrefixSumLteX(long long l, long long r, T x) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostPrefixSumLteX: needs 0 <= l <= r < size()");
        vector<pair<int, bool>> ps;
        pieces(root, l, r, ps);
        long long pos = l;  // (the index of the current piece's first value; acc: the sum before it)
        S acc = 0;
        for (auto [t, whole] : ps) {
            if (!whole) {
                acc += S(nd[t].val);
                if (acc <= S(x)) return pos;
                pos++;
                continue;
            }
            if (acc + nd[t].npre <= S(x)) {
                long long i = 0;
                while (true) {
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

    // O(logN) expected -- max of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S maxSuffixSum(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("maxSuffixSum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].suf;
        release(mark);
        return res;
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    void merge(PersistentTreap& other) { root = merge(root, other.root), other.root = 0; }
    void merge(PersistentTreap&& other) { merge(other); }  // (a temporary: merge(t.copy()))

    // O(logN) expected -- min of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < size(), else throws
    // out_of_range
    S minPrefixSum(long long l, long long r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("minPrefixSum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].npre;
        release(mark);
        return res;
    }

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

    // O(logN) expected -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums);
    // needs 0 <= l <= r < size(), else throws out_of_range
    long long rightmostSuffixSumGtX(long long l, long long r, T x) {
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
    long long rightmostSuffixSumGteX(long long l, long long r, T x) {
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

    // O(1) -- sum of the whole array a[0..n-1] (read off the root); needs n >= 1, else throws out_of_range
    auto sumAll() {
        if (size() < 1) throw out_of_range("sumAll: needs n >= 1");
        return nd[root].sm;
    }

    // ---- internals ----

    int newNode(T v) {
        Node n;
        n.val = v, n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.suf = S(v), n.npre = S(v);
        nd.push_back(n);
        return (int)nd.size() - 1;
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
        n.val = nd[x].val, n.L = nd[x].L, n.R = nd[x].R, n.sz = nd[x].sz, n.sm = nd[x].sm, n.suf = nd[x].suf,
        n.npre = nd[x].npre;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    void pull(int x) {  // recompute x from its children
        int l = nd[x].L, r = nd[x].R;
        nd[x].sz = nd[l].sz + nd[r].sz + 1;
        T v = nd[x].val;
        S s = S(v), q = S(v), u = S(v);  // the node alone, then with its left / right parts
        if (l) {
            S ls = nd[l].sm, lq = nd[l].suf, lu = nd[l].npre;
            S ns = ls + s, nq = max(q, s + lq), nu = min(lu, ls + u);
            s = ns, q = nq, u = nu;
        }
        if (r) {
            S rs = nd[r].sm, rq = nd[r].suf, ru = nd[r].npre;
            S ns = s + rs, nq = max(rq, rs + q), nu = min(u, s + ru);
            s = ns, q = nq, u = nu;
        }
        nd[x].sm = s, nd[x].suf = q, nd[x].npre = u;
    }

    void split(int t, long long k, int& a, int& b) {  // a = first k of t, b = the rest (as new nodes)
        if (!t) { a = b = 0; return; }
        t = clone(t);
        int x, y;  // (not straight into L[t] / R[t]: the clones below may move those arrays)
        if (nd[nd[t].L].sz >= k) split(nd[t].L, k, x, y), nd[t].L = y, a = x, b = t;
        else split(nd[t].R, k - nd[nd[t].L].sz - 1, x, y), nd[t].R = x, a = t, b = y;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's, as new nodes; the root is a with probability |a| / (|a| + |b|)
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

    void cut(long long l, long long r, int& a, int& b, int& c) {  // a[0..l-1], a[l..r], a[r+1..]
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    int locate(long long i) {  // the node holding a[i], every tag on the way pushed (harmless in place: see the top)
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
    void pieces(int t, long long l, long long r, vector<pair<int, bool>>& out) {
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
