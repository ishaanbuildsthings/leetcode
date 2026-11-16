// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-kd-tree-sum-min/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: minAll minGteGte minGteLte minLteGte minLteLte pointAdd pointAssign pointChmax pointChmin pointGet rectAdd rectAssign rectMin rectSum sumAll
// @data-structure-type: kd-tree
// @input: points
// @complexities:
//   minAll: 1
//   minGteGte: sqrt(N)
//   minGteLte: sqrt(N)
//   minLteGte: sqrt(N)
//   minLteLte: sqrt(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rectAdd: sqrt(N)
//   rectAssign: sqrt(N)
//   rectMin: sqrt(N)
//   rectSum: sqrt(N)
//   sumAll: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: sm[2*N] mn[2*N]
//   tags: addTag[2*N] setTag[2*N]
//   other: xMin[2*N] xMax[2*N] yMin[2*N] yMax[2*N] pts[2*N] pos[1*N]
//   note: a binary tree over the points in k-d order (2N - 1 nodes), each node with its points' bounding box

// K-d tree with lazy tags (sum, min): rectangle add and rectangle assign together with rectangle sum, min, over
// points known up front (any integers, negative is fine). O(sqrt N) per rectangle op, O(log N) per point op, linear
// memory. A tree of trees can't do rectangle updates with these queries (a tag can't be pushed down its outer tree);
// this can, because it is one tree: the points are split in half by x, each half by y, and so on, every node keeps
// the bounding box of its points, and a rectangle op only opens the nodes whose box the rectangle's border crosses
// (about sqrt N of them). The constructor takes every (x, y) that will ever be used; every point starts at 0.
// Rectangles are inclusive, x1..x2 by y1..y2, and their corners can be any integers; a rectangle update touches the
// given points inside it. A min / max over a rectangle with no given point in it is NO_MIN.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T). Coordinates are long
// long.
template <typename T>
struct KdTree2D {
    using ll = long long;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NO_MIN = numeric_limits<T>::max();  // what a min over no point gives
    static constexpr ll LOW = numeric_limits<ll>::min(), HIGH = numeric_limits<ll>::max();  // no bound on a coordinate
    int n;
    vector<pair<ll, ll>> pts;
    vector<int> pos;  // pos[i]: where point i (in sorted order) sits in k-d order
    vector<ll> xMin, xMax, yMin, yMax;
    vector<T> addTag, setTag;
    vector<char> hasSet;
    vector<S> sm;
    vector<T> mn;

    // O(N log N) -- points: every (x, y) that will ever be used (negative is fine, repeats are fine); needs at least
    // one,
    // else throws invalid_argument
    explicit KdTree2D(vector<pair<ll, ll>> points) : pts(std::move(points)) {
        if (pts.empty()) throw invalid_argument("KdTree2D: needs at least one point");
        sort(pts.begin(), pts.end());
        pts.erase(unique(pts.begin(), pts.end()), pts.end());
        n = (int)pts.size();
        size_t size = 2 * (size_t)n;
        xMin.assign(size, 0), xMax.assign(size, 0), yMin.assign(size, 0), yMax.assign(size, 0);
        pos.assign(n, 0);
        addTag.assign(size, T(0)), setTag.assign(size, T(0)), hasSet.assign(size, 0);
        sm.assign(size, 0);
        mn.assign(size, 0);
        vector<int> order(n);
        iota(order.begin(), order.end(), 0);
        build(order, 0, n - 1, 0);
    }

    // the number of the node for the stretch l..r of the k-d order
    static int id(int l, int r) { return (l + r) | (l != r); }

    // order[l..r] holds this node's points: split them in half by x (axis 0) or by y, ties by the other coordinate
    void build(vector<int>& order, int l, int r, int axis) {
        int node = id(l, r);
        xMin[node] = yMin[node] = HIGH, xMax[node] = yMax[node] = LOW;
        for (int i = l; i <= r; i++) {
            auto [x, y] = pts[order[i]];
            xMin[node] = min(xMin[node], x), xMax[node] = max(xMax[node], x);
            yMin[node] = min(yMin[node], y), yMax[node] = max(yMax[node], y);
        }
        if (l == r) {
            pos[order[l]] = l;
            return;
        }
        int mid = (l + r) >> 1;
        nth_element(order.begin() + l, order.begin() + mid, order.begin() + r + 1, [&](int a, int b) {
            if (axis == 0) return pts[a] < pts[b];
            return make_pair(pts[a].second, pts[a].first) < make_pair(pts[b].second, pts[b].first);
        });
        build(order, l, mid, axis ^ 1);
        build(order, mid + 1, r, axis ^ 1);
    }

    void applyAssign(int node, int cnt, T v) {
        hasSet[node] = 1, setTag[node] = v, addTag[node] = 0;
        sm[node] = S(v) * cnt;
        mn[node] = v;
    }

    void applyAdd(int node, int cnt, T v) {
        if (hasSet[node]) setTag[node] += v;
        else addTag[node] += v;
        sm[node] += S(v) * cnt;
        mn[node] += v;
    }

    // hands node (l, r)'s waiting assign / add to its two halves
    void push(int node, int l, int r) {
        if (!hasSet[node] && addTag[node] == 0) return;
        int mid = (l + r) >> 1;
        if (hasSet[node])
            applyAssign(id(l, mid), mid - l + 1, setTag[node]), applyAssign(id(mid + 1, r), r - mid, setTag[node]);
        else applyAdd(id(l, mid), mid - l + 1, addTag[node]), applyAdd(id(mid + 1, r), r - mid, addTag[node]);
        hasSet[node] = 0, addTag[node] = 0;
    }

    void pull(int node, int l, int r) {
        int mid = (l + r) >> 1, left = id(l, mid), right = id(mid + 1, r);
        sm[node] = sm[left] + sm[right];
        mn[node] = min(mn[left], mn[right]);
    }

    bool outside(int node, ll x1, ll y1, ll x2, ll y2) const {
        return xMin[node] > x2 || xMax[node] < x1 || yMin[node] > y2 || yMax[node] < y1;
    }

    bool inside(int node, ll x1, ll y1, ll x2, ll y2) const {
        return x1 <= xMin[node] && xMax[node] <= x2 && y1 <= yMin[node] && yMax[node] <= y2;
    }

    // every given point inside the rectangle: assign v (isAssign) or add v
    void update(int l, int r, ll x1, ll y1, ll x2, ll y2, bool isAssign, T v) {
        int node = id(l, r);
        if (outside(node, x1, y1, x2, y2)) return;
        if (inside(node, x1, y1, x2, y2)) {
            if (isAssign) applyAssign(node, r - l + 1, v);
            else applyAdd(node, r - l + 1, v);
            return;
        }
        push(node, l, r);
        int mid = (l + r) >> 1;
        update(l, mid, x1, y1, x2, y2, isAssign, v);
        update(mid + 1, r, x1, y1, x2, y2, isAssign, v);
        pull(node, l, r);
    }

    void sumOver(int l, int r, ll x1, ll y1, ll x2, ll y2, S& res) {
        int node = id(l, r);
        if (outside(node, x1, y1, x2, y2)) return;
        if (inside(node, x1, y1, x2, y2)) {
            res += sm[node];
            return;
        }
        push(node, l, r);
        int mid = (l + r) >> 1;
        sumOver(l, mid, x1, y1, x2, y2, res);
        sumOver(mid + 1, r, x1, y1, x2, y2, res);
    }

    S sumOf(ll x1, ll y1, ll x2, ll y2) {
        S res = S(0);
        sumOver(0, n - 1, x1, y1, x2, y2, res);
        return res;
    }

    void minOver(int l, int r, ll x1, ll y1, ll x2, ll y2, T& res) {
        int node = id(l, r);
        if (outside(node, x1, y1, x2, y2)) return;
        if (inside(node, x1, y1, x2, y2)) {
            res = min(res, mn[node]);
            return;
        }
        push(node, l, r);
        int mid = (l + r) >> 1;
        minOver(l, mid, x1, y1, x2, y2, res);
        minOver(mid + 1, r, x1, y1, x2, y2, res);
    }

    T minOf(ll x1, ll y1, ll x2, ll y2) {
        T res = NO_MIN;
        minOver(0, n - 1, x1, y1, x2, y2, res);
        return res;
    }

    // where point (x, y) sits in k-d order, with every tag above it handed down first
    int open(ll x, ll y, const char* name) {
        auto it = lower_bound(pts.begin(), pts.end(), make_pair(x, y));
        if (it == pts.end() || *it != make_pair(x, y))
            throw out_of_range(string(name) + ": (x, y) is not one of the points given to the constructor");
        int p = pos[it - pts.begin()];
        for (int l = 0, r = n - 1; l < r;) {
            push(id(l, r), l, r);
            int mid = (l + r) >> 1;
            if (p <= mid) r = mid;
            else l = mid + 1;
        }
        return p;
    }

    // the point at k-d position p becomes v, then every node above it
    void setLeaf(int l, int r, int p, T v) {
        if (l == r) {
            sm[id(l, r)] = v;
            mn[id(l, r)] = v;
            return;
        }
        int mid = (l + r) >> 1;
        if (p <= mid) setLeaf(l, mid, p, v);
        else setLeaf(mid + 1, r, p, v);
        pull(id(l, r), l, r);
    }

    // O(log N) -- the value at (x, y); needs (x, y) to be one of the points given, else throws out_of_range
    T pointGet(ll x, ll y) {
        return T(sm[2 * open(x, y, "pointGet")]);
    }

    // O(log N) -- the point (x, y) becomes v; needs (x, y) to be one of the points given, else throws out_of_range
    void pointAssign(ll x, ll y, T v) {
        int p = open(x, y, "pointAssign");
        setLeaf(0, n - 1, p, v);
    }

    // O(log N) -- adds v to the point (x, y); needs (x, y) to be one of the points given, else throws out_of_range
    void pointAdd(ll x, ll y, T v) {
        int p = open(x, y, "pointAdd");
        setLeaf(0, n - 1, p, T(sm[2 * p] + v));
    }

    // O(log N) -- the point (x, y) becomes max(itself, v); needs (x, y) to be one of the points given, else throws
    // out_of_range
    void pointChmax(ll x, ll y, T v) {
        int p = open(x, y, "pointChmax");
        if (v > T(sm[2 * p])) setLeaf(0, n - 1, p, v);
    }

    // O(log N) -- the point (x, y) becomes min(itself, v); needs (x, y) to be one of the points given, else throws
    // out_of_range
    void pointChmin(ll x, ll y, T v) {
        int p = open(x, y, "pointChmin");
        if (v < T(sm[2 * p])) setLeaf(0, n - 1, p, v);
    }

    // O(sqrt N) -- adds v to every given point with x1 <= x <= x2 and y1 <= y <= y2; needs x1 <= x2 and y1 <= y2, else
    // throws out_of_range
    void rectAdd(ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectAdd: needs x1 <= x2 and y1 <= y2");
        update(0, n - 1, x1, y1, x2, y2, false, v);
    }

    // O(sqrt N) -- every given point becomes v, for the points with x1 <= x <= x2 and y1 <= y <= y2; needs x1 <= x2 and
    // y1 <= y2, else throws out_of_range
    void rectAssign(ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectAssign: needs x1 <= x2 and y1 <= y2");
        update(0, n - 1, x1, y1, x2, y2, true, v);
    }

    // O(sqrt N) -- sum of the given points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); needs x1 <=
    // x2
    // and y1 <= y2, else throws out_of_range
    S rectSum(ll x1, ll y1, ll x2, ll y2) {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectSum: needs x1 <= x2 and y1 <= y2");
        return sumOf(x1, y1, x2, y2);
    }

    // O(1) -- sum of every point
    S sumAll() const {
        return sm[id(0, n - 1)];
    }

    // O(sqrt N) -- min of the given points with x1 <= x <= x2 and y1 <= y <= y2 (NO_MIN if no point is there); needs x1
    // <= x2 and y1 <= y2, else throws out_of_range
    T rectMin(ll x1, ll y1, ll x2, ll y2) {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectMin: needs x1 <= x2 and y1 <= y2");
        return minOf(x1, y1, x2, y2);
    }

    // O(1) -- min of every point
    T minAll() const {
        return mn[id(0, n - 1)];
    }

    // O(sqrt N) -- min of the given points with x <= the given x and y <= the given y (NO_MIN if there are none); any
    // integers
    T minLteLte(ll x, ll y) {
        return minOf(LOW, LOW, x, y);
    }

    // O(sqrt N) -- min of the given points with x <= the given x and y >= the given y (NO_MIN if there are none); any
    // integers
    T minLteGte(ll x, ll y) {
        return minOf(LOW, y, x, HIGH);
    }

    // O(sqrt N) -- min of the given points with x >= the given x and y <= the given y (NO_MIN if there are none); any
    // integers
    T minGteLte(ll x, ll y) {
        return minOf(x, LOW, HIGH, y);
    }

    // O(sqrt N) -- min of the given points with x >= the given x and y >= the given y (NO_MIN if there are none); any
    // integers
    T minGteGte(ll x, ll y) {
        return minOf(x, y, HIGH, HIGH);
    }
};
