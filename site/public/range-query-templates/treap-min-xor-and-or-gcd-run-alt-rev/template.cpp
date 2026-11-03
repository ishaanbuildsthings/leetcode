// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-min-xor-and-or-gcd-run-alt-rev/template.cpp
// @operations: append appendLeft cut getAll insertAt insertCopiesAt leftmostLtX leftmostLteX longestEqualRun maxAltSubseqSum merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeGcd rangeMin rangeOrQuery rangeReverse rangeRotateLeft rangeRotateRight rangeXorQuery rightmostLtX rightmostLteX split trisect
// @data-structure-type: treap
// @complexities:
//   append: log(N)*log(U) expected ?
//   appendLeft: log(N)*log(U) expected ?
//   cut: log(N)*log(U) expected ?
//   getAll: N
//   insertAt: log(N)*log(U) expected ?
//   insertCopiesAt: log(N)*log(U) expected ?
//   leftmostLtX: log(N)*log(U) expected ?
//   leftmostLteX: log(N)*log(U) expected ?
//   longestEqualRun: log(N)*log(U) expected ?
//   maxAltSubseqSum: log(N)*log(U) expected ?
//   merge: log(N)*log(U) expected ?
//   paste: log(N)*log(U) expected ?
//   pointAdd: log(N)*log(U) expected ?
//   pointAssign: log(N)*log(U) expected ?
//   pointChmax: log(N)*log(U) expected ?
//   pointChmin: log(N)*log(U) expected ?
//   pointGet: log(N) expected
//   rangeAndQuery: log(N)*log(U) expected ?
//   rangeGcd: log(N)*log(U) expected ?
//   rangeMin: log(N)*log(U) expected ?
//   rangeOrQuery: log(N)*log(U) expected ?
//   rangeReverse: log(N)*log(U) expected ?
//   rangeRotateLeft: log(N)*log(U) expected ?
//   rangeRotateRight: log(N)*log(U) expected ?
//   rangeXorQuery: log(N)*log(U) expected ?
//   rightmostLtX: log(N)*log(U) expected ?
//   rightmostLteX: log(N)*log(U) expected ?
//   split: log(N)*log(U) expected ?
//   trisect: log(N)*log(U) expected ?
//   build: N*log(U) ?
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] mn[1*N] xr[1*N] an[1*N] orr[1*N] g[1*N] fv[1*N] lv[1*N] pr[1*N] sr[1*N] br[1*N] a00[1*N] a01[1*N] a10[1*N] a11[1*N]
//   tags: rev[1*N]
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

// Implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, move, cut pieces
// out of (that is how to erase) and paste them back in O(logN) expected each; each node keeps its min, its xor, its
// AND, its OR, its gcd, its first / last value and the equal runs at its ends and inside, its best alternating (+ - +
// ...) subsequence sum for each start / end sign over its subtree. All indices 0-based, ranges inclusive [l, r], an
// index always the position in the CURRENT array; searches return -1 when nothing qualifies. Lazy tags mean "already
// applied to this node, not yet to its children".
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        S a00 = 0;
        S a01 = 0;
        S a10 = 0;
        S a11 = 0;
        T val = T(0);
        T mn = T(0);
        T xr = T(0);
        T an = ~T(0);
        T orr = T(0);
        T g = T(0);
        T fv = T(0);
        T lv = T(0);
        int L = 0;
        int R = 0;
        int sz = 0;
        int pr = 0;
        int sr = 0;
        int br = 0;
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

    // O(logN * logU) expected -- remove a[l..r] and return it as a treap of its own (indices from 0)
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

    // O(logN * logU) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(k + logN * logU) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0)
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] < x, or -1 (pruned by the subtree min)
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

    // O(logN * logU) expected -- the first i in [l, r] with a[i] <= x, or -1 (pruned by the subtree min)
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

    // O(logN * logU) expected -- the longest run of equal adjacent values in a[l..r]
    int longestEqualRun(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        int res = nd[b].br;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]
    S maxAltSubseqSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = max(nd[b].a00, nd[b].a01);
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- append all of other at the end; other is left empty
    void merge(ImplicitTreap& other) { root = merge(root, other.root), other.root = 0; }

    // O(logN * logU) expected -- insert all of other (any ImplicitTreap, e.g. a cut piece) so it starts at a[i]
    // (0 <= i <= size()); other is left empty
    void paste(int i, ImplicitTreap& other) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = 0;
    }

    // O(logN * logU) expected -- a[i] += v
    void pointAdd(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = nd[t].val + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = v
    void pointAssign(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = max(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN * logU) expected -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        vector<int> path;
        int t = locate(i, &path);
        nd[t].val = min(nd[t].val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]
    T pointGet(int i) { return nd[locate(i)].val; }

    // O(logN * logU) expected -- a[l] & ... & a[r]
    T rangeAndQuery(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].an;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|
    T rangeGcd(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].g;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- min of a[l..r]
    T rangeMin(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].mn;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- a[l] | ... | a[r]
    T rangeOrQuery(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].orr;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- reverse a[l..r] in place
    void rangeReverse(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }

    // O(logN * logU) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
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

    // O(logN * logU) expected -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    // length (negative shifts left)
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(logN * logU) expected -- a[l] ^ ... ^ a[r]
    T rangeXorQuery(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].xr;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] < x, or -1 (pruned by the subtree min)
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

    // O(logN * logU) expected -- the last i in [l, r] with a[i] <= x, or -1 (pruned by the subtree min)
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

    // O(logN * logU) expected -- (a[0..k-1], a[k..]) as two treaps of their own; this one is left empty
    pair<ImplicitTreap, ImplicitTreap> split(int k) {
        ImplicitTreap left = makeEmpty(), right = makeEmpty();
        split(root, k, left.root, right.root);
        root = 0;
        return {left, right};
    }

    // O(logN * logU) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    tuple<ImplicitTreap, ImplicitTreap, ImplicitTreap> trisect(int l, int r) {
        ImplicitTreap left = makeEmpty(), mid = makeEmpty(), right = makeEmpty();
        cut(l, r, left.root, mid.root, right.root);
        root = 0;
        return {left, mid, right};
    }

    // ---- internals ----

    int newNode(T v) {
        Node n;
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.mn = v, n.xr = v, n.an = v, n.orr = v,
        n.g = v < T(0) ? T(-v) : v, n.fv = v, n.lv = v, n.pr = 1, n.sr = 1, n.br = 1, n.a00 = S(v), n.a01 = NEG,
        n.a10 = NEG, n.a11 = -S(v), n.rev = 0;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
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
        nd[x].mn = v;
        if (l && nd[l].mn < nd[x].mn) nd[x].mn = nd[l].mn;
        if (r && nd[r].mn < nd[x].mn) nd[x].mn = nd[r].mn;
        nd[x].xr = nd[l].xr ^ v ^ nd[r].xr;
        nd[x].an = nd[l].an & v & nd[r].an;  // (node 0: the AND of nothing, ~0)
        nd[x].orr = nd[l].orr | v | nd[r].orr;
        nd[x].g = gcd(gcd(nd[l].g, v), nd[r].g);
        int rp = 1, rq = 1, bb = 1;
        if (l) {
            bool j = nd[l].lv == v;
            rp = nd[l].pr + (j && nd[l].pr == nd[l].sz);
            rq = j ? nd[l].sr + 1 : 1;
            bb = max(nd[l].br, rq);
        }
        if (r) {
            bool j = v == nd[r].fv;
            bb = max({bb, nd[r].br, j ? rq + nd[r].pr : 0});
            if (j && rp == nd[l].sz + 1) rp += nd[r].pr;
            rq = j && nd[r].sr == nd[r].sz ? nd[r].sr + rq : nd[r].sr;
        }
        nd[x].pr = rp, nd[x].sr = rq, nd[x].br = bb;
        nd[x].fv = l ? nd[l].fv : v;
        nd[x].lv = r ? nd[r].lv : v;
        array<S, 4> c{S(v), NEG, NEG, -S(v)};
        if (l) c = altJoin({nd[l].a00, nd[l].a01, nd[l].a10, nd[l].a11}, c);
        if (r) c = altJoin(c, {nd[r].a00, nd[r].a01, nd[r].a10, nd[r].a11});
        nd[x].a00 = c[0], nd[x].a01 = c[1], nd[x].a10 = c[2], nd[x].a11 = c[3];
    }

    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        swap(nd[x].L, nd[x].R), nd[x].rev ^= 1, swap(nd[x].fv, nd[x].lv), swap(nd[x].pr, nd[x].sr),
            swap(nd[x].a01, nd[x].a10);
    }

    void push(int x) {  // hand x's pending tags to its children
        if (nd[x].rev) applyRev(nd[x].L), applyRev(nd[x].R), nd[x].rev = 0;
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
