// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeOrApply rangeXorApply
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAndApply: log(N)
//   rangeOrApply: log(N)
//   rangeXorApply: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: val[1*N]
//   tags: AND[1*N] XOR[1*N]
//   other: none
//   note: each internal node holds one pending bit map x -> (x & AND) ^ XOR; val holds the leaf values

// Range and / or / xor + point ops, no range aggregates. All indices 0-based, ranges inclusive [l, r].
// Every update is a bit map (a, x): v -> (v & a) ^ x, and they compose into one:
//   and v -> (v, 0)    or v -> (~v, v)    xor v -> (~0, v)
// They don't commute (and then xor != xor then and), so the paths to l and r are pushed before tagging.
// T: any integral type, signed or unsigned.
template <typename T>
struct BitOpTree {
    static constexpr T ALL = T(~T(0));
    int n;
    vector<T> AND, XOR;  // internal nodes 1 .. n-1: pending map v -> (v & AND) ^ XOR
    vector<T> val;       // leaf values

    // O(N)
    explicit BitOpTree(const vector<T>& a) : n((int)a.size()), AND(a.size(), ALL), XOR(a.size(), 0), val(a) {}

    // apply (a, x) on top of whatever node y already holds
    void apply(int y, T a, T x) {
        if (y >= n) {
            val[y - n] = (val[y - n] & a) ^ x;
            return;
        }
        AND[y] &= a;
        XOR[y] = (XOR[y] & a) ^ x;
    }

    // O(logN) -- push every pending tag on leaf p's root-to-leaf path down to its children
    void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            
            if (!(AND[x] == ALL && XOR[x] == 0)) {
                apply(2 * x, AND[x], XOR[x]);
                apply(2 * x + 1, AND[x], XOR[x]);
                AND[x] = ALL, XOR[x] = 0;
            }
        }
    }
    void update(int l, int r, T a, T x) {
        l += n, r += n;
        push(l), push(r);
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) apply(l++, a, x);
            if (r & 1) apply(--r, a, x);
        }
    }

    // O(logN) -- a[i] &= v for i in [l, r]
    void rangeAndApply(int l, int r, T v) { update(l, r, v, 0); }

    // O(logN) -- a[i] |= v for i in [l, r]
    void rangeOrApply(int l, int r, T v) { update(l, r, T(~v), v); }

    // O(logN) -- a[i] ^= v for i in [l, r]
    void rangeXorApply(int l, int r, T v) { update(l, r, ALL, v); }

    // O(logN) -- a[i]: apply ancestors' maps bottom-up (deeper tags are older)
    T pointGet(int i) const {
        T v = val[i];
        for (int p = (i + n) >> 1; p; p >>= 1) v = (v & AND[p]) ^ XOR[p];
        return v;
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { push(i + n); val[i] = v; }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { push(i + n); val[i] = val[i] + delta; }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { push(i + n); if (v > val[i]) val[i] = v; }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { push(i + n); if (v < val[i]) val[i] = v; }
};
