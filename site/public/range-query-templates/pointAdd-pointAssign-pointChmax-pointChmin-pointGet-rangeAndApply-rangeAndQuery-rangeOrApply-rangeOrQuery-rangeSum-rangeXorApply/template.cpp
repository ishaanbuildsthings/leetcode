// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeOrApply rangeOrQuery rangeSum rangeXorApply
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(N)*log(U)
//   pointAssign: log(N)*log(U)
//   pointChmax: log(N)*log(U)
//   pointChmin: log(N)*log(U)
//   pointGet: log(N)*log(U)
//   rangeAndApply: log(N)*log(U)
//   rangeAndQuery: log(N)*log(U)
//   rangeOrApply: log(N)*log(U)
//   rangeOrQuery: log(N)*log(U)
//   rangeSum: log(N)*log(U)
//   rangeXorApply: log(N)*log(U)
//   build: N*log(U)
// @memory:
//   layout: 2n-iterative
//   node: cnt[2*N*log(U)]
//   tags: andTag[1*N] xorTag[1*N]
//   other: none
//   note: cnt keeps, per node and per bit, how many values below have that bit set (bits = log U, 20 by default); tags live on internal nodes only

// Range and= / or= / xor= with range sum / and / or queries, plus point ops. All indices 0-based, ranges inclusive.
// Values live in [0, 2^bits). Each node counts, for every bit, how many of its values have that bit set. Every
// update is v -> (v & a) ^ x (and X = (X, 0), or X = (~X, X), xor X = (FULL, X)), and per bit that is "keep",
// "force 0", "force 1" or "flip": force sets the count to 0 or the node length, flip turns c into length - c.
// So every update is an ordinary lazy tag, a true O(log N * bits) with no amortization (unlike bitwise beats,
// which cannot apply xor to a node whose values disagree on a bit). Sum = sum over bits of count * 2^bit.
// Iterative 2N lazy tree; a covering node at level s is a perfect subtree of 2^s leaves.
// T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct BitCountTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, h, bits;
    T full;
    vector<int> cnt;          // cnt[x * bits + b] = # of values under node x with bit b set (2N nodes)
    vector<T> andTag, xorTag; // N: tags on internal nodes

    // O(N * bits)
    explicit BitCountTree(const vector<T>& a, int bits = 20)
        : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())), bits(bits), full(T((T(1) << bits) - 1)),
          cnt(2 * a.size() * bits), andTag(a.size(), full), xorTag(a.size(), 0) {
        for (int i = 0; i < n; i++)
            for (int b = 0; b < bits; b++) cnt[(n + i) * bits + b] = a[i] >> b & 1;
        for (int x = n - 1; x > 0; x--)
            for (int b = 0; b < bits; b++) cnt[x * bits + b] = cnt[2 * x * bits + b] + cnt[(2 * x + 1) * bits + b];
    }

    // v -> (v & a) ^ xr on node x, which covers k slots
    void apply(int x, int k, T a, T xr) {
        int* c = &cnt[x * bits];
        for (int b = 0; b < bits; b++) {
            if (!(a >> b & 1)) c[b] = 0;
            if (xr >> b & 1) c[b] = k - c[b];
        }
        if (x < n) andTag[x] &= a, xorTag[x] = (xorTag[x] & a) ^ xr;
    }

    void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s;
            if (andTag[x] != full || xorTag[x]) {
                int k = 1 << (s - 1);
                apply(2 * x, k, andTag[x], xorTag[x]), apply(2 * x + 1, k, andTag[x], xorTag[x]);
                andTag[x] = full, xorTag[x] = 0;
            }
        }
    }

    void rebuild(int p) {
        for (int k = 2; p > 1; k <<= 1) {
            p >>= 1;
            for (int b = 0; b < bits; b++) {
                int v = cnt[2 * p * bits + b] + cnt[(2 * p + 1) * bits + b];
                if (!(andTag[p] >> b & 1)) v = 0;
                if (xorTag[p] >> b & 1) v = k - v;
                cnt[p * bits + b] = v;
            }
        }
    }

    void update(int l, int r, T a, T xr) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1, k = 1; i < j; i >>= 1, j >>= 1, k <<= 1) {
            if (i & 1) apply(i++, k, a, xr);
            if (j & 1) apply(--j, k, a, xr);
        }
        rebuild(l0), rebuild(r0);
    }

    // the canonical nodes of [l, r] with their lengths, after pushing the two boundary paths
    vector<pair<int, int>> nodes(int l, int r) {
        vector<pair<int, int>> out;
        l += n, r += n;
        push(l), push(r);
        for (int k = 1, rr = r + 1; l < rr; l >>= 1, rr >>= 1, k <<= 1) {
            if (l & 1) out.push_back({l++, k});
            if (rr & 1) out.push_back({--rr, k});
        }
        return out;
    }

    // O(logN * bits) -- a[i] &= X for i in [l, r]
    void rangeAndApply(int l, int r, T X) { update(l, r, X & full, 0); }

    // O(logN * bits) -- a[i] |= X for i in [l, r]
    void rangeOrApply(int l, int r, T X) { update(l, r, ~X & full, X & full); }

    // O(logN * bits) -- a[i] ^= X for i in [l, r]
    void rangeXorApply(int l, int r, T X) { update(l, r, full, X & full); }

    // O(logN * bits) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        if (l > r) return 0;
        S res = 0;
        for (auto [x, k] : nodes(l, r))
            for (int b = 0; b < bits; b++) res += S(cnt[x * bits + b]) << b;
        return res;
    }

    // O(logN * bits) -- a[l] & ... & a[r]
    T rangeAndQuery(int l, int r) {
        T res = full;
        for (auto [x, k] : nodes(l, r))
            for (int b = 0; b < bits; b++)
                if (cnt[x * bits + b] != k) res &= ~(T(1) << b);
        return res;
    }

    // O(logN * bits) -- a[l] | ... | a[r]
    T rangeOrQuery(int l, int r) {
        T res = 0;
        for (auto [x, k] : nodes(l, r))
            for (int b = 0; b < bits; b++)
                if (cnt[x * bits + b]) res |= T(1) << b;
        return res;
    }

    // O(logN * bits) -- a[i]
    T pointGet(int i) {
        int p = i + n;
        push(p);
        T v = 0;
        for (int b = 0; b < bits; b++) v |= T(cnt[p * bits + b]) << b;
        return v;
    }

    // O(logN * bits) -- a[i] = v & FULL
    void pointAssign(int i, T v) {
        int p = i + n;
        push(p);
        v &= full;
        for (int b = 0; b < bits; b++) cnt[p * bits + b] = v >> b & 1;
        rebuild(p);
    }

    // O(logN * bits) -- a[i] = (a[i] + delta) & FULL
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logN * bits) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logN * bits) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
