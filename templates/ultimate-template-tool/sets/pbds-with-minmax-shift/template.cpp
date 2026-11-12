// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/pbds-with-minmax-shift/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: add clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max medianHigh medianLow min pop popMax popMin remove removeInValRange shiftAll size smallestGtX smallestGteX
// @data-structure-type: pbds
// @values: online
// @keys: numbers
// @tracks: minmax shift
// @complexities:
//   add: log(N)
//   clear: 1 amortized
//   count: log(N)
//   countDistinct: 1
//   countGtX: log(N)
//   countGteX: log(N)
//   countInValRange: log(N)
//   countLtX: log(N)
//   countLteX: log(N)
//   firstIndex: log(N)
//   kth: log(N)
//   largestLtX: log(N)
//   largestLteX: log(N)
//   lastIndex: log(N)
//   max: 1
//   medianHigh: log(N)
//   medianLow: log(N)
//   min: 1
//   pop: log(N)
//   popMax: log(N)
//   popMin: log(N)
//   remove: log(N)
//   removeInValRange: log(N) amortized
//   shiftAll: 1
//   size: 1
//   smallestGtX: log(N)
//   smallestGteX: log(N)
//   build: 1
// @memory:
//   layout: none
//   node: key[2*N] size[1*N] color[1*N]
//   tags: none
//   other: children[2*N] parent[1*N]
//   note: N = copies present: one red-black tree node per copy, keyed (value, id), with its subtree size

#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

// Ordered multiset (online: any values, nothing known ahead) on GCC's order-statistics tree (pb_ds): one node per
// copy, keyed (value, id) so equal values stay distinct. No sums, no bulk adds. T: any type with < (and +1 for le).
template <typename T>
struct PbdsMultiset {
    template <class K>
    static K noneOf() {  // the lowest value of K, part by part for pairs and tuples
        if constexpr (is_arithmetic_v<K>) return numeric_limits<K>::lowest();
        else return apply([](auto... parts) { return K{noneOf<decltype(parts)>()...}; }, K{});
    }
    // what largestLtX, smallestGtX, ... return when nothing qualifies: compare with ms.NONE. It is the lowest T, so a
    // real value equal to it reads as "nothing"
    static inline const T NONE = noneOf<T>();

    using Tree = __gnu_pbds::tree<pair<T, int>, __gnu_pbds::null_type, less<pair<T, int>>, __gnu_pbds::rb_tree_tag,
                                  __gnu_pbds::tree_order_statistics_node_update>;
    Tree t;
    int ids = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    T mn{}, mx{};  // kept current by addRaw while n > 0
    T off = 0;  // every value v is stored as v - off: shiftAll only moves off

    // O(1) -- an empty multiset
    PbdsMultiset() {}

    long long insert(T x, long long c) {  // c = +1 or -1; returns x's new count
        if (c > 0) {
            long long k = countOf(x);
            if (!k) d++;
            t.insert({x, ids++});
            return k + 1;
        }
        t.erase(t.lower_bound({x, INT_MIN}));
        long long k = countOf(x);
        if (!k) d--;
        return k;
    }

    long long lt(T x) { return (long long)t.order_of_key({x, INT_MIN}); }
    long long le(T x) { return (long long)t.order_of_key({x, INT_MAX}); }
    T kthAt(long long k) { return t.find_by_order(k - 1)->first; }
    long long countOf(T x) { return le(x) - lt(x); }

    Info kthInfo(long long k) {  // the k-th smallest, copies before it, its copies
        T v = kthAt(k);
        long long b = lt(v);
        return {v, b, le(v) - b};
    }

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes); keeps min / max current
        n += c;
        long long f = insert(x, c);  // x's new count
        if (c > 0) {
            if (n == c) {  // the set was empty
                mn = mx = x;
                return;
            }
            if (x < mn) mn = x;
            if (x > mx) mx = x;
        } else {
            if (!n) return;
            if (!f) {  // x is gone: it may have been the min / max
                if (x == mn) mn = kthAt(1);
                if (x == mx) mx = kthAt(n);
            }
        }
    }

    void resetCached() {  // nothing counted: as newly built
        n = d = 0;
        off = 0;
    }

    void clearData() {
        t.clear();
        ids = 0;
    }

    // O(logN) -- add one copy of x
    void add(T x) {
        x -= off;
        addRaw(x, 1);
    }

    // O(1 amortized) -- remove everything (fine on an empty set): afterwards it is as if newly built (same constructor
    // arguments), so reuse it instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(logN) -- how many copies of x (0 if x isn't there, e.g. on an empty set)
    long long count(T x) {
        x -= off;
        return countOf(x);
    }

    // O(1) -- how many distinct values (0 if empty)
    long long countDistinct() {
        return d;
    }

    // O(logN) -- how many values > x (0 if there are none, e.g. on an empty set)
    long long countGtX(T x) {
        x -= off;
        return n - le(x);
    }

    // O(logN) -- how many values >= x (0 if there are none, e.g. on an empty set)
    long long countGteX(T x) {
        x -= off;
        return n - lt(x);
    }

    // O(logN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        lo -= off, hi -= off;
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN) -- how many values < x (0 if there are none, e.g. on an empty set)
    long long countLtX(T x) {
        x -= off;
        return lt(x);
    }

    // O(logN) -- how many values <= x (0 if there are none, e.g. on an empty set)
    long long countLteX(T x) {
        x -= off;
        return le(x);
    }

    // O(logN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in
    // the set
    long long firstIndex(T x) {
        x -= off;
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN) -- the value at sorted position i, 0-indexed: kth(0) is the smallest, kth(1) the 2nd smallest,
    // kth(size - 1) the largest (copies count: in {2, 2, 5}, kth(1) is 2); throws out_of_range unless 0 <= i < size
    T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return T(kthAt(i + 1) + off);
    }

    // O(logN) -- largest value < x; ms.NONE if there is none
    T largestLtX(T x) {
        x -= off;
        long long c = lt(x);
        if (!c) return NONE;
        return T(kthAt(c) + off);
    }

    // O(logN) -- largest value <= x; ms.NONE if there is none
    T largestLteX(T x) {
        x -= off;
        long long c = le(x);
        if (!c) return NONE;
        return T(kthAt(c) + off);
    }

    // O(logN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is
    // not in the set
    long long lastIndex(T x) {
        x -= off;
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(1) -- largest value; throws out_of_range if empty
    T max() {
        if (!n) throw out_of_range("max: the set is empty");
        return T(mx + off);
    }

    // O(logN) -- upper median: the (floor(size/2) + 1)-th smallest value; throws out_of_range if empty
    T medianHigh() {
        if (!n) throw out_of_range("medianHigh: the set is empty");
        return T(kthAt(n / 2 + 1) + off);
    }

    // O(logN) -- lower median: the ceil(size/2)-th smallest value; throws out_of_range if empty
    T medianLow() {
        if (!n) throw out_of_range("medianLow: the set is empty");
        return T(kthAt((n + 1) / 2) + off);
    }

    // O(1) -- smallest value; throws out_of_range if empty
    T min() {
        if (!n) throw out_of_range("min: the set is empty");
        return T(mn + off);
    }

    // O(logN) -- remove and return the value at sorted position i, 0-indexed: pop(0) removes the smallest (= popMin()),
    // pop(size - 1) the largest (copies count); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN) -- remove and return the largest value; throws out_of_range if empty
    T popMax() {
        if (!n) throw out_of_range("popMax: the set is empty");
        T v = mx;
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN) -- remove and return the smallest value; throws out_of_range if empty
    T popMin() {
        if (!n) throw out_of_range("popMin: the set is empty");
        T v = mn;
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN) -- remove one copy of x if present; returns how many were removed (0 or 1: 0 if x isn't there, e.g. on an
    // empty set)
    long long remove(T x) {
        x -= off;
        if (!countOf(x)) return 0;
        addRaw(x, -1);
        return 1;
    }

    // O(logN amortized) -- remove every value v with lo <= v <= hi; returns how many copies were removed (0 if lo > hi)
    long long removeInValRange(T lo, T hi) {
        lo -= off, hi -= off;
        if (hi < lo) return 0;
        long long removed = 0;
        while (n) {  // the smallest value >= lo, while it is <= hi
            auto it = t.lower_bound({lo, INT_MIN});
            if (it == t.end() || hi < it->first) break;
            addRaw(it->first, -1), removed++;
        }
        return removed;
    }

    // O(1) -- add d to every value (d may be negative; nothing happens on an empty set)
    void shiftAll(T d) {
        off += d;
    }

    // O(1) -- how many values (copies count; 0 if empty)
    long long size() {
        return n;
    }

    // O(logN) -- smallest value > x; ms.NONE if there is none
    T smallestGtX(T x) {
        x -= off;
        long long c = le(x);
        if (c == n) return NONE;
        return T(kthAt(c + 1) + off);
    }

    // O(logN) -- smallest value >= x; ms.NONE if there is none
    T smallestGteX(T x) {
        x -= off;
        long long c = lt(x);
        if (c == n) return NONE;
        return T(kthAt(c + 1) + off);
    }
};
