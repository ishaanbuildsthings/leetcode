// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-seg-tree-min-gcd-and-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: andAll gcdAll minAll minGteGte minGteLte minLteGte minLteLte orAll pointAdd pointAssign pointChmax pointChmin pointGet rectAnd rectGcd rectMin rectOr
// @data-structure-type: seg-tree
// @input: points
// @empty-cells: yes
// @complexities:
//   andAll: 1
//   gcdAll: 1
//   minAll: 1
//   minGteGte: log^2(N)
//   minGteLte: log^2(N)
//   minLteGte: log^2(N)
//   minLteLte: log^2(N)
//   orAll: 1
//   pointAdd: log^2(N)*log(U) ?
//   pointAssign: log^2(N)*log(U) ?
//   pointChmax: log^2(N)*log(U) ?
//   pointChmin: log^2(N)*log(U) ?
//   pointGet: log(N)
//   rectAnd: log^2(N)
//   rectGcd: log^2(N)+log(U) ?
//   rectMin: log^2(N)
//   rectOr: log^2(N)
//   build: N*log(N)
// @memory:
//   layout: 2n-iterative
//   node: mn[2*N*log(N)] gc[2*N*log(N)] an[2*N*log(N)] orr[2*N*log(N)]
//   tags: none
//   other: ys[1*N*log(N)] pts[2*N] vals[1*N] xs[1*N] off[2*N] cnt[2*N]
//   note: every point's y is listed in each of the O(log N) x-nodes above it; an x-node's column tree is twice its list

// 2D segment tree over points known up front (min, gcd, AND, OR): point updates and any-rectangle queries in O(log^2
// N), with N log N memory whatever the coordinates are (any integers, negative is fine). The constructor takes every
// (x, y) that will ever be updated. A bottom-up tree over the distinct x's; every node of it keeps the sorted y's of
// the points under it and a bottom-up tree over just those. Rectangles are inclusive, x1..x2 by y1..y2, and their
// corners can be any integers, given or not. Every point starts empty and queries only see points that have been set:
// a min / max over no set point is NO_MIN; a gcd / OR over none is 0; an AND over none is -1 (every bit set).
// T is any integer type (int, long long, ...). Coordinates are long long.
template <typename T>
struct PointsSegTree2D {
    using ll = long long;
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no set point gives
    static constexpr ll LOW = numeric_limits<ll>::min(), HIGH = numeric_limits<ll>::max();  // no bound on a coordinate
    int n;
    vector<pair<ll, ll>> pts;
    vector<T> vals;
    vector<char> isSet;
    vector<ll> xs, ys;
    vector<int> off, cnt;
    vector<T> mn;  // x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])
    vector<T> gc;  // x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])
    vector<T> an;  // x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])
    vector<T> orr;  // x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])

    static T gcdOf(T a, T b) { return std::gcd(a, b); }

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
        mn.assign(2 * ys.size(), NO_MIN);
        gc.assign(2 * ys.size(), T(0));
        an.assign(2 * ys.size(), T(-1));
        orr.assign(2 * ys.size(), T(0));
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
        T vMin = v;  // this aggregate over the points with this y under x-node p
        T vGcd = v;  // this aggregate over the points with this y under x-node p
        T vAnd = v;  // this aggregate over the points with this y under x-node p
        T vOr = v;  // this aggregate over the points with this y under x-node p
        while (true) {
            const ll* first = ys.data() + off[p];
            int base = 2 * off[p], k = (int)(lower_bound(first, first + cnt[p], y) - first) + cnt[p];
            mn[base + k] = vMin;
            gc[base + k] = vGcd;
            an[base + k] = vAnd;
            orr[base + k] = vOr;
            for (k >>= 1; k >= 1; k >>= 1) {
                mn[base + k] = min(mn[base + 2 * k], mn[base + 2 * k + 1]);
                gc[base + k] = gcdOf(gc[base + 2 * k], gc[base + 2 * k + 1]);
                an[base + k] = an[base + 2 * k] & an[base + 2 * k + 1];
                orr[base + k] = orr[base + 2 * k] | orr[base + 2 * k + 1];
            }
            if (p == 1) break;
            int s = p ^ 1;  // the other half of the parent: does it have this y too?
            first = ys.data() + off[s];
            int j = (int)(lower_bound(first, first + cnt[s], y) - first);
            if (j < cnt[s] && first[j] == y) {
                j += 2 * off[s] + cnt[s];
                vMin = min(vMin, mn[j]);
                vGcd = gcdOf(vGcd, gc[j]);
                vAnd &= an[j];
                vOr |= orr[j];
            }
            p >>= 1;
        }
    }

    // O(log N) -- the value at (x, y), NO_MIN if it was never set; needs (x, y) to be one of the points given, else
    // throws out_of_range
    T pointGet(ll x, ll y) const {
        int i = indexOf(x, y, "pointGet");
        return isSet[i] ? vals[i] : NO_MIN;
    }

    // O(log^2 N) gcds -- the point (x, y) becomes v (it may go down as well as up); needs (x, y) to be one of the
    // points
    // given, else throws out_of_range
    void pointAssign(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointAssign");
        vals[i] = v;
        isSet[i] = 1;
        setPoint(x, y, v);
    }

    // O(log^2 N) gcds -- adds v to the point (x, y); an empty point becomes v; needs (x, y) to be one of the points
    // given, else throws out_of_range
    void pointAdd(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointAdd");
        vals[i] = isSet[i] ? T(vals[i] + v) : v;
        isSet[i] = 1;
        setPoint(x, y, vals[i]);
    }

    // O(log^2 N) gcds -- the point (x, y) becomes max(itself, v); an empty point becomes v; needs (x, y) to be one of
    // the
    // points given, else throws out_of_range
    void pointChmax(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointChmax");
        if (isSet[i] && !(v > vals[i])) return;
        vals[i] = v;
        isSet[i] = 1;
        setPoint(x, y, v);
    }

    // O(log^2 N) gcds -- the point (x, y) becomes min(itself, v); an empty point becomes v; needs (x, y) to be one of
    // the
    // points given, else throws out_of_range
    void pointChmin(ll x, ll y, T v) {
        int i = indexOf(x, y, "pointChmin");
        if (isSet[i] && !(v < vals[i])) return;
        vals[i] = v;
        isSet[i] = 1;
        setPoint(x, y, v);
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

    T gcdOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = T(0);
        int l = (int)(lower_bound(xs.begin(), xs.end(), x1) - xs.begin()) + n;
        int r = (int)(upper_bound(xs.begin(), xs.end(), x2) - xs.begin()) + n;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) {
                const ll* first = ys.data() + off[l];
                int base = 2 * off[l], c = cnt[l];
                int lo = (int)(lower_bound(first, first + c, y1) - first) + c;
                int hi = (int)(upper_bound(first, first + c, y2) - first) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res = gcdOf(res, gc[base + lo++]);
                    if (hi & 1) res = gcdOf(res, gc[base + --hi]);
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
                    if (lo & 1) res = gcdOf(res, gc[base + lo++]);
                    if (hi & 1) res = gcdOf(res, gc[base + --hi]);
                }
            }
        }
        return res;
    }

    // O(log^2 N + log U) -- gcd of the set points with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs
    // x1 <=
    // x2 and y1 <= y2, else throws out_of_range
    T rectGcd(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectGcd: needs x1 <= x2 and y1 <= y2");
        return gcdOf(x1, y1, x2, y2);
    }

    // O(1) -- gcd of every set point (0 if there are none)
    T gcdAll() const {
        return gcdOf(gc[2 * off[1] + 1], T(0));
    }

    T andOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = T(-1);
        int l = (int)(lower_bound(xs.begin(), xs.end(), x1) - xs.begin()) + n;
        int r = (int)(upper_bound(xs.begin(), xs.end(), x2) - xs.begin()) + n;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) {
                const ll* first = ys.data() + off[l];
                int base = 2 * off[l], c = cnt[l];
                int lo = (int)(lower_bound(first, first + c, y1) - first) + c;
                int hi = (int)(upper_bound(first, first + c, y2) - first) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res &= an[base + lo++];
                    if (hi & 1) res &= an[base + --hi];
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
                    if (lo & 1) res &= an[base + lo++];
                    if (hi & 1) res &= an[base + --hi];
                }
            }
        }
        return res;
    }

    // O(log^2 N) -- AND of the set points with x1 <= x <= x2 and y1 <= y <= y2 (-1 (every bit set) if there are none);
    // needs x1 <= x2 and y1 <= y2, else throws out_of_range
    T rectAnd(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectAnd: needs x1 <= x2 and y1 <= y2");
        return andOf(x1, y1, x2, y2);
    }

    // O(1) -- AND of every set point (-1 (every bit set) if there are none)
    T andAll() const {
        return an[2 * off[1] + 1];
    }

    T orOf(ll x1, ll y1, ll x2, ll y2) const {
        T res = T(0);
        int l = (int)(lower_bound(xs.begin(), xs.end(), x1) - xs.begin()) + n;
        int r = (int)(upper_bound(xs.begin(), xs.end(), x2) - xs.begin()) + n;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) {
                const ll* first = ys.data() + off[l];
                int base = 2 * off[l], c = cnt[l];
                int lo = (int)(lower_bound(first, first + c, y1) - first) + c;
                int hi = (int)(upper_bound(first, first + c, y2) - first) + c;
                for (; lo < hi; lo >>= 1, hi >>= 1) {
                    if (lo & 1) res |= orr[base + lo++];
                    if (hi & 1) res |= orr[base + --hi];
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
                    if (lo & 1) res |= orr[base + lo++];
                    if (hi & 1) res |= orr[base + --hi];
                }
            }
        }
        return res;
    }

    // O(log^2 N) -- OR of the set points with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs x1 <= x2 and
    // y1 <= y2, else throws out_of_range
    T rectOr(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectOr: needs x1 <= x2 and y1 <= y2");
        return orOf(x1, y1, x2, y2);
    }

    // O(1) -- OR of every set point (0 if there are none)
    T orAll() const {
        return orr[2 * off[1] + 1];
    }
};
