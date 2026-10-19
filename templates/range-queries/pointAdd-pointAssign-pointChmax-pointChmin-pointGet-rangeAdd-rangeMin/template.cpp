// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeMin
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeMin: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: mn[2*N]
//   tags: add[1*N]
//   other: none
//   note: tags live on the N internal nodes only; each holds one clamp tag x -> x + add

// Range add with range min queries, plus point ops. All indices 0-based, ranges inclusive [l, r].
// Iterative 2N lazy tree: values on the leaves, a tag on each internal node meaning "applied here, not yet pushed
// to my children". The tag is the map x -> x + add; these maps compose into the same form, and each is
// monotone, so it sends a node's min / max straight to the new min / max.
// An update pushes the tags on its two boundary paths, tags the covering nodes, then rebuilds the two paths.
// T: int, long long, ...; the INF / NEG sentinels in the tags are never shifted.
template <typename T>
struct AddMinTree {
    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();
    int n, h;
    vector<T> mn;  // 2N: leaves are tree[n..2n)
    vector<T> add;  // N: tags on internal nodes

    // O(N)
    explicit AddMinTree(const vector<T>& a) : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())) {
        mn.assign(2 * n, INF);
        for (int i = 0; i < n; i++) mn[n + i] = a[i];
        for (int x = n - 1; x > 0; x--) mn[x] = std::min(mn[2 * x], mn[2 * x + 1]);
        add.assign(n, 0);
    }

    static T clampValue(T v, T c) { v += c; return v; }

    // apply the map to node x: to its values now, and (if internal) on top of its pending tag
    void apply(int x, T c) {
        mn[x] = clampValue(mn[x], c);
        if (x < n) {
            add[x] += c;
        }
    }

    // push every tag on the root-to-leaf path of leaf p down one level
    void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s;
            if (add[x] != 0) {
                apply(2 * x, add[x]), apply(2 * x + 1, add[x]);
                add[x] = 0;
            }
        }
    }

    // recompute the ancestors of leaf p; each keeps the effect of its own pending tag
    void rebuild(int p) {
        while (p > 1) {
            p >>= 1;
            mn[p] = clampValue(std::min(mn[2 * p], mn[2 * p + 1]), add[p]);
        }
    }

    void update(int l, int r, T c) {
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1; i < j; i >>= 1, j >>= 1) {
            if (i & 1) apply(i++, c);
            if (j & 1) apply(--j, c);
        }
        rebuild(l0), rebuild(r0);
    }

    // O(logN) -- a[i] += v for i in [l, r]
    void rangeAdd(int l, int r, T v) { update(l, r, v); }

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

    // O(logN) -- a[i]
    T pointGet(int i) {
        push(i + n);
        return mn[i + n];
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {
        int p = i + n;
        push(p);
        mn[p] = v;
        rebuild(p);
    }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
