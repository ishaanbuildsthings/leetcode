// @operations: countDistinct pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: BIT
// @complexities:
//   countDistinct: log(U)*log(U)
//   pointAdd: log(U)*log(U)
//   pointAssign: log(U)*log(U)
//   pointChmax: log(U)*log(U)
//   pointChmin: log(U)*log(U)
//   pointGet: 1
//   build: 1
// @memory:
//   layout: sparse
//   node: sets[3*log(U)] last[3*log(U)]
//   tags: none
//   other: nxt[1] chains[1] vals[1]
//   note: per point write, at most 3 nxt changes, each touching the O(logU) Fenwick nodes above its position; node j keeps an ordered set of the nxt values below it (C++: pb_ds trees in a hash map; Python: bucketed SortedLists, below, in a dict). No shared pool: every tree owns its memory

// Range count distinct with point updates in O(log^2 U), online, over any index range [lo, hi] (huge or negative is
// fine); every position starts at 0. Only nonzero positions are tracked: nxt[i] = the next position with the same
// value (none: NONE = hi + 1), and the distinct nonzero values in [l, r] are #{i in [l, r] : nxt[i] > r}, a 2D count
// on a Fenwick tree (hash maps over offsets) whose node j keeps an order-statistics set (GCC pb_ds) of the nxt values
// < NONE below it, plus a plain count of the NONE ones. 0 is one more distinct value when the range has fewer nonzero
// positions than its length. An assign changes at most 3 nxt values, in an order that never lets two positions share
// an nxt value. T: any type usable as a std::map key (0 must be a value).
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

template <typename T>
struct SparseDistinctBIT {
    using OrderedSet = __gnu_pbds::tree<long long, __gnu_pbds::null_type, less<long long>, __gnu_pbds::rb_tree_tag,
                                        __gnu_pbds::tree_order_statistics_node_update>;
    long long lo, hi, n, none;
    unordered_map<long long, T> vals;          // nonzero values only
    unordered_map<long long, long long> nxt;   // tracked (nonzero) positions only
    unordered_map<long long, long long> last;  // Fenwick tree counting positions with nxt == NONE
    unordered_map<long long, OrderedSet> sets; // Fenwick tree of nxt values < NONE
    map<T, set<long long>> chains;             // nonzero value -> sorted positions

    // O(1) -- all zeros over [lo, hi]
    SparseDistinctBIT(long long lo, long long hi) : lo(lo), hi(hi), n(hi - lo + 1), none(hi + 1) {}

    void lastAdd(long long i, long long d) {
        for (long long j = i - lo + 1; j <= n; j += j & -j) last[j] += d;
    }

    // how many tracked positions p <= x have nxt[p] > r (0 for x < lo)
    long long countPast(long long x, long long r) const {
        long long res = 0;
        for (long long j = x - lo + 1; j > 0; j &= j - 1) {
            auto lt = last.find(j);
            if (lt != last.end()) res += lt->second;
            auto st = sets.find(j);
            if (st != sets.end()) res += (long long)(st->second.size() - st->second.order_of_key(r + 1));
        }
        return res;
    }

    // O(log^2 U) -- nxt[i] = v (LLONG_MIN: i is not tracked, it holds 0)
    void setNxt(long long i, long long v) {
        auto it = nxt.find(i);
        long long old = it == nxt.end() ? LLONG_MIN : it->second;
        if (old == v) return;
        if (old == none) lastAdd(i, -1);
        else if (old != LLONG_MIN)
            for (long long j = i - lo + 1; j <= n; j += j & -j) {
                auto st = sets.find(j);
                st->second.erase(old);
                if (st->second.empty()) sets.erase(st);
            }
        if (v == none) lastAdd(i, 1);
        else if (v != LLONG_MIN)
            for (long long j = i - lo + 1; j <= n; j += j & -j) sets[j].insert(v);
        if (v == LLONG_MIN) nxt.erase(i);
        else nxt[i] = v;
    }

    // O(log^2 U) -- # of distinct values in a[l..r]
    long long countDistinct(long long l, long long r) const {
        if (l > r) return 0;
        long long nonzero = countPast(r, lo - 1) - countPast(l - 1, lo - 1);  // every nxt is > lo - 1
        return countPast(r, r) - countPast(l - 1, r) + (nonzero < r - l + 1);
    }

    // O(log^2 U) -- a[i] = v; rewires i's old predecessor, i's new predecessor, and i
    void pointAssign(long long i, T v) {
        T old = pointGet(i);
        if (old == v) return;
        if (old != T(0)) {
            auto oldIt = chains.find(old);
            set<long long>& from = oldIt->second;
            auto it = from.find(i);
            setNxt(i, LLONG_MIN);  // unlink i first, so its successor is free for its predecessor
            if (it != from.begin()) {
                auto nx = next(it);
                setNxt(*prev(it), nx == from.end() ? none : *nx);
            }
            from.erase(it);
            if (from.empty()) chains.erase(oldIt);
        }
        if (v != T(0)) {
            set<long long>& to = chains[v];
            auto jt = to.insert(i).first;
            auto nx = next(jt);
            if (jt != to.begin()) setNxt(*prev(jt), i);  // move the predecessor off the successor first, then hand it to i
            setNxt(i, nx == to.end() ? none : *nx);
            vals[i] = v;
        } else {
            vals.erase(i);
        }
    }

    // O(1) expected -- a[i]
    T pointGet(long long i) const {
        auto it = vals.find(i);
        return it == vals.end() ? T(0) : it->second;
    }

    // a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
