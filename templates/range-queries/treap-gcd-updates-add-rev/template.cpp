// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-gcd-updates-add-rev/template.cpp
// @operations: append appendLeft cut getAll insertAt insertCopiesAt merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeGcd rangeReverse rangeRotateLeft rangeRotateRight size split trisect
// @data-structure-type: treap
// @complexities:
//   append: log(N)*log(U) expected ?
//   appendLeft: log(N)*log(U) expected ?
//   cut: log(N)*log(U) expected ?
//   getAll: N
//   insertAt: log(N)*log(U) expected ?
//   insertCopiesAt: log(N)*log(U) expected ?
//   merge: log(N)*log(U) expected ?
//   paste: log(N)*log(U) expected ?
//   pointAdd: log(N)*log(U) expected ?
//   pointAssign: log(N)*log(U) expected ?
//   pointChmax: log(N)*log(U) expected ?
//   pointChmin: log(N)*log(U) expected ?
//   pointGet: log(N) expected
//   rangeAdd: log(N)*log(U) expected ?
//   rangeGcd: log(N)*log(U) expected ?
//   rangeReverse: log(N)*log(U) expected ?
//   rangeRotateLeft: log(N)*log(U) expected ?
//   rangeRotateRight: log(N)*log(U) expected ?
//   split: log(N)*log(U) expected ?
//   trisect: log(N)*log(U) expected ?
//   size: 1
//   build: N*log(U) ?
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] g[1*N] fv[1*N] lv[1*N]
//   tags: rev[1*N] add[1*N]
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

// Implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, move, cut pieces
// out of (that is how to erase) and paste them back in O(logN) expected each, with rangeAdd; each node keeps its gcd
// over its subtree. All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array;
// searches return -1 when nothing qualifies. Lazy tags mean "already applied to this node, not yet to its children".
// T: int, long long, ...
template <typename T>
struct ImplicitTreap {
    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        T val = T(0);
        T g = T(0);
        T fv = T(0);
        T lv = T(0);
        T add = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
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
            while (t) push(t), st.push_back(t), t = nd[t].L;
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

    // O(logN * logU) expected -- a[i] += v for i in [l, r]; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeAdd(int l, int r, T v) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeAdd: needs 0 <= l <= r < size()");
        upd(root, l, r, [&](int x, int off) { applyAdd(x, v); (void)off; },
            [&](T w, int off) { (void)off; return T(w + v); });
    }

    // O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < size(), else throws out_of_range
    T rangeGcd(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeGcd: needs 0 <= l <= r < size()");
        size_t mark;
        int b = rangeNode(l, r, mark);
        T res = gcd(nd[b].fv, nd[b].g);
        release(mark);
        return res;
    }

    // O(logN * logU) expected -- reverse a[l..r] in place; needs 0 <= l <= r < size(), else throws out_of_range
    void rangeReverse(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeReverse: needs 0 <= l <= r < size()");
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
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
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.g = T(0), n.fv = v, n.lv = v, n.rev = 0, n.add = T(0);
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
        T gg = gcd(nd[l].g, nd[r].g);
        if (l) gg = gcd(gg, T(v - nd[l].lv));
        if (r) gg = gcd(gg, T(nd[r].fv - v));
        nd[x].g = gg;
        nd[x].fv = l ? nd[l].fv : v;
        nd[x].lv = r ? nd[r].lv : v;
    }

    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        swap(nd[x].L, nd[x].R), nd[x].rev ^= 1, swap(nd[x].fv, nd[x].lv);
    }

    void applyAdd(int x, T v) {  // every value of x's subtree gains v
        if (!x) return;
        nd[x].val += v;
        nd[x].fv += v, nd[x].lv += v;
        nd[x].add += v;
    }

    void push(int x) {  // hand x's pending tags to its children
        if (nd[x].rev) applyRev(nd[x].L), applyRev(nd[x].R), nd[x].rev = 0;
        if (nd[x].add != T(0)) applyAdd(nd[x].L, nd[x].add), applyAdd(nd[x].R, nd[x].add), nd[x].add = T(0);
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

    // ---- queries, searches and range updates walk the pieces of [l, r] instead of cutting it out ----

    // a[l..r] of t's subtree as (node, whole subtree?) in order; pending tags on the way pushed down
    void pieces(int t, int l, int r, vector<pair<int, bool>>& out) {
        if (!t || r < 0 || l >= nd[t].sz) return;
        if (l <= 0 && nd[t].sz - 1 <= r) {
            out.push_back({t, true});
            return;
        }
        push(t);
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
        push(t);
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
        n.val = nd[x].val, n.pri = nd[x].pri, n.L = nd[x].L, n.R = nd[x].R, n.sz = nd[x].sz, n.g = nd[x].g,
        n.fv = nd[x].fv, n.lv = nd[x].lv, n.rev = nd[x].rev, n.add = nd[x].add;
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
        push(t);
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
