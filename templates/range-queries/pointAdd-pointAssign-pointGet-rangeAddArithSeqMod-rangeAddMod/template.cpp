// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddArithSeqMod-rangeAddMod/template.cpp
// @operations: pointAdd pointAssign pointGet rangeAddArithSeqMod rangeAddMod
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeAddArithSeqMod: log(N)
//   rangeAddMod: log(N)
//   build: N
// @memory:
//   layout: none
//   node: c[1*N] s[1*N]
//   tags: none
//   other: none
//   note: two Fenwick trees over differences, everything mod p; a[i] = prefix(c, i) + i * prefix(s, i)

// Range add of an arithmetic sequence mod p, point get. 0-based, inclusive. T: int, long long, ...
// Values are kept in [0, mod).
template <typename T>
struct ArithSeqBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    int n;
    T mod;
    vector<T> c, s;  // a[i] = prefix(c, i) + i * prefix(s, i)  (mod p)

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N)
    explicit ArithSeqBITMod(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), mod(mod), c(n + 1), s(n + 1) {
        T prev = 0;
        for (int i = 1; i <= n; i++) {
            T v = norm(a[i - 1]);
            c[i] = norm(W(c[i]) + v - prev);
            prev = v;
            int j = i + (i & -i);
            if (j <= n) c[j] = norm(W(c[j]) + c[i]);
        }
    }

    void add(int i, T k, T step) {
        for (i++; i <= n; i += i & -i) c[i] = norm(W(c[i]) + k), s[i] = norm(W(s[i]) + step);
    }

    // O(logN) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    void rangeAddArithSeqMod(int l, int r, T start, T step) {
        T st = norm(step), k = norm(W(start) - W(l) * st);
        add(l, k, st);
        if (r + 1 < n) add(r + 1, norm(-W(k)), norm(-W(st)));
    }

    // O(logN) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(int l, int r, T v) {
        T x = norm(v), y = norm(-W(x));
        for (int i = l + 1; i <= n; i += i & -i) c[i] = norm(W(c[i]) + x);
        for (int i = r + 2; i <= n; i += i & -i) c[i] = norm(W(c[i]) + y);
    }

    // O(logN) -- a[i], in [0, mod)
    T pointGet(int i) const {
        W k = 0, coef = 0;
        for (int j = i + 1; j > 0; j &= j - 1) k += c[j], coef += s[j];
        return norm(k % mod + W(i) * (coef % mod));
    }

    // O(logN) -- a[i] += delta (mod p)
    void pointAdd(int i, T delta) { rangeAddMod(i, i, delta); }

    // O(logN) -- a[i] = v (mod p)
    void pointAssign(int i, T v) { rangeAddMod(i, i, norm(W(v) - pointGet(i))); }
};
