// @operations: pointAdd pointAssign pointGet rangeAddArithSeqMod rangeAddMod rangeSumMod
// @data-structure-type: BIT
// @complexities:
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
//   note: prefix sums are kept as A(x) + B(x) * x + C(x) * x(x+1)/2 mod p with A, B, C three Fenwick trees

// Range add of an arithmetic sequence (and plain range add) + range sum, all mod p, with three Fenwick trees.
// All indices 0-based, ranges inclusive [l, r]. Values are residues in [0, mod); start / step may be negative.
// Adding c0 + c1 * i to every i in [l, r] changes the prefix sum P(x) = a[0] + ... + a[x] by
//   x in [l, r]:  c0 * (x - l + 1) + c1 * (T(x) - T(l - 1))        T(k) = k * (k + 1) / 2
//   x > r:        the whole added total
// so keep P(x) = A(x) + B(x) * x + C(x) * T(x). T(x) is an integer before reducing mod p, so no division (or
// modular inverse of 2) is ever needed and any modulus works.
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
    explicit ArithSeqSumBITMod(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), mod(mod), bA(n + 1), bB(n + 1), bC(n + 1) {
        for (int i = 0; i < n; i++) bA[i + 1] = norm(a[i]);
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) bA[j] = norm(W(bA[j]) + bA[i]);
        }
    }

    void point(int i, T a, T b, T c) {
        for (i++; i <= n; i += i & -i) bA[i] = norm(W(bA[i]) + a), bB[i] = norm(W(bB[i]) + b), bC[i] = norm(W(bC[i]) + c);
    }

    // O(logN) -- (a[0] + ... + a[x]) mod p (0 for x = -1)
    T prefix(int x) const {
        W sa = 0, sb = 0, sc = 0;
        for (int i = x + 1; i > 0; i &= i - 1) sa += bA[i], sb += bB[i], sc += bC[i];
        return norm(W(norm(sa)) + W(norm(sb)) * x % mod + W(norm(sc)) * tri(x) % mod);
    }

    // O(logN) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    void rangeAddArithSeqMod(int l, int r, T start, T step) {
        if (l > r) return;
        T c1 = norm(step), c0 = norm(W(start) - W(c1) * l);  // adding c0 + c1 * i at index i
        T a = norm(W(c0) * norm(1 - l) - W(c1) * tri(l - 1));
        point(l, a, c0, c1);
        if (r + 1 < n) {
            T total = norm(W(c0) * (r - l + 1) + W(c1) * norm(W(tri(r)) - tri(l - 1)));
            point(r + 1, norm(W(total) - a), norm(-W(c0)), norm(-W(c1)));
        }
    }

    // O(logN) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(int l, int r, T v) { rangeAddArithSeqMod(l, r, v, 0); }

    // O(logN) -- (a[l] + ... + a[r]) mod p
    T rangeSumMod(int l, int r) const { return l <= r ? norm(W(prefix(r)) - prefix(l - 1)) : T(0); }

    // O(logN) -- a[i], in [0, mod)
    T pointGet(int i) const { return rangeSumMod(i, i); }

    // O(logN) -- a[i] += delta (mod p)
    void pointAdd(int i, T delta) { rangeAddMod(i, i, delta); }

    // O(logN) -- a[i] = v (mod p)
    void pointAssign(int i, T v) { rangeAddMod(i, i, norm(W(v) - pointGet(i))); }
};
