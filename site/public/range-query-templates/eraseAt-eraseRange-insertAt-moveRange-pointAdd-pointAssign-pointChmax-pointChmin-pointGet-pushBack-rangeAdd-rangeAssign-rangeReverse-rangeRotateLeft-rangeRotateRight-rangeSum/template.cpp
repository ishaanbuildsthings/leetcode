// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/eraseAt-eraseRange-insertAt-moveRange-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-pushBack-rangeAdd-rangeAssign-rangeReverse-rangeRotateLeft-rangeRotateRight-rangeSum/template.cpp
// @operations: eraseAt eraseRange insertAt moveRange pointAdd pointAssign pointChmax pointChmin pointGet pushBack rangeAdd rangeAssign rangeReverse rangeRotateLeft rangeRotateRight rangeSum
// @data-structure-type: treap
// @complexities:
//   eraseAt: log(N) expected
//   eraseRange: log(N) expected
//   insertAt: log(N) expected
//   moveRange: log(N) expected
//   pointAdd: log(N) expected
//   pointAssign: log(N) expected
//   pointChmax: log(N) expected
//   pointChmin: log(N) expected
//   pointGet: log(N) expected
//   pushBack: log(N) expected
//   rangeAdd: log(N) expected
//   rangeAssign: log(N) expected
//   rangeReverse: log(N) expected
//   rangeRotateLeft: log(N) expected
//   rangeRotateRight: log(N) expected
//   rangeSum: log(N) expected
//   build: N
// @memory:
//   layout: none
//   node: val[1*N] sz[1*N] L[1*N] R[1*N] pri[1*N] sm[1*N]
//   tags: rev[1*N] add[1*N] asg[1*N] hasAsg[1*N]
//   other: none
//   note: N = every value ever inserted (the initial array plus each insertAt; erased nodes are not reused); split / merge recurse O(log N) deep in expectation

// Implicit treap: an array you can insert into / erase from anywhere, reverse, rotate and cut-and-paste, each in
// O(logN) expected, plus point ops, rangeAdd / rangeAssign and rangeSum. All indices 0-based, ranges inclusive [l,
// r], and an index always means the position in the CURRENT array. Nodes keep their values in array order (an
// in-order walk); a node's position is the size of everything left of it. Lazy tags mean "already applied to this
// node, not yet to its children".
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ImplicitTreap {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int root = 0;
    vector<T> val;  // node 0 is the empty tree
    vector<unsigned long long> pri;
    vector<int> L, R, sz;
    vector<char> rev;
    vector<S> sm;
    vector<T> add, asg;
    vector<char> hasAsg;

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N) -- arr: the initial array (may be empty)
    explicit ImplicitTreap(const vector<T>& arr) {
        int n = (int)arr.size();
        val.assign(1, T(0)), val.insert(val.end(), arr.begin(), arr.end());
        pri.assign(n + 1, 0), L.assign(n + 1, 0), R.assign(n + 1, 0), sz.assign(n + 1, 1), rev.assign(n + 1, 0);
        sz[0] = 0;
        for (int x = 1; x <= n; x++) pri[x] = rnd();
        sm.assign(n + 1, S(0));
        add.assign(n + 1, T(0)), asg.assign(n + 1, T(0)), hasAsg.assign(n + 1, 0);
        // Cartesian tree on (position, priority) in one pass: the stack is the current right spine
        vector<int> stk;
        for (int x = 1; x <= n; x++) {
            int last = 0;
            while (!stk.empty() && pri[stk.back()] < pri[x]) last = stk.back(), stk.pop_back();
            L[x] = last;
            if (!stk.empty()) R[stk.back()] = x;
            stk.push_back(x);
        }
        root = stk.empty() ? 0 : stk[0];
        vector<int> order, todo;
        if (n) todo.push_back(root);
        while (!todo.empty()) {  // pre-order; pulled in reverse, so children before parents
            int x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (L[x]) todo.push_back(L[x]);
            if (R[x]) todo.push_back(R[x]);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
    }

    // O(1) -- the current length of the array
    int size() const { return sz[root]; }

    // O(logN) expected -- remove a[i]; everything after it shifts left by one
    void eraseAt(int i) { eraseRange(i, i); }

    // O(logN) expected -- remove a[l..r]; everything after it shifts left by r - l + 1
    void eraseRange(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        root = merge(a, c);
    }

    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }

    // O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    // (0 <= i <= size() - (r - l + 1); i = 0 moves it to the front, the max moves it to the end)
    void moveRange(int l, int r, int i) {
        int a, b, c, x, y;
        cut(l, r, a, b, c);
        split(merge(a, c), i, x, y);
        root = merge(merge(x, b), y);
    }

    // O(logN) expected -- a[i] += v
    void pointAdd(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = val[t] + v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = v
    void pointAssign(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = v;
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = max(val[t], v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        vector<int> path;
        int t = find(i, &path);
        val[t] = min(val[t], v);
        pull(t);
        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);
    }

    // O(logN) expected -- a[i]
    T pointGet(int i) { return val[find(i)]; }

    // O(logN) expected -- append v to the end (it becomes a[size()])
    void pushBack(T v) {
        int x = newNode(v);
        root = merge(root, x);
    }

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

    // O(logN) expected -- reverse a[l..r] in place
    void rangeReverse(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }

    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any integer k, negative shifts right
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

    // O(logN) expected -- cyclic shift a[l..r] right by k (a[r - k + 1..r] move to the front); any integer k,
    // negative shifts left
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }

    // O(logN) expected -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        S res = sm[b];
        root = merge(merge(a, b), c);
        return res;
    }

    // ---- internals ----

    int newNode(T v) {
        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1), rev.push_back(0);
        sm.push_back(S(v));
        add.push_back(T(0)), asg.push_back(T(0)), hasAsg.push_back(0);
        return (int)val.size() - 1;
    }

    // recompute x from its children
    void pull(int x) {
        int l = L[x], r = R[x];
        sz[x] = sz[l] + sz[r] + 1;
        sm[x] = sm[l] + S(val[x]) + sm[r];
    }

    void applyRev(int x) {
        if (x) swap(L[x], R[x]), rev[x] ^= 1;
    }

    void applyAdd(int x, T v) {
        if (!x) return;
        val[x] += v;
        sm[x] += S(v) * sz[x];
        (hasAsg[x] ? asg[x] : add[x]) += v;  // an add on a pending assign shifts the assigned value
    }

    void applyAssign(int x, T v) {
        if (!x) return;
        val[x] = v;
        sm[x] = S(v) * sz[x];
        hasAsg[x] = 1, asg[x] = v, add[x] = 0;
    }

    // hand x's pending tags to its children
    void push(int x) {
        if (rev[x]) applyRev(L[x]), applyRev(R[x]), rev[x] = 0;
        if (hasAsg[x]) applyAssign(L[x], asg[x]), applyAssign(R[x], asg[x]), hasAsg[x] = 0;
        else if (add[x] != T(0)) applyAdd(L[x], add[x]), applyAdd(R[x], add[x]), add[x] = 0;
    }

    // a = first k elements of t, b = the rest
    void split(int t, int k, int& a, int& b) {
        if (!t) { a = b = 0; return; }
        push(t);
        if (sz[L[t]] >= k) split(L[t], k, a, L[t]), b = t;
        else split(R[t], k - sz[L[t]] - 1, R[t], b), a = t;
        pull(t);
    }

    // a's elements, then b's
    int merge(int a, int b) {
        if (!a || !b) return a | b;
        if (pri[a] > pri[b]) {
            push(a);
            R[a] = merge(R[a], b);
            pull(a);
            return a;
        }
        push(b);
        L[b] = merge(a, L[b]);
        pull(b);
        return b;
    }

    // a = a[0..l-1], b = a[l..r], c = a[r+1..] as three trees; put them back with merge(merge(a, b), c)
    void cut(int l, int r, int& a, int& b, int& c) {
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    // the node holding a[i], with every tag on the way pushed; path (if given) gets the nodes above it
    int find(int i, vector<int>* path = nullptr) {
        int t = root;
        while (true) {
            push(t);
            int ls = sz[L[t]];
            if (i == ls) return t;
            if (path) path->push_back(t);
            if (i < ls) t = L[t];
            else i -= ls + 1, t = R[t];
        }
    }
};
