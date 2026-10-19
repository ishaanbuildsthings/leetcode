// @operations: countOccurrences pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: positions
// @complexities:
//   countOccurrences: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: pos[1*N]
//   tags: none
//   other: a[1*N]
//   note: pos maps each value to its sorted indices (C++: an order-statistics tree per value; Python: plain sorted lists, so an assign is a memmove over that value's occurrences)

// "How many times does x appear in a[l..r]?" with point updates. All indices 0-based, ranges inclusive.
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

    // O(logN) -- # of i in [l, r] with a[i] == x
    int countOccurrences(int l, int r, const T& x) const {
        auto it = pos.find(x);
        if (it == pos.end() || l > r) return 0;
        return int(it->second.order_of_key(r + 1) - it->second.order_of_key(l));
    }

    // O(logN) -- a[i] = v
    void pointAssign(int i, const T& v) {
        if (a[i] == v) return;
        auto it = pos.find(a[i]);
        it->second.erase(i);
        if (it->second.empty()) pos.erase(it);
        pos[v].insert(i);
        a[i] = v;
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return a[i]; }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, const T& delta) { pointAssign(i, a[i] + delta); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, const T& v) { if (v > a[i]) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, const T& v) { if (v < a[i]) pointAssign(i, v); }
};
