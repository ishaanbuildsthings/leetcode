// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-treap-min-updates-assign-chmax-chmin-rev/template.cpp
// @operations: append appendLeft copy cut getAll insertAt insertCopiesAt leftmostLtX leftmostLteX merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeChmin rangeMin rangeReverse rangeRotateLeft rangeRotateRight rightmostLtX rightmostLteX split trisect
// @data-structure-type: persistent-treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   copy: log(N) expected
//   cut: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: log(N) expected
//   leftmostLtX: log(N) expected
//   leftmostLteX: log(N) expected
//   merge: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeAssign: log(N) expected
//   rangeChmax: log(N) expected
//   rangeChmin: log(N) expected
//   rangeMin: log(N) expected
//   rangeReverse: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rightmostLtX: log(N) expected
//   rightmostLteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] mn[1*N*log(N)]
//   tags: rev[1*N*log(N)] hi[1*N*log(N)] lo[1*N*log(N)]
//   other: none
//   note: nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and copies share every node they don't change; log(N) is of the length, which can be huge (long long)

// Persistent implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, cut
// pieces out of (that is how to erase), paste them back and copy (copy(l, r): a[l..r] as a treap of its own in
// O(logN) however long, since the copy shares the same nodes; this one is unchanged), with rangeAssign, rangeChmax,
// rangeChmin; each node keeps its min over its subtree. No node changes once another tree can see it: an op copies
// the nodes on its paths, so a copy and its original never affect each other. Lengths and indices are long long. All
// indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array; searches return -1
// when nothing qualifies. Lazy tags mean "already applied to this node, not yet to its children".
// T: int, long long, ...
template <typename T>
struct PersistentTreap {
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();
    // one node pool shared by every PersistentTreap<T>: cut / paste move nodes between them, so a piece from one can
    // go into any other (node 0 = the empty tree). Nodes are never freed (memory = O(log N) per op, over the whole
    // run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        long long sz = 0;
        T val = T(0);
        T mn = T(0);
        T hi = INF;
        T lo = NEG;
        int L = 0;
        int R = 0;
        char rev = 0;
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

    // O(logN) expected -- a[l..r] as a PersistentTreap of its own; this one is unchanged. The copy
    // shares this one's nodes, so it costs O(logN) however long it is
    PersistentTreap copy(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        PersistentTreap piece = makeEmpty();
        piece.root = b;
        return piece;
    }

    // O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
    PersistentTreap cut(long long l, long long r) {
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

    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(long long i, T v) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(long long i, T v, long long k) {
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN) expected -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min)
    long long leftmostLtX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && nd[t].mn < x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].L && nd[nd[t].L].mn < x) t = nd[t].L;
                else if (nd[t].val < x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the subtree min)
    long long leftmostLteX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && nd[t].mn <= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].L && nd[nd[t].L].mn <= x) t = nd[t].L;
                else if (nd[t].val <= x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        return res;
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    void merge(PersistentTreap& other) { root = merge(root, other.root), other.root = 0; }
    void merge(PersistentTreap&& other) { merge(other); }  // (a temporary: merge(t.copy()))

    // O(logN) expected -- insert all of other (any PersistentTreap, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(long long i, PersistentTreap& other) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }
    void paste(long long i, PersistentTreap&& other) { paste(i, other); }  // (a temporary: paste(i, t.copy(l, r)))

    // O(logN) expected -- a[i] += v
    void pointAdd(long long i, T v) {
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        nd[b].val = T(nd[b].val + v);
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i] = v
    void pointAssign(long long i, T v) {
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        nd[b].val = v;
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) {
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        nd[b].val = max(nd[b].val, v);
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) {
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        nd[b].val = min(nd[b].val, v);
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i]
    T pointGet(long long i) { return nd[locate(i)].val; }

    // O(logN) expected -- a[i] = v for i in [l, r]
    void rangeAssign(long long l, long long r, T v) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyClamp(b, v, v);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i] = max(a[i], v) for i in [l, r]
    void rangeChmax(long long l, long long r, T v) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyClamp(b, INF, v);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i] = min(a[i], v) for i in [l, r]
    void rangeChmin(long long l, long long r, T v) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyClamp(b, v, NEG);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- min of a[l..r]
    T rangeMin(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].mn;
        return res;
    }

    // O(logN) expected -- reverse a[l..r] in place
    void rangeReverse(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    // it is taken mod the length (negative shifts right)
    void rangeRotateLeft(long long l, long long r, long long k) {
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

    // O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left)
    void rangeRotateRight(long long l, long long r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(logN) expected -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min)
    long long rightmostLtX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && nd[t].mn < x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].R && nd[nd[t].R].mn < x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val < x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the subtree min)
    long long rightmostLteX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && nd[t].mn <= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].R && nd[nd[t].R].mn <= x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val <= x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        return res;
    }

    // O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    pair<PersistentTreap, PersistentTreap> split(long long k) {
        PersistentTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    tuple<PersistentTreap, PersistentTreap, PersistentTreap> trisect(long long l, long long r) {
        PersistentTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cut(l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // ---- internals ----

    int newNode(T v) {
        Node n;
        n.val = v, n.L = 0, n.R = 0, n.sz = 1, n.mn = v, n.rev = 0, n.hi = INF, n.lo = NEG;
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
        n.val = nd[x].val, n.L = nd[x].L, n.R = nd[x].R, n.sz = nd[x].sz, n.mn = nd[x].mn, n.rev = nd[x].rev,
        n.hi = nd[x].hi, n.lo = nd[x].lo;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    void pull(int x) {  // recompute x from its children
        int l = nd[x].L, r = nd[x].R;
        nd[x].sz = nd[l].sz + nd[r].sz + 1;
        T v = nd[x].val;
        nd[x].mn = v;
        if (l && nd[l].mn < nd[x].mn) nd[x].mn = nd[l].mn;
        if (r && nd[r].mn < nd[x].mn) nd[x].mn = nd[r].mn;
    }

    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        swap(nd[x].L, nd[x].R), nd[x].rev ^= 1;
    }

    void applyClamp(int x, T H, T Lo) {  // every value v of x's subtree becomes min(H, max(Lo, v))
        if (!x) return;
        nd[x].val = min(H, max(Lo, nd[x].val));
        nd[x].mn = min(H, max(Lo, nd[x].mn));
        T h = min(H, max(Lo, nd[x].hi));
        nd[x].lo = min(max(Lo, nd[x].lo), h);
        nd[x].hi = h;
    }

    void push(int x) {  // hand x's pending tags to its children
        if (!(nd[x].rev || (nd[x].hi != INF || nd[x].lo != NEG))) return;
        // (the children get tags: fresh copies of them, since other trees may share them)
        if (nd[x].L) nd[x].L = clone(nd[x].L);
        if (nd[x].R) nd[x].R = clone(nd[x].R);
        if (nd[x].rev) applyRev(nd[x].L), applyRev(nd[x].R), nd[x].rev = 0;
        if (nd[x].hi != INF || nd[x].lo != NEG) {
            applyClamp(nd[x].L, nd[x].hi, nd[x].lo), applyClamp(nd[x].R, nd[x].hi, nd[x].lo);
            nd[x].hi = INF, nd[x].lo = NEG;
        }
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
};

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     PersistentTreap<int> t({1, 2, 3, 4, 5});
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
