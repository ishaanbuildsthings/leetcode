// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/append-appendLeft-copyRange-cut-insertAt-merge-paste-pointAssign-pointGet-split-trisect/template.cpp
// @operations: append appendLeft copyRange cut getAll insertAt merge paste pointAssign pointGet split trisect
// @data-structure-type: persistent-treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   copyRange: log(N) expected
//   cut: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   merge: log(N) expected
//   paste: log(N) expected
//   pointAssign: log(N) expected
//   pointGet: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)]
//   tags: none
//   other: none
//   note: nodes are never changed or freed: each update copies O(log N) of them (N here counts updates too), and copies share every node they don't change

// Persistent implicit treap: an array you can insert into anywhere, cut pieces out of (that is how to erase) and
// paste them back and copy ranges inside (copyRange: a copy of a[l..r] inserted at index i, O(logN) however long,
// since the copy shares the same nodes), each in O(logN) expected. No node changes after it is made: updates copy the
// nodes on their paths. Merge picks its root at random weighted by size, so shared nodes need no priorities. All
// indices 0-based, ranges inclusive, always positions in the CURRENT array.
// T: int, long long, ...
template <typename T>
struct PersistentTreap {
    struct Pool {  // the node arrays (node 0 = the empty tree), shared with every piece cut from this treap
        vector<T> val{T(0)};
        vector<int> sz{0}, L{0}, R{0};
    };
    shared_ptr<Pool> pool;  // (freed with the last treap using it)
    vector<T>& val;
    vector<int>& sz;
    vector<int>& L;
    vector<int>& R;
    int root = 0;

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N) -- arr: the initial array (may be empty). No reset between test cases: a treap's nodes are freed with it
    explicit PersistentTreap(const vector<T>& arr = {}) : PersistentTreap(make_shared<Pool>()) {
        root = build(arr, 0, (int)arr.size());
    }

    // O(N) -- a PersistentTreap over arr that shares other's nodes, so pieces can move between the two (pieces cut from
    // it share them already)
    PersistentTreap(const vector<T>& arr, const PersistentTreap& other) : PersistentTreap(other.pool) {
        root = build(arr, 0, (int)arr.size());
    }

    // an empty PersistentTreap on pool p
    explicit PersistentTreap(shared_ptr<Pool> p)
        : pool(p), val(p->val), sz(p->sz), L(p->L), R(p->R) {}

    // O(1) -- the current length of the array
    int size() const { return sz[root]; }

    // O(logN) expected -- insert a copy of a[l..r] so it starts at index i (0 <= i <= size(); i is in the array
    // before the copy goes in); the copy shares a[l..r]'s nodes
    void copyRange(int l, int r, int i) {
        int a, b, c, x, y;
        cut(root, l, r, a, b, c);
        split(root, i, x, y);
        root = merge(merge(x, b), y);
    }

    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        int x, y;
        split(root, i, x, y);
        root = merge(merge(x, make(v, 0, 0)), y);
    }

    // O(logN) expected -- append v to the end
    void append(T v) { root = merge(root, make(v, 0, 0)); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0; drop it to erase)
    PersistentTreap cut(int l, int r) {
        int a, b, c;
        cut(root, l, r, a, b, c);
        root = merge(a, c);
        PersistentTreap piece(pool);
        piece.root = b;
        return piece;
    }

    // O(logN) expected -- insert other so it starts at a[i] (0 <= i <= size()), leaving it empty; it must share this
    // treap's nodes (a piece cut from it, or built with PersistentTreap(arr, this one))
    void paste(int i, PersistentTreap& other) {
        int x, y;
        split(root, i, x, y);
        root = merge(merge(x, other.root), y), other.root = 0;
    }

    // O(logN) expected -- append all of other at the end, leaving it empty (it must share this treap's nodes)
    void merge(PersistentTreap& other) { root = merge(root, other.root), other.root = 0; }

    // O(logN) expected -- (a[0..k-1], a[k..]) as two PersistentTreaps of their own; this one is left empty
    pair<PersistentTreap, PersistentTreap> split(int k) {
        PersistentTreap left(pool), right(pool);
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PersistentTreaps of their own; this one is left empty
    tuple<PersistentTreap, PersistentTreap, PersistentTreap> trisect(int l, int r) {
        PersistentTreap left(pool), mid(pool), right(pool);
        cut(root, l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // O(logN) expected -- a[i] = v
    void pointAssign(int i, T v) {
        int a, b, c;
        cut(root, i, i, a, b, c);
        root = merge(merge(a, make(v, 0, 0)), c);
    }

    // O(logN) expected -- a[i] (a read-only walk)
    T pointGet(int i) const {
        int t = root;
        while (true) {
            int lt = L[t];
            if (i < sz[lt]) t = lt;
            else if (i == sz[lt]) return val[t];
            else i -= sz[lt] + 1, t = R[t];
        }
    }

    // O(N) -- the whole current array
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(size());
        vector<int> st;
        int t = root;
        while (!st.empty() || t) {
            while (t) st.push_back(t), t = L[t];
            t = st.back(), st.pop_back();
            out.push_back(val[t]);
            t = R[t];
        }
        return out;
    }

    // ---- internals: every function returns new nodes and leaves its arguments as they were ----

    int make(T v, int l, int r) {
        val.push_back(v), L.push_back(l), R.push_back(r), sz.push_back(sz[l] + sz[r] + 1);
        return (int)val.size() - 1;
    }

    int build(const vector<T>& arr, int lo, int hi) {  // a balanced tree of arr[lo, hi)
        if (lo >= hi) return 0;
        int mid = (lo + hi) / 2, l = build(arr, lo, mid), r = build(arr, mid + 1, hi);
        return make(arr[mid], l, r);
    }

    void split(int t, int k, int& a, int& b) {  // a = first k of t, b = the rest
        if (!t) { a = b = 0; return; }
        T v;
        int l, r, x, y;
        v = val[t], l = L[t], r = R[t];
        if (sz[l] >= k) split(l, k, x, y), a = x, b = make(v, y, r);
        else split(r, k - sz[l] - 1, x, y), a = make(v, l, x), b = y;
    }

    int merge(int a, int b) {  // a's elements, then b's; the root is a with probability |a| / (|a| + |b|)
        if (!a || !b) return a ? a : b;
        T v;
        int l, r;
        if (rnd() % (unsigned long long)(sz[a] + sz[b]) < (unsigned long long)sz[a]) {
            v = val[a], l = L[a], r = R[a];
            int m = merge(r, b);
            return make(v, l, m);
        }
        v = val[b], l = L[b], r = R[b];
        int m = merge(a, l);
        return make(v, m, r);
    }

    void cut(int t, int l, int r, int& a, int& b, int& c) {  // a[0..l-1], a[l..r], a[r+1..]
        split(t, l, a, b);
        split(b, r - l + 1, b, c);
    }
};
