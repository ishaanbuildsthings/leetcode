// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/persistent-treap-value-map-rev-counts-sums/letters.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: append appendLeft copy countOccurrences cut getAll insertAt insertCopiesAt leftmostIndexOf leftmostIndexOfInRange merge paste pointAssign pointGet pop popLeft rangeAssign rangeReplace rangeReverse rangeRotateLeft rangeRotateRight rightmostIndexOf rightmostIndexOfInRange size split trisect
// @data-structure-type: persistent-treap
// @complexities:
//   append: U*log(N) expected
//   appendLeft: U*log(N) expected
//   copy: U*log(N) expected
//   countOccurrences: U*log(N) expected
//   cut: U*log(N) expected
//   getAll: N*log(N) expected
//   insertAt: U*log(N) expected
//   insertCopiesAt: U*log(N) expected
//   leftmostIndexOf: U*log(N) expected
//   leftmostIndexOfInRange: U*log(N) expected
//   merge: U*log(N) expected
//   paste: U*log(N) expected
//   pointAssign: U*log(N) expected
//   pointGet: log(N) expected
//   rangeAssign: U*log(N) expected
//   rangeReplace: U*log(N) expected
//   rangeReverse: U*log(N) expected
//   rangeRotateLeft: U*log(N) expected
//   rangeRotateRight: U*log(N) expected
//   rightmostIndexOf: U*log(N) expected
//   rightmostIndexOfInRange: U*log(N) expected
//   split: U*log(N) expected
//   trisect: U*log(N) expected
//   size: 1
//   pop: U*log(N) expected
//   popLeft: U*log(N) expected
//   build: N*U
// @memory:
//   layout: none
//   node: val[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] sz[1*N*log(N)] cnt[1*N*log(N)*U] sm[1*N*log(N)]
//   tags: mp[1*N*log(N)*U] rev[1*N*log(N)]
//   other: none
//   note: nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and copies share every node they don't change; U = valHi - valLo + 1; every PersistentValueMapTreap shares one node pool and so one value range [valLo, valHi] (the last constructor's); a pending tag is a whole map old value -> new value, so a push costs O(U)

// Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
// operations that make sense on characters are listed.
// Implicit treap whose lazy tag is a value map (mass change, CF 911G, with sequence edits): an array you can insert
// into anywhere, reverse, rotate, cut pieces out of (that is how to erase) and paste them back, and copy (copy(l, r):
// a[l..r] as a treap of its own in O(log N) however long; every op copies the nodes it changes, so copies never
// affect each other); plus rangeReplace(l, r, x, y) (every x in a[l..r] becomes y) and rangeAssign, in O(U log N)
// expected, U = valHi - valLo + 1: good when the values are few. A pending tag is a map old value -> new value, so
// any mix of changes composes into one map. Each node also keeps how many times each value appears in its subtree and
// its sum (countOccurrences, where x first / last appears, rangeSum; read without changing anything). All indices
// 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when
// nothing qualifies.
// T: int, long long, char, ...: the values; valLo / valHi bound every value the array will ever hold

template <typename T>
struct PersistentValueMapTreap {
    using S = long long;  // sums
    using Z = long long;  // lengths, indices and counts (long long: copies can make the array huge)
    // one node pool shared by every PersistentValueMapTreap<T>: pieces move between them (node 0 = the empty tree). Nodes are never
    // freed, so there is nothing to reset between test cases; every one shares the value range too (the last
    // constructor's [valLo, valHi]). val: the node's value - valLo (every map that reached it already applied); the
    // map it still owes its children is rows[row * U ..] (row = -1: none). A map row exists only while pending:
    // handed down, it is reused
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int val = 0, L = 0, R = 0;
        Z sz = 0;
        char rev = 0;
        int row = -1;
        S sm = 0;
    };
    static inline vector<Node> nd{Node{}};
    static inline vector<int> rows, freeRows, gbuf;  // U entries per map row
    static inline vector<Z> cnt, tmp;  // U entries per node: how many of each value in its subtree
    static inline int U = 0;
    static inline T valLo = T(0);
    int root = 0;

    PersistentValueMapTreap() {}  // (an empty one, on the current value range)

    // O(N*U) -- arr: the initial array; every value it will ever hold must be in [valLo, valHi]
    PersistentValueMapTreap(const vector<T>& arr, T lo, T hi) {
        setRange(lo, hi);
        vector<int> offs;
        offs.reserve(arr.size());
        for (const T& v : arr) offs.push_back(off(v));
        root = build(offs);
    }

    PersistentValueMapTreap makeEmpty() const { return PersistentValueMapTreap(); }

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(1) -- the current length of the array
    long long size() const { return nd[root].sz; }

    // O(U*logN) expected -- append v to the end; needs valLo <= v <= valHi
    void append(T v) { root = mergeNodes(root, newNode(off(v))); }

    // O(U*logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(U*logN) expected -- insert v so it becomes a[i]; needs valLo <= v <= valHi; needs 0 <= i <= size(), else
    // throws out_of_range
    void insertAt(Z i, T v) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int o = off(v), a, c;
        splitNodes(root, i, a, c);
        root = mergeNodes(mergeNodes(a, newNode(o)), c);
    }

    // O(k*U + U*logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    // 0 <= i <= size(), else throws out_of_range
    void insertCopiesAt(Z i, T v, Z k) {
        if (i < 0 || i > size()) throw out_of_range("insertCopiesAt: needs 0 <= i <= size()");
        if (k <= 0) return;
        int o = off(v), a, c;
        splitNodes(root, i, a, c);
        root = mergeNodes(mergeNodes(a, build(vector<int>(k, o))), c);
    }

    // O(1) -- the whole array as a PersistentValueMapTreap of its own; this one is unchanged (they share every node)
    PersistentValueMapTreap copy() const { return *this; }

    // O(U*logN) expected -- a[l..r] as a PersistentValueMapTreap of its own; this one is unchanged. The copy shares
    // this one's nodes, so it costs O(U*logN) however long it is; needs 0 <= l <= r < size(), else throws
    // out_of_range
    PersistentValueMapTreap copy(Z l, Z r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("copy: needs 0 <= l <= r < size()");
        int a, b, c;
        cutNodes(l, r, a, b, c);
        PersistentValueMapTreap piece = makeEmpty();
        piece.root = b;
        return piece;
    }

    // O(U*logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0); needs
    // 0 <= l <= r < size(), else throws out_of_range
    PersistentValueMapTreap cut(Z l, Z r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("cut: needs 0 <= l <= r < size()");
        int a, b, c;
        cutNodes(l, r, a, b, c);
        root = mergeNodes(a, c);
        PersistentValueMapTreap piece = makeEmpty();
        piece.root = b;
        return piece;
    }

    // O(U*logN) expected -- insert all of other (e.g. a cut piece) so it starts at a[i]; other is left empty; needs
    // 0 <= i <= size(), else throws out_of_range
    void paste(Z i, PersistentValueMapTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, c;
        splitNodes(root, i, a, c);
        root = mergeNodes(mergeNodes(a, other.root), c);
        other.root = 0;
    }
    void paste(Z i, PersistentValueMapTreap&& other) { paste(i, other); }  // (a temporary: paste(i, t.copy(l, r))

    // O(U*logN) expected -- append all of other at the end; other is left empty
    void merge(PersistentValueMapTreap& other) {
        root = mergeNodes(root, other.root);
        other.root = 0;
    }
    void merge(PersistentValueMapTreap&& other) { merge(other); }  // (a temporary: merge(t.copy())

    // O(U*logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty; needs
    // 0 <= k <= size(), else throws out_of_range
    pair<PersistentValueMapTreap, PersistentValueMapTreap> split(Z k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        PersistentValueMapTreap left = makeEmpty(), right = makeEmpty();
        splitNodes(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(U*logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty;
    // needs 0 <= l <= r < size(), else throws out_of_range
    tuple<PersistentValueMapTreap, PersistentValueMapTreap, PersistentValueMapTreap> trisect(Z l, Z r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("trisect: needs 0 <= l <= r < size()");
        PersistentValueMapTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cutNodes(l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // O(U*logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it is
    // taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateLeft(Z l, Z r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateLeft: needs 0 <= l <= r < size()");
        int a, b, c;
        cutNodes(l, r, a, b, c);
        long long m = r - l + 1;
        k = (k % m + m) % m;
        if (k) {
            int b1, b2;
            splitNodes(b, k, b1, b2);
            b = mergeNodes(b2, b1);
        }
        root = mergeNodes(mergeNodes(a, b), c);
    }

    // O(U*logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the length
    // (negative shifts left); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateRight(Z l, Z r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        long long m = r - l + 1;
        rangeRotateLeft(l, r, m - (k % m + m) % m);
    }

    // O(U*logN) expected -- reverse a[l..r] in place; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeReverse(Z l, Z r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReverse: needs 0 <= l <= r < size()");
        int a, b, c;
        cutNodes(l, r, a, b, c);
        applyRev(b);
        root = mergeNodes(mergeNodes(a, b), c);
    }

    // O(logN) expected -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(Z i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        int t = root;
        bool f = false;
        vector<int> path;
        while (true) {
            int lt = f ? nd[t].R : nd[t].L, rt = f ? nd[t].L : nd[t].R;
            Z ls = nd[lt].sz;
            if (i == ls) break;
            path.push_back(t);
            f ^= nd[t].rev;
            if (i < ls) t = lt;
            else i -= ls + 1, t = rt;
        }
        int v = nd[t].val;
        for (int k = (int)path.size() - 1; k >= 0; k--)  // (a map higher up is newer: apply them bottom-up)
            if (nd[path[k]].row >= 0) v = rows[(size_t)nd[path[k]].row * U + v];
        return T(v + valLo);
    }

    // O(U*logN) expected -- a[i] = v; needs valLo <= v <= valHi; needs 0 <= i < size(), else throws out_of_range
    void pointAssign(Z i, const T& v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        int o = off(v), a, b, c;
        cutNodes(i, i, a, b, c);
        nd[b].val = o;
        pull(b);
        root = mergeNodes(mergeNodes(a, b), c);
    }

    // O(U*logN) expected -- every a[i] == x with l <= i <= r becomes y; needs valLo <= y <= valHi; needs
    // 0 <= l <= r < size(), else throws out_of_range
    void rangeReplace(Z l, Z r, const T& x, const T& y) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReplace: needs 0 <= l <= r < size()");
        int to = off(y);
        long long from = (long long)x - (long long)valLo;
        if (from < 0 || from >= U || from == to) return;
        int a, b, c;
        cutNodes(l, r, a, b, c);
        applyRep(b, (int)from, to);
        root = mergeNodes(mergeNodes(a, b), c);
    }

    // O(U*logN) expected -- a[l..r] = v; needs valLo <= v <= valHi; needs 0 <= l <= r < size(), else throws
    // out_of_range
    void rangeAssign(Z l, Z r, const T& v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAssign: needs 0 <= l <= r < size()");
        vector<int> g(U, off(v));
        int a, b, c;
        cutNodes(l, r, a, b, c);
        applyMap(b, g.data());
        root = mergeNodes(mergeNodes(a, b), c);
    }

    // O(N logN) expected -- the whole current array (read without changing anything)
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(size());
        vector<int> path;
        auto go = [&](auto&& self, int t, bool f) -> void {
            if (!t) return;
            int lt = f ? nd[t].R : nd[t].L, rt = f ? nd[t].L : nd[t].R;
            f ^= nd[t].rev;
            path.push_back(t);
            self(self, lt, f);
            path.pop_back();
            int v = nd[t].val;
            for (int k = (int)path.size() - 1; k >= 0; k--)
                if (nd[path[k]].row >= 0) v = rows[(size_t)nd[path[k]].row * U + v];
            out.push_back(T(v + valLo));
            path.push_back(t);
            self(self, rt, f);
            path.pop_back();
        };
        go(go, root, false);
        return out;
    }

    // O(U*logN) expected -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    Z countOccurrences(Z l, Z r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countOccurrences: needs 0 <= l <= r < size()");
        long long a = (long long)x - (long long)valLo;
        if (a < 0 || a >= U) return 0;
        return fold(root, l, r, nullptr, false, [&](int t, const int* g) { return countWhole(t, (int)a, g); },
                    [&](int v) { return Z(v == a); });
    }

    // O(U*logN) expected -- the smallest i with a[i] == x, or -1 if x isn't in the array
    Z leftmostIndexOf(const T& x) const { return findIn(0, size() - 1, x, true); }

    // O(U*logN) expected -- the largest i with a[i] == x, or -1 if x isn't in the array
    Z rightmostIndexOf(const T& x) const { return findIn(0, size() - 1, x, false); }

    // O(U*logN) expected -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs
    // 0 <= l <= r < size(), else throws out_of_range
    Z leftmostIndexOfInRange(Z l, Z r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        return findIn(l, r, x, true);
    }

    // O(U*logN) expected -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs
    // 0 <= l <= r < size(), else throws out_of_range
    Z rightmostIndexOfInRange(Z l, Z r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        return findIn(l, r, x, false);
    }

    // O(U*logN) expected -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    S rangeSum(Z l, Z r) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeSum: needs 0 <= l <= r < size()");
        return fold(root, l, r, nullptr, false, [&](int t, const int* g) { return sumWhole(t, g); },
                    [&](int v) { return S(v) + S(valLo); });
    }

    // O(U*log(N) expected) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    T pop() {
        auto n = size();
        if (n < 1) throw out_of_range("pop: needs size() >= 1");
        T v = pointGet(n - 1);
        cut(n - 1, n - 1);
        return v;
    }

    // O(U*log(N) expected) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws out_of_range
    T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        T v = pointGet(0);
        cut(0, 0);
        return v;
    }

    // ---- internals ----

    static void setRange(T lo, T hi) {
        int u = int(hi - lo) + 1;
        if (u != U) {  // (a new value range: the pool's map rows change length, so it starts over)
            U = u;
            nd.assign(1, Node{});
            rows.clear(), freeRows.clear();
            cnt.assign(U, 0), tmp.assign(U, 0);
        }
        valLo = lo;
    }

    static int off(const T& v) {  // v's index into a map
        long long o = (long long)v - (long long)valLo;
        if (o < 0 || o >= U) throw invalid_argument("value outside [valLo, valHi]");
        return (int)o;
    }

    static int newNode(int o) {  // a node holding offset o
        Node x;
        x.val = o, x.sz = 1;
        x.sm = S(o) + S(valLo);
        nd.push_back(x);
        cnt.resize(cnt.size() + U);
        cnt[(nd.size() - 1) * U + o] = 1;
        return (int)nd.size() - 1;
    }

    static int clone(int x) {  // a new copy of node x (sharing its children)
        Node y = nd[x];
        if (y.row >= 0) {
            y.row = newRow();
            std::copy(rows.begin() + (size_t)nd[x].row * U, rows.begin() + (size_t)(nd[x].row + 1) * U,
                      rows.begin() + (size_t)y.row * U);
        }
        nd.push_back(y);
        cnt.resize(cnt.size() + U);
        std::copy(cnt.begin() + (size_t)x * U, cnt.begin() + (size_t)(x + 1) * U, cnt.end() - U);
        return (int)nd.size() - 1;
    }

    static int build(const vector<int>& offs, size_t lo = 0, size_t hi = SIZE_MAX) {  // balanced, offs[lo..hi) in order
        if (hi == SIZE_MAX) hi = offs.size();
        if (lo >= hi) return 0;
        size_t mid = (lo + hi) / 2;
        int x = newNode(offs[mid]);
        int l = build(offs, lo, mid), r = build(offs, mid + 1, hi);
        nd[x].L = l, nd[x].R = r;
        pull(x);
        return x;
    }

    static void pull(int x) {  // recompute x from its children
        int l = nd[x].L, r = nd[x].R;
        nd[x].sz = nd[l].sz + nd[r].sz + 1;
        Z* c = &cnt[(size_t)x * U];
        const Z* p = &cnt[(size_t)l * U];
        const Z* q = &cnt[(size_t)r * U];
        for (int v = 0; v < U; v++) c[v] = p[v] + q[v];
        c[nd[x].val]++;
        nd[x].sm = nd[l].sm + nd[r].sm + S(nd[x].val) + S(valLo);
    }

    static void applyMap(int x, const int* g) {  // x's subtree goes through map g (newer than anything already in it)
        if (!x) return;
        nd[x].val = g[nd[x].val];
        if (nd[x].row < 0) {
            int r = newRow();
            nd[x].row = r;
            std::copy(g, g + U, &rows[(size_t)r * U]);
        } else {
            int* m = &rows[(size_t)nd[x].row * U];
            for (int v = 0; v < U; v++) m[v] = g[m[v]];
        }
        Z* c = &cnt[(size_t)x * U];
        std::fill(tmp.begin(), tmp.end(), 0);
        for (int v = 0; v < U; v++) if (c[v]) tmp[g[v]] += c[v];
        std::copy(tmp.begin(), tmp.end(), c);
        nd[x].sm = 0;
        for (int v = 0; v < U; v++) if (c[v]) nd[x].sm += S(c[v]) * (S(v) + S(valLo));
    }

    static void applyRep(int x, int a, int b) {  // every a in x's subtree becomes b
        if (!x) return;
        if (nd[x].val == a) nd[x].val = b;
        if (nd[x].row < 0) {
            int r = newRow();
            nd[x].row = r;
            std::iota(&rows[(size_t)r * U], &rows[(size_t)r * U] + U, 0);
        }
        int* m = &rows[(size_t)nd[x].row * U];
        for (int v = 0; v < U; v++) if (m[v] == a) m[v] = b;
        Z* c = &cnt[(size_t)x * U];
        nd[x].sm += S(b - a) * S(c[a]);
        c[b] += c[a], c[a] = 0;
    }

    static void applyRev(int x) {  // reverse x's subtree
        if (x) swap(nd[x].L, nd[x].R), nd[x].rev ^= 1;
    }

    static void push(int x) {  // hand x's pending tags to its children (fresh copies of them: x is a copy only this tree has)
        if (!nd[x].rev && nd[x].row < 0) return;
        if (nd[x].L) {
            int c = clone(nd[x].L);
            nd[x].L = c;
        }
        if (nd[x].R) {
            int c = clone(nd[x].R);
            nd[x].R = c;
        }
        if (nd[x].rev) applyRev(nd[x].L), applyRev(nd[x].R), nd[x].rev = 0;
        if (nd[x].row >= 0) {
            gbuf.assign(rows.begin() + (size_t)nd[x].row * U, rows.begin() + (size_t)(nd[x].row + 1) * U);
            freeRows.push_back(nd[x].row), nd[x].row = -1;
            applyMap(nd[x].L, gbuf.data()), applyMap(nd[x].R, gbuf.data());
        }
    }

    static int newRow() {  // a map row (a freed one if there is one)
        if (!freeRows.empty()) {
            int r = freeRows.back();
            freeRows.pop_back();
            return r;
        }
        rows.resize(rows.size() + U);
        return int(rows.size() / U) - 1;
    }

    // (first k of t, the rest), as new nodes (t's are left as they were)
    static void splitNodes(int t, Z k, int& a, int& b) {
        if (!t) {
            a = b = 0;
            return;
        }
        t = clone(t);
        push(t);
        int x, y;  // (locals: the copies made below may move nd)
        if (nd[nd[t].L].sz >= k) {
            splitNodes(nd[t].L, k, x, y);
            nd[t].L = y, a = x, b = t;
        } else {
            splitNodes(nd[t].R, k - nd[nd[t].L].sz - 1, x, y);
            nd[t].R = x, a = t, b = y;
        }
        pull(t);
    }

    // a's elements, then b's, as new nodes; the root is a with probability |a| / (|a| + |b|)
    static int mergeNodes(int a, int b) {
        if (!a || !b) return a ? a : b;
        if ((Z)(rnd() % (unsigned long long)(nd[a].sz + nd[b].sz)) < nd[a].sz) {
            a = clone(a);
            push(a);
            int r = mergeNodes(nd[a].R, b);
            nd[a].R = r;
            pull(a);
            return a;
        }
        b = clone(b);
        push(b);
        int l = mergeNodes(a, nd[b].L);
        nd[b].L = l;
        pull(b);
        return b;
    }

    void cutNodes(Z l, Z r, int& a, int& b, int& c) const {  // (a[0..l-1], a[l..r], a[r+1..])
        int bc;
        splitNodes(root, l, a, bc);
        splitNodes(bc, r - l + 1, b, c);
    }

    static const int* composeAt(const int* g, int t, vector<int>& buf) {  // the map "t's pending map, then g"
        if (nd[t].row < 0) return g;
        const int* m = &rows[(size_t)nd[t].row * U];
        if (!g) return m;
        buf.resize(U);
        for (int v = 0; v < U; v++) buf[v] = g[m[v]];
        return buf.data();
    }

    static Z countWhole(int t, int a, const int* g) {  // how many a's in t's subtree once map g (null: none) is applied
        const Z* c = &cnt[(size_t)t * U];
        if (!g) return c[a];
        Z res = 0;
        for (int v = 0; v < U; v++) if (g[v] == a) res += c[v];
        return res;
    }

    static S sumWhole(int t, const int* g) {  // the sum of t's subtree once map g (null: none) is applied
        if (!g) return nd[t].sm;
        const Z* c = &cnt[(size_t)t * U];
        S res = 0;
        for (int v = 0; v < U; v++) if (c[v]) res += S(c[v]) * (S(g[v]) + S(valLo));
        return res;
    }

    // whole(subtree, map) summed over the subtrees inside a[l..r] of t's, plus one(value) for each node only partly
    // inside; g: the maps above t not yet handed down, f: a reverse above t not yet handed down (changes nothing)
    template <class W, class O>
    static auto fold(int t, Z l, Z r, const int* g, bool f, W whole, O one) -> decltype(whole(t, g)) {
        using R = decltype(whole(t, g));
        if (!t || r < 0 || l >= nd[t].sz) return R(0);
        if (l <= 0 && nd[t].sz - 1 <= r) return whole(t, g);
        int lt = f ? nd[t].R : nd[t].L, rt = f ? nd[t].L : nd[t].R;
        f ^= nd[t].rev;
        vector<int> buf;
        const int* h = composeAt(g, t, buf);
        Z ls = nd[lt].sz;
        R res = fold(lt, l, r, h, f, whole, one) + fold(rt, l - ls - 1, r - ls - 1, h, f, whole, one);
        if (l <= ls && ls <= r) res += one(g ? g[nd[t].val] : nd[t].val);
        return res;
    }

    Z findIn(Z l, Z r, const T& x, bool left) const {
        long long a = (long long)x - (long long)valLo;
        return a < 0 || a >= U ? -1 : findNode(root, l, r, (int)a, nullptr, false, left);
    }

    // the first (left) / last index in [l, r] of t's subtree holding a, or -1
    static Z findNode(int t, Z l, Z r, int a, const int* g, bool f, bool left) {
        if (!t || r < 0 || l >= nd[t].sz || (l <= 0 && nd[t].sz - 1 <= r && !countWhole(t, a, g))) return -1;
        int lt = f ? nd[t].R : nd[t].L, rt = f ? nd[t].L : nd[t].R;
        f ^= nd[t].rev;
        vector<int> buf;
        const int* h = composeAt(g, t, buf);
        Z ls = nd[lt].sz;
        int v = g ? g[nd[t].val] : nd[t].val;
        Z res;
        if (left) {
            if ((res = findNode(lt, l, r, a, h, f, left)) != -1) return res;
            if (l <= ls && ls <= r && v == a) return ls;
            return (res = findNode(rt, l - ls - 1, r - ls - 1, a, h, f, left)) != -1 ? res + ls + 1 : -1;
        }
        if ((res = findNode(rt, l - ls - 1, r - ls - 1, a, h, f, left)) != -1) return res + ls + 1;
        if (l <= ls && ls <= r && v == a) return ls;
        return findNode(lt, l, r, a, h, f, left);
    }
};
