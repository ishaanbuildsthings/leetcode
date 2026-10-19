// @operations: countDistinct pointAdd pointAssign pointChmax pointChmin pointGet
// @data-structure-type: BIT
// @complexities:
//   countDistinct: log^2(N)
//   pointAdd: log^2(N)
//   pointAssign: log^2(N)
//   pointChmax: log^2(N)
//   pointChmin: log^2(N)
//   pointGet: 1
//   build: N*log^2(N)
// @memory:
//   layout: none
//   node: sets[1*N*log(N)] last[1*N]
//   tags: none
//   other: a[1*N] nxt[1*N] chains[1*N]
//   note: Fenwick node j keeps an ordered set of the nxt values in its lowbit(j) positions, about N*log(N)/2 keys in all; those are balanced-tree / bucket entries, several times heavier than a plain int (measured ~100 MB peak in C++ at N = 2e5)

// Range count distinct with point updates in O(log^2 N), online. All indices 0-based, ranges inclusive [l, r].
// nxt[i] = next j > i with a[j] == a[i], else n. a[l..r] has one distinct value per position whose next occurrence
// is past r, so countDistinct(l, r) = #{i in [l, r] : nxt[i] > r}, a 2D count; an assign changes at most 3 nxt values.
// Positions with nxt[i] == n (last occurrences) always count, so a plain Fenwick tree tracks them. Every other nxt
// value is a distinct position < n, kept in a Fenwick tree of order-statistics sets (GCC pb_ds): node j holds the nxt
// values of the lowbit(j) positions it covers, so a prefix count of "nxt > r" visits log N nodes with one
// order_of_key each. chains[v] = the positions holding value v, for the predecessor / successor an assign rewires.
// T: any type usable as a std::map key.
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>

template <typename T>
struct DynamicDistinctBIT {
    using OrderedSet = __gnu_pbds::tree<int, __gnu_pbds::null_type, less<int>, __gnu_pbds::rb_tree_tag,
                                        __gnu_pbds::tree_order_statistics_node_update>;
    int n;
    vector<T> a;
    vector<int> nxt, last;    // last: Fenwick tree counting positions with nxt == n
    vector<OrderedSet> sets;  // 1-indexed Fenwick tree of nxt values < n
    map<T, set<int>> chains;

    // O(N log^2 N)
    explicit DynamicDistinctBIT(const vector<T>& arr) : n((int)arr.size()), a(arr), nxt(n, n), last(n + 1), sets(n + 1) {
        map<T, int> prev;
        for (int i = 0; i < n; i++) {
            auto it = prev.find(arr[i]);
            if (it != prev.end()) nxt[it->second] = i;
            prev[arr[i]] = i;
            chains[arr[i]].insert(i);
        }
        for (int i = 1; i <= n; i++) {
            last[i] += nxt[i - 1] == n;
            int j = i + (i & -i);
            if (j <= n) last[j] += last[i];
            for (int k = i - (i & -i); k < i; k++)
                if (nxt[k] < n) sets[i].insert(nxt[k]);
        }
    }

    void lastAdd(int i, int d) {
        for (i++; i <= n; i += i & -i) last[i] += d;
    }

    // how many i in [0, x] have nxt[i] > r (x = -1 gives 0)
    int countPast(int x, int r) const {
        int res = 0;
        for (int j = x + 1; j > 0; j &= j - 1) res += last[j] + int(sets[j].size() - sets[j].order_of_key(r + 1));
        return res;
    }

    // O(log^2 N) -- nxt[i] = v
    void setNxt(int i, int v) {
        int old = nxt[i];
        if (old == v) return;
        if (old == n) lastAdd(i, -1);
        else for (int j = i + 1; j <= n; j += j & -j) sets[j].erase(old);
        if (v == n) lastAdd(i, 1);
        else for (int j = i + 1; j <= n; j += j & -j) sets[j].insert(v);
        nxt[i] = v;
    }

    // O(log^2 N) -- # of distinct values in a[l..r]
    int countDistinct(int l, int r) const { return l > r ? 0 : countPast(r, r) - countPast(l - 1, r); }

    // O(log^2 N) -- a[i] = v; rewires i's old predecessor, i's new predecessor, and i. The order matters: no two
    // positions may share an nxt value < n at any moment, because the order-statistics trees are sets
    void pointAssign(int i, const T& v) {
        if (a[i] == v) return;
        auto oldIt = chains.find(a[i]);
        set<int>& from = oldIt->second;
        auto it = from.find(i);
        setNxt(i, n);  // unlink i first, so its successor is free for its predecessor
        if (it != from.begin()) {
            auto nx = next(it);
            setNxt(*prev(it), nx == from.end() ? n : *nx);
        }
        from.erase(it);
        if (from.empty()) chains.erase(oldIt);
        set<int>& to = chains[v];
        auto jt = to.insert(i).first;
        auto nx = next(jt);
        if (jt != to.begin()) setNxt(*prev(jt), i);  // move the predecessor off the successor first, then hand it to i
        setNxt(i, nx == to.end() ? n : *nx);
        a[i] = v;
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return a[i]; }

    // O(log^2 N) -- a[i] += delta
    void pointAdd(int i, const T& delta) { pointAssign(i, a[i] + delta); }

    // O(log^2 N) -- a[i] = max(a[i], v)
    void pointChmax(int i, const T& v) { if (v > a[i]) pointAssign(i, v); }

    // O(log^2 N) -- a[i] = min(a[i], v)
    void pointChmin(int i, const T& v) { if (v < a[i]) pointAssign(i, v); }
};
