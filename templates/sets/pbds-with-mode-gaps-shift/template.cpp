// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sets/pbds-with-mode-gaps-shift/template.cpp
// @operations: add clear count countDistinct countGtX countGteX countInValRange countLtX countLteX firstIndex kth largestLtX largestLteX lastIndex max maxGap medianHigh medianLow min minAdjacentDiff mode pop popMax popMin remove removeInValRange shiftAll size smallestGtX smallestGteX
// @data-structure-type: pbds
// @values: online
// @keys: numbers
// @tracks: mode gaps shift
// @complexities:
//   add: log(N)
//   clear: N
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
//   max: log(N)
//   maxGap: 1 amortized
//   medianHigh: log(N)
//   medianLow: log(N)
//   min: log(N)
//   minAdjacentDiff: 1 amortized
//   mode: 1
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
    using Tree = __gnu_pbds::tree<pair<T, int>, __gnu_pbds::null_type, less<pair<T, int>>, __gnu_pbds::rb_tree_tag,
                                  __gnu_pbds::tree_order_statistics_node_update>;
    Tree t;
    int ids = 0;
    long long n = 0, d = 0;
    struct Info { T v; long long before, c; };  // a value, copies before it, its copies
    map<long long, set<T>> bk;  // mode: count -> the values with that many copies
    multiset<long long> gaps;  // differences between neighbouring distinct values
    long long dups = 0;  // values with 2+ copies
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

    void addRaw(T x, long long c) {  // c copies of x (c < 0 removes)
        n += c;
        long long f = insert(x, c);  // x's new count
        long long g = f - c;  // x's old count
        {  // mode: x moves from the bucket of its old count to its new one
            if (g) {
                auto it = bk.find(g);
                it->second.erase(x);
                if (it->second.empty()) bk.erase(it);
            }
            if (f) bk[f].insert(x);
        }
        {  // gaps
            if ((g >= 2) != (f >= 2)) dups += f >= 2 ? 1 : -1;  // values with 2+ copies (then the smallest difference is 0)
            if (!g || !f) {  // x appeared or disappeared: the gap between its neighbours splits or comes back
                long long cl = lt(x), ce = le(x);  // (stored values: the public ops would shift x again)
                optional<T> p, q;
                if (cl) p = kthAt(cl);
                if (ce < n) q = kthAt(ce + 1);
                auto drop = [&](long long v) { gaps.erase(gaps.find(v)); };
                if (f) {
                    if (p && q) drop((long long)*q - (long long)*p);
                    if (p) gaps.insert((long long)x - (long long)*p);
                    if (q) gaps.insert((long long)*q - (long long)x);
                } else {
                    if (p) drop((long long)x - (long long)*p);
                    if (q) drop((long long)*q - (long long)x);
                    if (p && q) gaps.insert((long long)*q - (long long)*p);
                }
            }
        }
    }

    void resetCached() {  // nothing counted: as newly built
        bk.clear();
        gaps.clear(), dups = 0;
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

    // O(N) -- remove everything: afterwards it is as if newly built (same constructor arguments), so reuse it instead of building a new one
    void clear() {
        clearData();
        resetCached();
    }

    // O(logN) -- how many copies of x
    long long count(T x) {
        x -= off;
        return countOf(x);
    }

    // O(1) -- how many distinct values
    long long countDistinct() {
        return d;
    }

    // O(logN) -- how many values > x
    long long countGtX(T x) {
        x -= off;
        return n - le(x);
    }

    // O(logN) -- how many values >= x
    long long countGteX(T x) {
        x -= off;
        return n - lt(x);
    }

    // O(logN) -- how many values v with lo <= v <= hi (0 if lo > hi)
    long long countInValRange(T lo, T hi) {
        lo -= off, hi -= off;
        return lo <= hi ? le(hi) - lt(lo) : 0;
    }

    // O(logN) -- how many values < x
    long long countLtX(T x) {
        x -= off;
        return lt(x);
    }

    // O(logN) -- how many values <= x
    long long countLteX(T x) {
        x -= off;
        return le(x);
    }

    // O(logN) -- 0-indexed position of the first copy of x in sorted order (= how many values < x); -1 if x is not in the set
    long long firstIndex(T x) {
        x -= off;
        return countOf(x) ? lt(x) : -1;
    }

    // O(logN) -- the value at sorted position i (0-indexed: kth(0) is the min); throws out_of_range unless 0 <= i < size
    T kth(long long i) {
        if (i < 0 || i >= n) throw out_of_range("kth: needs 0 <= i < size");
        return T(kthAt(i + 1) + off);
    }

    // O(logN) -- largest value < x; nullopt if there is none
    optional<T> largestLtX(T x) {
        x -= off;
        long long c = lt(x);
        if (!c) return nullopt;
        return T(kthAt(c) + off);
    }

    // O(logN) -- largest value <= x; nullopt if there is none
    optional<T> largestLteX(T x) {
        x -= off;
        long long c = le(x);
        if (!c) return nullopt;
        return T(kthAt(c) + off);
    }

    // O(logN) -- 0-indexed position of the last copy of x in sorted order (= how many values <= x, minus 1); -1 if x is not in the set
    long long lastIndex(T x) {
        x -= off;
        return countOf(x) ? le(x) - 1 : -1;
    }

    // O(logN) -- largest value; nullopt if empty
    optional<T> max() {
        if (!n) return nullopt;
        return T(kthAt(n) + off);
    }

    // O(1 amortized) -- largest difference between two neighbouring distinct values; nullopt if fewer than 2 distinct values
    optional<long long> maxGap() {
        if (d < 2) return nullopt;
        return *gaps.rbegin();
    }

    // O(logN) -- upper median: the (floor(size/2) + 1)-th smallest value; nullopt if empty
    optional<T> medianHigh() {
        if (!n) return nullopt;
        return T(kthAt(n / 2 + 1) + off);
    }

    // O(logN) -- lower median: the ceil(size/2)-th smallest value; nullopt if empty
    optional<T> medianLow() {
        if (!n) return nullopt;
        return T(kthAt((n + 1) / 2) + off);
    }

    // O(logN) -- smallest value; nullopt if empty
    optional<T> min() {
        if (!n) return nullopt;
        return T(kthAt(1) + off);
    }

    // O(1 amortized) -- smallest difference between two values in the set (0 if some value has 2+ copies); nullopt if fewer than 2 values
    optional<long long> minAdjacentDiff() {
        if (n < 2) return nullopt;
        if (dups) return 0LL;
        return *gaps.begin();
    }

    // O(1) -- (a most frequent value, its count); nullopt if empty. C++ returns the smallest of the most frequent values
    optional<pair<T, long long>> mode() {
        if (!n) return nullopt;
        auto& [f, vs] = *bk.rbegin();
        return pair<T, long long>{T(*vs.begin() + off), f};
    }

    // O(logN) -- remove and return the value at sorted position i (0-indexed: pop(0) is popMin()); throws out_of_range unless 0 <= i < size
    T pop(long long i) {
        if (i < 0 || i >= n) throw out_of_range("pop: needs 0 <= i < size");
        T v = kthAt(i + 1);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN) -- remove and return the largest value; nullopt if empty
    optional<T> popMax() {
        if (!n) return nullopt;
        T v = kthAt(n);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN) -- remove and return the smallest value; nullopt if empty
    optional<T> popMin() {
        if (!n) return nullopt;
        T v = kthAt(1);
        addRaw(v, -1);
        return T(v + off);
    }

    // O(logN) -- remove one copy of x if present; returns how many were removed (0 or 1)
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

    // O(1) -- add d to every value (d may be negative)
    void shiftAll(T d) {
        off += d;
    }

    // O(1) -- how many values (copies count)
    long long size() {
        return n;
    }

    // O(logN) -- smallest value > x; nullopt if there is none
    optional<T> smallestGtX(T x) {
        x -= off;
        long long c = le(x);
        if (c == n) return nullopt;
        return T(kthAt(c + 1) + off);
    }

    // O(logN) -- smallest value >= x; nullopt if there is none
    optional<T> smallestGteX(T x) {
        x -= off;
        long long c = lt(x);
        if (c == n) return nullopt;
        return T(kthAt(c + 1) + off);
    }
};
