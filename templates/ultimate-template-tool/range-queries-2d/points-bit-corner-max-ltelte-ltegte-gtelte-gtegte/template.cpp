// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-bit-corner-max-ltelte-ltegte-gtelte-gtegte/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: maxAll maxGteGte maxGteLte maxLteGte maxLteLte pointChmax
// @data-structure-type: BIT
// @input: points
// @empty-cells: yes
// @complexities:
//   maxAll: 1
//   maxGteGte: log^2(N)
//   maxGteLte: log^2(N)
//   maxLteGte: log^2(N)
//   maxLteLte: log^2(N)
//   pointChmax: log^2(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: tree[4*N*log(N)]
//   tags: none
//   other: ys[4*N*log(N)] xs[4*N] off[4*N] cnt[4*N] pts[2*N]
//   note: one Fenwick-of-Fenwicks per corner direction asked for (a >= direction is the same structure on negated coordinates)

// Corner max over points known up front, with Fenwick trees: pointChmax at a point and the max over a corner of the
// plane (every point with x <= or >= a given x, and y <= or >= a given y) in O(log^2 N), with N log N memory per
// direction whatever the coordinates are (any integers, negative is fine). The constructor takes every (x, y) that
// will ever be updated. This works because values only move one way: a point can only go up, so a tree entry never
// has to forget a value; for a point that can move both ways, or for rectangles that aren't corners, use the segment
// tree version. Every point starts empty and queries only see points that have been set. A max over no set point is
// NO_MAX.
// T is any integer type (int, long long, ...). Coordinates are long long.
template <typename T>
struct PointsCornerMaxFenwick2D {
    using ll = long long;
    static constexpr T NO_MAX = numeric_limits<T>::min();  // what a max over no set point gives

    // max over the points with x <= a given x and y <= a given y, values only going up
    struct Prefix {
        int n = 0;
        vector<ll> xs, ys;
        vector<int> off, cnt;
        vector<T> tree;

        void build(vector<pair<ll, ll>> pts) {
            sort(pts.begin(), pts.end());
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
            tree.assign(ys.size(), NO_MAX);
        }

        void improve(ll x, ll y, T v) {
            for (int k = (int)(lower_bound(xs.begin(), xs.end(), x) - xs.begin()) + 1; k <= n; k += k & -k) {
                const ll* first = ys.data() + off[k];
                T* t = tree.data() + off[k] - 1;
                for (int j = (int)(lower_bound(first, first + cnt[k], y) - first) + 1; j <= cnt[k]; j += j & -j)
                    t[j] = max(t[j], v);
            }
        }

        T best(ll x, ll y) const {
            T res = NO_MAX;
            for (int k = (int)(upper_bound(xs.begin(), xs.end(), x) - xs.begin()); k > 0; k &= k - 1) {
                const ll* first = ys.data() + off[k];
                const T* t = tree.data() + off[k] - 1;
                for (int j = (int)(upper_bound(first, first + cnt[k], y) - first); j > 0; j &= j - 1)
                    res = max(res, t[j]);
            }
            return res;
        }
    };

    vector<pair<ll, ll>> pts;
    T top = NO_MAX;
    Prefix tLteLte, tLteGte, tGteLte, tGteGte;

    // O(N log N) -- points: every (x, y) that will ever be updated (negative is fine, repeats are fine); needs at least
    // one, else throws invalid_argument
    explicit PointsCornerMaxFenwick2D(vector<pair<ll, ll>> points) : pts(std::move(points)) {
        if (pts.empty()) throw invalid_argument("PointsCornerMaxFenwick2D: needs at least one point");
        sort(pts.begin(), pts.end());
        pts.erase(unique(pts.begin(), pts.end()), pts.end());
        tLteLte.build(pts);
        {
            auto flipped = pts;
            for (auto& p : flipped) p = {p.first, -p.second};
            tLteGte.build(std::move(flipped));
        }
        {
            auto flipped = pts;
            for (auto& p : flipped) p = {-p.first, p.second};
            tGteLte.build(std::move(flipped));
        }
        {
            auto flipped = pts;
            for (auto& p : flipped) p = {-p.first, -p.second};
            tGteGte.build(std::move(flipped));
        }
    }

    // O(log^2 N) -- the point (x, y) becomes max(itself, v); an empty point becomes v; needs (x, y) to be one of the
    // points given, else throws out_of_range
    void pointChmax(ll x, ll y, T v) {
        if (!binary_search(pts.begin(), pts.end(), make_pair(x, y)))
            throw out_of_range("pointChmax: (x, y) is not one of the points given to the constructor");
        top = max(top, v);
        tLteLte.improve(x, y, v);
        tLteGte.improve(x, -y, v);
        tGteLte.improve(-x, y, v);
        tGteGte.improve(-x, -y, v);
    }

    // O(log^2 N) -- max of the set points with x <= the given x and y <= the given y (NO_MAX if there are none); any
    // integers
    T maxLteLte(ll x, ll y) const {
        return tLteLte.best(x, y);
    }

    // O(log^2 N) -- max of the set points with x <= the given x and y >= the given y (NO_MAX if there are none); any
    // integers
    T maxLteGte(ll x, ll y) const {
        return tLteGte.best(x, -y);
    }

    // O(log^2 N) -- max of the set points with x >= the given x and y <= the given y (NO_MAX if there are none); any
    // integers
    T maxGteLte(ll x, ll y) const {
        return tGteLte.best(-x, y);
    }

    // O(log^2 N) -- max of the set points with x >= the given x and y >= the given y (NO_MAX if there are none); any
    // integers
    T maxGteGte(ll x, ll y) const {
        return tGteGte.best(-x, -y);
    }

    // O(1) -- max of every set point (NO_MAX if there are none)
    T maxAll() const {
        return top;
    }
};
