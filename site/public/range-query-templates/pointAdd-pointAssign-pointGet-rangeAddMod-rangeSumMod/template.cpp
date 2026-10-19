// @operations: pointAdd pointAssign pointGet rangeAddMod rangeSumMod
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeAddMod: log(N)
//   rangeSumMod: log(N)
//   build: N
// @memory:
//   layout: none
//   node: b1[1*N] b2[1*N]
//   tags: none
//   other: none
//   note: two Fenwick trees over the difference array d (d[i] = a[i] - a[i-1]): b1 over d[i], b2 over d[i] * i, all mod p

// Range add + range sum, everything mod p, with two Fenwick trees and no lazy tags. All indices 0-based, ranges
// inclusive [l, r]. a[0] + ... + a[x] = (x + 1) * sum(d[0..x]) - sum(d[i] * i for i in 0..x), d the difference array.
// Values are residues in [0, mod). T: int, long long, ...; products go through W (wide enough for two residues).
template <typename T>
struct RangeAddSumBITMod {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    int n;
    T mod;
    vector<T> b1, b2;  // 1-indexed

    T norm(W x) const { x %= mod; return T(x < 0 ? x + mod : x); }

    // O(N)
    explicit RangeAddSumBITMod(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), mod(mod), b1(n + 1), b2(n + 1) {
        T prev = 0;
        for (int i = 0; i < n; i++) {
            T v = norm(a[i]), d = norm(W(v) - prev);
            prev = v;
            b1[i + 1] = d, b2[i + 1] = norm(W(d) * i);
        }
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) b1[j] = norm(W(b1[j]) + b1[i]), b2[j] = norm(W(b2[j]) + b2[i]);
        }
    }

    void addDiff(int i, T d) {
        d = norm(d);
        T di = norm(W(d) * i);
        for (i++; i <= n; i += i & -i) b1[i] = norm(W(b1[i]) + d), b2[i] = norm(W(b2[i]) + di);
    }

    // O(logN) -- (a[0] + ... + a[x]) mod p (0 for x = -1)
    T prefix(int x) const {
        W s1 = 0, s2 = 0;
        for (int i = x + 1; i > 0; i &= i - 1) s1 += b1[i], s2 += b2[i];
        return norm(W(norm(s1)) * (x + 1) - norm(s2));
    }

    // O(logN) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(int l, int r, T v) {
        if (l > r) return;
        addDiff(l, v);
        if (r + 1 < n) addDiff(r + 1, norm(-W(v)));
    }

    // O(logN) -- (a[l] + ... + a[r]) mod p
    T rangeSumMod(int l, int r) const { return l <= r ? norm(W(prefix(r)) - prefix(l - 1)) : T(0); }

    // O(logN) -- a[i], in [0, mod)
    T pointGet(int i) const { return rangeSumMod(i, i); }

    // O(logN) -- a[i] += delta (mod p)
    void pointAdd(int i, T delta) { rangeAddMod(i, i, delta); }

    // O(logN) -- a[i] = v (mod p)
    void pointAssign(int i, T v) { rangeAddMod(i, i, norm(W(v) - pointGet(i))); }
};
