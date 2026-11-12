// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/merge-sort-tree-updates-offline-sums-xor/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countGtX countGteX countInValRange countLtX countLteX getAll largestLtX largestLteX pointAssign pointGet smallestGtX smallestGteX sumAbsDiffToX sumGtX sumGteX sumInValRange sumLtX sumLteX xorGtX xorGteX xorInValRange xorLtX xorLteX
// @data-structure-type: merge-sort-tree
// @fractional-cascading: no
// @values: offline
// @complexities:
//   countGtX: log^2(N)
//   countGteX: log^2(N)
//   countInValRange: log^2(N)
//   countLtX: log^2(N)
//   countLteX: log^2(N)
//   getAll: N
//   largestLtX: log^2(N)
//   largestLteX: log^2(N)
//   pointAssign: log^2(N)
//   pointGet: 1
//   smallestGtX: log^2(N)
//   smallestGteX: log^2(N)
//   sumAbsDiffToX: log^2(N)
//   sumGtX: log^2(N)
//   sumGteX: log^2(N)
//   sumInValRange: log^2(N)
//   sumLtX: log^2(N)
//   sumLteX: log^2(N)
//   xorGtX: log^2(N)
//   xorGteX: log^2(N)
//   xorInValRange: log^2(N)
//   xorLtX: log^2(N)
//   xorLteX: log^2(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: vals[1*N*log(N)] counts[1*N*log(N)] sums[1*N*log(N)] xors[1*N*log(N)]
//   tags: none
//   other: A[1*N] total[2*N] xorTotal[2*N] start[1*N] nodeSize[2*N]
//   note: the constructor takes every (i, v) a pointAssign will ever use, so N is the array length plus that list's length; worst-case bounds and flat arrays, the fastest of these

// Merge sort tree with point updates: a segment tree over positions (bottom-up: node p >= n is a[p - n]), each inner
// node keeping its positions' values in a searchable structure (the sorted values its positions can ever hold, with
// Fenwick trees over them). a[l..r] is O(log n) nodes, and a point update changes one value in each of the O(log n)
// nodes above it. All indices 0-based, ranges inclusive.
// Offline: the constructor takes every (i, v) that a pointAssign will ever use (read every query first). For adds
// or chmax / chmin, work out the new value yourself and list that.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct MergeSortTreeOffline {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    vector<T> A;
    vector<S> total;  // total[p]: sum of node p's values
    vector<T> xorTotal;  // xorTotal[p]: xor of node p's values
    // node p's possible values are vals[start[p] .. start[p + 1]); its Fenwick slots 1 .. size sit at
    vector<int> start;
                        // fenStart(p) + 1 .. fenStart(p) + size
    vector<T> vals;
    vector<int> counts;  // Fenwick trees of copies, one per node
    vector<S> sums;  // Fenwick trees of sums
    vector<T> xors;  // Fenwick trees of xors
    vector<int> nodeSize;  // nodeSize[p]: how many positions node p covers

    // O(build) -- arr: the initial array. updates: every (i, v) that pointAssign will ever be called with (any order,
    // repeats fine); a pointAssign with a pair not listed throws invalid_argument
    MergeSortTreeOffline(const vector<T>& arr, const vector<pair<int, T>>& updates) {
        n = (int)arr.size();
        A = arr;
        vector<vector<T>> possible(2 * n);  // node p's possible values, sorted, distinct
        vector<vector<int>> copiesNow(2 * n);  // and how many positions under p hold each right now
        for (int i = 0; i < n; i++) possible[n + i] = {A[i]};
        for (const auto& [i, v] : updates) {
            if (i < 0 || i >= n) throw out_of_range("MergeSortTreeOffline: every listed update needs 0 <= i < n");
            possible[n + i].push_back(v);
        }
        for (int i = 0; i < n; i++) {
            vector<T>& here = possible[n + i];
            sort(here.begin(), here.end());
            here.erase(unique(here.begin(), here.end()), here.end());
            copiesNow[n + i].assign(here.size(), 0);
            copiesNow[n + i][lower_bound(here.begin(), here.end(), A[i]) - here.begin()] = 1;
        }
        nodeSize.assign(2 * n, 1);
        for (int p = n - 1; p >= 1; p--) {  // merge the children's lists, adding up the copies
            nodeSize[p] = nodeSize[2 * p] + nodeSize[2 * p + 1];
            const vector<T>& a = possible[2 * p];
            const vector<T>& b = possible[2 * p + 1];
            const vector<int>& ca = copiesNow[2 * p];
            const vector<int>& cb = copiesNow[2 * p + 1];
            size_t x = 0, y = 0;
            while (x < a.size() || y < b.size()) {
                if (y == b.size() || (x < a.size() && a[x] < b[y])) {
                    possible[p].push_back(a[x]), copiesNow[p].push_back(ca[x++]);
                } else if (x == a.size() || b[y] < a[x]) {
                    possible[p].push_back(b[y]), copiesNow[p].push_back(cb[y++]);
                } else {
                    possible[p].push_back(a[x]), copiesNow[p].push_back(ca[x++] + cb[y++]);
                }
            }
            if (2 * p >= n) vector<T>().swap(possible[2 * p]), vector<int>().swap(copiesNow[2 * p]);
            if (2 * p + 1 >= n) vector<T>().swap(possible[2 * p + 1]), vector<int>().swap(copiesNow[2 * p + 1]);
        }
        start.assign(n + 1, 0);
        for (int p = 1; p < n; p++) start[p + 1] = start[p] + (int)possible[p].size();
        vals.resize(start[n]);
        size_t slots = (size_t)start[n] + n;
        counts.assign(slots, 0);
        sums.assign(slots, 0);
        xors.assign(slots, 0);
        for (int p = 1; p < n; p++) {
            int size = (int)possible[p].size(), f = fenStart(p);
            for (int j = 0; j < size; j++) {
                T v = possible[p][j];
                int c = copiesNow[p][j];
                vals[start[p] + j] = v;
                counts[f + j + 1] = c;
                sums[f + j + 1] = S(v) * c;
                xors[f + j + 1] = c & 1 ? v : T(0);
            }
            for (int j = 1; j <= size; j++) {  // (each slot into the Fenwick tree in O(1))
                int up = j + (j & -j);
                if (up <= size) {
                    counts[f + up] += counts[f + j];
                    sums[f + up] += sums[f + j];
                    xors[f + up] ^= xors[f + j];
                }
            }
            vector<T>().swap(possible[p]);
            vector<int>().swap(copiesNow[p]);
        }
        buildTotals();
    }

    // O(n) -- the whole array
    vector<T> getAll() const { return vector<T>(A.begin(), A.end()); }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return A[i];
    }

    // O(log^2(N)) -- a[i] = v (overwrite); needs 0 <= i < n, else throws out_of_range, and (i, v) listed in the
    // constructor's updates (or v == a[i]), else throws invalid_argument
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        T old = A[i];
        if (old == v) return;
        if (n > 1 && !listed((i + n) >> 1,
            v)) throw invalid_argument("pointAssign: (i, v) was not in the constructor's updates");
        for (int p = (i + n) >> 1; p >= 1; p >>= 1) {
            add(p, old, -1);
            add(p, v, 1);
            total[p] += S(v) - S(old);
            xorTotal[p] ^= old ^ v;
        }
        A[i] = v;
    }

    // O(log^2(N)) -- # of i in [l, r] with a[i] < x; needs 0 <= l <= r < n, else throws out_of_range
    long long countLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLtX: needs 0 <= l <= r < n");
        return countLess(l, r, x, true);
    }

    // O(log^2(N)) -- # of i in [l, r] with a[i] <= x; needs 0 <= l <= r < n, else throws out_of_range
    long long countLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countLteX: needs 0 <= l <= r < n");
        return countLess(l, r, x, false);
    }

    // O(log^2(N)) -- # of i in [l, r] with a[i] > x; needs 0 <= l <= r < n, else throws out_of_range
    long long countGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGtX: needs 0 <= l <= r < n");
        return (r - l + 1) - countLess(l, r, x, false);
    }

    // O(log^2(N)) -- # of i in [l, r] with a[i] >= x; needs 0 <= l <= r < n, else throws out_of_range
    long long countGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countGteX: needs 0 <= l <= r < n");
        return (r - l + 1) - countLess(l, r, x, true);
    }

    // O(log^2(N)) -- # of i in [l, r] with lowVal <= a[i] <= highVal (0 if lowVal > highVal); needs 0 <= l <= r < n,
    // else throws out_of_range
    long long countInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("countInValRange: needs 0 <= l <= r < n");
        if (lowVal > highVal) return 0;
        return countLess(l, r, highVal, false) - countLess(l, r, lowVal, true);
    }

    // O(log^2(N)) -- smallest a[i] >= x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws
    // out_of_range
    optional<T> smallestGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGteX: needs 0 <= l <= r < n");
        return firstAtLeast(l, r, x, false);
    }

    // O(log^2(N)) -- smallest a[i] > x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws
    // out_of_range
    optional<T> smallestGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("smallestGtX: needs 0 <= l <= r < n");
        return firstAtLeast(l, r, x, true);
    }

    // O(log^2(N)) -- largest a[i] <= x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws
    // out_of_range
    optional<T> largestLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLteX: needs 0 <= l <= r < n");
        return lastBelow(l, r, x, false);
    }

    // O(log^2(N)) -- largest a[i] < x in [l, r]; nullopt if there is none; needs 0 <= l <= r < n, else throws
    // out_of_range
    optional<T> largestLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("largestLtX: needs 0 <= l <= r < n");
        return lastBelow(l, r, x, true);
    }

    // O(log^2(N)) -- sum of a[i] < x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLtX: needs 0 <= l <= r < n");
        return sumLess(l, r, x, true);
    }

    // O(log^2(N)) -- sum of a[i] <= x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumLteX: needs 0 <= l <= r < n");
        return sumLess(l, r, x, false);
    }

    // O(log^2(N)) -- sum of a[i] > x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGtX: needs 0 <= l <= r < n");
        return sumAll(l, r) - sumLess(l, r, x, false);
    }

    // O(log^2(N)) -- sum of a[i] >= x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumGteX: needs 0 <= l <= r < n");
        return sumAll(l, r) - sumLess(l, r, x, true);
    }

    // O(log^2(N)) -- sum of a[i] with lowVal <= a[i] <= highVal in [l, r] (0 if lowVal > highVal); needs 0 <= l <= r <
    // n, else throws out_of_range
    S sumInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumInValRange: needs 0 <= l <= r < n");
        if (lowVal > highVal) return 0;
        return sumLess(l, r, highVal, false) - sumLess(l, r, lowVal, true);
    }

    // O(log^2(N)) -- sum of |a[i] - x| over [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    S sumAbsDiffToX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("sumAbsDiffToX: needs 0 <= l <= r < n");
        long long below = countLess(l, r, x, true);
        S belowSum = sumLess(l, r, x, true), total = sumAll(l, r);
        return S(x) * below - belowSum + (total - belowSum) - S(x) * ((r - l + 1) - below);
    }

    // O(log^2(N)) -- xor of a[i] < x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    T xorLtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorLtX: needs 0 <= l <= r < n");
        return xorLess(l, r, x, true);
    }

    // O(log^2(N)) -- xor of a[i] <= x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    T xorLteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorLteX: needs 0 <= l <= r < n");
        return xorLess(l, r, x, false);
    }

    // O(log^2(N)) -- xor of a[i] > x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    T xorGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorGtX: needs 0 <= l <= r < n");
        return xorAll(l, r) ^ xorLess(l, r, x, false);
    }

    // O(log^2(N)) -- xor of a[i] >= x in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    T xorGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorGteX: needs 0 <= l <= r < n");
        return xorAll(l, r) ^ xorLess(l, r, x, true);
    }

    // O(log^2(N)) -- xor of a[i] with lowVal <= a[i] <= highVal in [l, r] (0 if lowVal > highVal); needs 0 <= l <= r <
    // n, else throws out_of_range
    T xorInValRange(int l, int r, T lowVal, T highVal) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("xorInValRange: needs 0 <= l <= r < n");
        if (lowVal > highVal) return 0;
        return xorLess(l, r, highVal, false) ^ xorLess(l, r, lowVal, true);
    }

    // ---- internals ----

    void buildTotals() {  // the sum / xor of every node's values
        total.assign(2 * n, 0);
        for (int i = 0; i < n; i++) total[n + i] = A[i];
        for (int p = n - 1; p >= 1; p--) total[p] = total[2 * p] + total[2 * p + 1];
        xorTotal.assign(2 * n, 0);
        for (int i = 0; i < n; i++) xorTotal[n + i] = A[i];
        for (int p = n - 1; p >= 1; p--) xorTotal[p] = xorTotal[2 * p] ^ xorTotal[2 * p + 1];
    }

    template <class F>
    void forNodes(int l, int r, F f) const {  // the O(log n) nodes that cover a[l..r]
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) f(l++);
            if (r & 1) f(--r);
        }
    }

    long long countLess(int l, int r, T x, bool strict) const {  // # of values < x (strict) or <= x in a[l..r]
        long long res = 0;
        forNodes(l, r, [&](int p) {
            if (p >= n) res += strict ? A[p - n] < x : !(x < A[p - n]);
            else res += countBelow(p, x, strict);
        });
        return res;
    }

    optional<T> firstAtLeast(int l, int r, T x, bool strict) const {  // smallest value > x (strict) or >= x
        optional<T> best;
        forNodes(l, r, [&](int p) {
            optional<T> got;
            if (p >= n) {
                if (strict ? x < A[p - n] : !(A[p - n] < x)) got = A[p - n];
            } else {
                got = firstIn(p, x, strict);
            }
            if (got && (!best || *got < *best)) best = got;
        });
        return best;
    }

    optional<T> lastBelow(int l, int r, T x, bool strict) const {  // largest value < x (strict) or <= x
        optional<T> best;
        forNodes(l, r, [&](int p) {
            optional<T> got;
            if (p >= n) {
                if (strict ? A[p - n] < x : !(x < A[p - n])) got = A[p - n];
            } else {
                got = lastIn(p, x, strict);
            }
            if (got && (!best || *best < *got)) best = got;
        });
        return best;
    }

    S sumLess(int l, int r, T x, bool strict) const {
        S res = 0;
        forNodes(l, r, [&](int p) {
            if (p >= n) {
                if (strict ? A[p - n] < x : !(x < A[p - n])) res += A[p - n];
            } else {
                res += sumBelow(p, x, strict);
            }
        });
        return res;
    }

    S sumAll(int l, int r) const {
        S res = 0;
        forNodes(l, r, [&](int p) { res += p >= n ? S(A[p - n]) : total[p]; });
        return res;
    }

    T xorLess(int l, int r, T x, bool strict) const {
        T res = 0;
        forNodes(l, r, [&](int p) {
            if (p >= n) {
                if (strict ? A[p - n] < x : !(x < A[p - n])) res ^= A[p - n];
            } else {
                res ^= xorBelow(p, x, strict);
            }
        });
        return res;
    }

    T xorAll(int l, int r) const {
        T res = 0;
        forNodes(l, r, [&](int p) { res ^= p >= n ? A[p - n] : xorTotal[p]; });
        return res;
    }

    int fenStart(int p) const { return start[p] + p - 1; }

    int slotOf(int p, T x, bool strict) const {  // # of node p's possible values < x (strict) or <= x
        auto first = vals.begin() + start[p], last = vals.begin() + start[p + 1];
        return int((strict ? lower_bound(first, last, x) : upper_bound(first, last, x)) - first);
    }

    bool listed(int p, T v) const {
        auto first = vals.begin() + start[p], last = vals.begin() + start[p + 1];
        auto it = lower_bound(first, last, v);
        return it != last && !(v < *it);
    }

    void add(int p, T v, int delta) {
        int f = fenStart(p), size = start[p + 1] - start[p];
        for (int j = slotOf(p, v, true) + 1; j <= size; j += j & -j) addAt(f, j, v, delta);
    }

    void addAt(int f, int j, [[maybe_unused]] T v, int delta) {
        counts[f + j] += delta;
        sums[f + j] += S(v) * delta;
        xors[f + j] ^= v;
    }

    long long countBelow(int p, T x, bool strict) const {  // over node p's values < x (strict) or <= x
        long long res = 0;
        int f = fenStart(p);
        for (int j = slotOf(p, x, strict); j > 0; j &= j - 1) res += counts[f + j];
        return res;
    }

    S sumBelow(int p, T x, bool strict) const {  // over node p's values < x (strict) or <= x
        S res = 0;
        int f = fenStart(p);
        for (int j = slotOf(p, x, strict); j > 0; j &= j - 1) res += sums[f + j];
        return res;
    }

    T xorBelow(int p, T x, bool strict) const {  // over node p's values < x (strict) or <= x
        T res = 0;
        int f = fenStart(p);
        for (int j = slotOf(p, x, strict); j > 0; j &= j - 1) res ^= xors[f + j];
        return res;
    }

    T kth(int p, long long k) const {  // node p's k-th smallest value (1-indexed; 1 <= k <= nodeSize[p])
        int f = fenStart(p), size = start[p + 1] - start[p], pos = 0, step = 1;
        while (step * 2 <= size) step *= 2;
        for (; step; step >>= 1) {
            if (pos + step <= size && counts[f + pos + step] < k) {
                pos += step;
                k -= counts[f + pos];
            }
        }
        return vals[start[p] + pos];
    }

    optional<T> firstIn(int p, T x, bool strict) const {  // smallest value > x (strict) or >= x in node p
        long long below = countBelow(p, x, !strict);
        if (below >= nodeSize[p]) return nullopt;
        return kth(p, below + 1);
    }

    optional<T> lastIn(int p, T x, bool strict) const {  // largest value < x (strict) or <= x in node p
        long long below = countBelow(p, x, strict);
        if (below == 0) return nullopt;
        return kth(p, below);
    }
};

// Example:
//     vector<long long> a = {5, 1, 4};
//     MergeSortTreeOffline<long long> t(a, {{1, 7}, {0, 2}});  // later: pointAssign(1, 7) and pointAssign(0, 2)
//     t.countLtX(0, 2, 5);  // 2 (1 and 4)
//     t.pointAssign(1, 7);
//     t.countLtX(0, 2, 5);  // 1 (4)
