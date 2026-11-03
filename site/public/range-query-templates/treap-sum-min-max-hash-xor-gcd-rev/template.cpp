// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-min-max-hash-xor-gcd-rev/template.cpp
// @operations: append appendLeft cut getAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX leftmostLtX leftmostLteX merge paste pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd rangeHash rangeHashReversed rangeMax rangeMin rangeReverse rangeRotateLeft rangeRotateRight rangeSum rangeXorQuery rangesEqual rightmostGtX rightmostGteX rightmostLtX rightmostLteX split trisect
// @data-structure-type: treap
// @complexities:
//   append: log(N)*log(U) expected ?
//   appendLeft: log(N)*log(U) expected ?
//   cut: log(N)*log(U) expected ?
//   getAll: N
//   insertAt: log(N)*log(U) expected ?
//   insertCopiesAt: log(N)*log(U) expected ?
//   isPalindrome: log(N)*log(U) expected ?
//   leftmostGtX: log(N)*log(U) expected ?
//   leftmostGteX: log(N)*log(U) expected ?
//   leftmostLtX: log(N)*log(U) expected ?
//   leftmostLteX: log(N)*log(U) expected ?
//   merge: log(N)*log(U) expected ?
//   paste: log(N)*log(U) expected ?
//   pointAdd: log(N)*log(U) expected ?
//   pointAssign: log(N)*log(U) expected ?
//   pointChmax: log(N)*log(U) expected ?
//   pointChmin: log(N)*log(U) expected ?
//   pointGet: log(N) expected
//   rangeGcd: log(N)*log(U) expected ?
//   rangeHash: log(N)*log(U) expected ?
//   rangeHashReversed: log(N)*log(U) expected ?
//   rangeMax: log(N)*log(U) expected ?
//   rangeMin: log(N)*log(U) expected ?
//   rangeReverse: log(N)*log(U) expected ?
//   rangeRotateLeft: log(N)*log(U) expected ?
//   rangeRotateRight: log(N)*log(U) expected ?
//   rangeSum: log(N)*log(U) expected ?
//   rangeXorQuery: log(N)*log(U) expected ?
//   rangesEqual: log(N)*log(U) expected ?
//   rightmostGtX: log(N)*log(U) expected ?
//   rightmostGteX: log(N)*log(U) expected ?
//   rightmostLtX: log(N)*log(U) expected ?
//   rightmostLteX: log(N)*log(U) expected ?
//   split: log(N)*log(U) expected ?
//   trisect: log(N)*log(U) expected ?
//   build: N*log(U) ?
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mn[1*N] mx[1*N] fh[1*N] bh[1*N] pw[1*N] xr[1*N] g[1*N]
//   tags: rev[1*N]
//   other: none
//   note: N = every value ever inserted (the initial array plus each insert; erased nodes are not reused); every ImplicitTreap<T> shares one node pool (pieces move between any of them; nothing to reset)

// Implicit treap with composable aggregates: an array you can insert into anywhere, reverse, rotate, move, cut pieces
// out of (that is how to erase) and paste them back in O(logN) expected each; each node keeps its sum, its min, its
// max, its forward / backward hash (and B^size), its xor, its gcd over its subtree. All indices 0-based, ranges
// inclusive [l, r], an index always the position in the CURRENT array; searches return -1 when nothing qualifies.
// Lazy tags mean "already applied to this node, not yet to its children".
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    // one node pool shared by every ImplicitTreap<T>: cut / paste move nodes between them, so a piece from one can go
    // into any other (node 0 = the empty tree). Nodes are never freed (memory = every value ever inserted, over the
    // whole run), so there is nothing to reset between test cases
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        unsigned long long pri = 0;
        U64 fh = 0;
        U64 bh = 0;
        U64 pw = 1;
        S sm = 0;
        T val = T(0);
        T mn = T(0);
        T mx = T(0);
        T xr = T(0);
        T g = T(0);
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

    // O(logN * logU) expected -- is a[l..r] a palindrome (its two hashes agree)
    bool isPalindrome(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        bool res = nd[b].fh == nd[b].bh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- the first i in [l, r] with a[i] > x, or -1 (pruned by the subtree max)
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

    // O(logN * logU) expected -- the first i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max)
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

    // O(logN * logU) expected -- gcd of |a[l]|, ..., |a[r]|
    T rangeGcd(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].g;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal
    U64 rangeHash(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        U64 res = nd[b].fh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    U64 rangeHashReversed(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        U64 res = nd[b].bh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- max of a[l..r]
    T rangeMax(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].mx;
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

    // O(logN * logU) expected -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = nd[b].sm;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- a[l] ^ ... ^ a[r]
    T rangeXorQuery(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        T res = nd[b].xr;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN * logU) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    bool rangesEqual(int l1, int r1, int l2, int r2) {
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(logN * logU) expected -- the last i in [l, r] with a[i] > x, or -1 (pruned by the subtree max)
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

    // O(logN * logU) expected -- the last i in [l, r] with a[i] >= x, or -1 (pruned by the subtree max)
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
        n.val = v, n.pri = rnd(), n.L = 0, n.R = 0, n.sz = 1, n.sm = S(v), n.mn = v, n.mx = v, n.fh = hval(v),
        n.bh = hval(v), n.pw = HB(), n.xr = v, n.g = v < T(0) ? T(-v) : v, n.rev = 0;
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
        nd[x].mn = v;
        if (l && nd[l].mn < nd[x].mn) nd[x].mn = nd[l].mn;
        if (r && nd[r].mn < nd[x].mn) nd[x].mn = nd[r].mn;
        nd[x].mx = v;
        if (l && nd[l].mx > nd[x].mx) nd[x].mx = nd[l].mx;
        if (r && nd[r].mx > nd[x].mx) nd[x].mx = nd[r].mx;
        U64 B = HB(), hv = hval(v);
        nd[x].pw = hmul(hmul(nd[l].pw, B), nd[r].pw);
        nd[x].fh = hadd(hmul(hadd(hmul(nd[l].fh, B), hv), nd[r].pw), nd[r].fh);
        nd[x].bh = hadd(hmul(hadd(hmul(nd[r].bh, B), hv), nd[l].pw), nd[l].bh);
        nd[x].xr = nd[l].xr ^ v ^ nd[r].xr;
        nd[x].g = gcd(gcd(nd[l].g, v), nd[r].g);
    }

    void applyRev(int x) {  // reverse x's subtree
        if (!x) return;
        swap(nd[x].L, nd[x].R), nd[x].rev ^= 1, swap(nd[x].fh, nd[x].bh);
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
