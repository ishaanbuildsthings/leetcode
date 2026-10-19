// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeSum
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeAssign: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: pow2-iterative
//   node: sm[4*N]
//   tags: add[2*N] asg[2*N] hasAsg[2*N]
//   other: none
//   note: arrays are 2*size, size the next power of two >= n; a node's tag is either "assign v" (later adds fold into v) or "add d"
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/lazy/RangeAddRangeAssignRangeSum.cpp

// Range add + range assign + range sum (no mod), plus point ops. All indices 0-based, ranges inclusive [l, r].
// Iterative lazy tree over a power-of-two layout. Tags do not commute (add then assign != assign then add), so an
// update first pushes every tag on the two boundary root-to-leaf paths, then tags the O(log N) covering nodes, then
// recomputes the boundary paths bottom-up. A tag is either "assign v" or "add d"; an add landing on an assign tag
// just shifts v.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct AddAssignSumTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, size, H;
    vector<S> sm;
    vector<T> add, asg;      // tags, internal nodes only
    vector<char> hasAsg;

    // O(N)
    explicit AddAssignSumTree(const vector<T>& a) : n((int)a.size()), size(1), H(0) {
        while (size < max(n, 1)) size <<= 1, H++;
        sm.assign(2 * size, 0), add.assign(size, 0), asg.assign(size, 0), hasAsg.assign(size, 0);
        for (int i = 0; i < n; i++) sm[size + i] = a[i];
        for (int x = size - 1; x > 0; x--) sm[x] = sm[2 * x] + sm[2 * x + 1];
    }

    // node x covers `len` slots
    void apply(int x, int len, bool isAsg, T v) {
        if (isAsg) {
            sm[x] = S(v) * len;
            if (x < size) hasAsg[x] = 1, asg[x] = v, add[x] = 0;
        } else {
            sm[x] += S(v) * len;
            if (x < size) (hasAsg[x] ? asg[x] : add[x]) += v;
        }
    }

    // push node x's tag into its two children, which cover childLen slots each
    void push(int x, int childLen) {
        if (hasAsg[x]) {
            apply(2 * x, childLen, true, asg[x]), apply(2 * x + 1, childLen, true, asg[x]);
            hasAsg[x] = 0;
        } else if (add[x]) {
            apply(2 * x, childLen, false, add[x]), apply(2 * x + 1, childLen, false, add[x]);
            add[x] = 0;
        }
    }

    void pushToRoot(int p) {
        for (int s = H; s > 0; s--) push(p >> s, 1 << (s - 1));
    }

    // a node that got tagged during the update keeps its own tag's effect
    void recomputeToRoot(int p) {
        int len = 2;
        for (p >>= 1; p; p >>= 1, len <<= 1)
            sm[p] = hasAsg[p] ? S(asg[p]) * len : sm[2 * p] + sm[2 * p + 1] + S(add[p]) * len;
    }

    void update(int l, int r, bool isAsg, T v) {
        if (l > r) return;
        int l0 = l + size, r0 = r + size;
        pushToRoot(l0), pushToRoot(r0);
        for (int lo = l0, hi = r0 + 1, len = 1; lo < hi; lo >>= 1, hi >>= 1, len <<= 1) {
            if (lo & 1) apply(lo++, len, isAsg, v);
            if (hi & 1) apply(--hi, len, isAsg, v);
        }
        recomputeToRoot(l0), recomputeToRoot(r0);
    }

    // O(logN) -- a[i] += v for i in [l, r]
    void rangeAdd(int l, int r, T v) { update(l, r, false, v); }

    // O(logN) -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) { update(l, r, true, v); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        if (l > r) return 0;
        l += size, r += size;
        pushToRoot(l), pushToRoot(r);
        S res = 0;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res += sm[l++];
            if (r & 1) res += sm[--r];
        }
        return res;
    }

    // O(logN) -- a[i]
    T pointGet(int i) {
        pushToRoot(i + size);
        return T(sm[i + size]);
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { update(i, i, true, v); }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { update(i, i, false, delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
