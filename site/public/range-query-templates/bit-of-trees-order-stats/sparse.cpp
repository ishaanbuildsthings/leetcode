// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/bit-of-trees-order-stats/sparse.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin smallestGtX smallestGteX
// @data-structure-type: bit-of-trees
// @complexities:
//   countGtX: log(U)*log(U)
//   countGteX: log(U)*log(U)
//   countInValRange: log(U)*log(U)
//   countLtX: log(U)*log(U)
//   countLteX: log(U)*log(U)
//   countOccurrences: log(U)*log(U)
//   kthSmallest: log(U)*log(U)
//   largestLtX: log(U)*log(U)
//   largestLteX: log(U)*log(U)
//   pointAdd: log(U)*log(U)
//   pointAssign: log(U)*log(U)
//   pointChmax: log(U)*log(U)
//   pointChmin: log(U)*log(U)
//   pointGet: 1
//   rangeMax: log(U)*log(U)
//   rangeMin: log(U)*log(U)
//   smallestGtX: log(U)*log(U)
//   smallestGteX: log(U)*log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: L[1*log(U)*log(U)] R[1*log(U)*log(U)] C[1*log(U)*log(U)]
//   tags: none
//   other: root[1*log(U)] vals[1]
//   note: any index range [lo, hi], every position starting at 0; only nonzero values are stored, and the zeros of [l, r] are counted in closed form; U = the larger of the index range and the value range [valLo, valHi]; sizes are per point update

// a[l..r] as a sorted multiset, with point updates. A Fenwick tree (BIT) over the index range [lo, hi]: BIT node j is a dynamic
// value seg tree over [valLo, valHi] holding the values of a[j - lowbit(j) .. j - 1]. The multiset of a[l..r] is the BIT
// prefix of r + 1 minus the prefix of l, so a query walks down those ~2 log N value trees together (pos adds, neg
// subtracts). Values are integers; query arguments (x, lowVal, ...) can be anything.
// Sparse: every position of [lo, hi] starts at 0 and only nonzero values are stored; the zeros of [l, r] (its length
// minus the stored values in it) sit between the stored negatives and positives.
// T: int, long long, ....
template <typename T>
struct SparseDynamicOrderStats {
    struct SafeHash {
        size_t operator()(long long x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    long long lo, hi, vlo, vhi;
    unordered_map<long long, T, SafeHash> vals;     // nonzero values only
    unordered_map<long long, int, SafeHash> root;   // BIT node -> its value tree (missing: empty)
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        int L = 0;
        int R = 0;
        int C = 0;
    };
    vector<Node> nd;  // node 0 = the empty tree

    // O(1) -- indices: any integers in [lo, hi], every position starting at 0; every value a[i] ever holds must lie in
    // [valLo, valHi] (U = the larger of the two ranges' sizes)
    SparseDynamicOrderStats(long long lo, long long hi, long long valLo, long long valHi)
        : lo(lo), hi(hi), vlo(valLo), vhi(valHi), nd(1) {}

    // O(1) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return vals.count(i) ? vals.at(i) : T(0);
    }

    // O(logU * logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        T old = pointGet(i);
        if (v == old) return;
        if (old != T(0)) add(i, old, -1);
        if (v != T(0)) add(i, v, 1), vals[i] = v;
        else vals.erase(i);
    }

    // O(logU * logU) -- a[i] += v; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        pointAssign(i, pointGet(i) + v);
    }

    // O(logU * logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmax(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmax: needs lo <= i <= hi");
        pointAssign(i, max(pointGet(i), v));
    }

    // O(logU * logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmin(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmin: needs lo <= i <= hi");
        pointAssign(i, min(pointGet(i), v));
    }

    // O(logU * logU) -- # of i in [l, r] with a[i] == x; needs lo <= l <= r <= hi, else throws out_of_range
    long long countOccurrences(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countOccurrences: needs lo <= l <= r <= hi");
        return countInValRange(l, r, x, x);
    }

    // O(logU * logU) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs lo <= l <= r <= hi, else throws out_of_range
    long long countInValRange(long long l, long long r, T lowVal, T highVal) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countInValRange: needs lo <= l <= r <= hi");
        if (highVal < lowVal) return 0;
        return countBelow(l, r, ub(highVal)) - countBelow(l, r, lb(lowVal));
    }

    // O(logU * logU) -- # of values < x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    long long countLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countLtX: needs lo <= l <= r <= hi");
        return countBelow(l, r, lb(x));
    }

    // O(logU * logU) -- # of values <= x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    long long countLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countLteX: needs lo <= l <= r <= hi");
        return countBelow(l, r, ub(x));
    }

    // O(logU * logU) -- # of values > x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    long long countGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countGtX: needs lo <= l <= r <= hi");
        return r - l + 1 - countBelow(l, r, ub(x));
    }

    // O(logU * logU) -- # of values >= x in a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    long long countGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countGteX: needs lo <= l <= r <= hi");
        return r - l + 1 - countBelow(l, r, lb(x));
    }

    // O(logU * logU) -- the k-th smallest of a[l..r] (k = 1 is the min); needs lo <= l <= r <= hi and 1 <= k <= r - l + 1,
    // else throws out_of_range
    T kthSmallest(long long l, long long r, long long k) const {
        if (l < lo || l > r || r > hi) throw out_of_range("kthSmallest: needs lo <= l <= r <= hi");
        if (k < 1 || k > r - l + 1) throw out_of_range("kthSmallest: needs 1 <= k <= r - l + 1");
        return kth(l, r, k);
    }

    // O(logU * logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMin(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMin: needs lo <= l <= r <= hi");
        return kth(l, r, 1);
    }

    // O(logU * logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMax(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        return kth(l, r, r - l + 1);
    }

    // O(logU * logU) -- smallest value >= x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    optional<T> smallestGteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("smallestGteX: needs lo <= l <= r <= hi");
        long long c = countBelow(l, r, lb(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logU * logU) -- smallest value > x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    optional<T> smallestGtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("smallestGtX: needs lo <= l <= r <= hi");
        long long c = countBelow(l, r, ub(x));
        if (c == r - l + 1) return nullopt;
        return kth(l, r, c + 1);
    }

    // O(logU * logU) -- largest value <= x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    optional<T> largestLteX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("largestLteX: needs lo <= l <= r <= hi");
        long long c = countBelow(l, r, ub(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // O(logU * logU) -- largest value < x in a[l..r], or nullopt; needs lo <= l <= r <= hi, else throws out_of_range
    optional<T> largestLtX(long long l, long long r, T x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("largestLtX: needs lo <= l <= r <= hi");
        long long c = countBelow(l, r, lb(x));
        if (c == 0) return nullopt;
        return kth(l, r, c);
    }

    // ---- internals ----

    // a[i] = v gains d copies in every BIT node covering i
    void add(long long i, T v, int d) {
        for (long long j = i - lo + 1, m = hi - lo + 1; j <= m; j += j & -j) {
            auto it = root.find(j);
            int t = ins(it == root.end() ? 0 : it->second, v, d);
            root[j] = t;
        }
    }

    // trees to add / subtract for a[l..r]; returns the zeros in a[l..r]
    long long sides(long long l, long long r, vector<int>& pos, vector<int>& neg) const {
        for (long long j = r - lo + 1; j; j &= j - 1) if (auto it = root.find(j); it != root.end()) pos.push_back(it->second);
        for (long long j = l - lo; j; j &= j - 1) if (auto it = root.find(j); it != root.end()) neg.push_back(it->second);
        return (r - l + 1) - total(pos, neg, [&](int t) { return nd[t].C; });
    }

    // # of stored (nonzero) values < x
    long long storedBelow(const vector<int>& pos, const vector<int>& neg, long long x) const {
        if (x <= vlo) return 0;
        if (x > vhi) return total(pos, neg, [&](int t) { return nd[t].C; });
        return belowIn(pos, neg, x);
    }

    // the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    T kth(long long l, long long r, long long k) const {
        vector<int> pos, neg;
        long long zeros = sides(l, r, pos, neg), negs = storedBelow(pos, neg, 0);
        if (k <= negs) return kthIn(pos, neg, k);
        if (k <= negs + zeros) return T(0);
        return kthIn(pos, neg, k - zeros);
    }

    // # of values < x in a[l..r]
    long long countBelow(long long l, long long r, long long x) const {
        vector<int> pos, neg;
        long long zeros = sides(l, r, pos, neg);
        return storedBelow(pos, neg, x) + (0 < x ? zeros : 0);
    }

    // ---- internals: walks over the value trees in pos (added) and neg (subtracted) ----

    // a value threshold as "values < this": lb(x) = x, ub(x) = x + 1 (integers)
    static long long lb(T x) { return (long long)x; }
    static long long ub(T x) { return (long long)x + 1; }

    int newNode() {
        Node n;
        n.L = 0, n.R = 0, n.C = 0;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    // tree t (0: a new one) with d more copies of v
    int ins(int t, T v, int d) {
        if (!t) t = newNode();
        int top = t;
        long long nl = vlo, nh = vhi;
        while (true) {
            nd[t].C += d;
            if (nl == nh) return top;
            long long mid = nl + (nh - nl) / 2;
            if (v <= mid) {
                if (!nd[t].L) { int x = newNode(); nd[t].L = x; }
                t = nd[t].L, nh = mid;
            } else {
                if (!nd[t].R) { int x = newNode(); nd[t].R = x; }
                t = nd[t].R, nl = mid + 1;
            }
        }
    }

    // get(t): node t's field
    template <class F> auto total(const vector<int>& pos, const vector<int>& neg, F get) const {
        decltype(get(0)) s = 0;
        for (int t : pos) s += get(t);
        for (int t : neg) s -= get(t);
        return s;
    }
    void goLeft(vector<int>& v) const { for (int& t : v) t = nd[t].L; }
    void goRight(vector<int>& v) const { for (int& t : v) t = nd[t].R; }
    long long leftCount(const vector<int>& pos, const vector<int>& neg) const {
        long long c = 0;
        for (int t : pos) c += nd[nd[t].L].C;
        for (int t : neg) c -= nd[nd[t].L].C;
        return c;
    }

    // the k-th smallest value, 1 <= k <= the trees' count
    T kthIn(vector<int> pos, vector<int> neg, long long k) const {
        long long nl = vlo, nh = vhi;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2, c = leftCount(pos, neg);
            if (k <= c) goLeft(pos), goLeft(neg), nh = mid;
            else k -= c, goRight(pos), goRight(neg), nl = mid + 1;
        }
        return T(nl);
    }

    // # of values < x, valLo < x <= valHi
    long long belowIn(vector<int> pos, vector<int> neg, long long x) const {
        long long nl = vlo, nh = vhi, cnt = 0;
        while (nl != nh) {
            long long mid = nl + (nh - nl) / 2;
            if (x <= mid) goLeft(pos), goLeft(neg), nh = mid;
            else {  // the whole left half is below x
                cnt += leftCount(pos, neg);
                goRight(pos), goRight(neg), nl = mid + 1;
            }
        }
        return cnt;
    }
};
