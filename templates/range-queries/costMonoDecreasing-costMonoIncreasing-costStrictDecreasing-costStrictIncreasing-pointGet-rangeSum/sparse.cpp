// @operations: costMonoDecreasing costMonoIncreasing costStrictDecreasing costStrictIncreasing pointGet rangeSum
// @data-structure-type: sparse-table
// @complexities:
//   costMonoDecreasing: log(N)
//   costMonoIncreasing: log(N)
//   costStrictDecreasing: log(N)
//   costStrictIncreasing: log(N)
//   pointGet: log(N)
//   rangeSum: log(N)
//   build: N*log(N)
// @memory:
//   layout: sparse
//   node: sp[8*N*log(N)]
//   tags: none
//   other: idx[1*N] vals[1*N] starts[8*N] v[8*N] w[8*N] W[8*N] B[8*N] suff[8*N]
//   note: built from N (index, value) points over any index range [lo, hi], every other index 0; a view is the array cut into pieces (each point, each gap of zeros), with a sparse table of argmax and next-greater sums over the pieces; four views: a, a mirrored, a[i] - i, and a mirrored minus its index (decreasing costs are increasing costs on the mirror, strict costs subtract the index); each view is built on its first query. C++ sums wrap mod 2^64 (exact whenever the answer fits in long long)

// costMonoIncreasing (min +1 increments to make a[l..r] non-decreasing) over an array given as pieces: piece k
// starts at index starts[k], spans w[k] indices, and holds v[k] + slope[k] * t at its t-th index (slope 0 or -1, so
// a piece's own max is its first value). cost = sum of prefix maxes - sum of values. The prefix max is flat inside a
// piece, so sum over pieces of w * max(carry, max of v so far): a sparse table of argmax finds the first piece above
// the carry and the max, and suff[k] = sum over j >= k of w_j * max(v[k..j]) (by next-greater) does the rest.
// Sums are unsigned 64-bit and wrap, so results are exact whenever they fit in long long.
struct PieceCost {
    using W = unsigned long long;
    int n;
    vector<long long> starts, v, w;
    vector<int> slope;
    vector<W> Wp, Bp, suff;  // prefix weights, prefix value sums
    vector<vector<int>> sp;  // sp[j][k] = index of the (leftmost) max of v[k .. k + 2^j - 1]

    static W tri(long long m) {  // m(m-1)/2 mod 2^64, exact
        W a = W(m), b = W(m - 1);
        return a % 2 == 0 ? (a / 2) * b : a * (b / 2);
    }

    // O(N log N)
    PieceCost(vector<long long> starts_, vector<long long> v_, vector<long long> w_, vector<int> slope_)
        : n((int)v_.size()), starts(move(starts_)), v(move(v_)), w(move(w_)), slope(move(slope_)), Wp(n + 1), Bp(n + 1), suff(n + 1) {
        for (int k = 0; k < n; k++) {
            Wp[k + 1] = Wp[k] + W(w[k]);
            Bp[k + 1] = Bp[k] + W(w[k]) * W(v[k]) - (slope[k] ? tri(w[k]) : W(0));
        }
        sp.push_back(vector<int>(n));
        iota(sp[0].begin(), sp[0].end(), 0);
        for (int j = 1; (1 << j) <= n; j++) {
            const vector<int>& prev = sp[j - 1];
            int h = 1 << (j - 1);
            vector<int> cur(n - (1 << j) + 1);
            for (int k = 0; k + (1 << j) <= n; k++) cur[k] = v[prev[k]] >= v[prev[k + h]] ? prev[k] : prev[k + h];
            sp.push_back(move(cur));
        }
        vector<int> stack;
        for (int k = n - 1; k >= 0; k--) {
            while (!stack.empty() && v[stack.back()] <= v[k]) stack.pop_back();
            int ng = stack.empty() ? n : stack.back();
            suff[k] = W(v[k]) * (Wp[ng] - Wp[k]) + suff[ng];
            stack.push_back(k);
        }
    }

    int argmax(int a, int b) const {
        int j = 31 - __builtin_clz(b - a + 1);
        int x = sp[j][a], y = sp[j][b - (1 << j) + 1];
        return v[x] >= v[y] ? x : y;
    }

    // sum over pieces k in [a, b] of w_k * max(M, max(v[a..k]))
    W carry(int a, int b, long long M) const {
        int q = a;  // first piece in [a, b] above M: skip blocks whose max is <= M
        for (int j = (int)sp.size() - 1; j >= 0; j--)
            if (q + (1 << j) - 1 <= b && v[sp[j][q]] <= M) q += 1 << j;
        if (q > b) return W(M) * (Wp[b + 1] - Wp[a]);
        int p = argmax(q, b);
        return W(M) * (Wp[q] - Wp[a]) + suff[q] - suff[p] + W(v[p]) * (Wp[b + 1] - Wp[p]);
    }

    W part(int k, long long x, long long y) const {  // sum of piece k's values at indices x..y
        long long m = y - x + 1;
        return W(m) * W(v[k] + slope[k] * (x - starts[k])) - (slope[k] ? tri(m) : W(0));
    }

    int piece(long long i) const { return int(upper_bound(starts.begin(), starts.end(), i) - starts.begin()) - 1; }

    // O(logN) -- a[l] + ... + a[r] (mod 2^64)
    W sum(long long l, long long r) const {
        int k0 = piece(l), k1 = piece(r);
        if (k0 == k1) return part(k0, l, r);
        return part(k0, l, starts[k0] + w[k0] - 1) + Bp[k1] - Bp[k0 + 1] + part(k1, starts[k1], r);
    }

    // O(logN) -- min +1 increments to make a[l..r] non-decreasing
    long long cost(long long l, long long r) const {
        int k0 = piece(l), k1 = piece(r);
        long long m0 = v[k0] + slope[k0] * (l - starts[k0]);  // the value at l: the prefix max all through l's piece
        if (k0 == k1) return (long long)(W(r - l + 1) * W(m0) - sum(l, r));
        W pref = W(m0) * W(starts[k0] + w[k0] - l) + carry(k0 + 1, k1, m0);
        long long fin = max(m0, v[argmax(k0 + 1, k1)]);  // the prefix max all through r's piece
        pref -= W(starts[k1] + w[k1] - 1 - r) * W(fin);  // r's piece only counts up to r
        return (long long)(pref - sum(l, r));
    }

    // the pieces of b[i] = a[i] + c * (i - lo) (c = 0, or -1 for the strict costs) for sorted points over [lo, hi]
    template <typename T>
    static PieceCost of(long long lo, long long hi, const vector<pair<long long, T>>& pts, int c) {
        vector<long long> st, v, w;
        vector<int> sl;
        long long prev = lo - 1;
        auto gap = [&](long long s, long long e) { st.push_back(s), v.push_back(c * (s - lo)), w.push_back(e - s + 1), sl.push_back(c); };
        for (auto& [i, x] : pts) {
            if (i > prev + 1) gap(prev + 1, i - 1);
            st.push_back(i), v.push_back((long long)x + c * (i - lo)), w.push_back(1), sl.push_back(0);
            prev = i;
        }
        if (prev < hi) gap(prev + 1, hi);
        return PieceCost(st, v, w, sl);
    }
};

// Min +1 increments to make a[l..r] non-decreasing / non-increasing / strictly increasing / strictly decreasing,
// and range sum, over any index range [lo, hi], built from (index, value) points; every other index is 0.
// Decreasing costs are increasing costs on the mirror image (index i -> lo + hi - i); strict costs are the
// non-strict ones on a[i] - i (shifting by a constant changes nothing). Each view is built on its first query.
// T: int, long long, ...
template <typename T>
struct SparseMonoCosts {
    long long lo, hi;
    vector<long long> idx;
    vector<T> vals;
    vector<pair<long long, T>> pts, mirrored;
    mutable optional<PieceCost> views[2][2];  // [mirrored][strict]

    // O(N log N) -- [lo, hi] all 0 except the given (index, value) points (distinct indices)
    SparseMonoCosts(long long lo, long long hi, vector<pair<long long, T>> points) : lo(lo), hi(hi), pts(move(points)) {
        sort(pts.begin(), pts.end());
        for (auto& [i, v] : pts) idx.push_back(i), vals.push_back(v), mirrored.push_back({lo + hi - i, v});
        reverse(mirrored.begin(), mirrored.end());
    }

    const PieceCost& view(bool mir, bool strict) const {
        auto& v = views[mir][strict];
        if (!v) v.emplace(PieceCost::of(lo, hi, mir ? mirrored : pts, strict ? -1 : 0));
        return *v;
    }

    // O(logN) -- a[l] + ... + a[r]
    long long rangeSum(long long l, long long r) const { return l <= r ? (long long)view(false, false).sum(l, r) : 0; }

    // O(logN) -- min +1 increments to make a[l..r] non-decreasing
    long long costMonoIncreasing(long long l, long long r) const { return view(false, false).cost(l, r); }

    // O(logN) -- min +1 increments to make a[l..r] non-increasing
    long long costMonoDecreasing(long long l, long long r) const { return view(true, false).cost(lo + hi - r, lo + hi - l); }

    // O(logN) -- min +1 increments to make a[l..r] strictly increasing
    long long costStrictIncreasing(long long l, long long r) const { return view(false, true).cost(l, r); }

    // O(logN) -- min +1 increments to make a[l..r] strictly decreasing
    long long costStrictDecreasing(long long l, long long r) const { return view(true, true).cost(lo + hi - r, lo + hi - l); }

    // O(logN) -- a[i]
    T pointGet(long long i) const {
        auto it = lower_bound(idx.begin(), idx.end(), i);
        return it != idx.end() && *it == i ? vals[it - idx.begin()] : T(0);
    }
};
