// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-kd-tree-sum/template.cpp
#include <bits/stdc++.h>
using namespace std;
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectAdd rectAssign rectSum sumAll
// @data-structure-type: kd-tree
// @input: points
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rectAdd: sqrt(N)
//   rectAssign: sqrt(N)
//   rectSum: sqrt(N)
//   sumAll: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: sm[2*N]
//   tags: addTag[2*N] setTag[2*N]
//   other: xMin[2*N] xMax[2*N] yMin[2*N] yMax[2*N] pts[2*N] pos[1*N]
//   note: a binary tree over the points in k-d order (2N - 1 nodes), each node with its points' bounding box

// Sanitizers are skipped inside this template (its methods start with LEETCODE_NO_SANITIZE): where they run, like on
// LeetCode, that is most of its speed. The drawback: a bad memory access inside the template goes unreported. Arguments
// are still checked and still throw. Constructors are left alone. It needs GCC or Clang and C++17.

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

// K-d tree with lazy tags (sum): rectangle add and rectangle assign together with rectangle sum, over points known up
// front (any integers, negative is fine). O(sqrt N) per rectangle op, O(log N) per point op, linear memory. A tree of
// trees can't do rectangle updates with these queries (a tag can't be pushed down its outer tree); this can, because
// it is one tree: the points are split in half by x, each half by y, and so on, every node keeps the bounding box of
// its points, and a rectangle op only opens the nodes whose box the rectangle's border crosses (about sqrt N of
// them). The constructor takes every (x, y) that will ever be used; every point starts at 0. Rectangles are
// inclusive, x1..x2 by y1..y2, and their corners can be any integers; a rectangle update touches the given points
// inside it.
// T is any integer type (int, long long, ...); sums are kept in S (long long for a smaller T). Coordinates are long
// long.
template <typename T>
struct KdTree2D {
    using ll = long long;
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr ll LOW = numeric_limits<ll>::min(), HIGH = numeric_limits<ll>::max();  // no bound on a coordinate
    int n;
    HotVector<pair<ll, ll>> pts;
    HotVector<int> pos;  // pos[i]: where point i (in sorted order) sits in k-d order
    HotVector<ll> xMin, xMax, yMin, yMax;
    HotVector<T> addTag, setTag;
    HotVector<char> hasSet;
    unsigned long long seed = 1;  // for the random pivots of the build
    HotVector<S> sm;

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
        seed = chrono::steady_clock::now().time_since_epoch().count() | 1;
        vector<int> order(n);
        iota(order.begin(), order.end(), 0);
        buildNode(order.data(), 0, n - 1, 0);
    }

    // the number of the node for the stretch l..r of the k-d order
    LEETCODE_NO_SANITIZE static int id(int l, int r) { return (l + r) | (l != r); }

    // is point a before point b, by x then y (axis 0) or by y then x (axis 1)
    LEETCODE_NO_SANITIZE bool before(int a, int b, int axis) const {
        ll ka = axis ? pts[a].second : pts[a].first, kb = axis ? pts[b].second : pts[b].first;
        if (ka != kb) return ka < kb;
        return axis ? pts[a].first < pts[b].first : pts[a].second < pts[b].second;
    }

    // rearranges order[l..r] so the point that belongs at position mid is there, with everything before it in front:
    // quickselect around random pivots (random so that no input can make it slow), expected O(r - l)
    LEETCODE_NO_SANITIZE void splitAt(int* order, int l, int r, int mid, int axis) {
        while (l < r) {
            seed ^= seed << 13, seed ^= seed >> 7, seed ^= seed << 17;
            int pivot = order[l + (int)(seed % (unsigned long long)(r - l + 1))], i = l, j = r;
            while (i <= j) {
                while (before(order[i], pivot, axis)) i++;
                while (before(pivot, order[j], axis)) j--;
                if (i <= j) {
                    int held = order[i];
                    order[i++] = order[j], order[j--] = held;
                }
            }
            if (mid <= j) r = j;
            else if (mid >= i) l = i;
            else return;
        }
    }

    // order[l..r] holds this node's points: split them in half by x (axis 0) or by y, ties by the other coordinate
    LEETCODE_NO_SANITIZE void buildNode(int* order, int l, int r, int axis) {
        int node = id(l, r);
        ll loX = HIGH, hiX = LOW, loY = HIGH, hiY = LOW;
        for (int i = l; i <= r; i++) {
            ll x = pts[order[i]].first, y = pts[order[i]].second;
            if (x < loX) loX = x;
            if (x > hiX) hiX = x;
            if (y < loY) loY = y;
            if (y > hiY) hiY = y;
        }
        xMin[node] = loX, xMax[node] = hiX, yMin[node] = loY, yMax[node] = hiY;
        if (l == r) {
            pos[order[l]] = l;
            return;
        }
        int mid = (l + r) >> 1;
        splitAt(order, l, r, mid, axis);
        buildNode(order, l, mid, axis ^ 1);
        buildNode(order, mid + 1, r, axis ^ 1);
    }

    LEETCODE_NO_SANITIZE void applyAssign(int node, int cnt, T v) {
        hasSet[node] = 1, setTag[node] = v, addTag[node] = 0;
        sm[node] = S(v) * cnt;
    }

    LEETCODE_NO_SANITIZE void applyAdd(int node, int cnt, T v) {
        if (hasSet[node]) setTag[node] += v;
        else addTag[node] += v;
        sm[node] += S(v) * cnt;
    }

    // hands node (l, r)'s waiting assign / add to its two halves
    LEETCODE_NO_SANITIZE void push(int node, int l, int r) {
        if (!hasSet[node] && addTag[node] == 0) return;
        int mid = (l + r) >> 1;
        if (hasSet[node])
            applyAssign(id(l, mid), mid - l + 1, setTag[node]), applyAssign(id(mid + 1, r), r - mid, setTag[node]);
        else applyAdd(id(l, mid), mid - l + 1, addTag[node]), applyAdd(id(mid + 1, r), r - mid, addTag[node]);
        hasSet[node] = 0, addTag[node] = 0;
    }

    LEETCODE_NO_SANITIZE void pull(int node, int l, int r) {
        int mid = (l + r) >> 1, left = id(l, mid), right = id(mid + 1, r);
        sm[node] = sm[left] + sm[right];
    }

    LEETCODE_NO_SANITIZE bool outside(int node, ll x1, ll y1, ll x2, ll y2) const {
        return xMin[node] > x2 || xMax[node] < x1 || yMin[node] > y2 || yMax[node] < y1;
    }

    LEETCODE_NO_SANITIZE bool inside(int node, ll x1, ll y1, ll x2, ll y2) const {
        return x1 <= xMin[node] && xMax[node] <= x2 && y1 <= yMin[node] && yMax[node] <= y2;
    }

    // every given point inside the rectangle: assign v (isAssign) or add v
    LEETCODE_NO_SANITIZE void update(int l, int r, ll x1, ll y1, ll x2, ll y2, bool isAssign, T v) {
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

    LEETCODE_NO_SANITIZE void sumOver(int l, int r, ll x1, ll y1, ll x2, ll y2, S& res) {
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

    LEETCODE_NO_SANITIZE S sumOf(ll x1, ll y1, ll x2, ll y2) {
        S res = S(0);
        sumOver(0, n - 1, x1, y1, x2, y2, res);
        return res;
    }

    // where point (x, y) sits in k-d order, with every tag above it handed down first
    LEETCODE_NO_SANITIZE int open(ll x, ll y, const char* name) {
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
    LEETCODE_NO_SANITIZE void setLeaf(int l, int r, int p, T v) {
        if (l == r) {
            sm[id(l, r)] = v;
            return;
        }
        int mid = (l + r) >> 1;
        if (p <= mid) setLeaf(l, mid, p, v);
        else setLeaf(mid + 1, r, p, v);
        pull(id(l, r), l, r);
    }

    // O(log N) -- the value at (x, y); needs (x, y) to be one of the points given, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(ll x, ll y) {
        return T(sm[2 * open(x, y, "pointGet")]);
    }

    // O(log N) -- the point (x, y) becomes v; needs (x, y) to be one of the points given, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(ll x, ll y, T v) {
        int p = open(x, y, "pointAssign");
        setLeaf(0, n - 1, p, v);
    }

    // O(log N) -- adds v to the point (x, y); needs (x, y) to be one of the points given, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(ll x, ll y, T v) {
        int p = open(x, y, "pointAdd");
        setLeaf(0, n - 1, p, T(sm[2 * p] + v));
    }

    // O(log N) -- the point (x, y) becomes max(itself, v); needs (x, y) to be one of the points given, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(ll x, ll y, T v) {
        int p = open(x, y, "pointChmax");
        if (v > T(sm[2 * p])) setLeaf(0, n - 1, p, v);
    }

    // O(log N) -- the point (x, y) becomes min(itself, v); needs (x, y) to be one of the points given, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(ll x, ll y, T v) {
        int p = open(x, y, "pointChmin");
        if (v < T(sm[2 * p])) setLeaf(0, n - 1, p, v);
    }

    // O(sqrt N) -- adds v to every given point with x1 <= x <= x2 and y1 <= y <= y2; needs x1 <= x2 and y1 <= y2, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE void rectAdd(ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectAdd: needs x1 <= x2 and y1 <= y2");
        update(0, n - 1, x1, y1, x2, y2, false, v);
    }

    // O(sqrt N) -- every given point becomes v, for the points with x1 <= x <= x2 and y1 <= y <= y2; needs x1 <= x2 and
    // y1 <= y2, else throws out_of_range
    LEETCODE_NO_SANITIZE void rectAssign(ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectAssign: needs x1 <= x2 and y1 <= y2");
        update(0, n - 1, x1, y1, x2, y2, true, v);
    }

    // O(sqrt N) -- sum of the given points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); needs x1 <=
    // x2
    // and y1 <= y2, else throws out_of_range
    LEETCODE_NO_SANITIZE S rectSum(ll x1, ll y1, ll x2, ll y2) {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectSum: needs x1 <= x2 and y1 <= y2");
        return sumOf(x1, y1, x2, y2);
    }

    // O(1) -- sum of every point
    LEETCODE_NO_SANITIZE S sumAll() const {
        return sm[id(0, n - 1)];
    }
};
