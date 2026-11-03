// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-beats-both-add-rev/template.cpp
// @operations: append appendLeft cut getAll insertAt insertCopiesAt leftmostGtX leftmostGteX leftmostLtX leftmostLteX merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeMax rangeMin rangeReverse rangeRotateLeft rangeRotateRight rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX split trisect
// @data-structure-type: treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   cut: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: log(N) expected
//   leftmostGtX: log(N) expected
//   leftmostGteX: log(N) expected
//   leftmostLtX: log(N) expected
//   leftmostLteX: log(N) expected
//   merge: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   rangeAdd: log(N) expected
//   rangeAssign: log(N) expected
//   rangeChmax: log^2(N) amortized ?
//   rangeChmin: log^2(N) amortized ?
//   rangeMax: log(N) expected
//   rangeMin: log(N) expected
//   rangeReverse: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeSum: log(N) expected
//   rightmostGtX: log(N) expected
//   rightmostGteX: log(N) expected
//   rightmostLtX: log(N) expected
//   rightmostLteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mx[1*N] mx2[1*N] cmx[1*N] mn[1*N] mn2[1*N] cmn[1*N]
//   tags: rev[1*N] add[1*N]
//   other: none
//   note: N = every value ever inserted; no chmin / chmax / assign tags: a node's own max / min are its pending clamp, and a node whose values are all equal pushes that value as an assign; a treap and the pieces cut from it share their nodes (freed with the last of them: no reset needed)

// Implicit treap with segment tree beats: range chmin and chmax, range add and range assign with range sums, the
// range max, the range min, on an array you can insert into anywhere, reverse, rotate, move, cut pieces out of (that
// is how to erase) and paste them back. Each node keeps its max / min, strict second max / min and their copies over
// its subtree (its own value included), plus the sum. A chmin x stops at a node with second max < x: only the copies
// of the max move (the sum drops by (max - x) * copies). A node's own max / min double as its pending clamp: push
// clamps each child to them, so there are no chmin / chmax tags; and when all of a node's values are equal, push
// hands that value to both children as an assign, so there is no assign tag. All indices 0-based, ranges inclusive
// [l, r], an index always the position in the CURRENT array; searches return -1 when nothing qualifies.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();  // (no second max / min)
    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        S sm = 0;
        T val = T(0);
        T mx = T(0);
        T mx2 = NEG;
        T mn = T(0);
        T mn2 = INF;
        T add = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
        int cmx = 0;
        int cmn = 0;
        char rev = 0;
    };
    static inline vector<Node> nd{Node{}};  // node 0 = the empty tree
    int root = 0;

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit ImplicitTreap(const vector<T>& arr = {}) { root = build(arr); }

    ImplicitTreap makeEmpty() const { return ImplicitTreap(); }  // (a new, empty one)

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(1) -- the current length of the array
    int size() const { return nd[root].sz; }

    // O(logN) expected -- append v to the end
    void append(T v) { root = merge(root, newNode(v)); }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
    ImplicitTreap cut(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        root = merge(a, c);
        ImplicitTreap piece = makeEmpty();
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
    void insertAt(int i, T v) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN) expected -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max)
    int leftmostGtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx > x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].L && nd[nd[t].L].mx > x) t = nd[t].L;
                else if (nd[t].val > x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max)
    int leftmostGteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx >= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].L && nd[nd[t].L].mx >= x) t = nd[t].L;
                else if (nd[t].val >= x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min)
    int leftmostLtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mn < x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].L && nd[nd[t].L].mn < x) t = nd[t].L;
                else if (nd[t].val < x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the subtree min)
    int leftmostLteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mn <= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].L && nd[nd[t].L].mn <= x) t = nd[t].L;
                else if (nd[t].val <= x) { res = l + i + nd[nd[t].L].sz; break; }
                else i += nd[nd[t].L].sz + 1, t = nd[t].R;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- append all of other at the end; other is left empty
    void merge(ImplicitTreap& other) { root = merge(root, other.root), other.root = 0; }

    // O(logN) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(int i, ImplicitTreap& other) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }

    // O(logN) expected -- a[i] += v
    void pointAdd(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = nd[t].val + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = v
    void pointAssign(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = max(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = min(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]
    T pointGet(int i) { return nd[locate(i)].val; }

    // O(logN) expected -- a[i] += v for i in [l, r]
    void rangeAdd(int l, int r, T v) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyAdd(b, v);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyAssign(b, v);
        root = merge(merge(a, b), c);
    }

    // amortized O(log^2 N) expected -- a[i] = max(a[i], v) for i in [l, r]
    void rangeChmax(int l, int r, T v) {
        int a, b, c;
        cut(l, r, a, b, c);
        chmax(b, v);
        root = merge(merge(a, b), c);
    }

    // amortized O(log^2 N) expected -- a[i] = min(a[i], v) for i in [l, r]
    void rangeChmin(int l, int r, T v) {
        int a, b, c;
        cut(l, r, a, b, c);
        chmin(b, v);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- max of a[l..r]
    T rangeMax(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].mx;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- min of a[l..r]
    T rangeMin(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].mn;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- reverse a[l..r] in place
    void rangeReverse(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    // it is taken mod the length (negative shifts right)
    void rangeRotateLeft(int l, int r, long long k) {
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

    // O(logN) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left)
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(logN) expected -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].sm;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the subtree max)
    int rightmostGtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx > x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].R && nd[nd[t].R].mx > x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val > x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the subtree max)
    int rightmostGteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mx >= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].R && nd[nd[t].R].mx >= x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val >= x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the subtree min)
    int rightmostLtX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mn < x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].R && nd[nd[t].R].mn < x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val < x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the subtree min)
    int rightmostLteX(int l, int r, T x) {
        int a, b, c;
        cut(l, r, a, b, c);
        int t = b, i = 0, res = -1;
        if (t && nd[t].mn <= x) {  // some value in a[l..r] passes
            while (true) {
                push(t);
                if (nd[t].R && nd[nd[t].R].mn <= x) i += nd[nd[t].L].sz + 1, t = nd[t].R;
                else if (nd[t].val <= x) { res = l + i + nd[nd[t].L].sz; break; }
                else t = nd[t].L;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    pair<ImplicitTreap, ImplicitTreap> split(int k) {
        ImplicitTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    tuple<ImplicitTreap, ImplicitTreap, ImplicitTreap> trisect(int l, int r) {
        ImplicitTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cut(l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // ---- internals ----

    int newNode(T v) {
        Node n;
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.mx = v, n.mn = v, n.mx2 = NEG, n.cmx = 1,
        n.mn2 = INF, n.cmn = 1, n.rev = 0, n.add = T(0);
        nd.push_back(n);
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

    void pull(int x) {  // recompute x from its children (its own value is one more value of the subtree)
        int l = nd[x].L, r = nd[x].R;
        nd[x].sz = nd[l].sz + nd[r].sz + 1;
        T v = nd[x].val;
        nd[x].sm = nd[l].sm + S(v) + nd[r].sm;
        {
            T m = v, m2 = NEG;
            int k = 1;
            for (int y : {l, r}) {
                if (!y) continue;
                T a = nd[y].mx, a2 = nd[y].mx2;
                if (a > m) m2 = a2 > m ? a2 : m, m = a, k = nd[y].cmx;
                else if (a == m) k += nd[y].cmx, m2 = a2 > m2 ? a2 : m2;
                else if (a > m2) m2 = a;
            }
            nd[x].mx = m, nd[x].mx2 = m2, nd[x].cmx = k;
        }
        {
            T m = v, m2 = INF;
            int k = 1;
            for (int y : {l, r}) {
                if (!y) continue;
                T a = nd[y].mn, a2 = nd[y].mn2;
                if (a < m) m2 = a2 < m ? a2 : m, m = a, k = nd[y].cmn;
                else if (a == m) k += nd[y].cmn, m2 = a2 < m2 ? a2 : m2;
                else if (a < m2) m2 = a;
            }
            nd[x].mn = m, nd[x].mn2 = m2, nd[x].cmn = k;
        }
    }

    void applyAssign(int t, T v) {  // every value of t's subtree becomes v
        if (!t) return;
        int n = nd[t].sz;
        nd[t].val = v, nd[t].sm = S(v) * n;
        nd[t].mx = v;
        nd[t].mn = v;
        nd[t].mx2 = NEG, nd[t].cmx = n;
        nd[t].mn2 = INF, nd[t].cmn = n;
        nd[t].add = T(0);
    }

    void applyAdd(int t, T v) {  // every value of t's subtree gains v (a uniform one stays an assign)
        if (!t) return;
        if (nd[t].mn == nd[t].mx) { applyAssign(t, T(nd[t].mx + v)); return; }
        nd[t].val += v, nd[t].sm += S(v) * nd[t].sz;
        nd[t].mx += v;
        nd[t].mn += v;
        if (nd[t].mx2 != NEG) nd[t].mx2 += v;
        if (nd[t].mn2 != INF) nd[t].mn2 += v;
        nd[t].add += v;
    }

    void applyChmin(int t, T v) {  // chmin by v on t, with mx2 < v < mx: only the copies of the max move
        if (nd[t].mx2 == NEG) { applyAssign(t, v); return; }  // (all equal)
        if (nd[t].val == nd[t].mx) nd[t].val = v;
        if (nd[t].mn2 == nd[t].mx) nd[t].mn2 = v;
        nd[t].sm -= S(nd[t].mx - v) * nd[t].cmx;
        nd[t].mx = v;
    }

    void chmin(int t, T x) {  // a[i] = min(a[i], x) over t's subtree, walking down only where x <= the second max
        if (!t || nd[t].mx <= x) return;
        if (nd[t].mx2 < x) { applyChmin(t, x); return; }
        push(t);
        if (nd[t].val > x) nd[t].val = x;
        chmin(nd[t].L, x), chmin(nd[t].R, x);
        pull(t);
    }

    void applyChmax(int t, T v) {  // chmax by v on t, with mn < v < mn2: only the copies of the min move
        if (nd[t].mn2 == INF) { applyAssign(t, v); return; }  // (all equal)
        if (nd[t].val == nd[t].mn) nd[t].val = v;
        if (nd[t].mx2 == nd[t].mn) nd[t].mx2 = v;
        nd[t].sm += S(v - nd[t].mn) * nd[t].cmn;
        nd[t].mn = v;
    }

    void chmax(int t, T x) {  // a[i] = max(a[i], x) over t's subtree, walking down only where x >= the second min
        if (!t || nd[t].mn >= x) return;
        if (nd[t].mn2 > x) { applyChmax(t, x); return; }
        push(t);
        if (nd[t].val < x) nd[t].val = x;
        chmax(nd[t].L, x), chmax(nd[t].R, x);
        pull(t);
    }

    void applyRev(int x) {  // reverse x's subtree (every kept aggregate reads the same both ways)
        if (x) swap(nd[x].L, nd[x].R), nd[x].rev ^= 1;
    }

    void push(int t) {  // hand t's pending changes to its children: one value (an assign), else the add, then the clamp
        int l = nd[t].L, r = nd[t].R;
        if (nd[t].rev) applyRev(l), applyRev(r), nd[t].rev = 0;
        if (nd[t].mn == nd[t].mx) {
            applyAssign(l, nd[t].mx), applyAssign(r, nd[t].mx);
            nd[t].add = T(0);
            return;
        }
        if (nd[t].add != T(0)) applyAdd(l, nd[t].add), applyAdd(r, nd[t].add), nd[t].add = T(0);
        for (int y : {l, r})
            if (y && nd[y].mx > nd[t].mx) applyChmin(y, nd[t].mx);
        for (int y : {l, r})
            if (y && nd[y].mn < nd[t].mn) applyChmax(y, nd[t].mn);
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
