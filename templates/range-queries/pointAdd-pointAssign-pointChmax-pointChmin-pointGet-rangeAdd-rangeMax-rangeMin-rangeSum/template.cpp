// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeMax rangeMin rangeSum
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: sm[2*N] mn[2*N] mx[2*N]
//   tags: add[1*N]
//   other: none
//   note: tags live on the N internal nodes only; each holds a pending add

// Range add with range sum / min / max queries, plus point ops. All indices 0-based, ranges inclusive [l, r].
// Iterative 2N lazy tree: values on the leaves, and on each internal node a pending add, meaning "applied here, not
// yet pushed to my children". An update pushes the tags on its two boundary paths, tags the covering nodes, then
// rebuilds the two paths. A covering node at level s is a perfect subtree of 2^s leaves, so its length is 1 << s.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct AddSumMinMaxTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();
    int n, h;
    vector<S> sm;  // 2N: leaves are sm[n..2n)
    vector<T> mn, mx;
    vector<T> add;  // N: tags on internal nodes

    // O(N)
    explicit AddSumMinMaxTree(const vector<T>& a) : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())) {
        sm.assign(2 * n, 0);
        mn.assign(2 * n, INF);
        mx.assign(2 * n, NEG);
        for (int i = 0; i < n; i++) {
            sm[n + i] = a[i];
            mn[n + i] = a[i];
            mx[n + i] = a[i];
        }
        for (int x = n - 1; x > 0; x--) {
            sm[x] = sm[2 * x] + sm[2 * x + 1];
            mn[x] = std::min(mn[2 * x], mn[2 * x + 1]);
            mx[x] = std::max(mx[2 * x], mx[2 * x + 1]);
        }
        add.assign(n, 0);
    }

    // add c to every slot of node x, which covers k slots
    void applyAdd(int x, int k, T c) {
        sm[x] += S(c) * k;
        mn[x] += c;
        mx[x] += c;
        if (x < n) add[x] += c;
    }

    // push every tag on the root-to-leaf path of leaf p down one level
    void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s, k = 1 << (s - 1);
            if (add[x]) applyAdd(2 * x, k, add[x]), applyAdd(2 * x + 1, k, add[x]), add[x] = 0;
        }
    }

    // recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    void rebuild(int p) {
        for (int k = 2; p > 1; k <<= 1) {
            p >>= 1;
            sm[p] = sm[2 * p] + sm[2 * p + 1] + S(add[p]) * k;
            mn[p] = std::min(mn[2 * p], mn[2 * p + 1]) + add[p];
            mx[p] = std::max(mx[2 * p], mx[2 * p + 1]) + add[p];
        }
    }

    // O(logN) -- a[i] += v for i in [l, r]
    void rangeAdd(int l, int r, T v) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1, k = 1; i < j; i >>= 1, j >>= 1, k <<= 1) {
            if (i & 1) applyAdd(i++, k, v);
            if (j & 1) applyAdd(--j, k, v);
        }
        rebuild(l0), rebuild(r0);
    }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        if (l > r) return 0;
        l += n, r += n;
        push(l), push(r);
        S res = 0;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += sm[l++];
            if (r & 1) res += sm[--r];
        }
        return res;
    }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) {
        l += n, r += n;
        push(l), push(r);
        T res = INF;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = std::min(res, mn[l++]);
            if (r & 1) res = std::min(res, mn[--r]);
        }
        return res;
    }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) {
        l += n, r += n;
        push(l), push(r);
        T res = NEG;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = std::max(res, mx[l++]);
            if (r & 1) res = std::max(res, mx[--r]);
        }
        return res;
    }

    // O(logN) -- a[i]
    T pointGet(int i) {
        push(i + n);
        return T(sm[i + n]);
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        int p = i + n;
        push(p);
        sm[p] = v;
        mn[p] = v;
        mx[p] = v;
        rebuild(p);
    }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
