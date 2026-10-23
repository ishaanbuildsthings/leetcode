// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countInValRange-kthLargestInRange-kthSmallestInRange-pointGet-sumInValRange/template.cpp
// @operations: countInValRange kthLargestInRange kthSmallestInRange pointGet sumInValRange
// @data-structure-type: persistent
// @complexities:
//   countInValRange: log(N)
//   kthLargestInRange: log(N)
//   kthSmallestInRange: log(N)
//   pointGet: 1
//   sumInValRange: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: L[1*N*log(N)] R[1*N*log(N)] S[1*N*log(N)] C[1*N*log(N)]
//   tags: none
//   other: root[1*N] srt[1*N]
//   note: about N*log(N) persistent nodes; L/R are child pointers, S/C are sum and count
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/persistent/persistent-sum-denseOfflineWithCompressionLogN.cpp

// Static "count / sum of values in [lo, hi] among a[l..r]" and "k-th smallest / largest of a[l..r]" via a persistent
// segment tree over compressed values.
// Version i + 1 = version i with a[i] inserted; a query subtracts version l from version r + 1. All indices 0-based,
// ranges inclusive. Build O(N log N), queries O(log N), ~N * (log N + 1) nodes.
// T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct StaticValueRangeSum {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, m;
    vector<T> arr, srt;           // srt: sorted distinct values
    vector<int> root, L, R, C;    // node 0 is the shared null node
    vector<S> Sm;

    // O(N log N)
    explicit StaticValueRangeSum(const vector<T>& a) : n((int)a.size()), arr(a), srt(a), root(n + 1), L(1), R(1), C(1), Sm(1) {
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        int depth = 1;
        while ((1 << (depth - 1)) < max(m, 1)) depth++;
        L.reserve(1 + (size_t)n * depth), R.reserve(L.capacity()), C.reserve(L.capacity()), Sm.reserve(L.capacity());
        for (int i = 0; i < n; i++) root[i + 1] = insert(root[i], 0, m - 1, lb(a[i]), a[i]);
    }

    int newNode(int l, int r, S s, int c) {
        L.push_back(l), R.push_back(r), Sm.push_back(s), C.push_back(c);
        return (int)L.size() - 1;
    }

    int insert(int node, int nl, int nh, int rk, T w) {
        if (nl == nh) return newNode(0, 0, Sm[node] + S(w), C[node] + 1);
        int mid = (nl + nh) >> 1, l = L[node], r = R[node];
        if (rk <= mid) l = insert(l, nl, mid, rk, w);
        else r = insert(r, mid + 1, nh, rk, w);
        return newNode(l, r, Sm[l] + Sm[r], C[l] + C[r]);
    }

    int lb(const T& v) const { return int(lower_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    int ub(const T& v) const { return int(upper_bound(srt.begin(), srt.end(), v) - srt.begin()); }

    // (sum, count) of values with compressed rank in [lo, hi] among a[l..r]
    pair<S, int> ranks(int l, int r, int lo, int hi) const {
        if (!m || l > r || l < 0 || r >= n || lo > hi) return {0, 0};
        S s = 0;
        int c = 0;
        auto go = [&](auto&& self, int a, int b, int nl, int nh) -> void {
            if (nh < lo || hi < nl || (!a && !b)) return;
            if (lo <= nl && nh <= hi) { s += Sm[a] - Sm[b], c += C[a] - C[b]; return; }
            int mid = (nl + nh) >> 1;
            self(self, L[a], L[b], nl, mid), self(self, R[a], R[b], mid + 1, nh);
        };
        go(go, root[r + 1], root[l], 0, m - 1);
        return {s, c};
    }

    // O(logN) -- sum of a[i] for i in [l, r] with lowVal <= a[i] <= highVal
    S sumInValRange(int l, int r, const T& lowVal, const T& highVal) const { return ranks(l, r, lb(lowVal), ub(highVal) - 1).first; }

    // O(logN) -- how many i in [l, r] have lowVal <= a[i] <= highVal
    int countInValRange(int l, int r, const T& lowVal, const T& highVal) const { return ranks(l, r, lb(lowVal), ub(highVal) - 1).second; }

    // O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthSmallestInRange(int l, int r, int k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallestInRange: k outside [1, r - l + 1]");
        int a = root[r + 1], b = root[l], nl = 0, nh = m - 1;
        while (nl != nh) {  // walk down version r+1 minus version l: the left child holds the smaller ranks
            int mid = (nl + nh) >> 1, c = C[L[a]] - C[L[b]];
            if (k <= c) a = L[a], b = L[b], nh = mid;
            else k -= c, a = R[a], b = R[b], nl = mid + 1;
        }
        return srt[nl];
    }

    // O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else throws out_of_range
    T kthLargestInRange(int l, int r, int k) const {
        if (k < 1 || k > r - l + 1) throw out_of_range("kthLargestInRange: k outside [1, r - l + 1]");
        return kthSmallestInRange(l, r, r - l + 2 - k);
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }
};
