// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/sparse.cpp
// @operations: countOccurrences pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: positions
// @complexities:
//   countOccurrences: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: 1
//   build: 1
// @memory:
//   layout: sparse
//   node: pos[2]
//   tags: none
//   other: vals[1]
//   note: per point write, one index in its value's sorted list and one in the list of nonzero positions (order-statistics trees); zeros are counted as the range length minus the nonzero positions in it. No shared pool: every tree owns its memory

// "How many times does x appear in a[l..r]?" with point updates, over any index range [lo, hi] (huge or negative is
// fine); every position starts at 0. Each nonzero value keeps its indices in an order-statistics tree (GCC pb_ds),
// and so does "any nonzero value"; x != 0 is two order_of_key calls, x == 0 is the range length minus the nonzero
// positions in it. T: any type usable as a std::map key (0 must be a value).
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

template <typename T>
struct SparseOccurrenceLists {
    using IndexSet = __gnu_pbds::tree<long long, __gnu_pbds::null_type, less<long long>, __gnu_pbds::rb_tree_tag,
                                      __gnu_pbds::tree_order_statistics_node_update>;
    long long lo, hi;
    // splitmix64 with a random per-run offset: anti-hash tests can't predict buckets, so the tables stay O(1)
    struct SafeHash {
        size_t operator()(long long x) const {
            static const unsigned long long seed = chrono::steady_clock::now().time_since_epoch().count();
            unsigned long long z = (unsigned long long)x + seed + 0x9e3779b97f4a7c15ULL;
            z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
            z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
            return z ^ (z >> 31);
        }
    };
    unordered_map<long long, T, SafeHash> vals;  // nonzero values only
    map<T, IndexSet> pos;                        // nonzero values only

    // O(1) expected -- a[i]
    T valueAt(long long i) const {
        auto it = vals.find(i);
        return it == vals.end() ? T(0) : it->second;
    }
    IndexSet nz;                       // indices holding a nonzero value

    // O(1) -- all zeros over [lo, hi]
    SparseOccurrenceLists(long long lo, long long hi) : lo(lo), hi(hi) {}

    // O(logU) -- # of i in [l, r] with a[i] == x
    long long countOccurrences(long long l, long long r, const T& x) const {
        if (l > r) return 0;
        if (x == T(0)) return (r - l + 1) - (long long)(nz.order_of_key(r + 1) - nz.order_of_key(l));
        auto it = pos.find(x);
        if (it == pos.end()) return 0;
        return (long long)(it->second.order_of_key(r + 1) - it->second.order_of_key(l));
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        T old = pointGet(i);
        if (old == v) return;
        if (old != T(0)) {
            auto it = pos.find(old);
            it->second.erase(i);
            if (it->second.empty()) pos.erase(it);
        } else {
            nz.insert(i);
        }
        if (v != T(0)) {
            pos[v].insert(i);
            vals[i] = v;
        } else {
            nz.erase(i);
            vals.erase(i);
        }
    }

    // a[i]
    T pointGet(long long i) const { return valueAt(i); }

    // a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }
};
