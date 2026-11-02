// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/append-appendLeft-copyRange-cut-insertAt-merge-paste-pointAssign-pointGet-rangeReverse-rangeSum-split-trisect/template.cpp
// @operations: append appendLeft copyRange cut getAll insertAt merge paste pointAssign pointGet rangeReverse rangeSum split trisect
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
//   rangeReverse: log(N) expected
//   rangeSum: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] sm[1*N*log(N)]
//   tags: rev[1*N*log(N)]
//   other: none
//   note: nodes are never changed or freed: each update copies O(log N) of them (N here counts updates too), and copies share every node they don't change

// Persistent implicit treap: an array you can insert into anywhere, cut pieces out of (that is how to erase) and
// paste them back, reverse, and copy ranges inside (copyRange: a copy of a[l..r] inserted at index i, O(logN) however
// long, since the copy shares the same nodes), each in O(logN) expected. No node changes after it is made: updates
// copy the nodes on their paths. Merge picks its root at random weighted by size, so shared nodes need no priorities.
// All indices 0-based, ranges inclusive, always positions in the CURRENT array.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct PersistentTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // one node pool shared by every PersistentTreap<T>: cut / paste move nodes between them, so a piece from one can
    // go into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over
    // the whole run), so there is nothing to reset between test cases
    static inline vector<T> val{T(0)};
    static inline vector<int> sz{0}, L{0}, R{0};
    static inline vector<char> rev{0};
    static inline vector<S> sm{S(0)};
    int root = 0;

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit PersistentTreap(const vector<T>& arr = {}) { root = build(arr, 0, (int)arr.size()); }

    PersistentTreap makeEmpty() const { return PersistentTreap(); }  // (a new, empty one: same pool, like every one)

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
        PersistentTreap piece = makeEmpty();
        piece.root = b;
        return piece;
    }

    // O(logN) expected -- insert all of other (any PersistentTreap, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(int i, PersistentTreap& other) {
        int x, y;
        split(root, i, x, y);
        root = merge(merge(x, other.root), y), other.root = 0;
    }

    // O(logN) expected -- append all of other at the end, leaving it empty (it must share this treap's nodes)
    void merge(PersistentTreap& other) { root = merge(root, other.root), other.root = 0; }

    // O(logN) expected -- (a[0..k-1], a[k..]) as two PersistentTreaps of their own; this one is left empty
    pair<PersistentTreap, PersistentTreap> split(int k) {
        PersistentTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three PersistentTreaps of their own; this one is left empty
    tuple<PersistentTreap, PersistentTreap, PersistentTreap> trisect(int l, int r) {
        PersistentTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cut(root, l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // O(logN) expected -- reverse a[l..r] in place
    void rangeReverse(int l, int r) {
        int a, b, c;
        cut(root, l, r, a, b, c);
        root = merge(merge(a, flip(b)), c);
    }

    // O(logN) expected -- a[i] = v
    void pointAssign(int i, T v) {
        int a, b, c;
        cut(root, i, i, a, b, c);
        root = merge(merge(a, make(v, 0, 0)), c);
    }

    // O(logN) expected -- a[i] (a read-only walk: pending reverses only swap which child is which)
    T pointGet(int i) const {
        int t = root;
        bool f = false;
        while (true) {
            int lt = f ? R[t] : L[t], rt = f ? L[t] : R[t];
            f ^= rev[t];
            if (i < sz[lt]) t = lt;
            else if (i == sz[lt]) return val[t];
            else i -= sz[lt] + 1, t = rt;
        }
    }

    // O(logN) expected -- a[l] + ... + a[r] (the root doesn't change)
    S rangeSum(int l, int r) {
        int a, b, c;
        cut(root, l, r, a, b, c);
        return sm[b];
    }

    // O(N) -- the whole current array
    vector<T> getAll() const {
        vector<T> out;
        out.reserve(size());
        vector<pair<int, bool>> st;  // (node, whether its children are swapped by the reverses pending above it)
        int t = root;
        bool f = false;
        while (!st.empty() || t) {
            while (t) {
                st.push_back({t, f});
                int lt = f ? R[t] : L[t];
                f ^= rev[t];
                t = lt;
            }
            tie(t, f) = st.back();
            st.pop_back();
            out.push_back(val[t]);
            int rt = f ? L[t] : R[t];
            f ^= rev[t];
            t = rt;
        }
        return out;
    }

    // ---- internals: every function returns new nodes and leaves its arguments as they were ----

    int make(T v, int l, int r, char rv = 0) {
        val.push_back(v), L.push_back(l), R.push_back(r), rev.push_back(rv), sz.push_back(sz[l] + sz[r] + 1);
        sm.push_back(sm[l] + S(v) + sm[r]);
        return (int)val.size() - 1;
    }

    // t reversed: a copy with its children swapped and a pending reverse for them
    int flip(int t) { return t ? make(val[t], R[t], L[t], rev[t] ^ 1) : 0; }

    // value, left, right of t with its pending reverse handed to (copies of) the children
    void open(int t, T& v, int& l, int& r) {
        v = val[t];
        if (rev[t]) l = flip(L[t]), r = flip(R[t]);
        else l = L[t], r = R[t];
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
        open(t, v, l, r);
        if (sz[l] >= k) split(l, k, x, y), a = x, b = make(v, y, r);
        else split(r, k - sz[l] - 1, x, y), a = make(v, l, x), b = y;
    }

    int merge(int a, int b) {  // a's elements, then b's; the root is a with probability |a| / (|a| + |b|)
        if (!a || !b) return a ? a : b;
        T v;
        int l, r;
        if (rnd() % (unsigned long long)(sz[a] + sz[b]) < (unsigned long long)sz[a]) {
            open(a, v, l, r);
            int m = merge(r, b);
            return make(v, l, m);
        }
        open(b, v, l, r);
        int m = merge(a, l);
        return make(v, m, r);
    }

    void cut(int t, int l, int r, int& a, int& b, int& c) {  // a[0..l-1], a[l..r], a[r+1..]
        split(t, l, a, b);
        split(b, r - l + 1, b, c);
    }
};
