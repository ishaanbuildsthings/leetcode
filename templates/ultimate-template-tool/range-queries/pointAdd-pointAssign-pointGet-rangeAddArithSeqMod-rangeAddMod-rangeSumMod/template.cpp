// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointGet-rangeAddArithSeqMod-rangeAddMod-rangeSumMod/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointGet rangeAddArithSeqMod rangeAddMod rangeSumMod
// @data-structure-type: BIT
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeAddArithSeqMod: log(N)
//   rangeAddMod: log(N)
//   rangeSumMod: log(N)
//   build: N
// @memory:
//   layout: none
//   node: bA[1*N] bB[1*N] bC[1*N]
//   tags: none
//   other: none
//   note: prefix sums are kept as A(x) + B(x) * x + C(x) * x(x+1)/2 % MOD with A, B, C three Fenwick trees

// Range add of an arithmetic sequence (and plain range add) + range sum, all % MOD, with three Fenwick trees.
// All indices 0-based, ranges inclusive [l, r]. Values are residues in [0, mod); start / step may be negative.
// Adding c0 + c1 * i to every i in [l, r] changes the prefix sum P(x) = a[0] + ... + a[x] by
//   x in [l, r]:  c0 * (x - l + 1) + c1 * (T(x) - T(l - 1))        T(k) = k * (k + 1) / 2
//   x > r:        the whole added total
// so keep P(x) = A(x) + B(x) * x + C(x) * T(x). T(x) is an integer before reducing % MOD, so no division (or modular
// inverse of 2) is ever needed and any modulus works.
// T: int, long long, ...; products go through W (wide enough for two residues).
template <typename T>
struct ArithSeqSumBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    int n;
    T mod;
    vector<T> bA, bB, bC;  // 1-indexed

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }
    T tri(long long k) const { return norm(W(k) * (k + 1) / 2); }

    // O(N)
    explicit ArithSeqSumBITMod(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), mod(mod), bA(n + 1),
        bB(n + 1), bC(n + 1) {
        for (int i = 0; i < n; i++) bA[i + 1] = norm(a[i]);
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) bA[j] = norm(W(bA[j]) + bA[i]);
        }
    }

    void point(int i, T a, T b, T c) {
        for (i++; i <= n; i += i & -i) bA[i] = norm(W(bA[i]) + a), bB[i] = norm(W(bB[i]) + b),
            bC[i] = norm(W(bC[i]) + c);
    }

    // O(logN) -- (a[0] + ... + a[x]) % MOD (0 for x = -1)
    T prefix(int x) const {
        W sa = 0, sb = 0, sc = 0;
        for (int i = x + 1; i > 0; i &= i - 1) sa += bA[i], sb += bB[i], sc += bC[i];
        return norm(W(norm(sa)) + W(norm(sb)) * x % mod + W(norm(sc)) * tri(x) % mod);
    }

    // O(logN) -- a[l + j] += start + j * step (% MOD) for j in [0, r - l]; needs 0 <= l <= r < n, else throws
    // out_of_range
    void rangeAddArithSeqMod(int l, int r, T start, T step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddArithSeqMod: needs 0 <= l <= r < n");
        if (l > r) return;
        T c1 = norm(step), c0 = norm(W(start) - W(c1) * l);  // adding c0 + c1 * i at index i
        T a = norm(W(c0) * norm(1 - l) - W(c1) * tri(l - 1));
        point(l, a, c0, c1);
        if (r + 1 < n) {
            T total = norm(W(c0) * (r - l + 1) + W(c1) * norm(W(tri(r)) - tri(l - 1)));
            point(r + 1, norm(W(total) - a), norm(-W(c0)), norm(-W(c1)));
        }
    }

    // O(logN) -- a[i] += v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAddMod(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddMod: needs 0 <= l <= r < n");
        rangeAddArithSeqMod(l, r, v, 0);
    }

    // O(logN) -- (a[l] + ... + a[r]) % MOD; needs 0 <= l <= r < n, else throws out_of_range
    T rangeSumMod(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSumMod: needs 0 <= l <= r < n");
        return l <= r ? norm(W(prefix(r)) - prefix(l - 1)) : T(0);
    }

    // O(logN) -- a[i], in [0, mod); needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return rangeSumMod(i, i);
    }

    // O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    // i + lowbit(i) once complete), then one pass of running prefix sums
    vector<T> getAll() const {
        vector<T> A(bA), B(bB), C(bC);
        for (int i = n; i > 0; i--) {
            int j = i + (i & -i);
            if (j <= n) A[j] = norm(W(A[j]) - A[i]), B[j] = norm(W(B[j]) - B[i]), C[j] = norm(W(C[j]) - C[i]);
        }
        vector<T> out(n);
        T sa = 0, sb = 0, sc = 0, prev = 0;
        for (int x = 0; x < n; x++) {
            sa = norm(W(sa) + A[x + 1]), sb = norm(W(sb) + B[x + 1]), sc = norm(W(sc) + C[x + 1]);
            T p = norm(W(sa) + W(sb) * x % mod + W(sc) * tri(x) % mod);
            out[x] = norm(W(p) - prev), prev = p;
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
