// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointGet-rangeAddArithSeqMod-rangeAddMod/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointGet rangeAddArithSeqMod rangeAddMod
// @data-structure-type: BIT
// @complexities:
//   getAll: N
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
//   note: two Fenwick trees over differences, everything % MOD; a[i] = prefix(c, i) + i * prefix(s, i)

// Range add of an arithmetic sequence % MOD, point get. 0-based, inclusive. T: int, long long, ...
// Values are kept in [0, mod).
template <typename T>
struct ArithSeqBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // wide enough for a product of two residues
    int n;
    T mod;
    vector<T> c, s;  // a[i] = prefix(c, i) + i * prefix(s, i)  (% MOD)

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

    // O(logN) -- a[l + j] += start + j * step (% MOD) for j in [0, r - l]; needs 0 <= l <= r < n, else throws
    // out_of_range
    void rangeAddArithSeqMod(int l, int r, T start, T step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddArithSeqMod: needs 0 <= l <= r < n");
        T st = norm(step), k = norm(W(start) - W(l) * st);
        add(l, k, st);
        if (r + 1 < n) add(r + 1, norm(-W(k)), norm(-W(st)));
    }

    // O(logN) -- a[i] += v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAddMod(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddMod: needs 0 <= l <= r < n");
        T x = norm(v), y = norm(-W(x));
        for (int i = l + 1; i <= n; i += i & -i) c[i] = norm(W(c[i]) + x);
        for (int i = r + 2; i <= n; i += i & -i) c[i] = norm(W(c[i]) + y);
    }

    // O(logN) -- a[i], in [0, mod); needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        W k = 0, coef = 0;
        for (int j = i + 1; j > 0; j &= j - 1) k += c[j], coef += s[j];
        return norm(k % mod + W(i) * (coef % mod));
    }

    // O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    // i + lowbit(i) once complete), then one pass of running prefix sums
    vector<T> getAll() const {
        vector<T> C(c), D(s), out(n);
        for (int i = n; i > 0; i--) {
            int j = i + (i & -i);
            if (j <= n) C[j] = norm(W(C[j]) - C[i]), D[j] = norm(W(D[j]) - D[i]);
        }
        T k = 0, coef = 0;
        for (int i = 0; i < n; i++) {
            k = norm(W(k) + C[i + 1]), coef = norm(W(coef) + D[i + 1]);
            out[i] = norm(W(k) + W(i) * coef);
        }
        return out;
    }

    // O(logN) -- a[i] += delta (% MOD); needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAddMod(i, i, delta);
    }

    // O(logN) -- a[i] = v (% MOD); needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        rangeAddMod(i, i, norm(W(v) - pointGet(i)));
    }
};
