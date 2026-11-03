// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-hash-xor-and-rev-find/template.cpp
// @operations: append appendLeft cut find getAll insertAt insertCopiesAt isPalindrome merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeHash rangeHashReversed rangeReverse rangeRotateLeft rangeRotateRight rangeXorQuery rangesEqual split trisect
// @data-structure-type: treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   cut: log(N) expected
//   find: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: log(N) expected
//   isPalindrome: log(N) expected
//   merge: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeAndQuery: log(N) expected
//   rangeHash: log(N) expected
//   rangeHashReversed: log(N) expected
//   rangeReverse: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeXorQuery: log(N) expected
//   rangesEqual: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] fh[1*N] bh[1*N] pw[1*N] xr[1*N] an[1*N] par[1*N]
//   tags: rev[1*N]
//   other: where[1*N]
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset); find: a parent per node and a map value -> node

// Implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, move, cut pieces
// out of (that is how to erase) and paste them back in O(logN) expected each, and find any value's index (values
// distinct); each node keeps its forward / backward hash (and B^size), its xor, its AND over its subtree. All indices
// 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when
// nothing qualifies. Lazy tags mean "already applied to this node, not yet to its children".
// T: int, long long, ...
template <typename T>
struct ImplicitTreap {
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
        T val = T(0);
        T xr = T(0);
        T an = ~T(0);
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
        int a, b, c;
        cut(l, r, a, b, c);
        bool res = nd[b].fh == nd[b].bh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    void merge(ImplicitTreap& other) { root = merge(root, other.root), other.root = 0; }

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

    // O(logN) expected -- a[l] & ... & a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeAndQuery(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].an;
        root = merge(merge(a, b), c);
        return res;
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

    // O(logN) expected -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeXorQuery(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeXorQuery: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].xr;
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
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.fh = hval(v), n.bh = hval(v), n.pw = HB(), n.xr = v,
        n.an = v, n.rev = 0, n.par = 0;
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
        U64 B = HB(), hv = hval(v);
        nd[x].pw = hmul(hmul(nd[l].pw, B), nd[r].pw);
        nd[x].fh = hadd(hmul(hadd(hmul(nd[l].fh, B), hv), nd[r].pw), nd[r].fh);
        nd[x].bh = hadd(hmul(hadd(hmul(nd[r].bh, B), hv), nd[l].pw), nd[l].bh);
        nd[x].xr = nd[l].xr ^ v ^ nd[r].xr;
        nd[x].an = nd[l].an & v & nd[r].an;  // (node 0: the AND of nothing, ~0)
    }

    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        swap(nd[x].L, nd[x].R), nd[x].rev ^= 1, swap(nd[x].fh, nd[x].bh);
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
};

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     ImplicitTreap<int> t({1, 2, 3, 4, 5});
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
