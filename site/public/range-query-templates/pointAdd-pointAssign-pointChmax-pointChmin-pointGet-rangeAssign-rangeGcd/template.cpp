// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeGcd/template.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeGcd
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(N)*log(U) ?
//   pointAssign: log(N)*log(U) ?
//   pointChmax: log(N)*log(U) ?
//   pointChmin: log(N)*log(U) ?
//   pointGet: log(N)
//   rangeAssign: log(N)*log(U) ?
//   rangeGcd: log(N)+log(U) ?
//   build: N*log(U) ?
// @memory:
//   layout: 2n-iterative
//   node: t[2*N]
//   tags: asg[1*N] hasAsg[1*N]
//   other: none
//   note: leaves t[n..2n) hold the values, internal nodes the gcd of |values| below; tags live on internal nodes only

// Range assign + range gcd, plus point ops. All indices 0-based, ranges inclusive [l, r]. Gcds are of |values|.
// Iterative 2N lazy tree: leaves hold the values, internal nodes the gcd below them, and a pending assign on each
// internal node ("applied here, not yet pushed"). A node assigned v has gcd |v|, so assign is an ordinary lazy tag.
// Much lighter than the gcd beats tree when you only need assign. T: int, long long, ...
template <typename T>
struct AssignGcdTree {
    int n, h;
    vector<T> t, asg;  // t: 2N (leaves = values, internal = gcd); asg: N tags on internal nodes
    vector<char> hasAsg;

    static T absT(T x) { return x < 0 ? -x : x; }

    // O(N logU)
    explicit AssignGcdTree(const vector<T>& a)
        : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())), t(2 * a.size()), asg(a.size()), hasAsg(a.size()) {
        for (int i = 0; i < n; i++) t[n + i] = a[i];
        for (int x = n - 1; x > 0; x--) t[x] = std::gcd(absT(t[2 * x]), absT(t[2 * x + 1]));
    }

    void apply(int x, T v) {
        if (x < n) t[x] = absT(v), hasAsg[x] = 1, asg[x] = v;
        else t[x] = v;
    }

    void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s;
            if (hasAsg[x]) apply(2 * x, asg[x]), apply(2 * x + 1, asg[x]), hasAsg[x] = 0;
        }
    }

    void rebuild(int p) {
        for (p >>= 1; p; p >>= 1) t[p] = hasAsg[p] ? absT(asg[p]) : std::gcd(absT(t[2 * p]), absT(t[2 * p + 1]));
    }

    // O(logN logU) -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1; i < j; i >>= 1, j >>= 1) {
            if (i & 1) apply(i++, v);
            if (j & 1) apply(--j, v);
        }
        rebuild(l0), rebuild(r0);
    }

    // O(logN + logU) -- gcd of |a[l]|, ..., |a[r]| (the gcds telescope, so the fold costs one log U)
    T rangeGcd(int l, int r) {
        if (l > r) return 0;
        l += n, r += n;
        push(l), push(r);
        T res = 0;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = std::gcd(res, absT(t[l++]));
            if (r & 1) res = std::gcd(res, absT(t[--r]));
        }
        return res;
    }

    // O(logN) -- a[i]
    T pointGet(int i) {
        push(i + n);
        return t[i + n];
    }

    // O(logN logU) -- a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // O(logN logU) -- a[i] += delta
    void pointAdd(int i, T delta) { rangeAssign(i, i, pointGet(i) + delta); }

    // O(logN logU) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) rangeAssign(i, i, v); }

    // O(logN logU) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) rangeAssign(i, i, v); }
};
