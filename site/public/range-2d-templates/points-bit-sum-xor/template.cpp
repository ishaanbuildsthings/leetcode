// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-bit-sum-xor/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectSum rectXor sumAll xorAll
// @data-structure-type: BIT
// @input: points
// @complexities:
//   pointAdd: log^2(N)
//   pointAssign: log^2(N)
//   pointChmax: log^2(N)
//   pointChmin: log^2(N)
//   pointGet: log(N)
//   rectSum: log^2(N)
//   rectXor: log^2(N)
//   sumAll: 1
//   xorAll: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: sm[1*N*log(N)] xr[1*N*log(N)]
//   tags: none
//   other: ys[1*N*log(N)] pts[2*N] vals[1*N] xs[1*N] off[1*N] cnt[1*N]
//   note: every point's y is listed in each of the O(log N) Fenwick x-nodes covering it; an x-node's own Fenwick tree is as long as its list

// 2D Fenwick tree over points known up front (sum and xor): point updates and any-rectangle sum and xor in O(log^2
// N), with N log N memory whatever the coordinates are (any integers, negative is fine). The constructor takes every
// (x, y) that will ever be updated; every point starts at 0. A Fenwick tree over the distinct x's; every node of it
// keeps the sorted y's of the points it covers and a Fenwick tree over just those. Half the memory of the segment
// tree version and a smaller constant, for sum and xor only. Rectangles are inclusive, x1..x2 by y1..y2, and their
// corners can be any integers, given or not.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T). Coordinates are long
// long.
template <typename T>
struct PointsFenwick2D {
    using ll = long long;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    vector<pair<ll, ll>> pts;
    vector<T> vals;
    vector<ll> xs, ys;
    vector<int> off, cnt;
    vector<S> sm;  // x-node i's own Fenwick tree is [off[i], off[i] + cnt[i]), 1-based inside
    S totalSum = 0;
    vector<T> xr;  // x-node i's own Fenwick tree is [off[i], off[i] + cnt[i]), 1-based inside
    T totalXor = 0;

    // O(N log N) -- points: every (x, y) that will ever be updated (negative is fine, repeats are fine); needs at least
    // one, else throws invalid_argument
    explicit PointsFenwick2D(vector<pair<ll, ll>> points) : pts(std::move(points)) {
        if (pts.empty()) throw invalid_argument("PointsFenwick2D: needs at least one point");
        sort(pts.begin(), pts.end());
        pts.erase(unique(pts.begin(), pts.end()), pts.end());
        vals.assign(pts.size(), T(0));
        for (auto& p : pts)
            if (xs.empty() || xs.back() != p.first) xs.push_back(p.first);
        n = (int)xs.size();
        vector<int> byY(pts.size());
        iota(byY.begin(), byY.end(), 0);
        sort(byY.begin(), byY.end(), [&](int a, int b) { return pts[a].second < pts[b].second; });
        vector<vector<ll>> lists(n + 1);  // per Fenwick x-node: the distinct y's it covers, ascending
        for (int i : byY) {
            ll y = pts[i].second;
            int k = (int)(lower_bound(xs.begin(), xs.end(), pts[i].first) - xs.begin()) + 1;
            for (; k <= n; k += k & -k)
                if (lists[k].empty() || lists[k].back() != y) lists[k].push_back(y);
        }
        off.assign(n + 1, 0);
        cnt.assign(n + 1, 0);
        for (int i = 1; i <= n; i++) {
            off[i] = (int)ys.size();
            cnt[i] = (int)lists[i].size();
            ys.insert(ys.end(), lists[i].begin(), lists[i].end());
        }
        sm.assign(ys.size(), 0);
        xr.assign(ys.size(), 0);
    }

    // where (x, y) is in the sorted points
    int indexOf(long long x, long long y, const char* name) const {
        auto it = lower_bound(pts.begin(), pts.end(), make_pair(x, y));
        if (it == pts.end() || *it != make_pair(x, y))
            throw out_of_range(string(name) + ": (x, y) is not one of the points given to the constructor");
        return (int)(it - pts.begin());
    }

    // point number i, at (x, y), becomes v
    void setPoint(int i, ll x, ll y, T v) {
        T old = vals[i];
        vals[i] = v;
        int xi = (int)(lower_bound(xs.begin(), xs.end(), x) - xs.begin()) + 1;
        S dSum = S(v) - old;
        totalSum += dSum;
        for (int k = xi; k <= n; k += k & -k) {
            const ll* first = ys.data() + off[k];
            S* t = sm.data() + off[k] - 1;
            for (int j = (int)(lower_bound(first, first + cnt[k], y) - first) + 1; j <= cnt[k]; j += j & -j)
                t[j] += dSum;
        }
        T dXor = v ^ old;
        totalXor ^= dXor;
        for (int k = xi; k <= n; k += k & -k) {
            const ll* first = ys.data() + off[k];
            T* t = xr.data() + off[k] - 1;
            for (int j = (int)(lower_bound(first, first + cnt[k], y) - first) + 1; j <= cnt[k]; j += j & -j)
                t[j] ^= dXor;
        }
    }

    // sum of the points with x <= the given x and y <= the given y
    S prefixSum(ll x, ll y) const {
        S res = 0;
        for (int k = (int)(upper_bound(xs.begin(), xs.end(), x) - xs.begin()); k > 0; k &= k - 1) {
            const ll* first = ys.data() + off[k];
            const S* t = sm.data() + off[k] - 1;
            for (int j = (int)(upper_bound(first, first + cnt[k], y) - first); j > 0; j &= j - 1) res += t[j];
        }
        return res;
    }

    // xor of the points with x <= the given x and y <= the given y
    T prefixXor(ll x, ll y) const {
        T res = 0;
        for (int k = (int)(upper_bound(xs.begin(), xs.end(), x) - xs.begin()); k > 0; k &= k - 1) {
            const ll* first = ys.data() + off[k];
            const T* t = xr.data() + off[k] - 1;
            for (int j = (int)(upper_bound(first, first + cnt[k], y) - first); j > 0; j &= j - 1) res ^= t[j];
        }
        return res;
    }

    // O(log N) -- the value at (x, y); needs (x, y) to be one of the points given, else throws out_of_range
    T pointGet(ll x, ll y) const {
        return vals[indexOf(x, y, "pointGet")];
    }

    // O(log^2 N) -- the point (x, y) becomes v; needs (x, y) to be one of the points given, else throws out_of_range
    void pointAssign(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointAssign");
        setPoint(i, x, y, v);
    }

    // O(log^2 N) -- adds v to the point (x, y); needs (x, y) to be one of the points given, else throws out_of_range
    void pointAdd(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointAdd");
        setPoint(i, x, y, T(vals[i] + v));
    }

    // O(log^2 N) -- the point (x, y) becomes max(itself, v); needs (x, y) to be one of the points given, else throws
    // out_of_range
    void pointChmax(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointChmax");
        if (v > vals[i]) setPoint(i, x, y, v);
    }

    // O(log^2 N) -- the point (x, y) becomes min(itself, v); needs (x, y) to be one of the points given, else throws
    // out_of_range
    void pointChmin(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointChmin");
        if (v < vals[i]) setPoint(i, x, y, v);
    }

    // O(log^2 N) -- sum of the points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); needs x1 <= x2 and
    // y1 <= y2, else throws out_of_range
    S rectSum(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectSum: needs x1 <= x2 and y1 <= y2");
        return prefixSum(x2, y2) - prefixSum(x1 - 1, y2) - prefixSum(x2, y1 - 1) + prefixSum(x1 - 1, y1 - 1);
    }

    // O(1) -- sum of every point
    S sumAll() const {
        return totalSum;
    }

    // O(log^2 N) -- xor of the points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); needs x1 <= x2 and
    // y1 <= y2, else throws out_of_range
    T rectXor(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectXor: needs x1 <= x2 and y1 <= y2");
        return prefixXor(x2, y2) ^ prefixXor(x1 - 1, y2) ^ prefixXor(x2, y1 - 1) ^ prefixXor(x1 - 1, y1 - 1);
    }

    // O(1) -- xor of every point
    T xorAll() const {
        return totalXor;
    }
};
