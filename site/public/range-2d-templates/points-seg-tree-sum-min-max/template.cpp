// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-seg-tree-sum-min-max/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: maxAll maxGteGte maxGteLte maxLteGte maxLteLte minAll minGteGte minGteLte minLteGte minLteLte pointAdd pointAssign pointChmax pointChmin pointGet rectMax rectMin rectSum sumAll
// @data-structure-type: seg-tree
// @input: points
// @empty-cells: yes
// @complexities:
//   maxAll: 1
//   maxGteGte: log^2(N)
//   maxGteLte: log^2(N)
//   maxLteGte: log^2(N)
//   maxLteLte: log^2(N)
//   minAll: 1
//   minGteGte: log^2(N)
//   minGteLte: log^2(N)
//   minLteGte: log^2(N)
//   minLteLte: log^2(N)
//   pointAdd: log^2(N)
//   pointAssign: log^2(N)
//   pointChmax: log^2(N)
//   pointChmin: log^2(N)
//   pointGet: log(N)
//   rectMax: log^2(N)
//   rectMin: log^2(N)
//   rectSum: log^2(N)
//   sumAll: 1
//   build: N*log(N)
// @memory:
//   layout: 2n-iterative
//   node: sm[2*N*log(N)] mn[2*N*log(N)] mx[2*N*log(N)]
//   tags: none
//   other: ys[1*N*log(N)] pts[2*N] vals[1*N] xs[1*N] off[2*N] cnt[2*N]
//   note: every point's y is listed in each of the O(log N) x-nodes above it; an x-node's column tree is twice its list

// 2D segment tree over points known up front (sum, min, max): point updates and any-rectangle queries in O(log^2 N),
// with N log N memory whatever the coordinates are (any integers, negative is fine). The constructor takes every (x,
// y) that will ever be updated. A bottom-up tree over the distinct x's; every node of it keeps the sorted y's of the
// points under it and a bottom-up tree over just those. Rectangles are inclusive, x1..x2 by y1..y2, and their corners
// can be any integers, given or not. Every point starts empty and queries only see points that have been set: a min /
// max over no set point is NO_MIN / NO_MAX; a sum over none is 0.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T). Coordinates are long
// long.
template <typename T>
struct PointsSegTree2D {
    using ll = long long;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set point gives
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set point gives
    static constexpr ll LOW = numeric_limits<ll>::min(), HIGH = numeric_limits<ll>::max();  // no bound on a coordinate
    int n;
    vector<pair<ll, ll>> pts;
    vector<T> vals;
    vector<char> isSet;
    vector<ll> xs, ys;
    vector<int> off, cnt;
    vector<S> sm;  // x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])
    vector<T> mn;  // x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])
    vector<T> mx;  // x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])

    // O(N log N) -- points: every (x, y) that will ever be updated (negative is fine, repeats are fine); needs at least
    // one, else throws invalid_argument
    explicit PointsSegTree2D(vector<pair<ll, ll>> points) : pts(std::move(points)) {
        if (pts.empty()) throw invalid_argument("PointsSegTree2D: needs at least one point");
        sort(pts.begin(), pts.end());
        pts.erase(unique(pts.begin(), pts.end()), pts.end());
        vals.assign(pts.size(), T(0));
        isSet.assign(pts.size(), 0);
        for (auto& p : pts)
            if (xs.empty() || xs.back() != p.first) xs.push_back(p.first);
        n = (int)xs.size();
        vector<int> byY(pts.size());
        iota(byY.begin(), byY.end(), 0);
        sort(byY.begin(), byY.end(), [&](int a, int b) { return pts[a].second < pts[b].second; });
        vector<vector<ll>> lists(2 * n);  // per x-node: the distinct y's under it, ascending
        for (int i : byY) {
            ll y = pts[i].second;
            for (int p = (int)(lower_bound(xs.begin(), xs.end(), pts[i].first) - xs.begin()) + n; p >= 1; p >>= 1)
                if (lists[p].empty() || lists[p].back() != y) lists[p].push_back(y);
        }
        off.assign(2 * n, 0);
        cnt.assign(2 * n, 0);
        for (int p = 1; p < 2 * n; p++) {
            off[p] = (int)ys.size();
            cnt[p] = (int)lists[p].size();
            ys.insert(ys.end(), lists[p].begin(), lists[p].end());
        }
        sm.assign(2 * ys.size(), S(0));
        mn.assign(2 * ys.size(), NO_MIN);
        mx.assign(2 * ys.size(), NO_MAX);
    }

    // where (x, y) is in the sorted points
    int indexOf(long long x, long long y, const char* name) const {
        auto it = lower_bound(pts.begin(), pts.end(), make_pair(x, y));
        if (it == pts.end() || *it != make_pair(x, y))
            throw out_of_range(string(name) + ": (x, y) is not one of the points given to the constructor");
        return (int)(it - pts.begin());
    }

    // point (x, y) = v, then every node above it
    void setPoint(ll x, ll y, T v) {
        int p = (int)(lower_bound(xs.begin(), xs.end(), x) - xs.begin()) + n;
        S vSum = v;  // this aggregate over the points with this y under x-node p
        T vMin = v;  // this aggregate over the points with this y under x-node p
        T vMax = v;  // this aggregate over the points with this y under x-node p
        while (true) {
            const ll* first = ys.data() + off[p];
            int base = 2 * off[p], k = (int)(lower_bound(first, first + cnt[p], y) - first) + cnt[p];
            sm[base + k] = vSum;
            mn[base + k] = vMin;
            mx[base + k] = vMax;
            for (k >>= 1; k >= 1; k >>= 1) {
                sm[base + k] = sm[base + 2 * k] + sm[base + 2 * k + 1];
                mn[base + k] = min(mn[base + 2 * k], mn[base + 2 * k + 1]);
                mx[base + k] = max(mx[base + 2 * k], mx[base + 2 * k + 1]);
            }
            if (p == 1) break;
            int s = p ^ 1;  // the other half of the parent: does it have this y too?
            first = ys.data() + off[s];
            int j = (int)(lower_bound(first, first + cnt[s], y) - first);
            if (j < cnt[s] && first[j] == y) {
                j += 2 * off[s] + cnt[s];
                vSum += sm[j];
                vMin = min(vMin, mn[j]);
                vMax = max(vMax, mx[j]);
            }
            p >>= 1;
        }
    }

    // O(log N) -- the value at (x, y), NO_MAX if it was never set; needs (x, y) to be one of the points given, else
    // throws out_of_range
    T pointGet(ll x, ll y) const {
        int i = indexOf(x, y, "pointGet");
        return isSet[i] ? vals[i] : NO_MAX;
    }

    // O(log^2 N) -- the point (x, y) becomes v (it may go down as well as up); needs (x, y) to be one of the points
    // given, else throws out_of_range
    void pointAssign(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointAssign");
        vals[i] = v;
        isSet[i] = 1;
        setPoint(x, y, v);
    }

    // O(log^2 N) -- adds v to the point (x, y); an empty point becomes v; needs (x, y) to be one of the points given,
    // else throws out_of_range
    void pointAdd(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointAdd");
        vals[i] = isSet[i] ? T(vals[i] + v) : v;
        isSet[i] = 1;
        setPoint(x, y, vals[i]);
    }

    // O(log^2 N) -- the point (x, y) becomes max(itself, v); an empty point becomes v; needs (x, y) to be one of the
    // points given, else throws out_of_range
    void pointChmax(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointChmax");
        if (isSet[i] && !(v > vals[i])) return;
        vals[i] = v;
        isSet[i] = 1;
        setPoint(x, y, v);
    }

    // O(log^2 N) -- the point (x, y) becomes min(itself, v); an empty point becomes v; needs (x, y) to be one of the
    // points given, else throws out_of_range
    void pointChmin(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointChmin");
        if (isSet[i] && !(v < vals[i])) return;
        vals[i] = v;
        isSet[i] = 1;
        setPoint(x, y, v);
    }

    S sumOf(ll x1, ll y1, ll x2, ll y2) const {
        S res = S(0);
        int l = (int)(lower_bound(xs.begin(), xs.end(), x1) - xs.begin()) + n;
        int r = (int)(upper_bound(xs.begin(), xs.end(), x2) - xs.begin()) + n;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) {
                const ll* first = ys.data() + off[l];
                int base = 2 * off[l], c = cnt[l];
                int lo = (int)(lower_bound(first, first + c, y1) - first) + c;
                int hi = (int)(upper_bound(first, first + c, y2) - first) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res += sm[base + lo++];
                    if (hi & 1) res += sm[base + --hi];
                }
                l++;
            }
            if (r & 1) {
                --r;
                const ll* first = ys.data() + off[r];
                int base = 2 * off[r], c = cnt[r];
                int lo = (int)(lower_bound(first, first + c, y1) - first) + c;
                int hi = (int)(upper_bound(first, first + c, y2) - first) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res += sm[base + lo++];
                    if (hi & 1) res += sm[base + --hi];
                }
            }
        }
        return res;
    }

    // O(log^2 N) -- sum of the set points with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs x1 <= x2
    // and
    // y1 <= y2, else throws out_of_range
    S rectSum(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectSum: needs x1 <= x2 and y1 <= y2");
        return sumOf(x1, y1, x2, y2);
    }

    // O(1) -- sum of every set point (0 if there are none)
    S sumAll() const {
        return sm[2 * off[1] + 1];
    }

    T minOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = NO_MIN;
        int l = (int)(lower_bound(xs.begin(), xs.end(), x1) - xs.begin()) + n;
        int r = (int)(upper_bound(xs.begin(), xs.end(), x2) - xs.begin()) + n;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) {
                const ll* first = ys.data() + off[l];
                int base = 2 * off[l], c = cnt[l];
                int lo = (int)(lower_bound(first, first + c, y1) - first) + c;
                int hi = (int)(upper_bound(first, first + c, y2) - first) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res = min(res, mn[base + lo++]);
                    if (hi & 1) res = min(res, mn[base + --hi]);
                }
                l++;
            }
            if (r & 1) {
                --r;
                const ll* first = ys.data() + off[r];
                int base = 2 * off[r], c = cnt[r];
                int lo = (int)(lower_bound(first, first + c, y1) - first) + c;
                int hi = (int)(upper_bound(first, first + c, y2) - first) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res = min(res, mn[base + lo++]);
                    if (hi & 1) res = min(res, mn[base + --hi]);
                }
            }
        }
        return res;
    }

    // O(log^2 N) -- min of the set points with x1 <= x <= x2 and y1 <= y <= y2 (NO_MIN if there are none); needs x1
    // <= x2
    // and y1 <= y2, else throws out_of_range
    T rectMin(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectMin: needs x1 <= x2 and y1 <= y2");
        return minOf(x1, y1, x2, y2);
    }

    // O(1) -- min of every set point (NO_MIN if there are none)
    T minAll() const {
        return mn[2 * off[1] + 1];
    }

    // O(log^2 N) -- min of the set points with x <= the given x and y <= the given y (NO_MIN if there are none); any
    // integers
    T minLteLte(ll x, ll y) const {
        return minOf(LOW, LOW, x, y);
    }

    // O(log^2 N) -- min of the set points with x <= the given x and y >= the given y (NO_MIN if there are none); any
    // integers
    T minLteGte(ll x, ll y) const {
        return minOf(LOW, y, x, HIGH);
    }

    // O(log^2 N) -- min of the set points with x >= the given x and y <= the given y (NO_MIN if there are none); any
    // integers
    T minGteLte(ll x, ll y) const {
        return minOf(x, LOW, HIGH, y);
    }

    // O(log^2 N) -- min of the set points with x >= the given x and y >= the given y (NO_MIN if there are none); any
    // integers
    T minGteGte(ll x, ll y) const {
        return minOf(x, y, HIGH, HIGH);
    }

    T maxOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = NO_MAX;
        int l = (int)(lower_bound(xs.begin(), xs.end(), x1) - xs.begin()) + n;
        int r = (int)(upper_bound(xs.begin(), xs.end(), x2) - xs.begin()) + n;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) {
                const ll* first = ys.data() + off[l];
                int base = 2 * off[l], c = cnt[l];
                int lo = (int)(lower_bound(first, first + c, y1) - first) + c;
                int hi = (int)(upper_bound(first, first + c, y2) - first) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res = max(res, mx[base + lo++]);
                    if (hi & 1) res = max(res, mx[base + --hi]);
                }
                l++;
            }
            if (r & 1) {
                --r;
                const ll* first = ys.data() + off[r];
                int base = 2 * off[r], c = cnt[r];
                int lo = (int)(lower_bound(first, first + c, y1) - first) + c;
                int hi = (int)(upper_bound(first, first + c, y2) - first) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res = max(res, mx[base + lo++]);
                    if (hi & 1) res = max(res, mx[base + --hi]);
                }
            }
        }
        return res;
    }

    // O(log^2 N) -- max of the set points with x1 <= x <= x2 and y1 <= y <= y2 (NO_MAX if there are none); needs x1
    // <= x2
    // and y1 <= y2, else throws out_of_range
    T rectMax(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectMax: needs x1 <= x2 and y1 <= y2");
        return maxOf(x1, y1, x2, y2);
    }

    // O(1) -- max of every set point (NO_MAX if there are none)
    T maxAll() const {
        return mx[2 * off[1] + 1];
    }

    // O(log^2 N) -- max of the set points with x <= the given x and y <= the given y (NO_MAX if there are none); any
    // integers
    T maxLteLte(ll x, ll y) const {
        return maxOf(LOW, LOW, x, y);
    }

    // O(log^2 N) -- max of the set points with x <= the given x and y >= the given y (NO_MAX if there are none); any
    // integers
    T maxLteGte(ll x, ll y) const {
        return maxOf(LOW, y, x, HIGH);
    }

    // O(log^2 N) -- max of the set points with x >= the given x and y <= the given y (NO_MAX if there are none); any
    // integers
    T maxGteLte(ll x, ll y) const {
        return maxOf(x, LOW, HIGH, y);
    }

    // O(log^2 N) -- max of the set points with x >= the given x and y >= the given y (NO_MAX if there are none); any
    // integers
    T maxGteGte(ll x, ll y) const {
        return maxOf(x, y, HIGH, HIGH);
    }
};
