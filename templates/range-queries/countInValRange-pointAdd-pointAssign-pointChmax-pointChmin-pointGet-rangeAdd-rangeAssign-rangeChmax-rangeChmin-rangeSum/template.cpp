// @operations: countInValRange pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeSum
// @data-structure-type: sqrt
// @complexities:
//   countInValRange: sqrt(N)*log(N)
//   pointAdd: sqrt(N)
//   pointAssign: sqrt(N)
//   pointChmax: sqrt(N)
//   pointChmin: sqrt(N)
//   pointGet: 1
//   rangeAdd: sqrt(N)*log(N)
//   rangeAssign: sqrt(N)*log(N)
//   rangeChmax: sqrt(N)*log(N)
//   rangeChmin: sqrt(N)*log(N)
//   rangeSum: sqrt(N)*log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: sortedBeforeTags[1*N] pfSum[1*N]
//   tags: lazyAdd[1*sqrt(N)] lazyChmin[1*sqrt(N)] lazyChmax[1*sqrt(N)]
//   other: valsBeforeTags[1*N] blockEnd[1*sqrt(N)]
//   note: sqrt(N) blocks, each with a sorted copy and prefix sums; describes SqrtBlocks_PERFORMANT
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/other-range-queries/rangeChmin-Chmax-Add-Assign-Sum-CountValRange-SqrtDecomp-RootNLogN.cpp

// Sqrt decomposition: range chmin / chmax / add / assign, range sum, count of values in [low, high] over a range,
// point ops. All indices 0-based, ranges inclusive. Each block keeps its raw values, a sorted copy, prefix sums of
// that copy, and one pending tag "v -> clamp(v + add, floor, ceil)" (floor == ceil means assigned). A tag is
// monotone, so it keeps the sorted copy sorted: a whole block answers with a few binary searches, and pushing a
// tag rewrites the sorted copy in place without re-sorting. A partial block is pushed, edited, and re-sorted.
// Build O(N log N); range ops O(sqrt N log N); point assign O(sqrt N); pointGet O(1).
// T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct SqrtBlocks {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;  // for stored-space bounds low - add, high - add
    static constexpr T INF = numeric_limits<T>::max(), NINF = numeric_limits<T>::lowest();
    int n, B, nb;
    vector<T> vals;                // values before their block's tag
    vector<vector<T>> srt;         // srt[b] = sorted vals of block b (before tag)
    vector<vector<S>> pf;          // pf[b][k] = srt[b][0] + ... + srt[b][k]
    vector<T> lazyAdd, lazyChmin, lazyChmax;  // value = clamp(stored + add, lazyChmax, lazyChmin)

    // O(N log N)
    explicit SqrtBlocks(const vector<T>& a) : n((int)a.size()), vals(a) {
        B = max(1, (int)sqrtl(n));
        while ((long long)(B + 1) * (B + 1) <= n) B++;
        nb = (n + B - 1) / B;
        srt.resize(nb), pf.resize(nb);
        lazyAdd.assign(nb, 0), lazyChmin.assign(nb, INF), lazyChmax.assign(nb, NINF);
        for (int b = 0; b < nb; b++) refresh(b);
    }

    int lo(int b) const { return b * B; }
    int hi(int b) const { return min(n, (b + 1) * B) - 1; }
    bool tagged(int b) const { return lazyAdd[b] != 0 || lazyChmin[b] != INF || lazyChmax[b] != NINF; }

    T applyTag(int b, T v) const {
        v += lazyAdd[b];
        if (v < lazyChmax[b]) return lazyChmax[b];
        if (v > lazyChmin[b]) return lazyChmin[b];
        return v;
    }

    void buildPf(int b) {
        pf[b].resize(srt[b].size());
        S run = 0;
        for (size_t k = 0; k < srt[b].size(); k++) pf[b][k] = run += srt[b][k];
    }

    // O(sqrt N log N) -- re-sort one block after its raw values were edited directly
    void refresh(int b) {
        srt[b].assign(vals.begin() + lo(b), vals.begin() + hi(b) + 1);
        sort(srt[b].begin(), srt[b].end());
        buildPf(b);
    }

    // O(sqrt N) -- bake the tag into the block and clear it; the sorted copy stays sorted
    void push(int b) {
        if (!tagged(b)) return;
        for (int i = lo(b); i <= hi(b); i++) vals[i] = applyTag(b, vals[i]);
        for (T& v : srt[b]) v = applyTag(b, v);
        buildPf(b);
        lazyAdd[b] = 0, lazyChmin[b] = INF, lazyChmax[b] = NINF;
    }

    // whole blocks take tagOp; partial blocks are pushed, edited with valOp, then re-sorted
    template <class TagOp, class ValOp>
    void rangeApply(int l, int r, const TagOp& tagOp, const ValOp& valOp) {
        if (l > r) return;
        for (int b = l / B, br = r / B; b <= br; b++) {
            if (l <= lo(b) && hi(b) <= r) { tagOp(b); continue; }
            push(b);
            for (int i = max(l, lo(b)); i <= min(r, hi(b)); i++) vals[i] = valOp(vals[i]);
            refresh(b);
        }
    }

    // O(sqrt N log N) -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(int l, int r, T x) {
        rangeApply(l, r, [&](int b) {
            lazyChmin[b] = min(lazyChmin[b], x);  // drop the ceiling
            lazyChmax[b] = min(lazyChmax[b], x);  // and the floor, if the ceiling went below it
        }, [&](T v) { return min(v, x); });
    }

    // O(sqrt N log N) -- a[i] = max(a[i], x) for i in [l, r]
    void rangeChmax(int l, int r, T x) {
        rangeApply(l, r, [&](int b) {
            lazyChmax[b] = max(lazyChmax[b], x);  // raise the floor
            lazyChmin[b] = max(lazyChmin[b], x);  // and the ceiling, if the floor went above it
        }, [&](T v) { return max(v, x); });
    }

    // O(sqrt N log N) -- a[i] = x for i in [l, r]
    void rangeAssign(int l, int r, T x) {
        rangeApply(l, r, [&](int b) { lazyAdd[b] = 0, lazyChmin[b] = lazyChmax[b] = x; }, [&](T) { return x; });
    }

    // O(sqrt N log N) -- a[i] += x for i in [l, r]
    void rangeAdd(int l, int r, T x) {
        rangeApply(l, r, [&](int b) {
            lazyAdd[b] += x;
            if (lazyChmin[b] != INF) lazyChmin[b] += x;
            if (lazyChmax[b] != NINF) lazyChmax[b] += x;
        }, [&](T v) { return v + x; });
    }

    // whole block b: # of stored values below the floor / above the ceiling (they read as floor / ceil)
    pair<int, int> clampedCounts(int b) const {
        const vector<T>& s = srt[b];
        int lt = lazyChmax[b] == NINF ? 0 : int(lower_bound(s.begin(), s.end(), lazyChmax[b] - lazyAdd[b]) - s.begin());
        int gt = lazyChmin[b] == INF ? 0 : int(s.end() - upper_bound(s.begin(), s.end(), lazyChmin[b] - lazyAdd[b]));
        return {lt, gt};
    }

    // O(sqrt N log N) -- how many i in [l, r] have low <= a[i] <= high
    int countInValRange(int l, int r, T low, T high) const {
        if (l > r || high < low) return 0;
        int res = 0;
        for (int b = l / B, br = r / B; b <= br; b++) {
            if (!(l <= lo(b) && hi(b) <= r)) {
                for (int i = max(l, lo(b)); i <= min(r, hi(b)); i++) {
                    T v = applyTag(b, vals[i]);
                    res += low <= v && v <= high;
                }
                continue;
            }
            const vector<T>& s = srt[b];
            int sz = (int)s.size();
            if (lazyChmin[b] == lazyChmax[b]) {  // assigned
                if (low <= lazyChmin[b] && lazyChmin[b] <= high) res += sz;
                continue;
            }
            auto [lt, gt] = clampedCounts(b);
            if (lt && low <= lazyChmax[b] && lazyChmax[b] <= high) res += lt;
            if (gt && low <= lazyChmin[b] && lazyChmin[b] <= high) res += gt;
            // the untouched middle reads stored + add: count stored values in [low - add, high - add], in W so it can't overflow
            W add = lazyAdd[b];
            auto first = s.begin() + lt, last = s.begin() + (sz - gt);
            auto ub = upper_bound(first, last, W(high) - add, [](W x, T v) { return x < v; });
            auto lb = lower_bound(first, last, W(low) - add, [](T v, W x) { return v < x; });
            res += int(max(ub - lb, ptrdiff_t(0)));
        }
        return res;
    }

    // O(sqrt N log N) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) const {
        if (l > r) return 0;
        S res = 0;
        for (int b = l / B, br = r / B; b <= br; b++) {
            if (!(l <= lo(b) && hi(b) <= r)) {
                for (int i = max(l, lo(b)); i <= min(r, hi(b)); i++) res += applyTag(b, vals[i]);
                continue;
            }
            int sz = (int)srt[b].size();
            if (lazyChmin[b] == lazyChmax[b]) { res += S(lazyChmin[b]) * sz; continue; }
            auto [lt, gt] = clampedCounts(b);
            if (lt) res += S(lazyChmax[b]) * lt;
            if (gt) res += S(lazyChmin[b]) * gt;
            int mid = sz - lt - gt;
            if (mid > 0) res += pf[b][lt + mid - 1] - (lt ? pf[b][lt - 1] : S(0)) + S(lazyAdd[b]) * mid;
        }
        return res;
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return applyTag(i / B, vals[i]); }

    // O(sqrt N) -- a[i] = v; one value moves inside the sorted copy, so no re-sort
    void pointAssign(int i, T v) {
        int b = i / B;
        push(b);
        T old = vals[i];
        if (old == v) return;
        vals[i] = v;
        vector<T>& s = srt[b];
        s.erase(lower_bound(s.begin(), s.end(), old));
        s.insert(upper_bound(s.begin(), s.end(), v), v);
        buildPf(b);
    }

    // a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // a[i] += delta
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }
};
