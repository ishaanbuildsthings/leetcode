// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod/template.cpp
// @operations: getAll pointAdd pointAssign pointGet rangeAddMod
// @data-structure-type: BIT
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeAddMod: log(N)
//   build: N
// @memory:
//   layout: none
//   node: tree[1*N]
//   tags: none
//   other: none
//   note: one Fenwick tree over the differences d[i] = a[i] - a[i - 1], % MOD

// Range add (% MOD), point get. All indices 0-based, ranges inclusive [l, r]; values are kept in [0, mod).
// T: int, long long, ...
template <typename T>
struct RangeAddBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a sum of two residues
    int n;
    T mod;
    vector<T> tree;  // 1-indexed, over d[i] = a[i] - a[i - 1] (% MOD)

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N) -- mod: the modulus p
    explicit RangeAddBITMod(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), mod(mod), tree(n + 1) {
        T prev = 0;
        for (int i = 1; i <= n; i++) {
            T v = norm(a[i - 1]);
            tree[i] = norm(W(tree[i]) + v - prev);
            prev = v;
            int j = i + (i & -i);
            if (j <= n) tree[j] = norm(W(tree[j]) + tree[i]);
        }
    }

    void add(int i, T v) {
        for (i++; i <= n; i += i & -i) tree[i] = norm(W(tree[i]) + v);
    }

    // O(logN) -- a[i] += v (% MOD) for i in [l, r]
    void rangeAddMod(int l, int r, T v) {
        v = norm(v);
        add(l, v);
        if (r + 1 < n) add(r + 1, norm(-W(v)));
    }

    // O(logN) -- a[i], in [0, mod)
    T pointGet(int i) const {
        W s = 0;
        for (i++; i > 0; i &= i - 1) s += tree[i];
        return norm(s);
    }

    // O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    // i + lowbit(i) once complete), then one pass of running prefix sums
    vector<T> getAll() const {
        vector<T> d(tree), out(n);
        for (int i = n; i > 0; i--) {
            int j = i + (i & -i);
            if (j <= n) d[j] = norm(W(d[j]) - d[i]);
        }
        T s = 0;
        for (int i = 0; i < n; i++) out[i] = s = norm(W(s) + d[i + 1]);
        return out;
    }

    // O(logN) -- a[i] += delta (% MOD)
    void pointAdd(int i, T delta) { rangeAddMod(i, i, delta); }

    // O(logN) -- a[i] = v (% MOD)
    void pointAssign(int i, T v) { rangeAddMod(i, i, norm(W(v) - pointGet(i))); }
};
