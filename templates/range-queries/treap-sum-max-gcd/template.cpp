// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-max-gcd/template.cpp
// @operations: append appendLeft cut getAll insertAt insertCopiesAt leftmostGtX leftmostGteX merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd rangeMax rangeRotateLeft rangeRotateRight rangeSum rightmostGtX rightmostGteX size split trisect
// @data-structure-type: treap
// @complexities:
//   append: log(N)*log(U) expected ?
//   appendLeft: log(N)*log(U) expected ?
//   cut: log(N)*log(U) expected ?
//   getAll: N
//   insertAt: log(N)*log(U) expected ?
//   insertCopiesAt: log(N)*log(U) expected ?
//   leftmostGtX: log(N)*log(U) expected ?
//   leftmostGteX: log(N)*log(U) expected ?
//   merge: log(N)*log(U) expected ?
//   paste: log(N)*log(U) expected ?
//   pointAdd: log(N)*log(U) expected ?
//   pointAssign: log(N)*log(U) expected ?
//   pointChmax: log(N)*log(U) expected ?
//   pointChmin: log(N)*log(U) expected ?
//   pointGet: log(N) expected
//   rangeGcd: log(N)*log(U) expected ?
//   rangeMax: log(N)*log(U) expected ?
//   rangeRotateLeft: log(N)*log(U) expected ?
//   rangeRotateRight: log(N)*log(U) expected ?
//   rangeSum: log(N)*log(U) expected ?
//   rightmostGtX: log(N)*log(U) expected ?
//   rightmostGteX: log(N)*log(U) expected ?
//   split: log(N)*log(U) expected ?
//   trisect: log(N)*log(U) expected ?
//   size: 1
//   build: N*log(U) ?
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mx[1*N] g[1*N]
//   tags: none
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

// Implicit treap with composable aggregates: an array you can insert into anywhere, rotate, move, cut pieces out of
// (that is how to erase) and paste them back in O(logN) expected each; each node keeps its sum, its max, its gcd over
// its subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array;
// searches return -1 when nothing qualifies.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        S sm = 0;
        T val = T(0);
        T mx = T(0);
        T g = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
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

    // O(logN * logU) expected -- append v to the end
    void append(T v) { root = merge(root, newNode(v)); }

    // O(logN * logU) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN * logU) expected -- remove a[l..r] and return it as a treap of its own (indices from 0); needs
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

    // O(logN * logU) expected -- insert v so it becomes a[i]; needs 0 <= i <= size(), else throws out_of_range (i =
    // size() appends)
    void insertAt(int i, T v) {
        if (i < 0 || i > size()) throw out_of_range("insertAt: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN * logU) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0); needs
    // 0 <= i <= size(), else throws out_of_range
    void insertCopiesAt(int i, T v, long long k) {
        if (i < 0 || i > size()) throw out_of_range("insertCopiesAt: needs 0 <= i <= size()");
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] > x, or -1 (pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int leftmostGtX(int l, int r, T x) {
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

    // O(logN * logU) expected -- the first i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int leftmostGteX(int l, int r, T x) {
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

    // O(logN * logU) expected -- append all of other at the end; other is left empty
    void merge(ImplicitTreap& other) { root = merge(root, other.root), other.root = 0; }

    // O(logN * logU) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i]
    // (needs 0 <= i <= size(), else throws out_of_range); other is left empty
    void paste(int i, ImplicitTreap& other) {
        if (i < 0 || i > size()) throw out_of_range("paste: needs 0 <= i <= size()");
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }

    // O(logN * logU) expected -- a[i] += v; needs 0 <= i < size(), else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAdd: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = nd[t].val + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = max(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmax: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = max(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = min(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmin: needs 0 <= i < size()");
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = min(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return nd[locate(i)].val;
    }

    // O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeGcd(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeGcd: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        T res = nd[b].g;
        release(mark);
        return res;
    }

    // O(logN * logU) expected -- max of a[l..r]; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeMax: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        T res = nd[b].mx;
        release(mark);
        return res;
    }

    // O(logN * logU) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative: it
    // is taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else throws out_of_range
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

    // O(logN * logU) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left); needs 0 <= l <= r < size(), else throws out_of_range
    void rangeRotateRight(int l, int r, long long k) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeRotateRight: needs 0 <= l <= r < size()");
        rangeRotateLeft(l, r, -k);
    }

    // O(logN * logU) expected -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else throws out_of_range
    S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeSum: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        S res = nd[b].sm;
        release(mark);
        return res;
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] > x, or -1 (pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int rightmostGtX(int l, int r, T x) {
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

    // O(logN * logU) expected -- the last i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max); needs
    // 0 <= l <= r < size(), else throws out_of_range
    int rightmostGteX(int l, int r, T x) {
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

    // O(logN * logU) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty; needs
    // 0 <= k <= size(), else throws out_of_range
    pair<ImplicitTreap, ImplicitTreap> split(int k) {
        if (k < 0 || k > size()) throw out_of_range("split: needs 0 <= k <= size()");
        ImplicitTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN * logU) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty;
    // needs 0 <= l <= r < size(), else throws out_of_range
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
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.mx = v, n.g = v < T(0) ? T(-v) : v;
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

    void pull(int x) {  // recompute x from its children
        int l = nd[x].L, r = nd[x].R;
        nd[x].sz = nd[l].sz + nd[r].sz + 1;
        T v = nd[x].val;
        nd[x].sm = nd[l].sm + S(v) + nd[r].sm;
        nd[x].mx = v;
        if (l && nd[l].mx > nd[x].mx) nd[x].mx = nd[l].mx;
        if (r && nd[r].mx > nd[x].mx) nd[x].mx = nd[r].mx;
        nd[x].g = gcd(gcd(nd[l].g, v), nd[r].g);
    }

    void split(int t, int k, int& a, int& b) {  // a = first k of t, b = the rest
        if (!t) { a = b = 0; return; }
        if (nd[nd[t].L].sz >= k) split(nd[t].L, k, a, nd[t].L), b = t;
        else split(nd[t].R, k - nd[nd[t].L].sz - 1, nd[t].R, b), a = t;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's
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

    void cut(int l, int r, int& a, int& b, int& c) {  // a[0..l-1], a[l..r], a[r+1..]
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    int locate(int i, vector<int>* path = nullptr) {  // the node holding a[i], every tag on the way pushed
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
    void pieces(int t, int l, int r, vector<pair<int, bool>>& out) {
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
    int rangeNode(int l, int r, size_t& mark) {
        mark = nd.size();
        return rq(root, l, r);
    }

    // a node over a[l..r] of t's subtree: t itself if that is all of it, else temporaries made only where two parts
    // meet (pending tags on the way pushed down)
    int rq(int t, int l, int r) {
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

    int clone(int x) {  // a temporary copy of node x (sharing its children), dropped by release
        Node n;
        n.val = nd[x].val, n.pri = nd[x].pri, n.L = nd[x].L, n.R = nd[x].R, n.sz = nd[x].sz, n.sm = nd[x].sm,
        n.mx = nd[x].mx, n.g = nd[x].g;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    void release(size_t mark) {  // drop every node made after mark (temporaries: no tree points to them)
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
    void upd(int t, int l, int r, const F& f, const H& h) {
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
