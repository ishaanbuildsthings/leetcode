// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/treap-sum-min-max-hash-assign-rev-pointers/template.cpp
// @operations: append appendLeft concat cut eraseRange getAll insertAt insertCopiesAt isPalindrome leftmostGtX leftmostGteX leftmostLtX leftmostLteX moveRange paste pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft rangeAssign rangeHash rangeHashReversed rangeMax rangeMin rangeReverse rangeRotateLeft rangeRotateRight rangeSum rangesEqual rightmostGtX rightmostGteX rightmostLtX rightmostLteX split trisect
// @data-structure-type: treap
// @complexities:
//   append: log(N) expected
//   appendLeft: log(N) expected
//   concat: log(N) expected
//   cut: log(N) expected
//   eraseRange: log(N) expected
//   getAll: N
//   insertAt: log(N) expected
//   insertCopiesAt: log(N) expected
//   isPalindrome: log(N) expected
//   leftmostGtX: log(N) expected
//   leftmostGteX: log(N) expected
//   leftmostLtX: log(N) expected
//   leftmostLteX: log(N) expected
//   moveRange: log(N) expected
//   paste: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   pop: log(N) expected
//   popLeft: log(N) expected
//   rangeAssign: log(N) expected
//   rangeHash: log(N) expected
//   rangeHashReversed: log(N) expected
//   rangeMax: log(N) expected
//   rangeMin: log(N) expected
//   rangeReverse: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeSum: log(N) expected
//   rangesEqual: log(N) expected
//   rightmostGtX: log(N) expected
//   rightmostGteX: log(N) expected
//   rightmostLtX: log(N) expected
//   rightmostLteX: log(N) expected
//   split: log(N) expected
//   trisect: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N] mn[1*N] mx[1*N] fh[1*N] bh[1*N] pw[1*N] gs[1*N]
//   tags: rev[1*N] asg[1*N] hasAsg[1*N]
//   other: alloc[2*N]
//   note: N = the values in this treap; every node is allocated on its own (alloc: the allocator's per-node overhead), so cut / paste move nodes between treaps in O(log N) and erased nodes are freed; a treap frees its nodes when it goes out of scope (move-only)

// Implicit treap: an array you can insert into / erase from anywhere, reverse, rotate, move ranges, and cut out into
// a treap of its own / paste a treap into, each in O(logN) expected, plus point ops, rangeAssign, rangeSum, rangeMin,
// rangeMax, range hashes / isPalindrome / rangesEqual (polynomial hashes mod 2^61 - 1 both ways, the base random per
// run; a reverse swaps them). All indices 0-based, ranges inclusive [l, r], and an index always means the position in
// the CURRENT array. Nodes keep their values in array order (an in-order walk); a node's position is the size of
// everything left of it. Lazy tags mean "already applied to this node, not yet to its children".
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node {
        T val;
        unsigned long long pri;
        Node *l = nullptr, *r = nullptr;
        int sz = 1;
        bool rev = false;
        S sm;
        T mn, mx;
        T asg{};
        bool hasAsg = false;
        unsigned long long fh, bh, pw, gs;  // hashes (forward, backward), B^size, 1 + B + ... + B^(size-1)
        explicit Node(T v) : val(v), pri(rnd()), sm(v), mn(v), mx(v), fh(hval(v)), bh(hval(v)), pw(HB()), gs(1) {}
    };
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
    static unsigned long long hadd(unsigned long long a, unsigned long long b) { return a + b >= HP ? a + b - HP : a + b; }
    static unsigned long long hraw(T v) {  // v as a residue (what an add changes a hash by, per position)
        long long r = (long long)v % (long long)HP;
        return r < 0 ? (unsigned long long)(r + (long long)HP) : (unsigned long long)r;
    }
    static unsigned long long hval(T v) {  // the hash of value v: v + an offset random per run, so no common value is 0
        static unsigned long long off = 1 + rnd() % (HP - 1);
        return hadd(hraw(v), off);
    }

    Node* root = nullptr;

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(1) -- an empty array
    ImplicitTreap() {}

    // O(N) -- arr: the initial array (may be empty)
    explicit ImplicitTreap(const vector<T>& arr) {
        vector<Node*> stk;  // Cartesian tree on (position, priority) in one pass: the stack is the current right spine
        for (const T& v : arr) {
            Node *x = new Node(v), *last = nullptr;
            while (!stk.empty() && stk.back()->pri < x->pri) last = stk.back(), stk.pop_back();
            x->l = last;
            if (!stk.empty()) stk.back()->r = x;
            stk.push_back(x);
        }
        root = stk.empty() ? nullptr : stk[0];
        vector<Node*> order, todo;
        if (root) todo.push_back(root);
        while (!todo.empty()) {  // pre-order; pulled in reverse, so children before parents
            Node* x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (x->l) todo.push_back(x->l);
            if (x->r) todo.push_back(x->r);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
    }

    // a treap owns its nodes: it can be moved (cut returns one), not copied
    ImplicitTreap(ImplicitTreap&& o) noexcept : root(o.root) { o.root = nullptr; }
    ImplicitTreap& operator=(ImplicitTreap&& o) noexcept {
        if (this != &o) destroy(root), root = o.root, o.root = nullptr;
        return *this;
    }
    ImplicitTreap(const ImplicitTreap&) = delete;
    ImplicitTreap& operator=(const ImplicitTreap&) = delete;
    ~ImplicitTreap() { destroy(root); }

    // O(1) -- the current length of the array
    int size() const { return sz(root); }

    // O(logN) expected -- append v to the end (it becomes a[size()])
    void append(T v) { root = merge(root, new Node(v)); }

    // O(logN) expected -- append all of other at the end; other is left empty
    void concat(ImplicitTreap& other) {
        root = merge(root, other.root);
        other.root = nullptr;
    }

    // O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0 again); everything after
    // it shifts left by r - l + 1
    ImplicitTreap cut(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        root = merge(a, c);
        ImplicitTreap piece;
        piece.root = b;
        return piece;
    }

    // O(logN) expected -- remove a[l..r] (its nodes are freed: O(r - l + 1) more); everything after it shifts left
    // by r - l + 1
    void eraseRange(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        destroy(b);
        root = merge(a, c);
    }

    // O(N) -- the whole current array a[0..size()-1], every pending tag applied on the way
    vector<T> getAll() {
        vector<T> out;
        out.reserve(size());
        vector<Node*> st;
        Node* t = root;
        while (!st.empty() || t) {
            while (t) push(t), st.push_back(t), t = t->l;
            t = st.back(), st.pop_back();
            out.push_back(t->val);
            t = t->r;
        }
        return out;
    }

    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        Node *a, *c;
        split(root, i, a, c);
        root = merge(merge(a, new Node(v)), c);
    }

    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0): they are built as
    // one treap in O(k), then spliced in
    void insertCopiesAt(int i, T v, long long k) {
        if (k <= 0) return;
        Node *a, *c;
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }

    // O(logN) expected -- is a[l..r] a palindrome (its two hashes agree)
    bool isPalindrome(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        bool res = b->fh == b->bh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] > x, or -1: a walk down a[l..r]'s tree, pruned by the
    // subtree max
    int leftmostGtX(int l, int r, T x) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        int res = -1;
        if (b && b->mx > x) {  // some value in a[l..r] passes
            Node* t = b;
            int i = 0;
            while (true) {
                push(t);
                if (t->l && t->l->mx > x) t = t->l;
                else if (t->val > x) {
                    res = l + i + sz(t->l);
                    break;
                } else i += sz(t->l) + 1, t = t->r;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] >= x, or -1: a walk down a[l..r]'s tree, pruned by the
    // subtree max
    int leftmostGteX(int l, int r, T x) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        int res = -1;
        if (b && b->mx >= x) {  // some value in a[l..r] passes
            Node* t = b;
            int i = 0;
            while (true) {
                push(t);
                if (t->l && t->l->mx >= x) t = t->l;
                else if (t->val >= x) {
                    res = l + i + sz(t->l);
                    break;
                } else i += sz(t->l) + 1, t = t->r;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] < x, or -1: a walk down a[l..r]'s tree, pruned by the
    // subtree min
    int leftmostLtX(int l, int r, T x) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        int res = -1;
        if (b && b->mn < x) {  // some value in a[l..r] passes
            Node* t = b;
            int i = 0;
            while (true) {
                push(t);
                if (t->l && t->l->mn < x) t = t->l;
                else if (t->val < x) {
                    res = l + i + sz(t->l);
                    break;
                } else i += sz(t->l) + 1, t = t->r;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the first i in [l, r] with a[i] <= x, or -1: a walk down a[l..r]'s tree, pruned by the
    // subtree min
    int leftmostLteX(int l, int r, T x) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        int res = -1;
        if (b && b->mn <= x) {  // some value in a[l..r] passes
            Node* t = b;
            int i = 0;
            while (true) {
                push(t);
                if (t->l && t->l->mn <= x) t = t->l;
                else if (t->val <= x) {
                    res = l + i + sz(t->l);
                    break;
                } else i += sz(t->l) + 1, t = t->r;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    // (0 <= i <= size() - (r - l + 1); i = 0 moves it to the front, the max moves it to the end)
    void moveRange(int l, int r, int i) {
        Node *a, *b, *c, *x, *y;
        cut3(l, r, a, b, c);
        split(merge(a, c), i, x, y);
        root = merge(merge(x, b), y);
    }

    // O(logN) expected -- insert all of other so it starts at a[i] (0 <= i <= size(); i = size() appends); other is
    // left empty
    void paste(int i, ImplicitTreap& other) {
        Node *a, *c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = nullptr;
    }

    // O(logN) expected -- a[i] += v
    void pointAdd(int i, T v) {
        vector<Node*> path;
        Node* t = find(i, &path);
        t->val = t->val + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = v
    void pointAssign(int i, T v) {
        vector<Node*> path;
        Node* t = find(i, &path);
        t->val = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        vector<Node*> path;
        Node* t = find(i, &path);
        t->val = max(t->val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        vector<Node*> path;
        Node* t = find(i, &path);
        t->val = min(t->val, v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]
    T pointGet(int i) { return find(i)->val; }

    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[i] and return it; everything after it shifts left by one
    T pop(int i) {
        T v = pointGet(i);
        eraseRange(i, i);
        return v;
    }

    // O(logN) expected -- remove a[0] and return it
    T popLeft() { return pop(0); }

    // O(logN) expected -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        applyAssign(b, v);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- hash of a[l..r] read left to right (a[l] B^(len-1) + ... + a[r], mod 2^61 - 1; B random per run): equal ranges hash equal
    unsigned long long rangeHash(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        unsigned long long res = b->fh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    unsigned long long rangeHashReversed(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        unsigned long long res = b->bh;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- max of a[l..r]
    T rangeMax(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        T res = b->mx;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- min of a[l..r]
    T rangeMin(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        T res = b->mn;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- reverse a[l..r] in place
    void rangeReverse(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any integer k, negative shifts right
    void rangeRotateLeft(int l, int r, long long k) {
        Node *a, *b, *c;
        int len = r - l + 1;
        cut3(l, r, a, b, c);
        k = ((k % len) + len) % len;
        if (k) {
            Node *b1, *b2;
            split(b, (int)k, b1, b2);
            b = merge(b2, b1);
        }
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- cyclic shift a[l..r] right by k (a[r - k + 1..r] move to the front); any integer k,
    // negative shifts left
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(logN) expected -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        S res = b->sm;
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    bool rangesEqual(int l1, int r1, int l2, int r2) { return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2); }

    // O(logN) expected -- the last i in [l, r] with a[i] > x, or -1: a walk down a[l..r]'s tree, pruned by the
    // subtree max
    int rightmostGtX(int l, int r, T x) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        int res = -1;
        if (b && b->mx > x) {  // some value in a[l..r] passes
            Node* t = b;
            int i = 0;
            while (true) {
                push(t);
                if (t->r && t->r->mx > x) i += sz(t->l) + 1, t = t->r;
                else if (t->val > x) {
                    res = l + i + sz(t->l);
                    break;
                } else t = t->l;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] >= x, or -1: a walk down a[l..r]'s tree, pruned by the
    // subtree max
    int rightmostGteX(int l, int r, T x) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        int res = -1;
        if (b && b->mx >= x) {  // some value in a[l..r] passes
            Node* t = b;
            int i = 0;
            while (true) {
                push(t);
                if (t->r && t->r->mx >= x) i += sz(t->l) + 1, t = t->r;
                else if (t->val >= x) {
                    res = l + i + sz(t->l);
                    break;
                } else t = t->l;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] < x, or -1: a walk down a[l..r]'s tree, pruned by the
    // subtree min
    int rightmostLtX(int l, int r, T x) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        int res = -1;
        if (b && b->mn < x) {  // some value in a[l..r] passes
            Node* t = b;
            int i = 0;
            while (true) {
                push(t);
                if (t->r && t->r->mn < x) i += sz(t->l) + 1, t = t->r;
                else if (t->val < x) {
                    res = l + i + sz(t->l);
                    break;
                } else t = t->l;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- the last i in [l, r] with a[i] <= x, or -1: a walk down a[l..r]'s tree, pruned by the
    // subtree min
    int rightmostLteX(int l, int r, T x) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        int res = -1;
        if (b && b->mn <= x) {  // some value in a[l..r] passes
            Node* t = b;
            int i = 0;
            while (true) {
                push(t);
                if (t->r && t->r->mn <= x) i += sz(t->l) + 1, t = t->r;
                else if (t->val <= x) {
                    res = l + i + sz(t->l);
                    break;
                } else t = t->l;
            }
        }
        root = merge(merge(a, b), c);
        return res;
    }

    // O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own (0 <= k <= size()); this one is left empty
    pair<ImplicitTreap, ImplicitTreap> split(int k) {
        pair<ImplicitTreap, ImplicitTreap> res;
        split(root, k, res.first.root, res.second.root);
        root = nullptr;
        return res;
    }

    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    tuple<ImplicitTreap, ImplicitTreap, ImplicitTreap> trisect(int l, int r) {
        tuple<ImplicitTreap, ImplicitTreap, ImplicitTreap> res;
        cut3(l, r, get<0>(res).root, get<1>(res).root, get<2>(res).root);
        root = nullptr;
        return res;
    }

    // ---- internals ----

    static int sz(Node* x) { return x ? x->sz : 0; }

    static void destroy(Node* x) {  // free a whole subtree (iteratively: a long one would overflow the stack)
        vector<Node*> st;
        if (x) st.push_back(x);
        while (!st.empty()) {
            Node* y = st.back();
            st.pop_back();
            if (y->l) st.push_back(y->l);
            if (y->r) st.push_back(y->r);
            delete y;
        }
    }

    // recompute x from its children
    static void pull(Node* x) {
        Node *l = x->l, *r = x->r;
        x->sz = 1 + sz(l) + sz(r);
        x->sm = S(x->val) + (l ? l->sm : S(0)) + (r ? r->sm : S(0));
        x->mn = x->val;
        if (l) x->mn = min(x->mn, l->mn);
        if (r) x->mn = min(x->mn, r->mn);
        x->mx = x->val;
        if (l) x->mx = max(x->mx, l->mx);
        if (r) x->mx = max(x->mx, r->mx);
        unsigned long long B = HB(), hv = hval(x->val), lp = l ? l->pw : 1, rp = r ? r->pw : 1;
        x->pw = hmul(hmul(lp, B), rp);
        x->gs = hadd(hmul(hadd(hmul(l ? l->gs : 0, B), 1), rp), r ? r->gs : 0);
        x->fh = hadd(hmul(hadd(hmul(l ? l->fh : 0, B), hv), rp), r ? r->fh : 0);
        x->bh = hadd(hmul(hadd(hmul(r ? r->bh : 0, B), hv), lp), l ? l->bh : 0);
    }

    static void applyRev(Node* x) {
        if (x) swap(x->l, x->r), x->rev = !x->rev, swap(x->fh, x->bh);  // reversed: the hashes trade places
    }

    static void applyAssign(Node* x, T v) {
        if (!x) return;
        x->val = v;
        x->sm = S(v) * x->sz;
        x->mn = v;
        x->mx = v;
        x->fh = x->bh = hmul(hval(v), x->gs);
        x->hasAsg = true, x->asg = v;
    }

    // hand x's pending tags to its children
    static void push(Node* x) {
        if (x->rev) applyRev(x->l), applyRev(x->r), x->rev = false;
        if (x->hasAsg) applyAssign(x->l, x->asg), applyAssign(x->r, x->asg), x->hasAsg = false;
    }

    // a = first k elements of t, b = the rest
    static void split(Node* t, int k, Node*& a, Node*& b) {
        if (!t) { a = b = nullptr; return; }
        push(t);
        if (sz(t->l) >= k) split(t->l, k, a, t->l), b = t;
        else split(t->r, k - sz(t->l) - 1, t->r, b), a = t;
        pull(t);
    }

    // a's elements, then b's
    static Node* merge(Node* a, Node* b) {
        if (!a || !b) return a ? a : b;
        if (a->pri > b->pri) {
            push(a);
            a->r = merge(a->r, b);
            pull(a);
            return a;
        }
        push(b);
        b->l = merge(a, b->l);
        pull(b);
        return b;
    }

    // a = a[0..l-1], b = a[l..r], c = a[r+1..] as three trees; put them back with merge(merge(a, b), c)
    void cut3(int l, int r, Node*& a, Node*& b, Node*& c) {
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    // the node holding a[i], with every tag on the way pushed; path (if given) gets the nodes above it
    Node* find(int i, vector<Node*>* path = nullptr) {
        Node* t = root;
        while (true) {
            push(t);
            int ls = sz(t->l);
            if (i == ls) return t;
            if (path) path->push_back(t);
            if (i < ls) t = t->l;
            else i -= ls + 1, t = t->r;
        }
    }

    // a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    static Node* build(const vector<T>& vals) {
        vector<Node*> stk, order, todo;
        for (const T& v : vals) {
            Node *x = new Node(v), *last = nullptr;
            while (!stk.empty() && stk.back()->pri < x->pri) last = stk.back(), stk.pop_back();
            x->l = last;
            if (!stk.empty()) stk.back()->r = x;
            stk.push_back(x);
        }
        Node* rt = stk.empty() ? nullptr : stk[0];
        if (rt) todo.push_back(rt);
        while (!todo.empty()) {  // pre-order; pulled in reverse, so children before parents
            Node* x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (x->l) todo.push_back(x->l);
            if (x->r) todo.push_back(x->r);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
        return rt;
    }
};
