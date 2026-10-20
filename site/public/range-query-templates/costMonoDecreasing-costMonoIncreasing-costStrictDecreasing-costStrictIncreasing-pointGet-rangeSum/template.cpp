// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/costMonoDecreasing-costMonoIncreasing-costStrictDecreasing-costStrictIncreasing-pointGet-rangeSum/template.cpp
// @operations: costMonoDecreasing costMonoIncreasing costStrictDecreasing costStrictIncreasing pointGet rangeSum
// @data-structure-type: sparse-table
// @complexities:
//   costMonoDecreasing: 1
//   costMonoIncreasing: 1
//   costStrictDecreasing: 1
//   costStrictIncreasing: 1
//   pointGet: 1
//   rangeSum: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: sp[4*N*log(N)]
//   tags: none
//   other: arr[4*N] pf[4*N] suff[4*N]
//   note: four MonoIncreaseCost views (a, reversed a, a[i] - i, reversed a[i] + i); every view but the first is built on its first query, so you only pay for the ones you call
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/costToMakeSubarrayMonoIncreasing.cpp

// Min increments to make a range non-decreasing (increments only). Static array, 0-indexed, ranges inclusive.
// Build O(N log N); every query O(1). T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct MonoIncreaseCost {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    vector<T> arr;              // private copy of the input
    vector<S> pf, suff;         // suff[i] = sum of prefix maxes over [i, n), measured from i
    vector<vector<int>> sp;     // sparse table of argmax (leftmost on ties)

    explicit MonoIncreaseCost(const vector<T>& a) : n((int)a.size()), arr(a), pf(n + 1), suff(n + 1) {
        for (int i = 0; i < n; i++) pf[i + 1] = pf[i] + S(arr[i]);
        vector<int> st;
        for (int i = n - 1; i >= 0; i--) {
            while (!st.empty() && arr[st.back()] <= arr[i]) st.pop_back();
            int nxt = st.empty() ? n : st.back();
            suff[i] = S(arr[i]) * (nxt - i) + suff[nxt];
            st.push_back(i);
        }
        int levels = 1;
        while ((1 << levels) <= n) levels++;
        sp.assign(levels, {});
        sp[0].resize(n);
        iota(sp[0].begin(), sp[0].end(), 0);
        for (int j = 1; j < levels; j++) {
            int len = n - (1 << j) + 1, half = 1 << (j - 1);
            sp[j].resize(len);
            for (int i = 0; i < len; i++) {
                int x = sp[j - 1][i], y = sp[j - 1][i + half];
                sp[j][i] = arr[x] >= arr[y] ? x : y;
            }
        }
    }

    // O(1) -- a[l] + ... + a[r] (0 if l > r)
    S rangeSum(int l, int r) const { return r >= l ? pf[r + 1] - pf[l] : S(0); }

    // O(1) -- index of the max of a[l..r], leftmost on ties
    int argMax(int l, int r) const {
        int j = 31 - __builtin_clz(r - l + 1);
        int x = sp[j][l], y = sp[j][r - (1 << j) + 1];
        return arr[x] >= arr[y] ? x : y;
    }

    // O(1) -- min total +1 increments to make a[l..r] non-decreasing
    S costMonoIncreasing(int l, int r) const {
        int m = argMax(l, r);
        S endsAt = (suff[l] - suff[m]) + S(arr[m]) * (r - m + 1);
        return endsAt - rangeSum(l, r);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }
};

// Min +1 increments to make a[l..r] non-decreasing / non-increasing / strictly increasing / strictly decreasing.
// One structure answers "non-decreasing"; the other three reduce to it:
//   non-increasing on a        == non-decreasing on a reversed
//   strictly increasing on a   == non-decreasing on b[i] = a[i] - i      (a[i] < a[i+1]  <=>  b[i] <= b[i+1])
//   strictly decreasing on a   == non-increasing on c[i] = a[i] + i
// Adding +1 to a[i] adds it to b[i] / c[i] too, so the costs carry over. Each extra view is built on first use.
template <typename T>
struct MonoCosts {
    using Cost = MonoIncreaseCost<T>;
    using S = typename Cost::S;
    int n;
    vector<T> arr;
    Cost inc;
    unique_ptr<Cost> dec, sinc, sdec;

    // O(N log N); the other three views cost O(N log N) each on their first query
    explicit MonoCosts(const vector<T>& a) : n((int)a.size()), arr(a), inc(a) {}

    // O(1) -- min +1 increments to make a[l..r] non-decreasing
    S costMonoIncreasing(int l, int r) const { return inc.costMonoIncreasing(l, r); }

    // O(1) -- min +1 increments to make a[l..r] non-increasing
    S costMonoDecreasing(int l, int r) {
        if (!dec) dec = make_unique<Cost>(vector<T>(arr.rbegin(), arr.rend()));
        return dec->costMonoIncreasing(n - 1 - r, n - 1 - l);
    }

    // O(1) -- min +1 increments to make a[l..r] strictly increasing
    S costStrictIncreasing(int l, int r) {
        if (!sinc) {
            vector<T> b(n);
            for (int i = 0; i < n; i++) b[i] = arr[i] - T(i);
            sinc = make_unique<Cost>(b);
        }
        return sinc->costMonoIncreasing(l, r);
    }

    // O(1) -- min +1 increments to make a[l..r] strictly decreasing
    S costStrictDecreasing(int l, int r) {
        if (!sdec) {
            vector<T> c(n);
            for (int i = 0; i < n; i++) c[n - 1 - i] = arr[i] + T(i);
            sdec = make_unique<Cost>(c);
        }
        return sdec->costMonoIncreasing(n - 1 - r, n - 1 - l);
    }

    // O(1) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) const { return inc.rangeSum(l, r); }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }
};
