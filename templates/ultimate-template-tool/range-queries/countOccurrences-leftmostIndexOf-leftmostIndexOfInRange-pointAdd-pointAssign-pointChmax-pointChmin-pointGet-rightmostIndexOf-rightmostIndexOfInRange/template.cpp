// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rightmostIndexOf-rightmostIndexOfInRange/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countOccurrences getAll leftmostIndexOf leftmostIndexOfInRange pointAdd pointAssign pointChmax pointChmin pointGet rightmostIndexOf rightmostIndexOfInRange
// @data-structure-type: positions
// @letters: same
// @complexities:
//   countOccurrences: log(N)
//   getAll: N
//   leftmostIndexOf: log(N)
//   leftmostIndexOfInRange: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   rightmostIndexOf: log(N)
//   rightmostIndexOfInRange: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: pos[1*N]
//   tags: none
//   other: a[1*N]
//   note: pos maps each value to its sorted indices (an order-statistics tree per value)

// "How many times does x appear in a[l..r]?" and "where is x's first / last copy (in a[l..r])?", with point updates.
// All indices 0-based, ranges inclusive.
// Each value keeps its indices in an order-statistics tree (GCC pb_ds), so a query is two order_of_key calls and an
// assign moves one index from the old value's tree to the new one's. T: any type usable as a std::map key.
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

template <typename T>
struct DynamicOccurrenceLists {
    using IndexSet = __gnu_pbds::tree<int, __gnu_pbds::null_type, less<int>, __gnu_pbds::rb_tree_tag,
                                      __gnu_pbds::tree_order_statistics_node_update>;
    vector<T> a;
    map<T, IndexSet> pos;

    // O(N log N)
    explicit DynamicOccurrenceLists(const vector<T>& arr) : a(arr) {
        for (int i = 0; i < (int)arr.size(); i++) pos[arr[i]].insert(i);
    }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    int countOccurrences(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countOccurrences: needs 0 <= l <= r < size()");
        auto it = pos.find(x);
        if (it == pos.end() || l > r) return 0;
        return int(it->second.order_of_key(r + 1) - it->second.order_of_key(l));
    }

    // O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    int leftmostIndexOf(const T& x) const {
        auto it = pos.find(x);
        return it == pos.end() ? -1 : *it->second.begin();
    }

    // O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    int rightmostIndexOf(const T& x) const {
        auto it = pos.find(x);
        return it == pos.end() ? -1 : *it->second.rbegin();
    }

    // O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    int leftmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = pos.find(x);
        if (it == pos.end()) return -1;
        auto j = it->second.lower_bound(l);
        return j != it->second.end() && *j <= r ? *j : -1;
    }

    // O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    int rightmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = pos.find(x);
        if (it == pos.end()) return -1;
        auto j = it->second.upper_bound(r);
        if (j == it->second.begin()) return -1;
        --j;
        return *j >= l ? *j : -1;
    }

    // O(logN) -- a[i] = v; needs 0 <= i < size(), else throws out_of_range
    void pointAssign(int i, const T& v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAssign: needs 0 <= i < size()");
        if (a[i] == v) return;
        auto it = pos.find(a[i]);
        it->second.erase(i);
        if (it->second.empty()) pos.erase(it);
        pos[v].insert(i);
        a[i] = v;
    }

    // O(1) -- the length of the array
    int size() const { return (int)a.size(); }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return a[i];
    }

    // O(N) -- the whole array (a copy)
    vector<T> getAll() const { return a; }

    // O(logN) -- a[i] += delta; needs 0 <= i < size(), else throws out_of_range
    void pointAdd(int i, const T& delta) {
        if (i < 0 || i >= size()) throw out_of_range("pointAdd: needs 0 <= i < size()");
        pointAssign(i, a[i] + delta);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmax(int i, const T& v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmax: needs 0 <= i < size()");
        if (v > a[i]) pointAssign(i, v);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmin(int i, const T& v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmin: needs 0 <= i < size()");
        if (v < a[i]) pointAssign(i, v);
    }
};
