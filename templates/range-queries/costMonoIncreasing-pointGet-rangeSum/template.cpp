// @operations: costMonoIncreasing pointGet rangeSum
// @data-structure-type: sparse-table
// @complexities:
//   costMonoIncreasing: 1
//   pointGet: 1
//   rangeSum: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: sp[1*N*log(N)]
//   tags: none
//   other: arr[1*N] pf[1*N] suff[1*N]
//   note: sp is a sparse table of argmax indices; arr is a private copy of the input
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
