// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rightmostIndexOf-rightmostIndexOfInRange/sparse.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countOccurrences leftmostIndexOf leftmostIndexOfInRange pointAdd pointAssign pointChmax pointChmin pointGet rightmostIndexOf rightmostIndexOfInRange
// @data-structure-type: positions
// @complexities:
//   countOccurrences: log(U)
//   leftmostIndexOf: log(U)*log(U)
//   leftmostIndexOfInRange: log(U)*log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: 1
//   rightmostIndexOf: log(U)*log(U)
//   rightmostIndexOfInRange: log(U)*log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: pos[2]
//   tags: none
//   other: vals[1]
//   note: per point write, one index in its value's sorted list and one in the list of nonzero positions (order-statistics trees); zeros are counted as the range length minus the nonzero positions in it. No shared pool: every tree owns its memory

// "How many times does x appear in a[l..r]?" and "where is x's first / last copy (in a[l..r])?" with point updates,
// over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Each nonzero value keeps its
// indices in an order-statistics tree (GCC pb_ds), and so does "any nonzero value"; x != 0 is two order_of_key calls,
// x == 0 is the range length minus the nonzero positions in it. x == 0's first / last copy is a binary search over
// [l, r] for the first never-written index, O(log^2 U). T: any type usable as a std::map key (0 must be a value).
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

    // O(logU) -- # of i in [l, r] with a[i] == x; needs lo <= l <= r <= hi, else throws out_of_range
    long long countOccurrences(long long l, long long r, const T& x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("countOccurrences: needs lo <= l <= r <= hi");
        if (l > r) return 0;
        if (x == T(0)) return (r - l + 1) - (long long)(nz.order_of_key(r + 1) - nz.order_of_key(l));
        auto it = pos.find(x);
        if (it == pos.end()) return 0;
        return (long long)(it->second.order_of_key(r + 1) - it->second.order_of_key(l));
    }

    // O(logU * logU) -- the smallest i in [lo, hi] with a[i] == x, or lo - 1 if there is none
    long long leftmostIndexOf(const T& x) const { return leftmostIndexOfInRange(lo, hi, x); }

    // O(logU * logU) -- the largest i in [lo, hi] with a[i] == x, or lo - 1 if there is none
    long long rightmostIndexOf(const T& x) const { return rightmostIndexOfInRange(lo, hi, x); }

    // O(logU * logU) -- the smallest i in [l, r] with a[i] == x, or lo - 1 if there is none; needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostIndexOfInRange(long long l, long long r, const T& x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostIndexOfInRange: needs lo <= l <= r <= hi");
        if (l > r) return lo - 1;
        if (x == T(0)) {
            if (!vals.count(l)) return l;
            // the smallest m with a zero in [l, m] (r + 1: none)
            long long base = nz.order_of_key(l), a = l, b = r + 1;
            while (a < b) {
                long long m = a + (b - a) / 2;
                if ((long long)nz.order_of_key(m + 1) - base < m - l + 1) b = m;
                else a = m + 1;
            }
            return a <= r ? a : lo - 1;
        }
        auto it = pos.find(x);
        if (it == pos.end()) return lo - 1;
        auto j = it->second.lower_bound(l);
        return j != it->second.end() && *j <= r ? *j : lo - 1;
    }

    // O(logU * logU) -- the largest i in [l, r] with a[i] == x, or lo - 1 if there is none; needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostIndexOfInRange(long long l, long long r, const T& x) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostIndexOfInRange: needs lo <= l <= r <= hi");
        if (l > r) return lo - 1;
        if (x == T(0)) {
            if (!vals.count(r)) return r;
            // the largest m with a zero in [m, r] (l - 1: none)
            long long top = nz.order_of_key(r + 1), a = l - 1, b = r;
            while (a < b) {
                long long m = a + (b - a + 1) / 2;
                if (top - (long long)nz.order_of_key(m) < r - m + 1) a = m;
                else b = m - 1;
            }
            return a >= l ? a : lo - 1;
        }
        auto it = pos.find(x);
        if (it == pos.end()) return lo - 1;
        auto j = it->second.upper_bound(r);
        if (j == it->second.begin()) return lo - 1;
        return *prev(j) >= l ? *prev(j) : lo - 1;
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
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

    // O(1) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return valueAt(i);
    }

    // O(logU) -- a[i] += delta; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmax(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmax: needs lo <= i <= hi");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmin(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmin: needs lo <= i <= hi");
        if (v < pointGet(i)) pointAssign(i, v);
    }
};
