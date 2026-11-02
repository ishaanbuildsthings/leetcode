// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-treap-min-max-or-run-rev/template.cpp
// @operations: append appendLeft copy cut getAll insertAt insertCopiesAt leftmostGtX leftmostGteX leftmostLtX leftmostLteX longestEqualRun merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rangeOrQuery rangeReverse rangeRotateLeft rangeRotateRight rightmostGtX rightmostGteX rightmostLtX rightmostLteX split trisect
// @data-structure-type: persistent-treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   copy: log(N) expected
//   cut: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: log(N) expected
//   leftmostGtX: log(N) expected
//   leftmostGteX: log(N) expected
//   leftmostLtX: log(N) expected
//   leftmostLteX: log(N) expected
//   longestEqualRun: log(N) expected
//   merge: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeMax: log(N) expected
//   rangeMin: log(N) expected
//   rangeOrQuery: log(N) expected
//   rangeReverse: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rightmostGtX: log(N) expected
//   rightmostGteX: log(N) expected
//   rightmostLtX: log(N) expected
//   rightmostLteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N*log(N)] sz[1*N*log(N)] L[1*N*log(N)] R[1*N*log(N)] mn[1*N*log(N)] mx[1*N*log(N)] orr[1*N*log(N)] fv[1*N*log(N)] lv[1*N*log(N)] pr[1*N*log(N)] sr[1*N*log(N)] br[1*N*log(N)]
//   tags: rev[1*N*log(N)]
//   other: none
//   note: nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and copies share every node they don't change; log(N) is of the length, which can be huge (long long)

// Persistent implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, cut
// pieces out of (that is how to erase), paste them back and copy (copy(l, r): a[l..r] as a treap of its own in
// O(logN) however long, since the copy shares the same nodes; this one is unchanged); each node keeps its min, its
// max, its OR, its first / last value and the equal runs at its ends and inside over its subtree. No node changes
// once another tree can see it: an op copies the nodes on its paths, so a copy and its original never affect each
// other. Lengths and indices are long long. All indices 0-based, ranges inclusive [l, r], an index always the
// position in the CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already applied to this
// node, not yet to its children".
// T: int, long long, ...
template <typename T>
struct PersistentTreap {
    // one node pool shared by every PersistentTreap<T>: cut / paste move nodes between them, so a piece from one can
    // go into any other (node 0 = the empty tree). Nodes are never freed (memory = O(log N) per op, over the whole
    // run), so there is nothing to reset between test cases
    static inline vector<T> val{T(0)};
    static inline vector<int> L{0};
    static inline vector<int> R{0};
    static inline vector<long long> sz{0};
    static inline vector<T> mn{T(0)};
    static inline vector<T> mx{T(0)};
    static inline vector<T> orr{T(0)};
    static inline vector<T> fv{T(0)};
    static inline vector<T> lv{T(0)};
    static inline vector<long long> pr{0};
    static inline vector<long long> sr{0};
    static inline vector<long long> br{0};
    static inline vector<char> rev{0};
    int root = 0;

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit PersistentTreap(const vector<T>& arr = {}) { root = build(arr); }

    PersistentTreap makeEmpty() const { return PersistentTreap(); }  // (a new, empty one)

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(1) -- the current length of the array
    long long size() const { return sz[root]; }

    // O(logN) expected -- append v to the end
    void append(T v) { root = merge(root, newNode(v)); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(1) -- the whole array as a PersistentTreap of its own; this one is unchanged (they share nodes)
    PersistentTreap copy() const { return *this; }

    // O(logN) expected -- a[l..r] as a PersistentTreap of its own; this one is unchanged. The copy shares this one's
    // nodes, so it costs O(logN) however long it is
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
            while (t) push(t), st.push_back(t), t = L[t];
            t = st.back(), st.pop_back();
            out.push_back(val[t]);
            t = R[t];
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

    // O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max)
    long long leftmostGtX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && mx[t] > x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (L[t] && mx[L[t]] > x) t = L[t];
                else if (val[t] > x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
            }
        }
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max)
    long long leftmostGteX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && mx[t] >= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (L[t] && mx[L[t]] >= x) t = L[t];
                else if (val[t] >= x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
            }
        }
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min)
    long long leftmostLtX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && mn[t] < x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (L[t] && mn[L[t]] < x) t = L[t];
                else if (val[t] < x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
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
        if (t && mn[t] <= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (L[t] && mn[L[t]] <= x) t = L[t];
                else if (val[t] <= x) { res = l + i + sz[L[t]]; break; }
                else i += sz[L[t]] + 1, t = R[t];
            }
        }
        return res;
    }

    // O(logN) expected -- the longest run of equal adjacent values in a[l..r]
    long long longestEqualRun(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        int res = br[b];
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
        val[b] = T(val[b] + v);
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i] = v
    void pointAssign(long long i, T v) {
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        val[b] = v;
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) {
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        val[b] = max(val[b], v);
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) {
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        val[b] = min(val[b], v);
        pull(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i]
    T pointGet(long long i) { return val[locate(i)]; }

    // O(logN) expected -- max of a[l..r]
    T rangeMax(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = mx[b];
        return res;
    }

    // O(logN) expected -- min of a[l..r]
    T rangeMin(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = mn[b];
        return res;
    }

    // O(logN) expected -- a[l] | ... | a[r]
    T rangeOrQuery(long long l, long long r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = orr[b];
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

    // O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max)
    long long rightmostGtX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && mx[t] > x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (R[t] && mx[R[t]] > x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] > x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
            }
        }
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max)
    long long rightmostGteX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && mx[t] >= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (R[t] && mx[R[t]] >= x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] >= x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
            }
        }
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min)
    long long rightmostLtX(long long l, long long r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b;
        long long i = 0, res = -1;
        if (t && mn[t] < x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (R[t] && mn[R[t]] < x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] < x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
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
        if (t && mn[t] <= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (R[t] && mn[R[t]] <= x) i += sz[L[t]] + 1, t = R[t];
                else if (val[t] <= x) { res = l + i + sz[L[t]]; break; }
                else t = L[t];
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
        val.push_back(v), L.push_back(0), R.push_back(0), sz.push_back(1);
        mn.push_back(v), mx.push_back(v), orr.push_back(v), fv.push_back(v), lv.push_back(v), pr.push_back(1);
        sr.push_back(1), br.push_back(1), rev.push_back(0);
        return (int)val.size() - 1;
    }

    int build(const vector<T>& vals) { return build(vals, 0, (int)vals.size()); }

    int build(const vector<T>& vals, int lo, int hi) {  // a balanced tree of new nodes holding vals[lo, hi), O(len)
        if (lo >= hi) return 0;
        int mid = (lo + hi) / 2, x = newNode(vals[mid]);
        int l = build(vals, lo, mid), r = build(vals, mid + 1, hi);
        L[x] = l, R[x] = r;
        pull(x);
        return x;
    }

    int clone(int x) {  // a new copy of node x (sharing its children)
        val.push_back(val[x]);
        L.push_back(L[x]);
        R.push_back(R[x]);
        sz.push_back(sz[x]);
        mn.push_back(mn[x]);
        mx.push_back(mx[x]);
        orr.push_back(orr[x]);
        fv.push_back(fv[x]);
        lv.push_back(lv[x]);
        pr.push_back(pr[x]);
        sr.push_back(sr[x]);
        br.push_back(br[x]);
        rev.push_back(rev[x]);
        return (int)val.size() - 1;
    }

    void pull(int x) {  // recompute x from its children
        int l = L[x], r = R[x];
        sz[x] = sz[l] + sz[r] + 1;
        T v = val[x];
        mn[x] = v;
        if (l && mn[l] < mn[x]) mn[x] = mn[l];
        if (r && mn[r] < mn[x]) mn[x] = mn[r];
        mx[x] = v;
        if (l && mx[l] > mx[x]) mx[x] = mx[l];
        if (r && mx[r] > mx[x]) mx[x] = mx[r];
        orr[x] = orr[l] | v | orr[r];
        long long rp = 1, rq = 1, bb = 1;
        if (l) {
            bool j = lv[l] == v;
            rp = pr[l] + (j && pr[l] == sz[l]);
            rq = j ? sr[l] + 1 : 1;
            bb = max(br[l], rq);
        }
        if (r) {
            bool j = v == fv[r];
            bb = max({bb, br[r], j ? rq + pr[r] : 0});
            if (j && rp == sz[l] + 1) rp += pr[r];
            rq = j && sr[r] == sz[r] ? sr[r] + rq : sr[r];
        }
        pr[x] = rp, sr[x] = rq, br[x] = bb;
        fv[x] = l ? fv[l] : v;
        lv[x] = r ? lv[r] : v;
    }

    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        swap(L[x], R[x]), rev[x] ^= 1, swap(fv[x], lv[x]), swap(pr[x], sr[x]);
    }

    void push(int x) {  // hand x's pending tags to its children
        if (!(rev[x])) return;
        if (L[x]) L[x] = clone(L[x]);  // (the children get tags: fresh copies of them, since other trees may share them)
        if (R[x]) R[x] = clone(R[x]);
        if (rev[x]) applyRev(L[x]), applyRev(R[x]), rev[x] = 0;
    }

    void split(int t, long long k, int& a, int& b) {  // a = first k of t, b = the rest, as new nodes (t's are left as they were)
        if (!t) { a = b = 0; return; }
        t = clone(t);
        push(t);
        int x, y;  // (not straight into L[t] / R[t]: the clones below may move those arrays)
        if (sz[L[t]] >= k) split(L[t], k, x, y), L[t] = y, a = x, b = t;
        else split(R[t], k - sz[L[t]] - 1, x, y), R[t] = x, a = t, b = y;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's, as new nodes; the root is a with probability |a| / (|a| + |b|)
        if (!a || !b) return a | b;
        if (rnd() % (unsigned long long)(sz[a] + sz[b]) < (unsigned long long)sz[a]) {
            a = clone(a);
            push(a);
            R[a] = merge(R[a], b);
            pull(a);
            return a;
        }
        b = clone(b);
        push(b);
        L[b] = merge(a, L[b]);
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
            long long ls = sz[L[t]];
            if (i == ls) return t;
            if (i < ls) t = L[t];
            else i -= ls + 1, t = R[t];
        }
    }
};

// Example (pieces move between treaps; merge appends and leaves its argument empty):
//     PersistentTreap<int> t({1, 2, 3, 4, 5});
//     auto [left, mid, right] = t.trisect(1, 3);  // left = [1], mid = [2, 3, 4], right = [5]; t is empty now
//     t.merge(right);                             // t = [5]
//     t.merge(mid);                               // t = [5, 2, 3, 4]
//     t.merge(left);                              // t = [5, 2, 3, 4, 1]
